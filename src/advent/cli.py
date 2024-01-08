"""Command Line Interace for the Advent Tool."""
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta, timezone
from logging import INFO, getLogger, info
from time import sleep

from advent import load_puzzle

tz = timezone(timedelta(hours=-5), "EST")


def now() -> datetime:
    """The current time in EST / UTC-5.

    Returns:
        datetime: the time
    """
    return datetime.now(tz=tz)


def _countdown_string(delta: timedelta) -> str:
    hours, seconds = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    text = "Puzzle unlocks in"
    if delta.days > 0:
        text += f" {delta.days} day" + "s" if delta.days > 1 else ""
    if delta.days > 0:
        text += f" {hours} hour" + "s" if hours > 1 else ""
    if delta.days > 0:
        text += f" {minutes} minute" + "s" if minutes > 1 else ""
    if delta.days > 0:
        text += f" {seconds} second" + "s" if seconds > 1 else ""
    return text


def fetch_command(args: Namespace) -> None:
    """Handle the fetch command.

    Args:
        args (Namespace): the command line arguments
    """
    if args.year == now().year and args.day > now().day:
        print(_countdown_string(datetime(args.year, 12, args.day, tzinfo=tz) - now()))
        return

    puzzle = load_puzzle(args.year, args.day)
    print(f"Fetched {puzzle.day:02} {puzzle.year:04} {puzzle.title}")


def cache_command(args: Namespace) -> None:
    """Handle the cache command.

    Args:
        args (Namespace): the command line arguments
    """
    last_day = (
        max(now().day, 25) if now().month == 12 and args.year == now().year else 25
    )

    for day in range(1, last_day + 1):
        puzzle = load_puzzle(args.year, day)
        _ = puzzle.input_file
        info(f"Caching {puzzle.day:02}/12/{puzzle.year:04}: {puzzle.title}")


def countdown_command(args: Namespace) -> None:
    """Handle the countdown command."""
    # find the unlock time
    if now().month < 12:
        unlock = datetime(now().year, 12, 1, tzinfo=tz)
    elif now().day > 25:
        unlock = datetime(now().year + 1, 12, 1, tzinfo=tz)
    else:
        unlock = datetime(now().year, 12, now().day + 1, tzinfo=tz)

    # find the time difference
    if args.wait:
        while unlock > now():
            print(f"\r{_countdown_string(unlock - now())}", end="")
            sleep(0.1)
    else:
        print(_countdown_string(unlock - now()))


def _create_argument_parser() -> ArgumentParser:
    """Create the argument parser."""
    # get the current puzzle year
    year = now().year - 1 if now().month < 12 else now().year

    # create the main parser
    parser = ArgumentParser(
        description="Helper for downloading puzzles and input from"
        "the Advent of Code website."
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    # fetch sub-command
    fetch_parser = subparsers.add_parser("fetch", help="fetch help")
    fetch_parser.add_argument(
        "year",
        type=int,
        choices=range(2015, year + 1),
        metavar="year",
        help=f"the year to fetch (2015 to {year})",
    )
    fetch_parser.add_argument(
        "day",
        type=int,
        choices=range(1, 26),
        metavar="day",
        help="the day to fetch (1 to 25)",
    )
    fetch_parser.set_defaults(func=fetch_command)

    # cache sub-command
    cache_parser = subparsers.add_parser("cache", help="cache help")
    cache_parser.add_argument(
        "year",
        type=int,
        choices=range(2015, year + 1),
        metavar="year",
        help=f"the year to cache (2015 to {year})",
    )
    cache_parser.set_defaults(func=cache_command)

    # countdown sub-command
    countdown_parser = subparsers.add_parser("countdown", help="countdown help")
    countdown_parser.set_defaults(func=countdown_command)
    countdown_parser.add_argument(
        "--wait",
        "-w",
        action="store_true",
        help="wait until countdown reaches zero",
    )
    cache_parser.set_defaults(func=cache_command)

    return parser


def main() -> None:
    """Main CLI entry point."""
    getLogger().setLevel(INFO)
    args = _create_argument_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
