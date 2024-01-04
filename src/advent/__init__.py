"""Initialise the package, loading the tool settings."""

from advent.lib.puzzle import Puzzle


def load_puzzle(year: int, day: int) -> Puzzle:
    """Main entry to the puzzle data.

    Args:
        year (int): the year
        day (int): the day

    Returns:
        Puzzle: requested puzzle data
    """
    return Puzzle(year, day)
