"""Templating system."""
from pathlib import Path

from advent.lib.config import settings
from advent.lib.puzzle import Puzzle


def save_template(puzzle: Puzzle) -> None:
    """Find the template content.

    Args:
        puzzle (Puzzle): the puzzle to build the template for
    """
    # format the save path
    path = Path(
        settings.template_save_path.format(
            year=puzzle.year,
            day=puzzle.day,
        )
    )

    if not path.exists():
        # get the unformatted template
        if settings.template_file and Path(settings.template_file).exists():
            with Path(settings.template_file).open() as file:
                content = file.read()
        else:
            content = _default

        # format the template
        content = content.format(
            year=puzzle.year,
            day=puzzle.day,
            title=puzzle.title,
            url=puzzle.url,
        )

        # save the template file
        path = Path(
            settings.template_save_path.format(
                year=puzzle.year,
                day=puzzle.day,
            )
        )

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as file:
            file.write(content)


_default = '''"""Solve the puzzle Advent of Code for day {day} of the {year} event.

{title}

{url}
"""
from advent import load_puzzle


def solve() -> None:
    """Solve the puzzle."""
    # load file
    ...
    input = load_puzzle({year}, {day})

    # solve part one
    ...
    print(-1)

    # solve part two
    ...
    print(-1)

if __name__ == "__main__":  # pragma: no cover
    solve()
'''
