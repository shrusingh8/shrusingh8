"""Builds the profile README's SVG graphics in the style of shrusingh8.github.io.

Edit the text below, then run:  python assets/build.py
Fonts are subset per image and embedded, so they render on GitHub without loading anything.
"""
import base64
import io
import re
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONTS = {"serif": "InstrumentSerif-Regular", "serif-i": "InstrumentSerif-Italic",
         "sans": "Inter-Regular", "sans-b": "Inter-SemiBold"}

BG, SURFACE, LINE = "#0a0a0a", "#131113", "#2a2428"
INK, MUTED = "#f7f1f4", "#a39aa0"
PINK, PINK2, DEEP = "#ff4fa3", "#ff8cc6", "#c2186b"


def font_face(key, text):
    opts = subset.Options()
    opts.flavor = "woff"
    f = TTFont(HERE / "fonts" / f"{FONTS[key]}.ttf")
    s = subset.Subsetter(opts)
    s.populate(text=text + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{key}';src:url(data:font/woff;base64,{b64}) format('woff');}}"


def svg(w, h, body, extra_css=""):
    """Wrap body in an SVG, embedding only the glyphs each font actually uses."""
    used = {k: "" for k in FONTS}
    for key, text in re.findall(r'class="(serif-i|serif|sans-b|sans)[^"]*"[^>]*>([^<]*)<', body):
        used[key] += text
    faces = "".join(font_face(k, t) for k, t in used.items() if t)
    css = (faces + f".serif{{font-family:'serif',Georgia,serif}}.serif-i{{font-family:'serif-i',Georgia,serif;font-style:italic}}"
           f".sans{{font-family:'sans',Inter,system-ui,sans-serif}}.sans-b{{font-family:'sans-b',Inter,system-ui,sans-serif;font-weight:600}}"
           + extra_css)
    defs = f"""<defs>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="14" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .07 0"/></filter>
<linearGradient id="pinkText" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset=".5" stop-color="{PINK2}"/><stop offset="1" stop-color="{PINK}"/>
<animate attributeName="x1" values="0;-1;0" dur="6s" repeatCount="indefinite"/><animate attributeName="x2" values="1;0;1" dur="6s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="tileBig" x1="0" y1="0" x2=".6" y2="1"><stop offset="0" stop-color="#2a0f1e"/><stop offset=".65" stop-color="{SURFACE}"/></linearGradient>
<clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f"<style>{css}</style>{defs}{body}</svg>")


_metrics = {}


def width(key, text, size):
    """Advance width of `text` in px, read from the font itself."""
    if key not in _metrics:
        f = TTFont(HERE / "fonts" / f"{FONTS[key]}.ttf")
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[key]
    return sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / upm


def t(x, y, text, cls="sans", size=16, fill=INK, extra=""):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(text)}</text>'


def card(x, y, w, h, big=False):
    fill = "url(#tileBig)" if big else SURFACE
    stroke = "rgba(255,79,163,.35)" if big else LINE
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="{fill}" stroke="{stroke}"/>'


def pill(x, y, text, filled=False):
    w = 16 + width("sans-b", text, 11.5) + 0.04 * 11.5 * len(text)
    bg, fg, st = (PINK, BG, PINK) if filled else ("rgba(255,79,163,.1)", PINK2, "rgba(255,79,163,.3)")
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{bg}" stroke="{st}"/>'
            + t(x + 8, y + 17.5, text, "sans-b", 11.5, fg, 'letter-spacing=".04em"')), w


def pills(x, y, labels, first_filled=False):
    out = ""
    for i, label in enumerate(labels):
        p, w = pill(x, y, label, first_filled and i == 0)
        out += p
        x += w + 8
    return out


def lines(x, y, texts, size, fill=MUTED, gap=1.5, cls="sans"):
    return "".join(t(x, y + i * size * gap, s, cls, size, fill) for i, s in enumerate(texts))


def write(name, content):
    (HERE / name).write_text(content, encoding="utf-8")
    print(f"{name}: {len(content) // 1024} KB")


# ---- header ---------------------------------------------------------------
W, H = 1200, 440
write("header.svg", svg(W, H, f"""<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<g filter="url(#blur)" opacity=".75">
  <circle cx="1020" cy="40" r="230" fill="{DEEP}"><animate attributeName="cx" values="1020;960;1020" dur="18s" repeatCount="indefinite"/></circle>
  <circle cx="120" cy="470" r="190" fill="#7a1d52"><animate attributeName="cy" values="470;420;470" dur="22s" repeatCount="indefinite"/></circle>
  <circle cx="640" cy="230" r="130" fill="{PINK}" opacity=".25"><animate attributeName="cx" values="640;700;640" dur="14s" repeatCount="indefinite"/></circle>
</g>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<circle cx="76" cy="84" r="5" fill="#3ddc97"><animate attributeName="r" values="5;6.5;5" dur="2s" repeatCount="indefinite"/></circle>
<circle cx="76" cy="84" r="10" fill="#3ddc97" opacity=".2"/>
{t(94, 90, "New York · NYU Honors Biology & CS · Class of 2027", "sans", 17, MUTED)}
{t(64, 222, "Hi, I'm", "serif", 128, INK, 'letter-spacing="-.02em"')}
{t(60, 352, "Shru.", "serif-i", 140, "url(#pinkText)", 'letter-spacing="-.02em" filter="url(#glow)"')}
{t(640, 228, "I find where AI looks right", "serif", 40, INK)}
{t(640, 276, "for the wrong reasons.", "serif-i", 40, PINK2)}
{pills(640, 312, ["LLM evaluation", "post-training", "clinical AI"])}
</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{LINE}"/>"""))

