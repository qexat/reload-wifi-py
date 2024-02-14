import dataclasses
import enum
import sys
import typing

from reload_wifi_py.messages import MESSAGES


LOG_TEMPLATE = "\x1b[1;38;5;{}m{}:\x1b[22;39m {}"


@dataclasses.dataclass(slots=True, frozen=True)
class LogKindData:
    color: int
    default_output: typing.TextIO


class LogKind(enum.Enum):
    ERROR = LogKindData(1, sys.stderr)
    SUCCESS = LogKindData(2, sys.stdout)
    INFO = LogKindData(4, sys.stdout)
    NOTE = LogKindData(5, sys.stderr)


def log(kind: LogKind, message: str, *, file: typing.TextIO | None = None) -> None:
    _file = file or kind.value.default_output
    print(LOG_TEMPLATE.format(kind.value.color, kind.name, message), file=_file)


def flag_note(message: str, flag: str) -> None:
    template = MESSAGES["flag_note_template"]
    log(LogKind.NOTE, template.format(message, flag.replace("_", "-")))
