"""Command Line Interace for the Advent Tool."""


import logging

from advent import load_puzzle


def main() -> None:
    """Main CLI entry point."""
    logging.getLogger().setLevel(logging.INFO)

    puzzle = load_puzzle(2023, 10)
    #puzzle.refresh()
    # print(puzzle.title)
    # print(puzzle.day)
    # print(puzzle.year)
    # print(puzzle.answers)
    # print(puzzle.url)
    print(puzzle._html)
    #print(puzzle.input_file)


if __name__ == "__main__":
    main()
