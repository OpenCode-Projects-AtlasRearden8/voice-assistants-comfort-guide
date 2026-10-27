#!/usr/bin/env python3
"""Build script: converts docs/*.md into a static HTML site in site/.

No dependencies: uses only the Python standard library. Run:

    python3 build.py

Optionally verify output:

    python3 build.py --check
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

SITE_NAME = "Smart Speakers, Explained Like a Friend Would"
OWNER = "Asdale Dynamics, LLC"
FOOTER = f"{OWNER} · part of the <a href='https://dylanasdale.github.io'>Massive AI Manual</a> family · educational only, never medical or legal advice"

# Order of the handbook (nav + reading order)
PAGE_ORDER = [
    "00-welcome",
    "01-setup",
    "02-privacy",
    "03-daily-commands",
    "04-routines",
    "05-shopping",
    "06-kids-guests",
    "07-troubleshooting",
    "08-phone-vs-speaker",
    "cheat-sheets",
    "setup-checklists",
    "glossary",
]


# ------------------------- minimal Markdown renderer -------------------------

def inline(text: str) -> str:
    """Inline markdown: code, bold, italic, links."""
    # protect code spans first
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    # restore code spans
    text = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{html.escape(spans[int(m.group(1))], quote=False)}</code>", text)
    return text


def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    in_para = False

    def close_para():
        nonlocal in_para
        if in_para:
            out.append("</p>")
            in_para = False

    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            close_para()
            out.append("<pre><code>")
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                out.append(html.escape(lines[i]))
                i += 1
            out.append("</code></pre>")
            i += 1
            continue

        # table: header | separator | rows
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1]) and "|" in lines[i + 1]:
            close_para()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append("<table>")
            out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>")
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</table>")
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            close_para()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            close_para()
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if line.strip().startswith(">"):
            close_para()
            out.append("<blockquote>")
            while i < len(lines) and lines[i].strip().startswith(">"):
                out.append(f"<p>{inline(lines[i].lstrip(' >'))}</p>")
                i += 1
            out.append("</blockquote>")
            continue

        # checkbox list
        m = re.match(r"^\s*- \[([ xX])\] (.*)$", line)
        if m:
            close_para()
            checked = " checked" if m.group(1).strip().lower() == "x" else ""
            out.append(f'<div class="todo"><input type="checkbox" disabled{checked}><span>{inline(m.group(2))}</span></div>')
            i += 1
            continue

        # unordered list
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            close_para()
            out.append(f"<{tag}>")
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append(f"</{tag}>")
            continue

        # paragraph
        stripped = line.strip()
        if stripped:
            if not in_para:
                out.append("<p>")
                in_para = True
            out.append(inline(stripped))
        else:
            close_para()
        i += 1
    close_para()
    return "\n".join(out)


# ------------------------------- page plumbing -------------------------------

def extract_title(md_text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def md_links_to_html(text: str) -> str:
    # [label](file.md) -> [label](file.html), [label](file.md#anchor) likewise
    return re.sub(
        r"\]\(([^)#]+?)\.md(\.md)*(?=[#)])",
        lambda m: "](" + m.group(1) + ".html",
        text,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {site}</title>
<meta name="description" content="{desc}">
<style>
:root {{
  --bg:#fdf8f2; --ink:#2b2620; --soft:#6b6259; --accent:#b4502f;
  --card:#fff; --line:#e8ded2; --code-bg:#f3ece2;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Georgia,'Times New Roman',serif; background:var(--bg); color:var(--ink); line-height:1.7; }}
a {{ color:var(--accent); }}
.layout {{ display:flex; min-height:100vh; }}
nav.sidebar {{ width:250px; flex-shrink:0; background:var(--card); border-right:1px solid var(--line); padding:1.5rem 1.2rem; }}
nav.sidebar .brand {{ font-weight:bold; font-size:1.05rem; margin-bottom:1.2rem; display:block; color:var(--ink); text-decoration:none; }}
nav.sidebar .brand span {{ color:var(--accent); }}
nav.sidebar a.item {{ display:block; padding:.28rem .4rem; color:var(--soft); text-decoration:none; font-size:.93rem; border-radius:6px; }}
nav.sidebar a.item:hover {{ background:var(--code-bg); color:var(--ink); }}
nav.sidebar a.item.current {{ background:var(--code-bg); color:var(--accent); font-weight:bold; }}
main {{ flex:1; max-width:760px; padding:2.5rem 2rem 3rem; }}
@media (max-width:820px) {{ .layout {{ flex-direction:column; }} nav.sidebar {{ width:100%; border-right:none; border-bottom:1px solid var(--line); }} main {{ padding:1.5rem 1.2rem 2.5rem; }} }}
h1 {{ font-size:1.9rem; line-height:1.25; margin-top:0; }}
h2 {{ font-size:1.35rem; margin-top:2.2rem; border-bottom:1px solid var(--line); padding-bottom:.3rem; }}
h3 {{ font-size:1.1rem; margin-top:1.6rem; }}
p, li {{ font-size:1.02rem; }}
table {{ border-collapse:collapse; width:100%; margin:1.2rem 0; font-size:.95rem; }}
th, td {{ border:1px solid var(--line); padding:.45rem .6rem; text-align:left; vertical-align:top; }}
th {{ background:var(--code-bg); }}
tr:nth-child(even) td {{ background:#fbf5ec; }}
code {{ background:var(--code-bg); padding:.1rem .35rem; border-radius:4px; font-size:.9em; font-family:ui-monospace,Menlo,Consolas,monospace; }}
pre code {{ display:block; padding:.8rem 1rem; overflow-x:auto; }}
blockquote {{ margin:1.2rem 0; padding:.6rem 1rem; background:var(--code-bg); border-left:4px solid var(--accent); border-radius:0 6px 6px 0; }}
blockquote p {{ margin:.2rem 0; }}
.todo {{ display:flex; gap:.55rem; align-items:flex-start; margin:.3rem 0; }}
.todo input {{ margin-top:.45rem; }}
.pager {{ display:flex; justify-content:space-between; gap:1rem; margin-top:3rem; padding-top:1rem; border-top:1px solid var(--line); }}
.pager a {{ text-decoration:none; }}
.pager .next {{ margin-left:auto; text-align:right; }}
footer {{ color:var(--soft); font-size:.85rem; margin-top:3rem; padding-top:1rem; border-top:1px solid var(--line); }}
.pill {{ display:inline-block; background:var(--code-bg); color:var(--soft); font-size:.8rem; padding:.15rem .6rem; border-radius:999px; margin-bottom:1rem; }}
</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
<a class="brand" href="00-welcome.html">Smart Speakers<br><span>like a friend would say it</span></a>
{nav}
</nav>
<main>
<span class="pill">Handbook page {num} of {total}</span>
{body}
<div class="pager">
{prev_link}
{next_link}
</div>
<footer>{footer}</footer>
</main>
</div>
</body>
</html>
"""


