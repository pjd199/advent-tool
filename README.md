# Advent Tool

This tool follows the
[automation guidelines](https://www.reddit.com/r/adventofcode/wiki/faqs/automation)
on the /r/adventofcode community wiki.

Specifically:

- Outbound calls are throttled to every x minutes in _advent.lib.http.fetch()_
- Once inputs are downloaded, they are cached locally by
  _advent.lib.cache.\_cached_or_fetch()_
- If you suspect your input is corrupted, you can manually request a fresh copy
  using _Puzzle.refresh()_
- The User-Agent header in _advent.lib.http.fetch()_ is set to me since I
  maintain this tool

  # License

  MIT License
