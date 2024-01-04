"""HTTP interface for the Advent of Code website."""
import logging
from urllib.error import HTTPError

# from ratelimit.decorators import sleep_and_retry
# from ratelimit_requests_cache import limits_if_not_cached
from requests import Response, get
# from requests_cache import NEVER_EXPIRE, SQLiteCache, install_cache

# from advent.lib.cache import read, write
from advent.lib.config import settings

# # Install requests caching
# install_cache(
#     cache_name="aoc",
#     backend=SQLiteCache(".advent-tool/http_cache.sqlite"),
#     expire_after=NEVER_EXPIRE,
# )


# @sleep_and_retry
# @limits_if_not_cached(calls=2, period=20)
def cached_and_limited_get(
    url: str, headers: dict[str, str], force_refresh: bool = False
) -> Response:
    """Request a webpage, using both rate limiting and caching.

    Args:
        url (str): the URL to get
        headers (dict[str, str]): the HTTP Request headers
        force_refresh (bool): When True, forces a cache refresh

    Returns:
        Response: the Response object
    """
    return get(
        url,
        headers=headers,
        timeout=10,
        #        force_refresh=force_refresh,
    )


def fetch(url: str, force_refresh: bool = False) -> str:
    """Download file from URL.

    Args:
        url (str): the URL to download.
        force_refresh (bool): refresh from the server

    Raises:
        HTTPError: Raised if unable to download
    """
    # prepare to download
    headers = {"User-Agent": settings.http_user_agent}
    if settings.session:
        headers["Cookie"] = f"session={settings.session}"
    else:
        logging.warning("No SESSION ID found.")

    headers[
        "Cookie"
    ] = "session=53616c7465645f5f83dc98098b10409cc49444d0bbd6c1bf9b9be7b98e34f61d49bc33562d5a9467500f1eb438b48c3f6bddfbd8922a42e6b18ed0c2e364ae4d"
    response = get(url, headers=headers)

    # get the file
    # response = cached_and_limited_get(url, headers, force_refresh=force_refresh)
    logging.info(
        f"GET - {url} - {response.status_code} {response.reason}"  # ({'HIT' if response.from_cache else 'MISS'})"
    )
    if response.status_code != 200:
        raise HTTPError(url, response.status_code, response.reason)
    return response.text


def fetch_puzzle_page(year: int, day: int, force_refresh: bool = False) -> str:
    """Fetch the puzzle page from the website.

    Args:
        year (int): the year
        day (int): the day
        force_refresh (bool): refresh from the server

    Returns:
        str: the html page
    """
    return fetch(url_for(year, day), force_refresh)


def fetch_puzzle_input(year: int, day: int) -> str:
    """Fetch teh puzzle input file.

    Args:
        year (int): the year
        day (int): the day

    Returns:
        str: the puzzle input file
    """
    return fetch(f"{url_for(year,day)}/input")


def url_for(year: int, day: int) -> str:
    """Get the full URL for this puzzle.

    Args:
        year (int): the year
        day (int): the day

    Returns:
        str: the URL
    """
    return f"{settings.http_root}/{year}/day/{day}"
