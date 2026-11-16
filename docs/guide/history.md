# Steam Games to Calendar: history

Two short eras, 290 days apart: two days of building in March 2025, then
an automated maintenance pass.

## Built over two days

The whole tool was built over two days, 2025-03-10 (a Monday) and
2025-03-11 (a Tuesday). The first commit, that Monday night, already laid
down the full shape readers see today: `main.py`, `steam_api.py` (at this
point just Steam search and release-date lookup), `calendar_generator.py`,
and a README already written as a full "Complete Setup Guide for
Beginners" — including a `git clone` line pointing at a URL,
`github.com/yourusername/steamGamesToCalendar`, that was never this repo's
actual address, boilerplate nobody replaced before it was committed
(`a430569`). Twenty minutes later the same night, `steam_api.py` gained
its wishlist-fetching code, including the HTML-scraping method with
rotating user agents and spoofed age-verification cookies described in
[features.md](features.md#wishlist-fetching) — code that, as it turns
out, nothing in `main.py` ever calls (`176d7e1`).

The next morning, `fetch_wishlist_api.py` was added as the standalone
script `main.py` actually shells out to for fetching a wishlist, with two
working methods (a community/profile route and a store endpoint) and a
third, since-removed fallback to the player's owned-games list;
`requirements.txt` grew to five packages in this same
commit, including `selenium` and `webdriver_manager`, which nothing in the
repo has ever imported (`e78c70d`). That evening, a third method — the
official `IWishlistService` API — was added ahead of the other two, and
successful fetches started saving their raw response to
`wishlist_api_response.json` (`48e5211`).

The repo then went 290 days without a commit, from `48e5211` on
2025-03-11 to an automated commit refreshing its checked-in wishlist and
log output on 2025-12-26 (`9730eb9`) (fact sheet, 2026-11-16).

## A maintenance pass

In January 2026 the repo picked up the same `vibecheck.yml` static-analysis
workflow several of this account's other small repos did around the same
time (`67c6629`, updated six days later in `650f613`). The same day the
workflow was added, three Copilot-authored commits landed: prefixing
unused loop variables (`0dc0d4b`), dropping an unnecessary `f`-string
prefix (`bf27b1e`), and adding explicit workflow permissions (`abab435`).
A fourth Copilot-authored commit, six days later, added a missing
type-stub dependency so the project's mypy check could resolve
`beautifulsoup4`'s types (`2195b34`). None of these changed what the tool
does.

## Trivia

A stray script, `test_api_key.py`, was added the tool's second morning
and deleted again that same evening — it lived under ten hours
(`e78c70d` → `48e5211`).
