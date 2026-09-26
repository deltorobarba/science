#!/usr/bin/env python3
"""Build the public HTML view of science.md.

science.md stays the only source. This script turns it into one self-contained
page: collapsible parts and sections, one card per paper summary, a sidebar
table of contents, search, filters, and KaTeX for the formulas.

Usage:
  python site/build.py                          # GitHub Pages build -> _site/index.html
  python site/build.py --mode artifact --out preview.html --banner banner.jpg --katex-dir node_modules/katex/dist
"""
import argparse
import base64
import datetime
import html
import pathlib
import re
import shutil
import unicodedata

from markdown_it import MarkdownIt

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
KATEX_VERSION = "0.16.47"
FONTS = ("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600"
         "&family=Public+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap")
GLYPH = re.compile(r"(?:🟢|🔴|🟡)(?:→(?:🟢|🔴|🟡))?")
GLYPH_CODE = {"🟢": "g", "🔴": "r", "🟡": "y"}
TASKS = ("Searching", "Identifying", "Estimating")

md = MarkdownIt("commonmark", {"html": True, "typographer": False}).enable("table").enable("strikethrough")


def slugify(text, used):
    s = re.sub(r"<[^>]+>|\$[^$]*\$", "", text).lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-") or "section"
    base, n = s, 2
    while s in used:
        s, n = f"{base}-{n}", n + 1
    used.add(s)
    return s


def github_slug(text):
    """Anchor that GitHub and VS Code give a Markdown heading."""
    s = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"\s", "-", s)


def resolve_anchor(target, ctx):
    """Map a GitHub-style anchor from the Markdown source to the id on the page."""
    return target if target in ctx["used"] else ctx["gh"].get(target, target)


# ---------- markdown rendering with protected math ----------

DISPLAY_MATH = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE_MATH = re.compile(r"(?<!\\)\$([^$\n]+?)(?<!\\)\$")
PH = re.compile("\ue000(\\d+)\ue001")
FENCE = re.compile(r"^(```.*?^```[ \t]*$)", re.M | re.S)
MERMAID = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)


def render(text, ctx):
    """Markdown to HTML; formulas are shielded from the Markdown parser, code fences stay as they are."""
    store = []

    def keep(display):
        def sub(m):
            store.append((m.group(1), display))
            return f"\ue000{len(store) - 1}\ue001"
        return sub

    pieces = FENCE.split(text)
    for i in range(0, len(pieces), 2):
        pieces[i] = INLINE_MATH.sub(keep(False), DISPLAY_MATH.sub(keep(True), pieces[i]))
    out = md.render("".join(pieces))
    out = MERMAID.sub(r'<div class="diagram"><pre class="mermaid">\1</pre></div>', out)

    def restore(m):
        tex, display = store[int(m.group(1))]
        cls = "math display" if display else "math"
        return f'<span class="{cls}" data-tex="{html.escape(tex)}">{html.escape(tex)}</span>'

    out = PH.sub(restore, out)
    out = re.sub(r'<a href="(https?:)', r'<a target="_blank" rel="noopener" href="\1', out)
    out = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{resolve_anchor(m.group(1), ctx)}"', out)
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out).replace("</table>", "</table></div>")
    out = re.sub(r"<tr>\s*<td><strong>(.+?)</strong>", lambda m: row_anchor(m, ctx), out)
    out = re.sub(r"<h([3-6])>(.+?)</h\1>", lambda m: heading_anchor(m, ctx), out)
    return out


def plain_rendered(inner):
    return html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()


def plain_source(text):
    return re.sub(r"[$*`]", "", text).strip()


def row_anchor(m, ctx):
    rid = ctx["rows"].get(plain_rendered(m.group(1)))
    if rid in ctx["placed"]:
        rid = None
    elif rid:
        ctx["placed"].add(rid)
    attr = f' id="{rid}"' if rid else ""
    return f"<tr{attr}>\n<td><strong>{m.group(1)}</strong>"


def heading_anchor(m, ctx):
    level, inner = m.group(1), m.group(2)
    text = plain_rendered(inner)
    hid = ctx["hmap"].get(text)
    if not hid or hid in ctx["placed"]:
        hid = slugify(text, ctx["used"])
    ctx["placed"].add(hid)
    return f'<h{level} id="{hid}">{inner}</h{level}>'


# ---------- cross-references in the Markdown source ----------

