"""Module to ensure filenames are safe."""
from re import sub
from urllib.parse import quote, unquote

BLANK = "__blank__"


def encode(filename: str) -> str:
    """Make a filename safe, encoding non-alphanumeric characters as % hex.

    Args:
        filename (str): the filename

    Returns:
        str: the encoded filename
    """
    if filename == "":
        return BLANK
    return sub(r"[^%a-zA-Z0-9]", lambda m: f"%{ord(m[0]):X}", quote(filename, safe=""))


def decode(filename: str) -> str:
    """Inverse of encode.

    Args:
        filename (str): the encoded filename

    Returns:
        str: the decoded filename
    """
    if filename == BLANK:
        return ""
    return unquote(filename)
