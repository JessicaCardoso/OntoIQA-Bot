import settings
import os

from telegram.ext import Updater, PicklePersistence

from controllers import ConversationController


def main():
    persistence = PicklePersistence(os.path.join("logs", "conversations"))
    updater = Updater(
        token=os.getenv("TOKEN"), use_context=True, persistence=persistence
    )
    dp = updater.dispatcher
    with ConversationController(dispatcher=dp) as cc:
        dp.add_error_handler(cc.error)
        if os.getenv("MODE") == "webhook":
            updater.start_webhook(
                listen=os.getenv("LISTEN"),
                port=os.getenv("PORT"),
                url_path=os.getenv("TOKEN"),
            )
            updater.bot.set_webhook(
                os.path.join(os.getenv("URL"), os.getenv("TOKEN"))
            )
        else:
            updater.start_polling(timeout=15, read_latency=4)
        updater.idle()


if __name__ == "__main__":
    main()
