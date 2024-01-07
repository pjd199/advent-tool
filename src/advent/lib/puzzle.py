"""Puzzle Class."""
from re import finditer

from bs4 import BeautifulSoup
from markdownify import ATX, BACKSLASH, MarkdownConverter  # type: ignore

from advent.lib.cache import get_puzzle_input, get_puzzle_page
from advent.lib.config import settings


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
        self._html = get_puzzle_page(year, day)

    @property
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

    @property
    def descriptions(self) -> list[str]:
        """The puzzle desciptions for part one and part two, in markdown format.

        Returns:
            list[str]: the descriptions
        """
        converter = MarkdownConverter(
            heading_style=ATX,
            wrap=True,
            wrap_width=80,
            newline_style=BACKSLASH,
        )
        return [
            converter.convert_soup(article)
            for article in BeautifulSoup(self._html, "html.parser").find_all(
                "article", attrs={"class": "day-desc"}
            )
        ]

    @property
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

    @property
    def input_file(self) -> str:
        """The puzzle input file.

        Returns:
            str: the file
        """
        return get_puzzle_input(self.year, self.day)

    @property
    def url(self) -> str:
        """Advent of Code URL for this puzzle.

        Returns:
            str: the URL
        """
        return f"{settings.http_root}/{self.year}/day/{self.day}"

    def refresh(self) -> None:
        """Force refresh the puzzle in the cache."""
        self._html = get_puzzle_page(self.year, self.day, refresh=True)
