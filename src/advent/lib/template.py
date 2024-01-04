"""Templating system."""
from pathlib import Path

from advent import settings
from advent.lib.puzzle import Puzzle


def write_template(puzzle: Puzzle) -> None:
    """Find the template content.

    Args:
        puzzle (Puzzle): the puzzle to build the template for
    """
    if settings.template_content:
        content = settings.template_content
    elif settings.template_file:
        with Path(settings.template_file).open() as file:
            content = file.read()
    else:
        content = default_template

    # format the template
    content = content.format(
        year=puzzle.year,
        day=puzzle.day,
        title=puzzle.title,
        url=puzzle.url,
    )

    # write the template content
    filename = settings.template_path.format(
        year=puzzle.year,
        day=puzzle.day,
    )
    with Path(filename).open("w") as file:
        file.write(content)


default_template = '''
"""Solves the puzzle for Day {day} of Advent of Code {year}.

{title}

For puzzle specification and desciption, visit {url}.
"""
from advent_of_code.utils.parser import parse_lines, str_processor
from advent_of_code.utils.runner import runner
from advent_of_code.utils.solver_interface import SolverInterface


class Solver(SolverInterface):
    """Solves the puzzle."""

    YEAR = {year}
    DAY = {day}
    TITLE = "{title}"

    def __init__(self, puzzle_input: list[str]) -> None:
        """Initialise the puzzle and parse the input.

        Args:
            puzzle_input (list[str]): The lines of the input file
        """
        self.input = parse_lines(puzzle_input, (r".*", str_processor))

    def solve_part_one(self) -> int:
        """Solve part one of the puzzle.

        Returns:
            int: the answer
        """
        return -1

    def solve_part_two(self) -> int:
        """Solve part two of the puzzle.

        Returns:
            int: the answer
        """
        return -1


if __name__ == "__main__":  # pragma: no cover
    runner(Solver)
'''
