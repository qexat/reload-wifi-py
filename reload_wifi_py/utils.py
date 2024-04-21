import math
import re

from reload_wifi_py.messages import MESSAGES


FLAG_PATTERN = re.compile(r"(--\w+(-\w+)*)")


def number(raw_value: str) -> float:
    """
    "Type" function for an `argparse` argument.

    It is basically `float` without `nan` and `±inf`.
    """

    value = float(raw_value)

    if math.isnan(value):
        raise ValueError(MESSAGES["error_value_nan"])
    if value in {float("inf"), float("-inf")}:
        raise ValueError(MESSAGES["error_value_inf"])

    return value


def prettify_flag(message: str) -> str:
    """
    Return a copy of `message` where shell flags are in light cyan (ANSI).
    """

    return re.sub(FLAG_PATTERN, lambda match: f"\x1b[96m{match[0]}\x1b[39m", message)


def format_ssid(ssid: str) -> str:
    """
    Return a prettier version of the SSID string.
    """

    return f"\x1b[1m{ssid}\x1b[22m"
