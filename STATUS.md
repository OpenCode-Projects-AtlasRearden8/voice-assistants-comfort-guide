# STATUS.md — Voice Assistants Comfort Guide

Last updated: 2026-10-27

## What was built

A complete beginner manual for smart speakers (Alexa, Google Assistant/Siri on HomePod), in the "explains it like a friend would" voice of the Massive AI Manual series by Asdale Dynamics, LLC.

**Docs (12 Markdown files, all readable standalone in `docs/`):**
- Guides: welcome, setup-in-a-weekend, privacy settings, daily commands, routines (reminders/timers), voice-shopping + 3 scam warnings, kids-and-guests settings, troubleshooting ladder (7 rungs), "phone vs. speaker" honest comparison.
- Reference: per-brand command cheat sheets + a cross-brand translation table, printable setup checklists (universal + per brand, checkbox-formatted), plain-English glossary.

**Build system (`build.py`, Python 3 standard library only, zero dependencies):**
- Converts `docs/*.md` → static HTML site in `site/` with sidebar nav, reading order, prev/next pager, mobile-responsive styling, and brand-specific rendering for tables, code spans, blockquotes, numbered/bulleted lists, and checkbox lists.
- Optional built-in check mode (runs automatically): verifies pages are non-empty, every internal markdown link resolves to a real page, and the Asdale Dynamics, LLC credit appears on every page. Exit code reflects pass/fail.

**Repo files:** README.md (with run instructions + LLC credit), MIT LICENSE with the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`, `.gitignore`, this STATUS.md.

## How to run it

```bash
python3 build.py          # builds site/ from docs/ and self-checks
# optional local preview:
python3 -m http.server 8000 --directory site
# then open http://localhost:8000
```

No internet, no installs, no accounts. Read the Markdown directly, or open `site/00-welcome.html` in a browser.

## Verification results (all passing)

- `python3 build.py` → exit code 0, 12 pages built, "All checks passed."
- Link audit: 0 broken internal links in the generated HTML.
- Content coverage spot-check: key terms (voice profile, PIN, wake word, 2.4GHz) present; no placeholders or glitch characters.
- Checklist rendering verified (43 checkbox items render as `<input type="checkbox">` in HTML).
- Table rendering verified (cheat-sheet tables output as proper `<table><tr><th>…` HTML).
- License file content verified against the required exact copyright line.
- No secrets, API keys, or personal data present in any file.

## Known gaps

- Apple HomePod coverage is lighter than Alexa/Google (HomePod genuinely has fewer settings, e.g., no named timers as of writing); worth revisiting after major iOS updates.
- No search box on the site (static site is only 12 pages; browser Ctrl+F is honestly fine).
- Exact screen-by-screen app menu names will drift as Amazon/Google/Apple redesign apps; the doc comments flag this where known.
- The `smart-home-comfort-guide` is linked as a companion but lives in its own repo; the cross-link assumes its GitHub location stays valid.
- Ratios: one wake-word edge case (Alexa's "Computer" wake word) is mentioned but not exhaustively walked through.
