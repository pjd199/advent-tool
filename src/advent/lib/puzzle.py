"""Puzzle Class."""
from enum import Enum, unique
from functools import cached_property
from logging import getLogger
from re import finditer

from bs4 import BeautifulSoup
from markdownify import ATX, BACKSLASH, MarkdownConverter  # type: ignore

from advent.lib.cache import (
    get_puzzle_input,
    get_puzzle_page,
    lookup_answers,
    post_puzzle_answer,
)
from advent.lib.config import settings
from advent.lib.part import PART_ONE, PART_TWO, Part

log = getLogger(__name__)

md = MarkdownConverter(
    heading_style=ATX,
    wrap=True,
    wrap_width=80,
    newline_style=BACKSLASH,
)


@unique
class AnswerStatus(Enum):
    """Enumeration for the answer status."""

    HIGH = "high"
    LOW = "low"
    WAIT = "wait"
    CORRECT = "correct"
    INCORRECT = "incorrect"


class Puzzle:
    """Puzzle Class."""

    def __init__(self, year: int, day: int) -> None:
        """Initializer.

        Args:
            year (int): the puzzle year
            day (int): the puzzle day
        """
        log.info(f"Loading puzzle for {year} {day}")

        self.year = year
        self.day = day
        self.page_url = f"{settings.http_root}/{self.year}/day/{self.day}"
        self.input_url = f"{settings.http_root}/{self.year}/day/{self.day}/input"
        self.answer_url = f"{settings.http_root}/{self.year}/day/{self.day}/answer"

    @cached_property
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

    @cached_property
    def descriptions(self) -> dict[Part, str | None]:
        """The puzzle desciptions for part one and part two, in markdown format.

        Returns:
            dict[Part, str | None]: the descriptions
        """
        found = [
            md.convert_soup(article)
            for article in BeautifulSoup(self._html, "html.parser").find_all(
                "article", attrs={"class": "day-desc"}
            )
        ]
        return {
            PART_ONE: found[0] if len(found) >= 1 else None,
            PART_TWO: found[1] if len(found) == 2 else None,
        }

    @cached_property
    def answers(self) -> dict[Part, str | None]:
        """The accepted answers for part one and part two.

        Returns:
            dict[Part, str | None]: the answers
        """
        found = [
            p.code.string
            for p in BeautifulSoup(self._html, "html.parser").find_all("p")
            if p.text.startswith("Your puzzle answer was")
        ]
        return {
            PART_ONE: found[0] if len(found) >= 1 else None,
            PART_TWO: found[1] if len(found) == 2 else None,
        }

    def _extract_submit_message(self, html: str) -> str:
        """Extract the message form the submit html.

        Args:
            html (str): the html to parse

        Returns:
            str: the message
        """
        article = BeautifulSoup(html, "html.parser").article
        if article:
            text = md.convert_soup(article.p)
            if isinstance(text, str):
                return text.split(".")[0]
        return ""

    @cached_property
    def submitted(self) -> dict[Part, dict[str, str]]:
        """Lookup the submitted answers in the cache.

        Returns:
            dict[Part, dict[str, str]]: results in form {part: {answer: message}}
        """
        return {
            part: {
                answer: self._extract_submit_message(html)
                for answer, html in lookup_answers(self.year, self.day, part).items()
            }
            for part in Part
        }

    def submit(self, part: Part, answer: int | str | None) -> None:  # noqa: C901
        """Submit an answer.

        Args:
            part (Part): part one or part two
            answer (int | str | None): the answer
        """
        if answer is None:
            return

        # create a formated part string
        part_str = {PART_ONE: "Part One", PART_TWO: "Part Two"}[part]

        # print the result
        print(f"Your answer to {part_str} is {answer}")

        # check if this answer appears as one of the examples
        if str(answer) in [
            code.text
            for article in BeautifulSoup(self._html, "html.parser").find_all(
                "article", attrs={"class": "day-desc"}
            )
            for code in article.find_all("code")
            if not code.findParent("pre")
        ]:
            print("It looks like you are using example input data")
            return

        # check for previously submitted answers on the puzzle page
        if self.answers[part] is not None:
            if str(answer) != self.answers[part]:
                print(
                    "That's not the right answer; "
                    f"your correct answer was {self.answers[part]}"
                )
            return

        # check for previoiusly submitted correct answers in the submissions cache
        correct = next(
            (
                submitted
                for (submitted, message) in self.submitted[part].items()
                if "That's the right answer!" in message
            ),
            None,
        )
        if correct is not None and correct == str(answer):
            if str(answer) != correct:
                print(f"That's not the right answer; your correct answer was {correct}")
            return

        # check for high / low advice from previous submissions
        for previous, message in self.submitted[part].items():
            if (
                str(answer).isnumeric()
                and previous.isnumeric()
                and (
                    ("too low" in message and int(answer) <= int(previous))
                    or ("too high" in message and int(answer) >= int(previous))
                )
            ):
                print(
                    "Looking at previous responses "
                    f"your answer is too {'low' if 'low' in message else 'high'}"
                )
                return

        # ask for user input before submitting
        if input("Ready to submit (Y/N)? ").upper() != "Y":
            return

        # submit the results (or get the cached result)
        html = post_puzzle_answer(self.year, self.day, part, str(answer), refresh=True)
        self.__dict__.pop("submitted", None)

        # print and log the message
        print(f"Submitted {self.year} {self.day} {part_str}: {answer}")

        message = self._extract_submit_message(html)
        print(message)

        if "That's the right answer!" in message:
            self.refresh()

    @cached_property
    def input_file(self) -> str:
        """The puzzle input file.

        Returns:
            str: the file
        """
        return get_puzzle_input(self.year, self.day)

    @cached_property
    def _html(self) -> str:
        return get_puzzle_page(self.year, self.day)

    def refresh(self) -> None:
        """Force refresh the puzzle in the cache."""
        get_puzzle_page(self.year, self.day, refresh=True)
        self.__dict__.pop("_html", None)
        self.__dict__.pop("title", None)
        self.__dict__.pop("descriptions", None)
        self.__dict__.pop("answers", None)
        self.__dict__.pop("submitted", None)
