import base64
import urllib.parse
from html import escape
from pathlib import Path

from palette import INK, PAPER, TRADITIONAL, both_themes_tone, ink_on, lift_on
from projects import MORE, PROFILE, PROJECTS
from scenes import SCENES
from svgdoc import FALLBACKS, Doc, fit, fmt, measure

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = Path(__file__).parent / "data"
WIDTH = 1300
EDGE = "rgba(140,140,140,.38)"
HAIR = "rgba(140,148,158,.45)"
DIM = "rgba(249,244,220,.6)"


def hairline(h):
    return f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{h - 1}" fill="none" stroke="{EDGE}"/>'


def card(p):
    doc = Doc(WIDTH, 360, f"{p.name}：{p.slogan_zh} {p.slogan_en}")
    ink = ink_on(p.color_hex)
    x, right = 44, 520 - 40
    span = right - x
    left = [f'<rect width="520" height="360" fill="{p.color_hex}"/>',
            doc.text(f"№ {p.no} · {p.kind_en}", "mono", 14, x, 58, fill=ink, opacity=".72", tracking=.12),
            doc.text(f"{p.color_name} {p.color_hex}", "mono", 14, right, 58, fill=ink, opacity=".72", anchor="end"),
            doc.text(p.name, "bold", fit(p.name, "bold", 50, span), x, 134, fill=ink),
            doc.text(p.slogan_zh, "medium", fit(p.slogan_zh, "medium", 22, span), x, 178, fill=ink),
            doc.text(p.slogan_en, "serif", fit(p.slogan_en, "serif", 21, span), x, 210, fill=ink, opacity=".82")]
    sx = x
    for value, label in p.stats:
        label = label.upper()
        left.append(doc.text(value, "bold", 40, sx, 298, fill=ink))
        left.append(doc.text(label, "mono", 13, sx, 324, fill=ink, opacity=".72", tracking=.08))
        sx += max(measure(value, "bold", 40), measure(label, "mono", 13, .08)) + 32
    assert sx - 32 <= right, f"{p.repo} stats overflow the left panel ({sx - 32:.0f} > {right})"
    scene = SCENES[p.scene](doc, p)
    doc.defs.append('<clipPath id="scene"><rect x="520" width="780" height="360"/></clipPath>')
    body = (f'<rect width="{WIDTH}" height="360" fill="{INK}"/>{"".join(left)}'
            f'<g clip-path="url(#scene)"><g transform="translate(520 0)">{scene}</g></g>{hairline(360)}')
    return doc.render(body)


def header():
    h = 272
    title = f"{PROFILE['name']} {PROFILE['name_en']} · {PROFILE['slogan_zh']} {PROFILE['slogan_en']}"
    doc = Doc(WIDTH, h, title)
    avatar = base64.b64encode((DATA / "avatar.jpg").read_bytes()).decode()
    out = [f'<rect width="{WIDTH}" height="{h}" fill="{INK}"/>',
           f'<image x="40" y="40" width="144" height="144" href="data:image/jpeg;base64,{avatar}"/>',
           '<rect x="40.5" y="40.5" width="143" height="143" fill="none" stroke="rgba(255,255,255,.18)"/>',
           doc.text(PROFILE["name"], "bold", 62, 214, 106, fill=PAPER),
           doc.text(f"{PROFILE['name_en']} · {PROFILE['handle']}", "mono", 18, 216, 144, fill=DIM, tracking=.04),
           doc.text(PROFILE["site_label"], "mono", 18, 216, 174, fill=DIM, tracking=.04),
           '<path d="M600 44V180" stroke="rgba(255,255,255,.14)"/>',
           '<path d="M40 212H1260" stroke="rgba(255,255,255,.1)"/>']
    rx, rmax = 640, WIDTH - 40
    out.append(doc.text(PROFILE["slogan_zh"], "medium", fit(PROFILE["slogan_zh"], "medium", 34, rmax - rx), rx, 98, fill=PAPER))
    en_size = fit(PROFILE["slogan_en"], "serif", 23, rmax - rx)
    out.append(doc.text(PROFILE["slogan_en"], "serif", en_size, rx, 138, fill=PAPER, opacity=".78"))
    underline = doc.animate(8, [(0, "transform:scaleX(0)"), (.4, "transform:scaleX(0)"), (1.6, "transform:scaleX(1)"),
                                (7.2, "transform:scaleX(1)"), (7.8, "transform:scaleX(0)"), (8, "transform:scaleX(0)")],
                            ease="cubic-bezier(.6,0,.2,1)", extra="transform-box:fill-box;transform-origin:left center")
    en_w = measure(PROFILE["slogan_en"], "serif", en_size)
    out.append(f'<rect class="{underline}" x="{rx}" y="150" width="{fmt(en_w)}" height="2" fill="{TRADITIONAL["藤黄"]}"/>')

    size, square = 16, 12
    entries = [(p, f"{p.no} {p.name}") for p in PROJECTS]
    widths = [square + 10 + measure(label, "mono", size, .04) for _, label in entries]
    gap = (WIDTH - 80 - sum(widths)) / (len(entries) - 1)
    assert gap >= 24, f"header index row too wide (gap {gap:.0f}px)"
    slot = 1.4
    cycle = slot * len(entries)
    x, y = 40, 248
    for i, ((p, label), w) in enumerate(zip(entries, widths)):
        walk = doc.slot(cycle, i * slot, (i + 1) * slot)
        out.append(f'<rect x="{fmt(x)}" y="{y - 12}" width="{square}" height="{square}" fill="{p.color_hex}"/>'
                   f'{doc.text(label, "mono", size, x + square + 10, y, fill=PAPER, opacity=".85", tracking=.04)}'
                   f'<rect class="{walk}"{"" if i == 0 else " opacity=\"0\""} x="{fmt(x)}" y="{y + 9}" width="{fmt(w)}" height="2" '
                   f'fill="{lift_on(p.color_hex, INK, 3)}"/>')
        x += w + gap
    out.append(hairline(h))
    return doc.render("".join(out))


