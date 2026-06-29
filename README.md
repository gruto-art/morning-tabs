# Morning Tabs

> A tiny macOS app that walks you through your morning browser routine — one tab at a time, across many Chrome profiles, with one click.

If you start your day on the same 15 links spread across 5 different Chrome
profiles (personal, work, side project, that one for your spouse, the burner
account that's logged into TikTok…), you know the dance: command-clicking,
profile switching, getting lost.

**Morning Tabs** is a 600-line Python/Tkinter app that solves exactly that and
nothing more. You configure a plain-text file per profile listing the URLs you
want to open. You double-click an icon on your Desktop. You click **"Open &
Next"**. Each click opens the next link **in the correct Chrome profile**.
That's the whole thing.

![Morning Tabs UI](docs/screenshot.png)

## Why this exists

Chrome's "open all bookmarks" opens everything at once, in one profile. Browser
sync doesn't help. Bookmark folders don't help. You wanted: linear, paced,
profile-aware morning routine. So here it is.

## Install (60 seconds)

```bash
git clone https://github.com/gruto-art/morning-tabs.git
cd morning-tabs

# 1. Discover your Chrome profile directory names
bash scripts/list-profiles.sh
#   Directory      Display name              Email / account
#   --------------------------------------------------------
#   Default        Personal                  you@gmail.com
#   Profile 1      Work                      you@company.com
#   Profile 2      Side project              you@startup.io

# 2. Create one .txt file per profile in profiles/
#    The first comment line MUST be `# PROFILE=<directory>`.
#    See profiles/01-example-*.txt for the format.

# 3. Install the Desktop app (creates "Morning Tabs.app" on your Desktop)
bash scripts/install-desktop-app.sh
```

Double-click **Morning Tabs.app** on your Desktop. Done.

## File format

`profiles/01-anything.txt`:

```
# PROFILE=Profile 1
# Display name: My side project   ← optional, shown in the app
https://github.com/me/my-project
https://my-project.com/admin
https://stripe.com/dashboard
```

- Files are picked up in alphabetical order — prefix with `01-`, `02-` to
  control the order in which profiles cycle.
- Lines starting with `#` are comments (except the magic `# PROFILE=` line).
- Empty lines are ignored.
- You can also edit URLs inside the app — click **Edit profile**.

## Features

- **Cycle through URLs one click at a time** — no batch dump
- **Each URL opens in the correct Chrome profile** automatically
- **Edit URLs inside the app** — add, remove, reorder, save
- **Skip, go back, jump to any URL** with double-click
- **Visual progress** — ✓ for visited, ○ for pending, ► for current
- **Plain-text config** — edit profiles/*.txt in any editor you like
- **Zero dependencies** — uses only the Python 3 standard library
- **No data leaves your machine** — opens local URLs in local Chrome, that's it

## Use cases

- Morning routine — inboxes, dashboards, social, news
- Daily standup prep — Linear, GitHub PRs, Slack
- Multi-client work — open each client's dashboards in their own profile
- Investigations — keep different identities completely isolated
- Anyone tired of right-clicking → "Open Link As → Profile X"

## Bonus: `open-chrome.sh`

The original "open everything at once" script is included as
[open-chrome.sh](open-chrome.sh). Wire it to a macOS LaunchAgent if you want
your full morning routine to pop open at 9:00 AM every weekday. The Python app
exists because that script was too aggressive — sometimes you want to walk
through your tabs at your own pace.

## Requirements

- macOS 10.13+
- Python 3 (Apple ships it; `/usr/bin/python3`)
- Google Chrome

## License

MIT — see [LICENSE](LICENSE). PRs welcome.

## Acknowledgments

Born out of "I have 14 Chrome profiles and I refuse to install yet another
launcher app for one button." Built in an afternoon with Claude.
