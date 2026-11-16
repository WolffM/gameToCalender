# Steam Games to Calendar: features

What each part of the pipeline does and how to run it. How it's put
together is in [contributing.md](contributing.md).

## Wishlist fetching

**What it does.** `main.py` shells out to `fetch_wishlist_api.py` as a
subprocess. That script takes a Steam ID and tries three methods in order:
the official `IWishlistService` API, a Steam Community/profile-API route,
then a third store endpoint. Each is a fallback for when the one before it
is blocked or returns nothing useful. Whichever method succeeds writes the
game names to `wishlist.txt` and (for the official-API path) the raw
response to `wishlist_api_response.json`.

A fourth, unreachable method also exists: `steam_api.py` separately
defines `get_wishlist`/`scrape_wishlist_page`, which rotates through
several browser user agents and sends spoofed age-verification cookies to
scrape the wishlist page's HTML directly. `main.py` never imports or calls
either function, so this scraping path cannot run from a normal invocation
of the tool (see [contributing.md](contributing.md) for where it's imported
instead).

**How to use it.** `python main.py YOUR_STEAM_ID` runs the fetch and the
rest of the pipeline in one step; `main.py` shells out to
`fetch_wishlist_api.py` itself and reads back `wishlist.txt`.

**What it does not do.** All three reachable methods require your Steam
profile and wishlist to be set to public; a private wishlist fails every
method and the tool prints troubleshooting steps rather than finding a way
around it.

## Manual game lists

**What it does.** As an alternative to fetching, you can hand the tool game
names directly: a comma-separated list, or a text file with one name per
line (lines starting with `#` are treated as comments and skipped).

**How to use it.** `python main.py -g "Game1, Game2"` or
`python main.py -f wishlist.txt`.

**What it does not do.** Neither path validates that a name is a real Steam
game before passing it to the release lookup below — an unmatched name is
silently skipped later, with a console message, not an error.

## Release lookup

**What it does.** For each game name, `steam_api.py`'s `search_game` queries
Steam's store search API for the closest match, then `get_game_details`
fetches that app's full store page details (including its release date),
retrying with exponential backoff on a 429. `parse_release_date` tries eight
different date formats Steam is known to return (a bare year, "Dec 2023",
"25 December, 2023", and others) before giving up and keeping the raw
string.

**How to use it.** Automatic once games are loaded by either of the two
methods above — no separate step.

**What it does not do.** Lookup matches by name through Steam's search, not
by app ID, so an ambiguous or misspelled name can resolve to the wrong
game; there is no confirmation step before a game's release date is used.

## Calendar export

**What it does.** For every game with a usable, non-past release date,
`calendar_generator.py` writes an individual `.ics` file, plus one combined
`.ics` covering every game. It then builds an HTML page listing each game
with three buttons: add it to Google Calendar directly, download its own
`.ics` file, or view it on Steam. One more button, "Download All Events",
sits at the top for the combined file. The page opens automatically in your
default browser when the run finishes.

**How to use it.** No separate step; it runs at the end of every `main.py`
invocation and writes into `calendar_events/` (configurable with
`-o`/`--output-dir`).

**What it does not do.** Games whose release date is unparseable, missing,
or already in the past are silently skipped rather than listed with a
placeholder; there is no way to include past or "coming soon with no date"
releases in the output.

## Trivia

`requirements.txt` has pinned `selenium` and `webdriver_manager` since the
tool's second day, but nothing in the repo ever imports either one — the
unreachable scraping method in `steam_api.py` uses plain HTTP requests and
BeautifulSoup instead (`e78c70d`; see [contributing.md](contributing.md)).