def link_references(text, ctx):
    """Turn quoted section or row names and plain arXiv IDs into internal links (not inside code fences)."""
    out = []
    fenced = False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        if fenced or line.startswith("#") or line.startswith("```"):
            out.append(line)
            continue

        def quoted(m):
            target = ctx["titles"].get(m.group(1))
            return f'"[{m.group(1)}](#{target})"' if target else m.group(0)

        line = re.sub(r'"([^"\n]{3,110})"', quoted, line)

        def arxiv(m):
            pid = ctx["papers"].get(m.group(1))
            return f"[arXiv:{m.group(1)}](#{pid})" if pid else m.group(0)

        line = re.sub(r"(?<![\[/])arXiv:((?:\d{4}\.\d{4,5})|(?:[a-z-]+/\d{7}))(?!\]\()", arxiv, line)
        out.append(line)
    return "\n".join(out)


# ---------- structure ----------

def split_blocks(lines, prefix):
    """Split lines at headings with the given prefix ('# ' or '## ')."""
    pre, blocks = [], []
    for line in lines:
        if line.startswith(prefix):
            blocks.append([line[len(prefix):].strip(), []])
        elif blocks:
            blocks[-1][1].append(line)
        else:
            pre.append(line)
    return pre, blocks


def parse_paper(title, body):
    m = re.search(r"\(arXiv:([^)]+)\)\s*$", title)
    arxiv = m.group(1) if m else ""
    name = title[: m.start()].strip() if m else title
    intro, subs = split_blocks(body, "### ")
    intro_text = "\n".join(intro)
    authors, venue = "", ""
    am = re.search(r"\*\*(.+?)\*\*\s*\(", intro_text)
    if am:
        authors = am.group(1)
        depth, i = 1, am.end()
        while i < len(intro_text) and depth:
            depth += {"(": 1, ")": -1}.get(intro_text[i], 0)
            i += 1
        venue = intro_text[am.end():i - 1].split(";")[-1].replace("*", "").strip()
    status, promise = [], ""
    for line in body:
        if line.startswith("* **Status:**") and not status:
            status = GLYPH.findall(line)[:3]
        if line.startswith("* **Promise:**") and not promise:
            promise = line[len("* **Promise:**"):].strip()
    return dict(title=name, arxiv=arxiv, authors=authors, venue=venue,
                status=status, promise=promise, intro=intro_text, subs=subs)


def short_authors(authors):
    names = [a.strip() for a in re.split(r",\s*(?:and\s+)?|\s+and\s+", authors) if a.strip()]
    if len(names) > 3:
        return names[0].split()[-1] + " et al."
    return ", ".join(n.split()[-1] for n in names)


def first_clause(text, limit=190):
    """Text up to the first '. ' or '; ' outside a formula."""
    in_math = False
    for i, ch in enumerate(text):
        if ch == "$":
            in_math = not in_math
        elif not in_math and ch in ".;" and text[i + 1:i + 2] == " ":
            return text[:i + 1]
    return text


def status_pills(status):
    labels = ("Copies", "Time", "Memory")
    pills = []
    for label, glyph in zip(labels, status):
        parts = glyph.split("→")
        cls = "".join(GLYPH_CODE[p] for p in parts)
        word = {"g": "efficient", "r": "inefficient", "y": "partial"}
        text = " → ".join(word[GLYPH_CODE[p]] for p in parts)
        pills.append(f'<span class="pill s-{cls}" title="{label}: {text}"><i></i>{label}</span>')
    return "".join(pills)


