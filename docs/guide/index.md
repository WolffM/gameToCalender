---
title: Steam Games to Calendar
summary: >-
  A command-line tool that takes a Steam wishlist (by Steam ID, or a plain
  text list of game names) and builds calendar events for each game's
  upcoming release, as downloadable .ics files and a browser page with
  one-click "add to Google Calendar" links.
features:
  - name: Wishlist fetching
    summary: 'Pulls your Steam wishlist by Steam ID, with several fallback methods if the first one is blocked.'
    anchor: wishlist-fetching
  - name: Manual game lists
    summary: 'Pass game names directly, or from a text file, when you''d rather not fetch a wishlist.'
    anchor: manual-game-lists
  - name: Release lookup
    summary: 'Looks each game up on Steam''s store search to find its release date.'
    anchor: release-lookup
  - name: Calendar export
    summary: 'Writes one .ics file per game, plus a page to add them to Google Calendar or download them all at once.'
    anchor: calendar-export
trivia:
  - 'A stray test script, `test_api_key.py`, was added on the tool''s second day and deleted again that same evening — it lived under ten hours (`e78c70d` → `48e5211`).'
  - 'Fetching a wishlist tries three API-style methods in order — the official `IWishlistService` API, then a community/store-API route, then a third store endpoint (`e78c70d`, `48e5211`). A fourth, HTML-scraping approach also exists in `steam_api.py`, but nothing in the tool''s actual run path ever calls it.'
  - '`requirements.txt` has pinned `selenium` and `webdriver_manager` since the tool''s second day, but no file in the repo ever imports either one (`e78c70d`).'
  - 'The README''s own "Download This Project" instructions have told a reader to clone a URL that was never this repo''s address — `github.com/yourusername/steamGamesToCalendar` — since the very first commit (`a430569`).'
---

# Steam Games to Calendar

A single command turns a Steam wishlist into calendar reminders. Give it a
Steam ID (or just a list of game names), and it looks up each game's
release date on Steam. It writes an `.ics` calendar file for every
upcoming release, and opens a page where you can add them to Google
Calendar one at a time, or download them all in one file.

![The page the tool opens when it finishes: two upcoming releases, each with a release date, a short description, and buttons to add it to Google Calendar, download its .ics file, or view it on Steam](images/calendar-page.webp)

- [Features](features.md): what each piece does and how to run it.
- [Contributing](contributing.md): running it locally, its layout, what has no tests.
- [History](history.md): two days of building in March 2025, then a lint-and-typing pass ten months later.
- [Trivia](trivia.md)

## Trivia

Fetching a Steam wishlist tries three API-style methods in sequence; a
fourth, HTML-scraping method also exists in the repo but is never actually
reachable from a normal run
([features](features.md#wishlist-fetching)).
