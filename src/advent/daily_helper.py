"""A helper script for downloading puzzle webpages and puzzle input."""
from argparse import ArgumentParser
from datetime import date, datetime, timezone
from importlib import import_module
from json import dump, load
from pathlib import Path
from re import match
from sys import path
from typing import Any
from webbrowser import open as webbrowser_open

import pytest
from bs4 import BeautifulSoup
from markdownify import ATX, markdownify  # type: ignore
from requests import get

if __name__ == "__main__":
    path.append(str(Path(__file__).parent.parent))  # pragma: no cover

from advent_of_code.utils.function_timer import function_timer
from advent_of_code.utils.input_loader import load_puzzle_input_file
from advent_of_code.utils.runner import runner
from advent_of_code.utils.solver_status import puzzle_date_generator

AOC_ROOT = "https://adventofcode.com"
REPOSITORY = "https://github.com/pjd199/advent_of_code_python"
cache_path = "./.aoc_website_cache"


def sorted_with_numeric_key(d: dict[str, Any]) -> dict[str, Any]:
    """Sort the dictionary using numeric string key.

    Args:
        d (dict[str, Any]): the input dictionary

    Returns:
        dict[str, Any]: a new, sorted dictionary
    """
    return dict(sorted(d.items(), key=lambda x: int(x[0])))


