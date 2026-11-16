# Steam Games to Calendar: trivia

Each fact names the commit or sheet it comes from.

## Trivia

- **Three ways to ask Steam for the same list, and a fourth that never
  runs.** Fetching a wishlist tries an official API, then a
  community/profile route, then a third store endpoint, in that order
  (`e78c70d`, `48e5211`). A fourth method, HTML scraping with rotating
  user agents and spoofed age-verification cookies, also exists in
  `steam_api.py` — but `main.py` never calls it, so it cannot run from a
  normal use of the tool (`176d7e1`).
- **An unused dependency since the tool's second day.** `requirements.txt`
  grew to include `selenium` and `webdriver_manager` on 2025-03-11, but no
  file in the repo has ever imported either package (`e78c70d`).
- **A placeholder clone URL, committed from the start.** The README's
  beginner setup guide has told readers to `git clone` a URL —
  `github.com/yourusername/steamGamesToCalendar` — that was never this
  repo's real address, since the very first commit (`a430569`).
- **290 quiet days, then an automated commit.** After the two days it was
  built in, the repo didn't change again for 290 days, until an automated
  commit refreshed its checked-in wishlist and log files on 2025-12-26
  (`48e5211` → `9730eb9`; fact sheet, 2026-11-16).