def divider(tones, title):
    doc = Doc(WIDTH, 44, title)
    stops = "".join(f'<stop offset="{fmt((i + 1) / (len(tones) + 1), 3)}" stop-color="{t}"/>' for i, t in enumerate(tones))
    doc.defs.append(f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{tones[0]}" stop-opacity="0"/>'
                    f'{stops}<stop offset="1" stop-color="{tones[-1]}" stop-opacity="0"/></linearGradient>'
                    '<clipPath id="ln"><rect x="0" y="19" width="616" height="6"/><rect x="684" y="19" width="616" height="6"/></clipPath>')
    sweep = doc.animate(4.5, [(0, "transform:translateX(0)"), (3.15, "transform:translateX(1620px)"), (4.5, "transform:translateX(1620px)")],
                        ease="cubic-bezier(.45,0,.25,1)")
    pulse = doc.animate(2.8, [(0, "transform:scale(1)"), (1.4, "transform:scale(.62)"), (2.8, "transform:scale(1)")],
                        ease="ease-in-out", extra="transform-box:fill-box;transform-origin:center")
    tint = ""
    if len(tones) > 1:
        tint = doc.animate(1.2 * len(tones), [(i * 1.2, f"fill:{t}") for i, t in enumerate(tones)] + [(1.2 * len(tones), f"fill:{tones[0]}")])
    body = (f'<path d="M0 22H616M684 22H1300" stroke="{HAIR}" stroke-width="1.5"/>'
            f'<g clip-path="url(#ln)"><rect class="{sweep}" x="-320" y="20.5" width="320" height="3" fill="url(#sw)"/></g>'
            f'<rect x="620" y="20" width="4" height="4" fill="{HAIR}"/><rect x="676" y="20" width="4" height="4" fill="{HAIR}"/>'
            f'<g class="{pulse}"><rect{f" class={chr(34)}{tint}{chr(34)}" if tint else ""} x="643" y="15" width="14" height="14" '
            f'fill="{tones[0]}" transform="rotate(45 650 22)"/></g>')
    return doc.render(body)


def footer():
    h = 190
    doc = Doc(WIDTH, h, f"{PROFILE['thanks_zh']} {PROFILE['thanks_en']} X {PROFILE['x_handle']} · {PROFILE['site_label']}")
    out = [f'<rect width="{WIDTH}" height="{h}" fill="{INK}"/>']
    size = 12
    total = len(PROJECTS) * size + (len(PROJECTS) - 1) * 10
    x0 = WIDTH / 2 - total / 2
    cycle = 0.5 * len(PROJECTS) + 3
    for i, p in enumerate(PROJECTS):
        t = 0.5 * i
        glow = doc.animate(cycle, [(0, "opacity:.3"), (t, "opacity:.3"), (t + .3, "opacity:1"), (cycle - 1, "opacity:1"),
                                   (cycle - .4, "opacity:.3"), (cycle, "opacity:.3")])
        out.append(f'<rect class="{glow}" x="{fmt(x0 + i * (size + 10))}" y="38" width="{size}" height="{size}" fill="{p.color_hex}"/>')
    out.append(doc.text(PROFILE["thanks_zh"], "bold", 28, WIDTH / 2, 98, fill=PAPER, anchor="middle"))
    out.append(doc.text(PROFILE["thanks_en"], "serif", 20, WIDTH / 2, 132, fill=PAPER, opacity=".78", anchor="middle"))
    out.append(doc.text(f"X {PROFILE['x_handle']}  ·  {PROFILE['site_label']}", "mono", 15, WIDTH / 2, 164, fill=DIM,
                        anchor="middle", tracking=.06))
    out.append(hairline(h))
    return doc.render("".join(out))


