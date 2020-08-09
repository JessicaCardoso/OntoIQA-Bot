from telegram.ext import CommandHandler, CallbackQueryHandler
import pandas as pd

from settings import get_logger
from .utils import only_owner, add_handlers
from dialogs import MessageDialog

from models.db_util import DbUtil
import json

logger = get_logger()


class MainController:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.__process_handlers()
        self.message_dialogue = MessageDialog()
        self._database = DbUtil()

    def __enter__(self):
        print("__enter__")
        self._database.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__")
        self._database.__exit__(exc_type, exc_val, exc_tb)

    def welcome_cmd(self, update, context):
        self.message_dialogue.send_welcome_message(
            update.message, context.bot, first_call=True
        )

    def json_cmd(self, update, context):
        if update.message.reply_to_message:
            reply_to_message = update.message.reply_to_message.to_dict()
            update.message.reply_text(
                text=json.dumps(reply_to_message, indent=4)
            )

    def help_cmd(self, update, context):
        self.message_dialogue.send_help_message(
            update.message, context.bot, first_call=True
        )

    def about_cmd(self, update, context):
        self.message_dialogue.send_about_message(
            update.message, context.bot, first_call=True
        )

    def cmd_button(self, update, context):
        query = update.callback_query
        command, _, _, value = query.data.split("_")
        index = int(value)
        query.answer()
        if command == "help":
            self.message_dialogue.send_help_message(
                query.message, context.bot, index
            )
        elif command == "welcome":
            self.message_dialogue.send_welcome_message(
                query.message, context.bot, index=index
            )
        elif command == "about":
            self.message_dialogue.send_about_message(
                query.message, context.bot, index
            )

    def counter_button(self, update, context):
        query = update.callback_query
        query.answer("👀 look at me!")

    def error(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def __process_handlers(self):
        self.handlers = [
            CommandHandler("start", self.welcome_cmd),
            CommandHandler("help", self.help_cmd),
            CommandHandler("about", self.about_cmd),
            CommandHandler("show_json", self.json_cmd),
            CallbackQueryHandler(
                self.cmd_button, pattern=r"(welcome|about|help)_"
            ),
            CallbackQueryHandler(self.counter_button, pattern=r"this_"),
        ]
        add_handlers(self.dispatcher, self.handlers)
