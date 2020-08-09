from .utils import (
    load_template_json,
    load_template_config,
)

from .message_build import (
    paginate_data,
    build_eval_buttons,
    build_menu,
    build_reply_keyboard,
)

from .send_message import SendMessage

import os

from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class MessageDialog:
    def __init__(self):
        self.template = load_template_json()
        self.config = load_template_config()
        self.help_length = len(self.template["help"])
        self.welcome_length = len(self.template["welcome"])
        self.about_length = len(self.template["about"])
        self.answer_config = self.config["answer"]

    def send_start_message(self, message, bot, chat_type="private"):
        content = self.template["start_iqa"][chat_type]
        if chat_type == "private":
            SendMessage.send_message_text(
                message, content["text"], parse_mode="markdown"
            )
        else:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=content["button_text"],
                            url=f"https://t.me/{bot.username}?start=start_iqa",
                        )
                    ]
                ]
            )
            SendMessage.send_message_text(
                message, content["text"], markup, parse_mode="markdown"
            )

    def send_welcome_message(self, message, bot, index=0, first_call=False):
        content = self.template["welcome"][index]
        SendMessage.send(
            "welcome",
            content,
            message,
            bot,
            index,
            self.welcome_length,
            first_call,
        )

    def send_help_message(self, message, bot, index=0, first_call=False):
        content = self.template["help"][index]
        SendMessage.send(
            "help", content, message, bot, index, self.help_length, first_call,
        )

    def send_about_message(self, message, bot, index=0, first_call=False):
        content = self.template["about"][index]
        SendMessage.send(
            "about",
            content,
            message,
            bot,
            index,
            self.about_length,
            first_call,
        )

    def send_goodbye_message(self, message, bot, redirect=False):
        content = self.template["done"]["default"]
        if redirect:
            content = dict(self.template["done"]["redirect"])
            text = content["text"].format(message.from_user.id)
        SendMessage.send_message_text(
            message,
            text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="markdown",
        )

    def reply_answer(self, message, content):
        eval_options = None

        if content["eval_options"]:
            eval_options = self.template["eval_options"]

        rating_options = build_eval_buttons(
            eval_options, message.from_user.id, message.message_id
        )
        response = SendMessage.send_message_text(
            message, content["text"], parse_mode="markdown"
        )
        if not content["results"]:
            options = build_menu(rating_options)
            if options:
                response.edit_reply_markup(reply_markup=options)
        else:
            text, reply_markup = paginate_data(
                "result",
                content["results"],
                list_size=len(content["results"]),
                rating_options=rating_options,
                message_id=message.message_id,
                page_size=self.answer_config["page_size"],
                line_sep=self.answer_config["line_sep"],
                col_sep=self.answer_config["col_sep"],
                col_name_pos=self.answer_config["col_name_pos"],
                number_format=self.answer_config["number_format"],
            )
            response = SendMessage.send_message_text(
                message, text, reply_markup=reply_markup, parse_mode="markdown"
            )
        if content["related"]:
            markup = build_reply_keyboard(content["related"], n_cols=1)
            SendMessage.send_message_text(
                message, content["suggestion_text"], reply_markup=markup,
            )
        return response

    def edit_answer(
        self,
        query,
        answer,
        message_id,
        index=0,
        list_index=0,
        rating_options=False,
    ):
        eval_options = None
        if rating_options:
            eval_options = self.template["eval_options"]
        rating_options = build_eval_buttons(
            eval_options, query.message.chat.id, message_id
        )
        text, reply_markup = paginate_data(
            "result",
            answer,
            list_index=list_index,
            list_size=len(answer),
            index=index,
            rating_options=rating_options,
            message_id=message_id,
            page_size=self.answer_config["page_size"],
            line_sep=self.answer_config["line_sep"],
            col_sep=self.answer_config["col_sep"],
            col_name_pos=self.answer_config["col_name_pos"],
            number_format=self.answer_config["number_format"],
        )
        return query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode="markdown"
        )

    def loading_message(self, update, context):
        content = self.template["loading"]["text"]
        return SendMessage.send_message_text(
            update.message,
            content,
            parse_mode="markdown",
            reply_markup=ReplyKeyboardRemove(),
        )

    def send_examples(self, update, context):
        content = self.template["examples"]
        markup = build_reply_keyboard(content["examples"], n_cols=1)
        SendMessage.send_message_text(
            update.message, content["text"], reply_markup=markup,
        )

    def show_details(self, callback_query, details):
        details_str = "ℹ️ Info\n\n"
        if details:
            for key, value in details.items():
                details_str += f"{key}: {value}\n"
        else:
            details_str += "Informações não encontradas."
        callback_query.answer(details_str, show_alert=True)

    @staticmethod
    def remove_eval_buttons(query):
        reply_markup = query.message.reply_markup
        keyboard = []
        # Retorna o inline keyboard atualizado
        inline_keyboards = iter(reply_markup["inline_keyboard"])
        next(inline_keyboards)
        for inline_keyboard in inline_keyboards:
            keyboard.append(inline_keyboard)
        query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