def build(src, mode, banner, katex_dir):
    lines = src.split("\n")
    head_pre, parts = split_blocks(lines, "# ")

    ctx = {"used": set(), "titles": {}, "rows": {}, "papers": {}, "hmap": {}, "placed": set(), "gh": {}}
    # anchors for parts, sections, papers, headings and table rows
    plan = []
    for ptitle, plines in parts:
        pid = slugify(ptitle, ctx["used"])
        ctx["titles"].setdefault(ptitle, pid)
        ctx["gh"].setdefault(github_slug(ptitle), pid)
        _, secs = split_blocks(plines, "## ")
        entries = []
        for stitle, slines in secs:
            m = re.search(r"\(arXiv:([^)]+)\)\s*$", stitle)
            if ptitle.endswith("(Papers)") and m:
                sid = "p-" + re.sub(r"[^\w.-]", "-", m.group(1))
                ctx["used"].add(sid)
                ctx["papers"][m.group(1)] = sid
            else:
                sid = slugify(stitle, ctx["used"])
                ctx["titles"].setdefault(stitle, sid)
                if ": " in stitle:
                    ctx["titles"].setdefault(stitle.split(": ")[0], sid)
                for line in slines:
                    hm = re.match(r"#{3,6} (.+)", line)
                    if hm and plain_source(hm.group(1)) not in ctx["hmap"]:
                        hid = slugify(plain_source(hm.group(1)), ctx["used"])
                        ctx["hmap"][plain_source(hm.group(1))] = hid
                        ctx["titles"].setdefault(hm.group(1).strip(), hid)
                        ctx["gh"].setdefault(github_slug(hm.group(1)), hid)
            ctx["gh"].setdefault(github_slug(stitle), sid)
            entries.append(sid)
        plan.append((pid, entries))
    for line in lines:
        rm = re.match(r"\| \*\*(.+?)\*\*", line)
        if rm and plain_source(rm.group(1)) not in ctx["rows"]:
            rid = slugify("row " + plain_source(rm.group(1)), ctx["used"])
            ctx["rows"][plain_source(rm.group(1))] = rid
            ctx["titles"].setdefault(rm.group(1), rid)

    counts = {t: 0 for t in TASKS}
    toc, main = [], []
    for (ptitle, plines), (pid, sids) in zip(parts, plan):
        if ptitle == "Quantum Learning":
            continue
        pre, secs = split_blocks(plines, "## ")
        is_papers = ptitle.endswith("(Papers)")
        task = ptitle.replace(" (Papers)", "") if ptitle.replace(" (Papers)", "") in TASKS else ""
        body, toc_items = [], []
        pre_html = render(link_references("\n".join(pre), ctx), ctx).strip()
        if pre_html:
            body.append(f'<div class="prose part-intro">{pre_html}</div>')
        for (stitle, slines), sid in zip(secs, sids):
            if is_papers and sid.startswith("p-"):
                p = parse_paper(stitle, slines)
                counts[task] += 1
                subs = []
                for h3, h3lines in p["subs"]:
                    own = " own" if h3.startswith("Connections") else ""
                    open_attr = "" if h3.startswith("Questions for further study") else " open"
                    subs.append(
                        f'<details class="sub{own}"{open_attr}><summary><h3>{html.escape(h3)}</h3></summary>'
                        f'<div class="prose">{render(link_references(chr(10).join(h3lines), ctx), ctx)}</div></details>')
                sc = [GLYPH_CODE[g.split("→")[0]] for g in p["status"]] + ["", "", ""]
                promise = render(first_clause(p["promise"]), ctx) if p["promise"] else ""
                meta = " · ".join(x for x in (html.escape(short_authors(p["authors"])), html.escape(p["venue"])) if x)
                body.append(
                    f'<article class="paper" id="{sid}" data-unit data-task="{task}" '
                    f'data-c="{sc[0]}" data-t="{sc[1]}" data-m="{sc[2]}">'
                    f'<details class="paper-d"><summary>'
                    f'<div class="p-top"><h2 class="p-title">{render_inline(p["title"], ctx)}</h2>'
                    f'<a class="p-id" target="_blank" rel="noopener" href="https://arxiv.org/abs/{p["arxiv"]}">arXiv:{p["arxiv"]}</a></div>'
                    f'<div class="p-meta"><span>{meta}</span><span class="pills">{status_pills(p["status"])}</span></div>'
                    + (f'<div class="p-promise"><b>Promise</b> {promise_inline(promise)}</div>' if promise else "")
                    + f'</summary><div class="p-body"><div class="prose">{render(link_references(p["intro"], ctx), ctx)}</div>'
                    f'{"".join(subs)}</div></details></article>')
                toc_items.append(f'<li><a href="#{sid}" title="{html.escape(p["title"])}">{html.escape(p["title"])}</a></li>')
            else:
                open_attr = " open" if (ptitle == "Efficiency Boundaries" and sid == sids[0]) else ""
                body.append(
                    f'<details class="sec" id="{sid}" data-unit{open_attr}><summary><h2>{render_inline(stitle, ctx)}</h2></summary>'
                    f'<div class="prose">{render(link_references(chr(10).join(slines), ctx), ctx)}</div></details>')
                toc_items.append(f'<li><a href="#{sid}">{html.escape(re.sub(r"[$*]", "", stitle))}</a></li>')
        label = f"{counts[task]} papers" if is_papers else f"{len(secs)} sections"
        main.append(
            f'<details class="part" id="{pid}" open><summary><h1>{html.escape(ptitle)}</h1>'
            f'<span class="part-count">{label}</span></summary><div class="part-body">{"".join(body)}</div></details>')
        toc_open = "" if is_papers else " open"
        toc.append(
            f'<details class="toc-part"{toc_open}><summary><a href="#{pid}">{html.escape(ptitle)}</a></summary>'
            f'<ul>{"".join(toc_items)}</ul></details>')

    total = sum(counts.values())
    banner_src = banner or "https://raw.githubusercontent.com/deltorobarba/science/main/nature.JPG"
    built = datetime.date.today().isoformat()
    header = f"""
<header class="masthead">
  <div class="mast-text">
    <p class="eyebrow">Study notes · learning from quantum experiments</p>
    <h1 class="doc-title">Quantum Learning</h1>
    <p class="byline">Alexander Del Toro Barba, PhD</p>
    <p class="mast-sum">{total} paper summaries, sorted by task type: searching {counts['Searching']}, identifying {counts['Identifying']}, estimating {counts['Estimating']}. Every paper is rated on three budgets: copies, time, memory.</p>
  </div>
  <img class="banner" src="{banner_src}" alt="">
</header>"""

    toolbar = """
<div class="toolbar" role="search">
  <button class="toc-btn" id="toc-btn" type="button" aria-controls="sidebar" aria-expanded="false">Contents</button>
  <label class="search"><span class="sr">Search the notes</span>
    <input id="q" type="search" placeholder="Search, e.g. Bell sampling, LWE, 2403.03469" autocomplete="off"></label>
  <div class="chips" id="task-chips" aria-label="Papers by task type">
    <button type="button" data-task="" aria-pressed="true">All papers</button>
    <button type="button" data-task="Searching" aria-pressed="false">Searching</button>
    <button type="button" data-task="Identifying" aria-pressed="false">Identifying</button>
    <button type="button" data-task="Estimating" aria-pressed="false">Estimating</button>
  </div>
  <div class="chips" id="status-chips" aria-label="Papers by status">
    <button type="button" data-status="" aria-pressed="true">Any status</button>
    <button type="button" data-status="ggg" aria-pressed="false">Efficient in all three</button>
    <button type="button" data-status="t-r" aria-pressed="false">Time inefficient</button>
    <button type="button" data-status="c-r" aria-pressed="false">Copies inefficient</button>
  </div>
  <div class="tb-actions">
    <button type="button" id="expand">Expand all</button>
    <button type="button" id="collapse">Collapse all</button>
    <span class="result" id="result" aria-live="polite"></span>
  </div>
</div>"""

    css = (HERE / "style.css").read_text(encoding="utf-8")
    js = (HERE / "app.js").read_text(encoding="utf-8")
    if mode == "artifact":
        katex_css = inline_katex_css(pathlib.Path(katex_dir))
        head_links = f'<link rel="stylesheet" href="{FONTS}">'
    else:
        katex_css = ""
        head_links = (f'<link rel="stylesheet" href="{FONTS}">\n'
                      f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css">')
    katex_js = f'<script src="https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js"></script>'

    page = f"""<title>Quantum Learning</title>
<meta name="description" content="Study notes on quantum learning theory: {total} paper summaries on searching, identifying and estimating, rated by copies, time and memory.">
{head_links}
<style>{katex_css}
{css}</style>
<div class="layout">
  <nav class="sidebar" id="sidebar" aria-label="Contents">
    <p class="side-title">Contents</p>
    {''.join(toc)}
    <p class="built">Built {built} from science.md</p>
  </nav>
  <main id="main">
    {header}
    {toolbar}
    <p class="empty" id="empty" hidden>Nothing matches. Clear the search or pick another filter.</p>
    {''.join(main)}
  </main>
</div>
{katex_js}
<script>{js}</script>"""
    if mode == "pages":
        page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + page.replace("<div class=\"layout\">", "</head>\n<body>\n<div class=\"layout\">", 1)
                + "\n</body>\n</html>\n")
    return page


