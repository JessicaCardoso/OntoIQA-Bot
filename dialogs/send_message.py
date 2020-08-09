import inspect
from telegram import InputMediaAnimation, InputMediaVideo, InputMediaPhoto

from .message_build import build_nav_menu
from settings import get_logger


logger = get_logger()


class SendMessage:
    @staticmethod
    def send_message_media(message, content, src_type, reply_markup=None):
        user = message.from_user
        logger.info("[%s]: %s", user.id, message.text)
        logger.info(inspect.stack()[1][3])
        if src_type == "animation":
            return message.reply_animation(
                content["src"],
                caption=content["text"],
                reply_markup=reply_markup,
                parse_mode="markdown",
            )
        elif src_type == "video":
            return message.reply_video(
                content["src"],
                caption=content["text"],
                reply_markup=reply_markup,
                parse_mode="markdown",
            )
        elif src_type == "photo":
            return message.reply_photo(
                content["src"],
                caption=content["text"],
                reply_markup=reply_markup,
                parse_mode="markdown",
            )

    @staticmethod
    def edit_message_media(message, bot, content, src_type, reply_markup=None):
        logger.info(inspect.stack()[1][3])
        media = None
        if src_type == "animation":
            media = InputMediaAnimation(
                content["src"], caption=content["text"], parse_mode="markdown"
            )
        elif src_type == "video":
            media = InputMediaVideo(
                content["src"], caption=content["text"], parse_mode="markdown"
            )
        elif src_type == "photo":
            media = InputMediaPhoto(
                content["src"], caption=content["text"], parse_mode="markdown"
            )

        if media:
            return bot.edit_message_media(
                message.chat.id,
                message.message_id,
                media=media,
                reply_markup=reply_markup,
            )

    @staticmethod
    def send_message_text(message, text, reply_markup=None, parse_mode=None):
        user = message.from_user
        logger.info("[%s]: %s", user.id, message.text)
        logger.info(inspect.stack()[1][3])
        return message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            reply_to_message_id=message.message_id,
            disable_web_page_preview=True,
        )

    @staticmethod
    def send_document(message, text, filename, reply_markup=None):
        user = message.from_user
        logger.info("[%s]: %s", user.id, message.text)
        logger.info(inspect.stack()[1][3])
        return message.reply_document(
            document=open(filename, "rb"), caption=text, parse_mode="markdown"
        )

    @staticmethod
    def edit_message_text(message, bot, text, reply_markup=None):
        logger.info(inspect.stack()[1][3])
        return bot.edit_message_text(
            text,
            message.chat.id,
            message.message_id,
            reply_markup=reply_markup,
            parse_mode="markdown",
        )

    @staticmethod
    def send(
        label,
        content,
        message,
        bot,
        index=0,
        content_length=1,
        first_call=True,
    ):
        reply_markup = build_nav_menu(label, message, content_length, index)
        if content["src"]:
            if index == 0 and first_call:
                return SendMessage.send_message_media(
                    message, content, content["src_type"], reply_markup
                )
            else:
                return SendMessage.edit_message_media(
                    message,
                    bot,
                    content,
                    content["src_type"],
                    reply_markup=reply_markup,
                )
        else:
            if index == 0 and first_call:
                return SendMessage.send_message_text(
                    message,
                    content["text"],
                    reply_markup,
                    parse_mode="markdown",
                )
            else:
                return SendMessage.edit_message_text(
                    message, bot, content["text"], reply_markup
                )
