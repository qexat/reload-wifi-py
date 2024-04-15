import dataclasses
import enum
import sys
import typing

import anstrip

from reload_wifi_py.messages import MESSAGES
from reload_wifi_py.utils import prettify_flag

LOG_TEMPLATE = "\x1b[38;5;{}m<\x1b[1m{}\x1b[22m>\x1b[39m {}"

Symbol: typing.TypeAlias = typing.Literal["!", "?", "*", "i", "✓"]


@dataclasses.dataclass(slots=True, frozen=True)
class LogKindData:
    symbol: Symbol
    color: int
    default_output: typing.TextIO


class LogKind(enum.Enum):
    ERROR = LogKindData("!", 9, sys.stderr)
    SUCCESS = LogKindData("✓", 10, sys.stdout)
    INFO = LogKindData("i", 12, sys.stdout)
    NOTE = LogKindData("*", 13, sys.stderr)


def get_message(kind: LogKind, message: str) -> str:
    return LOG_TEMPLATE.format(
        kind.value.color,
        kind.value.symbol,
        message.replace("reload-wifi", "\x1b[3mreload-wifi\x1b[23m"),
    )


def log(kind: LogKind, message: str, *, file: typing.TextIO | None = None) -> None:
    _file = file or kind.value.default_output
    anstrip.auto_print(get_message(kind, message), file=_file)


def flag_note(message: str, flag: str, *, file: typing.TextIO | None = None) -> None:
    template = MESSAGES["flag_note_template"]
    log(
        LogKind.NOTE,
        prettify_flag(template.format(message, flag.replace("_", "-"))),
        file=file,
    )
