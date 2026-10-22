import re

_INTERNAL = re.compile(r"^(SH|SZ|BJ)\.(\d{6})$")
_VENDOR = re.compile(r"^(\d{6})\.(SH|SZ|BJ)$")


def normalize_internal(value: str) -> str:
    value = value.strip().upper()
    if match := _INTERNAL.fullmatch(value):
        return f"{match.group(1)}.{match.group(2)}"
    if match := _VENDOR.fullmatch(value):
        return f"{match.group(2)}.{match.group(1)}"
    raise ValueError(f"Unsupported security code: {value}")


def to_vendor(value: str) -> str:
    internal = normalize_internal(value)
    exchange, code = internal.split(".")
    return f"{code}.{exchange}"


def from_vendor(value: str) -> str:
    return normalize_internal(value)