def shield(text):
    return urllib.parse.quote(text.replace("-", "--").replace("_", "__").replace(" ", "_"), safe="")


def badge(label, message, color):
    return (f"https://img.shields.io/badge/{shield(label)}-{shield(message)}-{color.lstrip('#')}"
            f"?style=for-the-badge&amp;labelColor={INK.lstrip('#')}")


def dynamic(path, label, color):
    return (f"https://img.shields.io/{path}?style=for-the-badge&amp;label={urllib.parse.quote(label)}"
            f"&amp;color={color.lstrip('#')}&amp;labelColor={INK.lstrip('#')}")


def link_img(href, src, alt, width=None):
    w = f' width="{width}"' if width else ""
    return f'<a href="{href}"><img src="{src}"{w} alt="{escape(alt)}"></a>'


def readme():
    gold = both_themes_tone(TRADITIONAL["姜黄"])
    lines = [
        link_img(PROFILE["site"], "assets/header.svg",
                 f"{PROFILE['name']} {PROFILE['name_en']} · {PROFILE['slogan_zh']} {PROFILE['slogan_en']}", "100%"),
        "",
        f"<b>{PROFILE['intro_zh']}</b><br>",
        f"<b>{PROFILE['intro_en']}</b>",
        "",
        link_img(f"{PROFILE['github']}?tab=repositories", dynamic("github/stars/nevertoday", "total stars", gold), "Total stars"),
        link_img(f"{PROFILE['github']}?tab=followers", dynamic("github/followers/nevertoday", "followers", TRADITIONAL["胭脂红"]),
                 "Followers"),
        link_img(PROFILE["x"], badge("X", PROFILE["x_handle"], INK), f"X {PROFILE['x_handle']}"),
        link_img(PROFILE["site"], badge("website", PROFILE["site_label"], TRADITIONAL["靛青"]), f"Website {PROFILE['site_label']}"),
        "",
    ]
    for p in PROJECTS:
        tone = both_themes_tone(p.color_hex)
        lines += [
            f'<img src="assets/divider-{p.repo}.svg" width="100%" alt="Next: {escape(p.name)}">',
            "",
            f"## {p.name}",
            "",
            link_img(p.url, f"assets/card-{p.repo}.svg", f"{p.name}：{p.slogan_zh} {p.slogan_en}", "100%"),
            "",
            f"<b>{p.lead_zh}</b>{p.body_zh}<br>",
            f"<b>{p.lead_en}</b> {p.body_en}",
            "",
            link_img(p.cta_url, badge(f"▶ {p.cta_en}", p.cta_zh, tone), p.cta_en) + "\n"
            + link_img(p.url, dynamic(f"github/stars/nevertoday/{p.repo}", p.name, gold), f"{p.name} on GitHub"),
            "",
        ]
    lines += ["<b>更多 / More</b>", ""]
    lines += [f"- [{name}]({url}) {zh} · {en}" for name, url, zh, en in MORE]
    lines += [
        "",
        '<img src="assets/divider-end.svg" width="100%" alt="End of the project list">',
        "",
        link_img(PROFILE["x"], "assets/footer.svg",
                 f"{PROFILE['thanks_zh']} {PROFILE['thanks_en']} X {PROFILE['x_handle']} · {PROFILE['site_label']}", "100%"),
        "",
        f'<p align="center"><sub>X <a href="{PROFILE["x"]}">{PROFILE["x_handle"]}</a> · '
        f'<a href="{PROFILE["site"]}">{PROFILE["site_label"]}</a> · 微信 / WeChat <code>{PROFILE["wechat"]}</code></sub></p>',
    ]
    return "\n".join(lines) + "\n"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def outputs():
    yield ASSETS / "header.svg", header
    for i, p in enumerate(PROJECTS):
        yield ASSETS / f"divider-{p.repo}.svg", lambda p=p: divider([both_themes_tone(p.color_hex)], f"Next: {p.name}")
        yield ASSETS / f"card-{p.repo}.svg", lambda p=p: card(p)
    yield ASSETS / "divider-end.svg", lambda: divider([both_themes_tone(p.color_hex) for p in PROJECTS], "End of the project list")
    yield ASSETS / "footer.svg", footer
    yield ROOT / "README.md", readme


def main():
    produced = set()
    for path, render in outputs():
        changed = write(path, render())
        produced.add(path)
        print(f"{'wrote ' if changed else 'same  '} {path.stat().st_size / 1024:8.1f} KB  {path.relative_to(ROOT)}")
    for stale in ASSETS.glob("*.svg"):
        if stale not in produced:
            stale.unlink()
            print(f"removed stale {stale.relative_to(ROOT)}")
    for (face, primary, used), chars in sorted(FALLBACKS.items()):
        print(f"fallback: face {face} ({primary}) drew {''.join(sorted(chars))} with {used}")


if __name__ == "__main__":
    main()
