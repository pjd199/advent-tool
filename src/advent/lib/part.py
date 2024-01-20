"""Puzzle part enum."""
from enum import Enum, unique


@unique
class Part(Enum):
    """Puzzle parts one and two."""

    PART_ONE = 1
    PART_TWO = 2


PART_ONE = Part.PART_ONE
PART_TWO = Part.PART_TWO