class DailyHelper:
    """The help for a specific day."""

    def __init__(
        self,
        year: int,
        day: int,
        session: str | None = None,
        flush: bool = False,
        verbose: bool = False,
        test: bool = False,
        open_webpage: bool = False,
        run_puzzle_cli: bool = False,
        timing: bool = False,
    ) -> None:
        """Initialise the helper for a specific day.

        Args:
            year (int): the year for the puzzle
            day (int): the day for the puzzle
            session (str | None): the session cookie for the Advent of Code website
            flush (bool): if True, ignores cached files. Default False
            verbose (bool): if True, enables logging. Default False
            test (bool): if True, enables testing. Default False
            open_webpage (bool): if True, open the url in a browser. Default False
            run_puzzle_cli (bool): if True, run the puzzle CLI. Default False
            timing (bool): if True, store the timings. Default False
        """
        self.year = year
        self.day = day
        self.session = session
        self.flush = flush
        self.verbose = verbose
        self.test = test
        self.open_webpage = open_webpage
        self.run_puzzle_cli = run_puzzle_cli
        self.timing = timing

        self.title = ""
        self.answers: list[str] = []

        self.html_path = Path(f"{cache_path}/year{year}/day{day}/index.html")
        self.part_one_path = Path(f"{cache_path}/year{year}/day{day}/part_one.md")
        self.part_two_path = Path(f"{cache_path}/year{year}/day{day}/part_two.md")
        self.response_path = Path(f"{cache_path}/year{year}/day{day}/response.json")
        self.expected_path = Path("./tests/expected.json")
        self.puzzle_metadata_path = Path("./advent_of_code/puzzle_metadata.json")
        self.puzzle_input_path = Path(f"./puzzle_input/year{year}/day{day}.txt")
        self.solver_module_path = Path(f"./advent_of_code/year{year}/day{day}.py")
        self.solver_init_path = Path(f"./advent_of_code/year{year}/__init__.py")
        self.template_text_path = Path("./advent_of_code/template.txt")

    def run(self) -> int:
        """The download, parsing and file creation sequence.

        Returns:
            int: the return code, 0 unless an error
        """
        self._flush()

        # define the page and input url's
        page_url = f"{AOC_ROOT}/{self.year}/day/{self.day}"
        input_url = f"{AOC_ROOT}/{self.year}/day/{self.day}/input"

        # open in a browser, if requested
        if self.open_webpage:
            webbrowser_open(page_url)
            webbrowser_open(input_url)

        # download the webpage from Advent of Code website
        self._download(page_url, self.html_path, ok_if_exists=True)

        # parse the html file
        with Path(self.html_path).open() as file:
            soup = BeautifulSoup(file, "html.parser")

        # find and save the part descriptions
        parts = soup.find_all("article", attrs={"class": "day-desc"})
        md_paths = [self.part_one_path, self.part_two_path]
        for i in range(min(len(parts), len(md_paths))):
            self._save(
                md_paths[i], markdownify(str(parts[i]), heading_style=ATX, wrap=80)
            )

        # save the puzzle input file
        self._download(
            f"{AOC_ROOT}/{self.year}/day/{self.day}/input",
            self.puzzle_input_path,
            ok_if_exists=True,
        )

        # find the puzzle title
        h2 = soup.find_all("h2")
        for x in h2:
            if m := match(r"--- Day (?:\d+): (?P<title>.+) ---", x.string):
                self.title = m["title"].replace('"', "'")

        # find and save the answers, if solved
        para = soup.find_all("p")
        self.answers = [
            x.code.string for x in para if x.text.startswith("Your puzzle answer was")
        ]
        self._save_response()

        # extract the excerpt
        self.excerpt = parts[0].find_all("p")[0].text

        # save the expected responses
        self._save_expected()

        # create and save a new python solver file
        desc = soup.find_all("article", attrs={"class": "day-desc"})
        for d in desc:
            d.h2.extract()

        with Path(self.template_text_path).open() as file:
            template = "".join(file.readlines())

        self._save(
            self.solver_module_path,
            template.format(
                year=self.year,
                day=self.day,
                title=self.title,
            ),
            ok_if_exists=True,
        )

        # make sure the folder has an __init__.py
        self._save(
            self.solver_init_path,
            '"""Nothing to initialise."""',
            ok_if_exists=True,
        )

        # run the puzzle solver
        if self.run_puzzle_cli:
            runner(
                import_module(f"advent_of_code.year{self.year}.day{self.day}").Solver
            )

        # save the puzzle metadata
        self._save_metadata()

        # run the testing
        self._testing()

        return 0

    def _log(self, line: str) -> None:
        """Print line if in verbose mode.

        Args:
            line (str): the line to print
        """
        if self.verbose:
            print(line)

    def _flush(self) -> None:
        """Flush cached files."""
        if self.flush:
            paths_to_remove = [
                self.html_path,
                self.part_one_path,
                self.part_two_path,
                self.response_path,
                self.puzzle_input_path,
            ]
            for x in paths_to_remove:
                self._log(f"Flushing cache for {x}")
                x.unlink(missing_ok=True)

    def _save(
        self,
        path: Path,
        data: str | dict[str, Any],
        force: bool = False,
        ok_if_exists: bool = False,
    ) -> None:
        """Save data to a file.

        Args:
            path (Path): the save path
            data (str | dict[str, Any]): the data to save
            force (bool): If True, overwrites existing file. Defaults to False.
            ok_if_exists (bool): If False, warn if already exists. Defaults to False.
        """
        if not force and path.is_file():
            if not ok_if_exists:
                self._log(f"File {path} already exists")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with Path(path).open("w") as file:
                if isinstance(data, str):
                    file.write(data)
                else:
                    dump(data, file, indent=4)
                self._log(f"Saved {path}")

    def _save_expected(self) -> None:
        """Save expected.json."""
        data = {
            "title": self.title,
            "year": self.year,
            "day": self.day,
        }
        if len(self.answers) >= 1:
            data["part_one"] = self.answers[0]

            if len(self.answers) >= 2:
                data["part_two"] = self.answers[1]

        # open expected existing file
        with Path(self.expected_path).open() as file:
            expected = load(file)

        if str(self.year) not in expected:
            expected[str(self.year)] = {}

        if (
            str(self.day) not in expected[str(self.year)]
            or expected[str(self.year)][str(self.day)] != data
        ):
            expected[str(self.year)][str(self.day)] = data

            self._save(
                self.expected_path,
                sorted_with_numeric_key(
                    {k: sorted_with_numeric_key(v) for k, v in expected.items()}
                ),
                force=True,
            )
        else:
            self._log(f"Data already stored in {self.expected_path}")

    def _save_response(self) -> None:
        """Save JSON response."""
        response = {
            "title": self.title,
            "year": self.year,
            "day": self.day,
        }
        if len(self.answers) > 0:
            response["part_one"] = self.answers[0]

        if len(self.answers) > 1:
            response["part_two"] = self.answers[1]

        # save the answers
        self._save(Path(self.response_path), response)

    def _save_metadata(self) -> None:
        """Save metadata.json."""
        # open existing metadata file
        file_updated = False
        with Path(self.puzzle_metadata_path).open() as file:
            metadata = load(file)

        if str(self.year) not in metadata:
            metadata[str(self.year)] = {}

        if str(self.day) not in metadata[str(self.year)]:
            self._log(f"Creating entry in {self.puzzle_metadata_path}")
            # first save of metadata
            metadata[str(self.year)][str(self.day)] = {
                "year": self.year,
                "day": self.day,
                "title": self.title,
                "excerpt": self.excerpt,
                "has_part_one": True,
                "has_part_two": self.day != 25,
                "part_one_solved": len(self.answers) >= 1,
                "part_two_solved": len(self.answers) == 2,
            }
            file_updated = True
        elif metadata[str(self.year)][str(self.day)]["part_one_solved"] != (
            len(self.answers) >= 1
        ) or metadata[str(self.year)][str(self.day)]["part_two_solved"] != (
            len(self.answers) == 2
        ):
            self._log(f"Updating status in {self.puzzle_metadata_path}")
            metadata[str(self.year)][str(self.day)]["part_one_solved"] = (
                len(self.answers) >= 1
            )
            metadata[str(self.year)][str(self.day)]["part_two_solved"] = (
                len(self.answers) == 2
            )
            file_updated = True

        if (
            len(self.answers) == 2 or (len(self.answers) == 1 and self.day == 25)
        ) and "completion_date" not in metadata[str(self.year)][str(self.day)]:
            self._log(f"Updating completion date {self.puzzle_metadata_path}")
            metadata[str(self.year)][str(self.day)]["completion_date"] = datetime.now(
                tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S%zZ")
            file_updated = True

        if self.timing:
            self._log(f"Updating timings {self.puzzle_metadata_path}")

            metadata[str(self.year)][str(self.day)]["timings"] = {}
            metadata[str(self.year)][str(self.day)]["timings"]["unit"] = "ms"

            self._log("Timing parse")
            mod = import_module(f"advent_of_code.year{self.year}.day{self.day}")
            puzzle_input = load_puzzle_input_file(self.year, self.day)
            solver, time = function_timer(mod.Solver, puzzle_input)
            metadata[str(self.year)][str(self.day)]["timings"]["parse"] = time

            self._log("Timing part one")
            _, time = function_timer(solver.solve_part_one)
            metadata[str(self.year)][str(self.day)]["timings"]["part_one"] = time

            if self.day != 25:
                self._log("Timing for part two")
                _, time = function_timer(solver.solve_part_two)
                metadata[str(self.year)][str(self.day)]["timings"]["part_two"] = time
            file_updated = True
        elif "timings" not in metadata[str(self.year)][str(self.day)]:
            print("No timings in metadata - run daily_helper with -T to time function.")

        if file_updated:
            self._save(
                self.puzzle_metadata_path,
                sorted_with_numeric_key(
                    {k: sorted_with_numeric_key(v) for k, v in metadata.items()}
                ),
                force=True,
            )
        else:
            self._log(f"Data already stored in {self.puzzle_metadata_path}")

    def _download(self, url: str, path: Path, ok_if_exists: bool) -> None:
        """Download file from URL.

        Args:
            url (str): the URL to download.
            path (Path): the location of the downloaded file.
            ok_if_exists (bool): if True, logs message is file exists

        Raises:
            RuntimeError: Raised if unable to download
        """
        if path.is_file() and ok_if_exists:
            self._log(f"URL {url} already downloaded to {path}")
        else:
            self._log(f"Downloading {url}")
            path.parent.mkdir(parents=True, exist_ok=True)
            headers = {
                "User-Agent": REPOSITORY,
            }
            if self.session:
                headers["cookie"] = f"session={self.session}"
            response = get(url, headers=headers, timeout=60)
            if response.status_code == 200:
                self._save(path, response.text)
            else:
                raise RuntimeError(  # noqa: TRY003
                    f"Unable to download file: "
                    f"server status code {response.status_code}"
                )

    def _testing(self) -> None:
        """Test the Solver."""
        if self.test:
            options = [
                "./tests/unit",
                "-k",
                f"{self.year}-{self.day:02}",
                f"--cov=advent_of_code.year{self.year}.day{self.day}",
                "--no-cov-on-fail",
                "--cov-fail-under=100",
                "--cov-reset",
                "-W ignore::DeprecationWarning",
            ]
            if self.verbose:
                options += ["-v", "--cov-report", "term-missing"]
            else:
                options += ["-q", "--cov-report="]

            pytest.main(options)


def main() -> int:
    """Main function, called from the command line.

    Returns:
        int: the return code, ussually 0.
    """
    parser = ArgumentParser(
        description="Helper for downloading puzzles and input from"
        "the Advent of Code website."
    )
    parser.add_argument("year", type=int, help="the year to download.")
    parser.add_argument(
        "day",
        type=int,
        help="the day to download.",
    )
    parser.add_argument(
        "--session",
        "-s",
        type=str,
        help="set the session cookie for the Advent of Code website.",
        action="store",
    )
    parser.add_argument(
        "--save_session",
        "-ss",
        help="set and store the session cookie for the Advent of Code website",
        action="store",
        metavar="SESSION",
    )
    parser.add_argument(
        "--flush",
        "-f",
        help="flush the cache for this year and day",
        action="store_true",
    )
    parser.add_argument(
        "--open",
        "-o",
        help="open puzzle on the Advent of Code website",
        action="store_true",
    )
    parser.add_argument(
        "--timing", "-T", help="update timing in metadata", action="store_true"
    )
    parser.add_argument("--verbose", "-v", help="verbose mode", action="store_true")
    parser.add_argument("--run", "-r", help="run the puzzle file", action="store_true")
    parser.add_argument("--test", "-t", help="run unit tests", action="store_true")

    args = parser.parse_args()

    # handle the session cookie loading and saving
    session_path = Path(f"{cache_path}/.session")
    if args.session:
        session = args.session
    elif args.save_session:
        session = args.save_session
        session_path.parent.mkdir(exist_ok=True, parents=True)
        with Path(session_path).open("w") as file:
            file.write(session)
    elif session_path.is_file():
        with Path(session_path).open() as file:
            session = file.readline()
    else:
        session = None

    if date(args.year, 12, args.day) in puzzle_date_generator():
        return DailyHelper(
            args.year,
            args.day,
            session,
            args.flush,
            args.verbose,
            args.test,
            args.open,
            args.run,
            args.timing,
        ).run()

    print(f"Invalid date: year={args.year}, day={args.day}")
    return 1


if __name__ == "__main__":
    main()
