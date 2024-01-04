"""Puzzle Class."""
from functools import cached_property
from re import finditer

from bs4 import BeautifulSoup
from markdownify import ATX, markdownify

from advent.lib.config import settings
from advent.lib.http import fetch_puzzle_input, fetch_puzzle_page, url_for


class Puzzle:
    """Puzzle Class."""

    def __init__(self, year: int, day: int) -> None:
        """Initializer.

        Args:
            year (int): the puzzle year
            day (int): the puzzle day
        """
        self.year = year
        self.day = day
        self._html = fetch_puzzle_page(self.year, self.day)

    # @cached_property
    def title(self) -> str:
        """Puzzle Title.

        Returns:
            str: the puzzle title
        """
        return next(
            m["title"].replace('"', "'")
            for heading in BeautifulSoup(self._html, "html.parser").find_all("h2")
            for m in finditer(r"--- Day (?:\d+): (?P<title>.+) ---", heading.string)
        )

    # @cached_property
    def descriptions(self) -> list[str]:
        """The puzzle desciptions for part one and part two, in markdown format.

        Returns:
            list[str]: the descriptions
        """
        return [
            markdownify(str(article), heading_style=ATX, wrap=80)
            for article in BeautifulSoup(self._html, "html.parser").find_all(
                "article", attrs={"class": "day-desc"}
            )
        ]

    # @cached_property
    def answers(self) -> list[str]:
        """The accepted answers for part one and part two.

        Returns:
            list[str]: the answers
        """
        return [
            p.code.string
            for p in BeautifulSoup(self._html, "html.parser").find_all("p")
            if p.text.startswith("Your puzzle answer was")
        ]

    # @cached_property
    def input_file(self) -> str:
        """The puzzle input file.

        Returns:
            str: the file
        """
        return fetch_puzzle_input(self.year, self.day)

    # @cached_property
    def url(self) -> str:
        """Advent of Code URL for this puzzle.

        Returns:
            str: the URL
        """
        return url_for(self.year, self.day)

    def refresh(self) -> None:
        """Force refresh the puzzle in the cache."""
        self._html = fetch_puzzle_page(self.year, self.day, force_refresh=True)
        # del self.url
        # del self.title
        # del self.descriptions
        # del self.input_file
        # del self.answers
