"""Command Line Interace for the Advent Tool."""
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta, timezone
from logging import DEBUG, INFO, WARNING, basicConfig, getLogger
from subprocess import PIPE, STDOUT, Popen
from sys import executable
from time import sleep
from webbrowser import open_new_tab

from colorama import Fore, Style, init

from advent import __version__, load_puzzle
from advent.lib.config import settings
from advent.lib.part import PART_ONE, Part
from advent.lib.template import save_template

# configure the logger
basicConfig(
    level=WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = getLogger(__name__)

EST = timezone(timedelta(hours=-5), "EST")

# initialize colorama
init()


def now() -> datetime:
    """The current time in EST / UTC-5.

    Returns:
        datetime: the time
    """
    return datetime.now(tz=EST)


def _countdown_string(delta: timedelta) -> str:
    hours, seconds = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    text: list[str] = []
    if delta.days > 0:
        text.append(f"{delta.days} day" + "s" if delta.days > 1 else "")
    if delta.days > 0:
        text.append(f" {hours} hour" + "s" if hours > 1 else "")
    if delta.days > 0:
        text.append(f" {minutes} minute" + "s" if minutes > 1 else "")
    if delta.days > 0:
        text.append(f" {seconds} second" + "s" if seconds > 1 else "")
    return "Puzzle unlocks in " + ",".join(text)


def fetch_command(args: Namespace) -> None:
    """Handle the fetch command.

    Args:
        args (Namespace): the command line arguments
    """
    if args.year == now().year and args.day > now().day:
        print(_countdown_string(datetime(args.year, 12, args.day, tzinfo=EST) - now()))
        return

    puzzle = load_puzzle(args.year, args.day)
    if args.force:
        puzzle.refresh()
    log.info(f"Fetched {puzzle.day:02} {puzzle.year:04} {puzzle.title}")

    if settings.template_save_enabled:
        save_template(puzzle)


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
        print(f"Caching {puzzle.day:02}/12/{puzzle.year:04}: {puzzle.title}")


def countdown_command(args: Namespace) -> None:
    """Handle the countdown command.

    Args:
        args (Namespace): the command line arguments
    """
    # find the unlock time
    if now().month < 12:
        unlock = datetime(now().year, 12, 1, tzinfo=EST)
    elif now().day > 25:
        unlock = datetime(now().year + 1, 12, 1, tzinfo=EST)
    else:
        unlock = datetime(now().year, 12, now().day + 1, tzinfo=EST)

    # find the time difference
    if args.wait:
        try:
            while unlock > now():
                print(f"\r{_countdown_string(unlock - now())}", end="")
                sleep(0.1)
        except KeyboardInterrupt:
            print()
    else:
        print(_countdown_string(unlock - now()))


def open_command(args: Namespace) -> None:
    """Handle the open sub-command.

    Args:
        args (Namespace): the command line arguments
    """
    puzzle = load_puzzle(args.year, args.day)
    open_new_tab(puzzle.page_url)
    open_new_tab(puzzle.input_url)


def read_command(args: Namespace) -> None:
    """Handle the read sub-command.

    Args:
        args (Namespace): the command line arguments
    """
    part = Part(args.part)
    puzzle = load_puzzle(args.year, args.day)

    if puzzle.descriptions[part]:
        print(puzzle.descriptions[part])
    else:
        print(f"Part {'One' if part == PART_ONE else 'Two'} not yet fetched")


def status_command(args: Namespace) -> None:
    """Handle the status sub-command.

    Args:
        args (Namespace): the command line arguments
    """
    puzzle = load_puzzle(args.year, args.day)
    for part in Part:
        part_str = f"Part {'One' if part == PART_ONE else 'Two'}"
        if puzzle.answers[part]:
            print(f"Your answer to {part_str} was {puzzle.answers[part]}")
            print(f"{Fore.GREEN}That's the right answer!{Style.RESET_ALL}")
        else:
            for answer, message in puzzle.submitted[part].items():
                color = (
                    Fore.GREEN if "That's the right answer!" in message else Fore.RED
                )
                print(f"Your answer to {part_str} was {answer}")
                print(f"{color}{message}{Style.RESET_ALL}")


def run_command(args: Namespace) -> None:
    """Handle the run sub-command.

    Args:
        args (Namespace): the command line arguments
    """
    name = settings.template_save_path.format(
        year=args.year,
        day=args.day,
    )

    print(f"Executing {executable} {name}")
    process = Popen(
        [executable, name],  # noqa: S603
        stdout=PIPE,
        stderr=STDOUT,
        bufsize=0,
    )
    if process.stdout is not None:
        with process.stdout:
            for line in iter(process.stdout.readline, b""):  # b'\n'-separated lines
                print(bytes.decode(line).strip())


def set_verbose_level(args: Namespace) -> None:
    """Handle the verbose command."""
    match args.verbose:
        case 0:
            log.setLevel(WARNING)
        case 1:
            log.setLevel(INFO)
        case _:
            log.setLevel(DEBUG)


def _create_argument_parser() -> ArgumentParser:
    """Create the argument parser."""

    def add_year_argument(parser: ArgumentParser) -> None:
        year = now().year - 1 if now().month < 12 else now().year
        parser.add_argument(
            "year",
            type=int,
            choices=range(2015, year + 1),
            metavar="year",
            help=f"the year to fetch (2015 to {year})",
        )

    def add_day_argument(parser: ArgumentParser) -> None:
        parser.add_argument(
            "day",
            type=int,
            choices=range(1, 26),
            metavar="day",
            help="the day to open (1 to 25)",
        )

    def add_part_argument(parser: ArgumentParser) -> None:
        parser.add_argument(
            "part",
            type=int,
            choices=range(1, 3),
            metavar="part",
            default=1,
            nargs="?",
            help="the part to read (1 or 2)",
        )

    # create the main parser
    parser = ArgumentParser(
        description="Helper for downloading puzzles and input "
        "from the Advent of Code website."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="verbose (can be supplied multiple times to increase verbosity)",
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"%(prog)s {__version__}"
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subparsers = parser.add_subparsers(help="sub-commands")

    # fetch sub-command
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="fetch a puzzle, save input and create code template.",
    )
    add_year_argument(fetch_parser)
    add_day_argument(fetch_parser)
    fetch_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="force a cache refresh",
    )
    fetch_parser.set_defaults(func=fetch_command)

    # cache sub-command
    cache_parser = subparsers.add_parser(
        "cache",
        help="cache puzzle page and puzzle input from the AOC server",
    )
    add_year_argument(cache_parser)
    cache_parser.set_defaults(func=cache_command)

    # countdown sub-command
    countdown_parser = subparsers.add_parser(
        "countdown",
        help="countdown to the next puzzle unlock",
    )
    countdown_parser.add_argument(
        "--wait",
        "-w",
        action="store_true",
        help="wait until countdown reaches zero",
    )
    countdown_parser.set_defaults(func=countdown_command)

    # open sub-command
    open_parser = subparsers.add_parser(
        "open", help="open puzzle on the Advent of Code website"
    )
    add_year_argument(open_parser)
    add_day_argument(open_parser)
    open_parser.set_defaults(func=open_command)

    # read sub-command
    read_parser = subparsers.add_parser(
        "read", help="read the puzzle on the command line"
    )
    add_year_argument(read_parser)
    add_day_argument(read_parser)
    add_part_argument(read_parser)
    read_parser.set_defaults(func=read_command)

    # status sub-command
    status_parser = subparsers.add_parser("status", help="show the status of a puzzle")
    add_year_argument(status_parser)
    add_day_argument(status_parser)
    status_parser.set_defaults(func=status_command)

    # run sub-command
    run_parser = subparsers.add_parser("run", help="run the puzzle")
    add_year_argument(run_parser)
    add_day_argument(run_parser)
    run_parser.set_defaults(func=run_command)

    return parser


def main() -> None:
    """Main CLI entry point."""
    args = _create_argument_parser().parse_args()
    set_verbose_level(args)
    args.func(args)


if __name__ == "__main__":
    main()
