import os
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)

from .main_controller import MainController

from models import User, History, Turn
from models import UserDao, HistoryDao, TurnDao

from models.interface_iqa import InterfaceIQA

from .utils import save_results, send_typing_action, load_results


class ConversationController(MainController):

    STATES = {
        "iqa_1": 1,
    }

    def __init__(self, dispatcher):
        MainController.__init__(self, dispatcher)
        self.__process_handlers()
        self.user_dao = UserDao(self._database)
        self.history_dao = HistoryDao(self._database)
        self.turn_dao = TurnDao(self._database)
        self.interface_iqa = InterfaceIQA(os.getenv("USE_ONTOEX") == "yes")

    def welcome_cmd(self, update, context):
        if context.args:
            if context.args[0] == "start_iqa":
                return self.start_iqa_cmd(update, context)
        else:
            self.message_dialogue.send_welcome_message(
                update.message, context.bot, first_call=True
            )

    def start_iqa_cmd(self, update, context):
        if update.effective_chat.type == "private":
            from_user = update.message.from_user
            exists, user = self.user_dao.get_user_by_id(from_user.id)
            # Adicionar usuário no BD caso não exista
            if not exists:
                user.set_basic_info(from_user.id, from_user.first_name)
                self.user_dao.add_user(user)

            # Adicionar histórico atual no BD
            history = History(bot_id=context.bot.getMe().id)
            history.id = self.history_dao.add_history(from_user.id, history)

            context.user_data["history_id"] = history.id
            context.user_data["has_dialogue"] = False

            self.message_dialogue.send_start_message(
                update.message, context.bot
            )
            return self.STATES["iqa_1"]
        else:
            self.message_dialogue.send_start_message(
                update.message, context.bot, "public"
            )

    def done_cmd(self, update, context):
        has_dialogue = context.user_data["has_dialogue"]
        if has_dialogue:
            self.message_dialogue.send_goodbye_message(
                update.message, context.bot, redirect=True
            )
            return ConversationHandler.END
        else:
            self.message_dialogue.send_goodbye_message(
                update.message, context.bot
            )

    @send_typing_action
    def msg_handler(self, update, context):
        loading = self.message_dialogue.loading_message(update, context)
        text = update.message.text
        if update.message.reply_to_message:
            quoted_text = update.message.reply_to_message.text
            text = quoted_text + "[QUOTED_TEXT]" + text

        # Mensagem a ser enviada para o usuário
        answer = self.interface_iqa.get_answer(
            text,
            update.message.from_user.id,
            context.user_data["history_id"],
            context.bot.getMe().id,
        )

        # Deletar mensagem de loading após obter alguma resposta do IQA
        loading.delete()
        self.message_dialogue.reply_answer(update.message, answer)
        if answer["success"]:
            context.user_data["has_dialogue"] = True
            # Criar Turno
            turn = Turn(message_id=update.message.message_id)
            turn.set_bot_answer(
                answer["text"], answer["results"], answer["related"]
            )
            turn.user_text = update.message.text
            turn.id = self.turn_dao.add_turn(
                context.user_data["history_id"], turn
            )

            if turn.results is not None:
                # Salvar dataframe com resultados no disco
                save_results(
                    update.message.from_user.id,
                    turn.id,
                    context.bot.getMe().id,
                    turn.results,
                    answer["details"],
                )
            if turn.suggestions:
                # Salvar sugestões no banco de dados
                self.turn_dao.add_suggestions(turn.id, turn.suggestions)

            # Dados sobre a mensagem atual
            context.user_data[turn.message_id] = {
                "turn_id": turn.id,
                "confidence": None,
                "has_evaluation": answer["eval_options"],
            }

    def answer_button(self, update, context):
        query = update.callback_query
        command, list_index, user_message_id, value = query.data.split("_")
        # Botão que realiza a paginação dos resultados
        if command.startswith("result"):
            query.answer("updated content")
            index = int(value)
            message_info = context.user_data[int(user_message_id)]
            rating_options = False
            if message_info["confidence"] is None:
                rating_options = message_info["has_evaluation"]
            results, _ = load_results(
                query.from_user.id,
                message_info["turn_id"],
                context.bot.getMe().id,
            )
            if command == "result":
                self.message_dialogue.edit_answer(
                    query,
                    results,
                    user_message_id,
                    index,
                    int(list_index),
                    rating_options,
                )
            else:
                self.message_dialogue.edit_answer(
                    query,
                    results,
                    user_message_id,
                    rating_options,
                    list_index=int(value),
                )
        # Botão de avaliação abaixo da mensagem
        elif command == "confidence":
            value = int(value)
            user_message_id = int(user_message_id)
            turn_id = context.user_data[user_message_id]["turn_id"]
            context.user_data[user_message_id]["confidence"] = value
            turn = self.turn_dao.get_turn_by_id(turn_id)
            turn.answer_confidence = value
            # Atualizar tabela de turnos no banco de dados
            self.turn_dao.update_turn(turn)
            self.message_dialogue.remove_eval_buttons(query)

    def details_button(self, update, context):
        query = update.callback_query
        _, _, message_id, l_index = query.data.split("_")
        message_info = context.user_data[int(message_id)]
        _, infos = load_results(
            query.from_user.id, message_info["turn_id"], context.bot.getMe().id
        )
        if infos:
            self.message_dialogue.show_details(query, infos[int(l_index)])
        else:
            query.answer()

    def examples_cmd(self, update, context):
        self.message_dialogue.send_examples(update, context)

    def __process_handlers(self):
        self.dispatcher.remove_handler(self.handlers[0])
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start_iqa", self.start_iqa_cmd),
                CommandHandler("start", self.welcome_cmd),
            ],
            states={
                self.STATES["iqa_1"]: [
                    MessageHandler(
                        Filters.regex("^(?!/).*$"), self.msg_handler
                    )
                ],
            },
            fallbacks=[
                CommandHandler("examples", self.examples_cmd),
                CommandHandler("done", self.done_cmd),
            ],
            persistent=True,
            name="iqa",
        )
        self.dispatcher.add_handler(
            CallbackQueryHandler(
                self.answer_button, pattern=r"(result(-list)*|confidence)_"
            )
        )
        self.dispatcher.add_handler(
            CallbackQueryHandler(self.details_button, pattern=r"details_")
        )

        self.dispatcher.add_handler(conv_handler)
