import json
import locale
import os
import typing


__all__ = ["MESSAGES"]

DEFAULT_LANG = "en_US"


class MessageDictionary(typing.TypedDict):
    """
    Dictionary representing every possible message.

    Static type checkers can catch typos in keys or unexisting ones.
    """

    attempts_report_template: str
    cant_establish_template: str
    dry_run_mode: str
    error_value_nan: str
    error_value_inf: str
    flag_note_template: str
    ignored_failure: str
    no_wifi_established: str
    note_instant_disconnection: str
    reset_anyway: str
    restart_failure: str
    started_restarting: str
    user_exit_requested: str
    wifi_already_established_template: str
    wifi_established_template: str


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


def fix_missing_translations(source: dict[str, str]) -> MessageDictionary:
    """
    Add default messages for missing translations.
    """

    with open(get_file_path(DEFAULT_LANG)) as default_messages_json:
        default_messages = json.load(default_messages_json)

    # ensure that the default dictionary contains only and all messages
    # if we add more messages in the future, it will make sure we don't forget
    # something somewhere :')
    assert is_dictionary_complete(default_messages)

    return typing.cast(MessageDictionary, default_messages | source)


def is_dictionary_complete(
    dictionary: dict[str, str],
) -> typing.TypeGuard[MessageDictionary]:
    """
    Check whether a dictionary is complete, i.e. supports every possible
    message.
    """

    return MessageDictionary.__annotations__.keys() == dictionary.keys()


MESSAGES_FILE_PATH = get_file_path(locale.getlocale()[0] or DEFAULT_LANG)

with open(MESSAGES_FILE_PATH, "r") as messages_json:
    MESSAGES = fix_missing_translations(json.load(messages_json))
