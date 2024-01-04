"""Configuration manager."""
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, TypeVar
from os import environ

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
            if "tool.advent" in pyproject:
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
        else:
            return section[arg]
    return default


def _find_session() -> str | None:
    if (_TOOL_PATH / "session.txt").exists():
        with (_TOOL_PATH / "session.txt").open() as file:
            return file.read()

    if environ("AOC_SESSION"):
        return environ("AOC_SESSION")

    return None


@dataclass
class Settings:
    """User settings."""

    tool_path: Path
    http_root: str
    http_user_agent: str
    template_enabled: bool
    template_content: str
    template_file: str
    template_path: str
    input_path: str
    input_save_enabled: bool
    session: str | None


settings = Settings(
    tool_path=_TOOL_PATH,
    http_root=_config_property("http", "root", default="https://www.adventofcode.com"),
    http_user_agent=_config_property(
        "http", "agent", default="https://github.com/pjd199/advent-tool"
    ),
    template_enabled=_config_property("template", "enabled", default=True),
    template_content=_config_property("template", "content", default=""),
    template_file=_config_property("template", "file", default=""),
    input_path=_config_property(
        "cache", "input", default="src/{year:04}/{day:02}/input.txt"
    ),
    template_path=_config_property(
        "path", "code", default="src/{year:04}/{day:02}/solution.py"
    ),
    input_save_enabled=_config_property("input", "save", default=False),
    session=_find_session(),
)
