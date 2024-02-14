import json
import locale
import os


__all__ = ["MESSAGES"]

DEFAULT_LANG = "en_US"


def get_file_path(lang: str) -> str:
    """
    Get the messages file path given a language.

    If the language is not supported, return the default.
    """

    dir = os.path.dirname(__file__)
    path = os.path.join(dir, f"{lang}.json")

    if not os.path.exists(path):
        return os.path.join(dir, f"{DEFAULT_LANG}.json")

    return path


def fix_messages(source: dict[str, str]) -> dict[str, str]:
    """
    Add original english messages for missing translations.
    """

    with open(get_file_path(DEFAULT_LANG)) as default_messages_json:
        default_messages = json.load(default_messages_json)

    return default_messages | source


MESSAGES_FILE_PATH = get_file_path(locale.getlocale()[0] or DEFAULT_LANG)

with open(MESSAGES_FILE_PATH, "r") as messages_json:
    MESSAGES = fix_messages(json.load(messages_json))
