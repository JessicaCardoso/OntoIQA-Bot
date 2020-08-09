# settings.py
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import logging
import os

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path, verbose=True)


def get_logger():
    logger = logging.getLogger()
    logging.basicConfig(
        # filename=os.path.join('logs', "logging-info.log"),
        # filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    return logger
