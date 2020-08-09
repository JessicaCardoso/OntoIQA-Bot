import os
import glob
import configparser
import json
import pathlib


_ROOT = pathlib.Path(__file__).parent.parent.absolute()


def _edit_sep(text):
    if not text:
        return "\n"
    return text.replace("\\n", "\n").replace("\\t", "\t")


def load_template_config() -> dict:
    config = configparser.ConfigParser()
    config.read(os.path.join(_ROOT, "templates/template.ini"))
    return config


def load_template_json() -> dict:
    with open(os.path.join(_ROOT, "templates/template.json")) as json_file:
        return json.load(json_file)