def render_inline(text, ctx):
    out = render(text, ctx).strip()
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def promise_inline(rendered):
    return re.sub(r"^<p>(.*)</p>$", r"\1", rendered.strip(), flags=re.S)


def inline_katex_css(dist):
    """KaTeX stylesheet with its woff2 fonts embedded, for pages that cannot load external CSS."""
    css = (dist / "katex.min.css").read_text(encoding="utf-8")

    def font(m):
        path = dist / "fonts" / (m.group(1) + ".woff2")
        data = base64.b64encode(path.read_bytes()).decode()
        return f'src:url(data:font/woff2;base64,{data}) format("woff2")'

    return re.sub(r"src:url\(fonts/([\w-]+)\.woff2\)[^;}]*", font, css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "science.md"))
    ap.add_argument("--out", default=str(ROOT / "_site" / "index.html"))
    ap.add_argument("--mode", choices=("pages", "artifact"), default="pages")
    ap.add_argument("--banner", help="image file embedded as the banner (artifact mode)")
    ap.add_argument("--katex-dir", help="local katex/dist folder (artifact mode)")
    a = ap.parse_args()
    banner = None
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.banner:
        banner = "data:image/jpeg;base64," + base64.b64encode(pathlib.Path(a.banner).read_bytes()).decode()
    elif a.mode == "pages" and (HERE / "banner.jpg").exists():
        shutil.copyfile(HERE / "banner.jpg", out.parent / "banner.jpg")
        banner = "banner.jpg"
    page = build(pathlib.Path(a.src).read_text(encoding="utf-8"), a.mode, banner, a.katex_dir)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({len(page) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
