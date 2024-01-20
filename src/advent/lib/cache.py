"""Cache module for the puzzle pages and puzzle input."""
from pathlib import Path

from advent.lib.config import settings
from advent.lib.filename import decode, encode
from advent.lib.http import fetch
from advent.lib.part import PART_ONE, PART_TWO, Part

_level = {PART_ONE: "1", PART_TWO: "2"}


def get_puzzle_page(
    year: int, day: int, user: str = "default", refresh: bool = False
) -> str:
    """Get the puzzle page from the cache, or download if needed.

    Args:
        year (int): the year
        day (int): the day
        user (str): the user
        refresh (bool): if True, forces a cache refresh.

    Returns:
        str: the html page
    """
    return _cached_or_fetch(
        settings.tool_path / f"cache/{user}/{year}/{day:02}/index.html",
        f"{settings.http_root}/{year}/day/{day}",
        None,
        refresh,
    )


def get_puzzle_input(
    year: int, day: int, user: str = "default", refresh: bool = False
) -> str:
    """Get the puzzle input from the cache, or down if needed.

    Args:
        year (int): year
        day (int): day
        user (str): the user
        refresh (bool): if True, force a cache refresh

    Returns:
        str: the plaintext puzzle input file
    """
    return _cached_or_fetch(
        settings.tool_path / f"cache/{user}/{year}/{day:02}/input.txt",
        f"{settings.http_root}/{year}/day/{day}/input",
        None,
        refresh,
    )


def post_puzzle_answer(
    year: int,
    day: int,
    part: Part,
    answer: int | str,
    user: str = "default",
    refresh: bool = False,
) -> str:
    """Get the puzzle input from the cache, or down if needed.

    Args:
        year (int): year
        day (int): day
        part (Part): the part to submit, one or two
        answer (int | str): the answer to submit
        user (str): the user
        refresh (bool): if True, force a cache refresh

    Returns:
        str: the result of the submit
    """
    name = encode(str(answer))
    data = {"level": _level[part], "answer": str(answer)}
    return _cached_or_fetch(
        settings.tool_path
        / f"cache/{user}/{year}/{day:02}/answer/{_level[part]}/{name}.html",
        f"{settings.http_root}/{year}/day/{day}/answer",
        data,
        refresh,
    )


def lookup_answers(
    year: int,
    day: int,
    part: Part,
    user: str = "default",
) -> dict[str, str]:
    """Retrieve all the submitted answers from the cache.

    Args:
        year (int): the year
        day (int): the day
        part (Part): the part
        user (str): the user

    Returns:
        dict[str, str]: mapping of answer to html
    """
    path = settings.tool_path / f"cache/{user}/{year}/{day:02}/answer/{_level[part]}/"
    found = {}
    if path.exists():
        for child in sorted(path.iterdir(), key=lambda x: x.stat().st_mtime):
            if child.is_file() and child.name.endswith(".html"):
                with child.open() as file:
                    found[decode(child.name[:-5])] = file.read()
    return found


def _cached_or_fetch(
    cache_path: Path,
    url: str,
    data: dict[str, str] | None,
    refresh: bool,
) -> str:
    """Read file from the cache, or get from the URL.

    Args:
        cache_path (Path): the path in the cache
        url (str): the URL to download
        data (dict[str, str] | None): the data
        refresh (bool): if True, forces a cache refresh.

    Returns:
        str: the requested file
    """
    # fetch the file, if required
    if refresh or not cache_path.exists():
        html = fetch(url, data)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w") as file:
            file.write(html)

    # return the file
    with cache_path.open() as file:
        return file.read()
