import pickle
import pathlib
import os
from functools import wraps
import shelve


from telegram import ChatAction

_ROOT = pathlib.Path(__file__).parent.parent.absolute()

allowed_users = [1091438586, 1072982844, 684342838]


def add_handlers(dispatcher, handlers):
    for handler in handlers:
        dispatcher.add_handler(handler)


def save_results(user_id, turn_id, bot_id, results, details):
    bot_dir = os.path.join("data", str(bot_id))
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(bot_dir):
        os.makedirs(bot_dir)
    filename = os.path.join(bot_dir, str(user_id))
    with shelve.open(filename, "c") as shelf:
        shelf[str(turn_id)] = [results, details]
    shelf.close()


def load_results(user_id, turn_id, bot_id):
    bot_dir = os.path.join("data", str(bot_id))
    filename = os.path.join(bot_dir, str(user_id))
    if os.path.isfile(filename + ".bak"):
        turn_id = str(turn_id)
        with shelve.open(filename, "r") as shelf:
            if turn_id in shelf.keys():
                return shelf[turn_id]


def only_owner(func):
    @wraps(func)
    def wrapped(self, update, context):
        user_id = update.effective_user.id
        if user_id != int(os.getenv("OWNER_ID")):
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(self, update, context)

    return wrapped


def restrict(func):
    @wraps(func)
    def wrapped(self, update, context):
        user_id = update.effective_user.id
        if user_id not in allowed_users:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(self, update, context)

    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(self, update, context):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            return func(self, update, context)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
