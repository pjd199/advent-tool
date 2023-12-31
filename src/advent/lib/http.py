"""HTTP interface for the Advent of Code website."""
import logging
from sqlite3 import connect

from pyrate_limiter.abstracts.rate import Duration, Rate
from pyrate_limiter.buckets.sqlite_bucket import Queries, SQLiteBucket
from pyrate_limiter.limiter import Limiter
from requests import get

from advent.lib.config import settings

# create the rate limiter using an SQLite backend, to allow
# 3 requests every 3 seconds (i.e. average of one a second).
_bucket_size = 3
_rates = [
    Rate(_bucket_size, _bucket_size * Duration.SECOND),
]
_table = "my-bucket-table"
_sqlite_connection = connect(
    ".advent-tool/pyrate.sqlite",
    isolation_level="EXCLUSIVE",
    check_same_thread=False,
)
_sqlite_connection.cursor().execute(Queries.CREATE_BUCKET_TABLE.format(table=_table))
_bucket = SQLiteBucket(_rates, _sqlite_connection, _table)
limiter = Limiter(_bucket, max_delay=Duration.MINUTE)


def fetch(url: str) -> str:
    """Download file from URL.

    Args:
        url (str): the URL to download.

    Returns:
        str: the download file

    Raises:
        HTTPError: Raised if unable to download
    """
    # apply the rate limiter, delaying until we're good to go
    if _bucket.count() > _bucket_size:
        logging.info("Enforcing HTTP rate limits")
    limiter.try_acquire(url)

    # prepare the headers and cookies
    headers = {"User-Agent": settings.http_user_agent}
    cookies = {}
    if settings.session:
        cookies["session"] = settings.session
    else:
        logging.warning("No SESSION ID found.")

    # get the URL
    response = get(url, headers=headers, cookies=cookies, timeout=60)
    logging.info(f"GET - {url} - {response.status_code} {response.reason}")

    # check the response and return the file
    if response.status_code != 200:
        raise FileNotFoundError
    return response.text
