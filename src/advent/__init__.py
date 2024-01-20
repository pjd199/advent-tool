"""Initialise the package."""
from importlib.metadata import PackageNotFoundError, version

from advent.lib.part import PART_ONE, PART_TWO
from advent.lib.puzzle import Puzzle

try:
    __version__ = version("advent-tool")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"


def load_puzzle(year: int, day: int) -> Puzzle:
    """Main entry to the puzzle data.

    Args:
        year (int): the year
        day (int): the day

    Returns:
        Puzzle: requested puzzle data
    """
    return Puzzle(year, day)


__all__ = [
    "load_puzzle",
    "PART_ONE",
    "PART_TWO",
]
