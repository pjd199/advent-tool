"""Configuration manager."""
from dataclasses import dataclass
from functools import cache
from os import environ
from pathlib import Path
from typing import Any, TypeVar, cast

from tomllib import load

T = TypeVar("T", bound=str | int | bool | float)

_TOOL_PATH = Path(".advent-tool")


def _load_config_file() -> dict[str, Any]:
    """Load the TOML configuration file.

    Returns:
        dict[str, Any]: the loaded TOML
    """
    # look for a custom config file
    path = Path(".advent-tool.toml")
    if path.exists():
        with path.open("rb") as file:
            return load(file)

    # look for a section in the pyproject file
    path = Path("pyproject.toml")
    if path.exists():
        with path.open("rb") as file:
            pyproject = load(file)
            if "tool.advent" in pyproject and isinstance(
                pyproject["tool.advent"], dict
            ):
                return pyproject["tool.advent"]

    return {}


config_file = _load_config_file()


@cache
def _config_property(*args: str, default: T) -> T:
    """Read a property from the config file.

    Args:
        *args (str):  the path to the property in the TOML file
        default (T): the default value

    Returns:
        T: the value from the file, or the default if not found
    """
    section = config_file
    for arg in args:
        if arg not in section:
            break
        if isinstance(section[arg], dict):
            section = section[arg]
        if type(section[arg]) is type(default):
            return cast(T, section[arg])
    return default


def _find_session() -> str | None:
    if (_TOOL_PATH / "session.txt").exists():
        with (_TOOL_PATH / "session.txt").open() as file:
            return file.read()

    if environ["AOC_SESSION"]:
        return environ["AOC_SESSION"]

    return None


@dataclass
class Settings:
    """User settings."""

    # system path
    tool_path: Path
    # HTTP
    http_root: str
    http_user_agent: str
    # template
    template_save_enabled: bool
    template_file: str
    template_save_path: str
    # input
    input_save_enabled: bool
    input_save_path: str
    # session cookie
    session: str | None


settings = Settings(
    # system path
    tool_path=_TOOL_PATH,
    # HTTP
    http_root=_config_property("http", "root", default="https://www.adventofcode.com"),
    http_user_agent="https://github.com/pjd199/advent-tool",
    # template
    template_save_enabled=_config_property("template", "enabled", default=True),
    template_file=_config_property("template", "file", default=""),
    template_save_path=_config_property(
        "template", "path", default="src/{year:04}/{day:02}/solution.py"
    ),
    # input file
    input_save_enabled=_config_property("input", "enabled", default=True),
    input_save_path=_config_property(
        "input", "path", default="src/{year:04}/{day:02}/input.txt"
    ),
    # session cookie
    session=_find_session(),
)
