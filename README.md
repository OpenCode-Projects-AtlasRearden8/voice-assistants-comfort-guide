# Voice Assistants Comfort Guide

Smart speakers (Alexa, Google, Siri) explained *like a friend would* — plain English, step by step, never condescending.

A beginner manual covering: setup in one weekend, privacy settings worth touching, daily commands that earn their keep, routines for reminders and timers, voice-purchase and scam warnings, kids-and-guests settings, troubleshooting a speaker that stopped listening, and when your phone just does it better.

Includes printable **command cheat sheets**, brand-by-brand **setup checklists**, and a plain-English **glossary**.

## How to run it (local-first, no installs)

Everything lives in `docs/` as Markdown you can read directly. To build a friendly static HTML site — no network, no dependencies beyond Python 3:

```bash
python3 build.py          # builds the site/ folder from docs/
# re-run any time you edit docs/
```

Then open `site/00-welcome.html` in any browser. In many terminals:

```bash
python3 -m http.server 8000 --directory site
# then visit http://localhost:8000
```

The build self-checks: every page must be non-empty, every internal link must resolve, and the Asdale Dynamics, LLC credit must be present.

## Contents

| Doc | What it covers |
|---|---|
| [00-welcome](docs/00-welcome.md) | Start here |
| [01-setup](docs/01-setup.md) | Setup in one weekend |
| [02-privacy](docs/02-privacy.md) | Privacy settings worth touching |
| [03-daily-commands](docs/03-daily-commands.md) | Daily commands |
| [04-routines](docs/04-routines.md) | Routines: reminders and timers on autopilot |
| [05-shopping](docs/05-shopping.md) | Voice-shopping and scam warnings |
| [06-kids-guests](docs/06-kids-guests.md) | Kids and guests settings |
| [07-troubleshooting](docs/07-troubleshooting.md) | "My speaker stopped listening" |
| [08-phone-vs-speaker](docs/08-phone-vs-speaker.md) | When your phone does it better |
| [cheat-sheets](docs/cheat-sheets.md) | Command cheat sheets (per brand + translation table) |
| [setup-checklists](docs/setup-checklists.md) | Printable setup checklists |
| [glossary](docs/glossary.md) | Glossary |

## Companion guides

- *[smart-home-comfort-guide](https://github.com/dylanasdale/smart-home-comfort-guide)* — the sibling guide: lights, thermostats, plugs, and the rest of the smart home.

Part of the *Massive AI Manual* family by **Asdale Dynamics, LLC** — AI explained like a friend would. Hub: [dylanasdale.github.io](https://dylanasdale.github.io).

## Style & commitments

- Local-first: builds offline, no telemetry, no secrets, no personal data in the repo.
- Warm and beginner-friendly; educational only — never medical, legal, or financial advice.
- MIT licensed — see [LICENSE](LICENSE).