# ---- stats bento ------------------------------------------------------------
W, H = 1200, 380
small = [("3", ["peer-reviewed", "publications"]), ("2×", ["GRPO accuracy", "23.7% → 46.4%"]),
         ("70", ["live clinical consults", "in a blinded trial"]), ("3.88", ["GPA · Presidential", "Honors Scholar"])]
tiles = ""
for i, (num, label) in enumerate(small):
    x, y = 612 + (i % 2) * 300, 0 + (i // 2) * 194
    tiles += card(x, y, 288, 182) + t(x + 28, y + 86, num, "serif", 64, INK) + lines(x + 28, y + 124, label, 15)
write("stats.svg", svg(W, H, f"""{card(0, 0, 600, 376, big=True)}
{t(34, 54, "HEADLINE FINDING", "sans-b", 13, MUTED, 'letter-spacing=".14em"')}
{t(30, 210, "39.43", "serif", 150, PINK, 'filter="url(#glow)" letter-spacing="-.02em"')}
{t(30 + width("serif", "39.43", 150) - 0.02 * 150 * 5 + 10, 210, "pts", "sans", 18, MUTED)}
{lines(34, 266, ["drop in LLM accuracy on medical exam questions once the", "answer choices were taken away, from my first-author", "paper in Scientific Reports. Benchmarks can overstate", "how well these models actually reason."], 15.5)}
{tiles}"""))

# ---- section headers -------------------------------------------------------
def section(name, num, label, plain, italic):
    """A dark panel, so the title reads the same on GitHub's light and dark themes."""
    W, H = 1200, 150
    x2 = 36 + width("serif", plain, 56) - 0.01 * 56 * len(plain)
    write(name, svg(W, H, f"""<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="{BG}"/>
<circle cx="1120" cy="-20" r="120" fill="{DEEP}" opacity=".55" filter="url(#blur)"/>
<rect width="{W}" height="{H}" filter="url(#grain)"/></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="none" stroke="{LINE}"/>
{t(38, 50, f"{num} — {label}", "sans-b", 14, PINK, 'letter-spacing=".14em"')}
{t(36, 116, plain, "serif", 56, INK, 'letter-spacing="-.01em"')}{t(x2, 116, italic, "serif-i", 56, PINK2)}"""))


section("sec-research.svg", "01", "RESEARCH", "Three papers, ", "one question.")
section("sec-projects.svg", "02", "PROJECTS", "Things I've built ", "& open-sourced.")
section("sec-toolkit.svg", "03", "TOOLKIT", "What I ", "build with.")
section("sec-contact.svg", "04", "CONTACT", "Let's ", "talk.")

# ---- research + project cards ------------------------------------------
def info_card(name, w, h, badges, title, desc, metric=None, metric_label=None, foot=None):
    body = card(1, 1, w - 2, h - 2) + pills(28, 28, badges, first_filled=True)
    body += t(28, 108, title, "serif", 40, INK) + lines(28, 142, desc, 15)
    if metric:
        body += t(28, h - 34, metric, "serif", 40, PINK) + t(28 + width("serif", metric, 40) + 10, h - 38, metric_label, "sans", 13.5, MUTED)
    if foot:
        body += t(28, h - 30, foot, "sans-b", 13.5, PINK2, 'letter-spacing=".04em"')
    write(name, svg(w, h, body))


info_card("card-freemedqa.svg", 400, 300, ["FIRST AUTHOR", "Sci Rep 2025"], "FreeMedQA",
          ["Medical benchmark showing LLMs", "exploit multiple-choice patterns", "instead of reasoning."], "39.43", "pt accuracy drop")
info_card("card-grpo.svg", 400, 300, ["FIRST AUTHOR", "CNS 2025"], "GRPO vs. SFT",
          ["Reinforcement-learning post-training", "for neurosurgical decision support,", "8 model configurations."], "2×", "exam accuracy")
info_card("card-obsidian.svg", 400, 300, ["CO-AUTHOR", "arXiv 2025"], "CNS-Obsidian",
          ["34B vision-language model; I built", "fine-tuning and data pipelines and", "ran evaluation with 20 clinicians."], "70", "live consults")
info_card("card-groundedqa.svg", 600, 250, ["RAG", "FastAPI", "Docker", "CI"], "groundedqa",
          ["Answers must cite their sources or refuse, with an eval", "suite for retrieval, hallucinations, and refusals."], foot="VIEW REPO →")
info_card("card-freemedqa-code.svg", 600, 250, ["OPEN SOURCE", "Python", "CI"], "FreeMedQA",
          ["The pipeline behind my first-author paper: LLM filtering,", "a token-masking study, and LLM-judge scoring."], foot="VIEW REPO →")

# ---- contact buttons -------------------------------------------------------
def button(name, label, filled):
    w, h = 190, 56
    bg, fg, st = (PINK, BG, PINK) if filled else ("#131113", INK, LINE)
    tw = width("sans-b", label + " ↗", 16)
    write(name, svg(w, h, f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27" fill="{bg}" stroke="{st}"/>'
                          + t((w - tw) / 2, 34, label + " ↗", "sans-b", 16, fg)))


button("btn-email.svg", "Email me", True)
button("btn-linkedin.svg", "LinkedIn", False)
button("btn-scholar.svg", "Scholar", False)
button("btn-site.svg", "Website", False)
