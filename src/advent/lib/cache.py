"""Cache module for the puzzle pages and puzzle input."""
from pathlib import Path

from advent.lib.config import settings
from advent.lib.http import fetch


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
        refresh,
    )


def _cached_or_fetch(
    cache_path: Path,
    url: str,
    refresh: bool = False,
) -> str:
    """Read file from the cache, or get from the URL.

    Args:
        cache_path (Path): the path in the cache
        url (str): the URL to download
        refresh (bool): if True, forces a cache refresh.

    Returns:
        str: the requested file
    """
    # fetch the file, if required
    if refresh or not cache_path.exists():
        html = fetch(url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w") as file:
            file.write(html)

    # return the file
    with cache_path.open() as file:
        return file.read()