def build() -> list:
    SITE.mkdir(exist_ok=True)
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    # load docs
    pages = {}
    for md_file in sorted(DOCS.glob("*.md")):
        slug = md_file.stem
        text = md_file.read_text(encoding="utf-8")
        pages[slug] = text

    # order pages; anything unlisted goes last
    ordered = [s for s in PAGE_ORDER if s in pages] + [s for s in pages if s not in PAGE_ORDER]

    nav_items = []
    for slug in ordered:
        title = extract_title(pages[slug], slug)
        cls = " item"  # current marked at page render time
        nav_items.append((slug, title))
        _ = cls

    results = []
    total = len(ordered)
    for idx, slug in enumerate(ordered, 1):
        text = pages[slug]

        # split front matter (optional `--- key: value ---` block)
        desc = ""
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k.strip() == "description":
                        desc = v.strip()
            text = text[m.end():]

        body = md_to_html(md_links_to_html(text))
        title = extract_title(text, slug)

        nav = []
        for s, t in nav_items:
            current = " current" if s == slug else ""
            nav.append(f'<a class="item{current}" href="{s}.html">{t}</a>')
        nav_html = "\n".join(nav)

        prev_link = ""
        if idx > 1:
            pslug = ordered[idx - 2]
            ptitle = extract_title(pages[pslug], pslug)
            prev_link = f'<a href="{pslug}.html">&larr; {ptitle}</a>'
        next_link = ""
        if idx < total:
            nslug = ordered[idx]
            ntitle = extract_title(pages[nslug], nslug)
            next_link = f'<a class="next" href="{nslug}.html">{ntitle} &rarr;</a>'

        page = TEMPLATE.format(
            title=html.escape(title),
            site=html.escape(SITE_NAME),
            desc=html.escape(desc or f"{title} — {SITE_NAME}"),
            nav=nav_html,
            body=body,
            prev_link=prev_link,
            next_link=next_link,
            num=idx,
            total=total,
            footer=FOOTER,
        )

        out_path = SITE / f"{slug}.html"
        out_path.write_text(page, encoding="utf-8")
        results.append((slug, out_path))

    return results


def check(built: list) -> int:
    """Sanity-check the built site. Returns count of problems."""
    problems = 0
    for _, path in built:
        if not path.exists() or path.stat().st_size == 0:
            print(f"FAIL: empty/missing {path}")
            problems += 1
    # every internal .html link must resolve
    names = {p.stem + ".html" for _, p in built}
    for _, path in built:
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"#]+?)(?:#[^"]*)?"', text):
            href = m.group(1)
            if href.startswith(("http", "mailto:")) or href.endswith((".css", ".js", ".ico")):
                continue
            target = href.split("#")[0]
            if target and not (SITE / target).exists():
                print(f"FAIL: broken link {href!r} in {path}")
                problems += 1
    # all pages should have the footer credit
    for _, path in built:
        if OWNER not in path.read_text(encoding="utf-8"):
            print(f"FAIL: missing credit in {path}")
            problems += 1
    return problems


def main() -> int:
    built = build()
    print(f"Built {len(built)} pages into site/:")
    for slug, path in built:
        print(f"  {slug}.html  ({path.stat().st_size:,} bytes)")
    problems = check(built)
    if problems:
        print(f"\n{problems} problem(s) found.")
        return 1
    print("\nAll checks passed: pages non-empty, links resolve, credit present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
