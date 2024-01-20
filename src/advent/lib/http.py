"""HTTP interface for the Advent of Code website."""
from logging import getLogger
from sqlite3 import connect

from pyrate_limiter.abstracts.rate import Duration, Rate
from pyrate_limiter.buckets.sqlite_bucket import Queries, SQLiteBucket
from pyrate_limiter.limiter import Limiter
from requests import get, post

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

# get the logger
log = getLogger(__name__)


def fetch(url: str, data: dict[str, str] | None = None) -> str:
    """Download file from URL, optionally POSTing data.

    Args:
        url (str): the URL to download.
        data (dict[str,str] | None): the data to POST

    Returns:
        str: the download file

    Raises:
        HTTPError: Raised if unable to download
    """
    # apply the rate limiter, delaying until we're good to go
    if _bucket.count() > _bucket_size:
        log.info("Enforcing HTTP rate limits")
    limiter.try_acquire(url)

    # prepare the headers and cookies
    headers = {"User-Agent": settings.http_user_agent}
    cookies = {}
    if settings.session:
        cookies["session"] = settings.session
    else:
        log.warning("No SESSION ID found.")

    if data:
        # POST the URL
        response = post(url, headers=headers, cookies=cookies, timeout=60, data=data)
        log.info(f"POST - {url} - {response.status_code} {response.reason}")
    else:
        # GET the URL
        response = get(url, headers=headers, cookies=cookies, timeout=60)
        log.info(f"GET - {url} - {response.status_code} {response.reason}")

    # check the response and return the file
    if response.status_code != 200:
        raise FileNotFoundError
    return response.text
