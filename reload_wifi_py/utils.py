import math

from reload_wifi_py.messages import MESSAGES


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
