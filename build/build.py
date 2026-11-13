from html import escape
from pathlib import Path

from palette import INK, both_themes_tone, panel_tone
from projects import MORE, PROFILE, PROJECTS
from scenes import SCENES
from svgdoc import FALLBACKS, Doc, fit, fmt, measure

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
WIDTH = 1300
EDGE = "rgba(140,140,140,.38)"


def hairline(h):
    return f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{h - 1}" fill="none" stroke="{EDGE}"/>'


def card(p):
    doc = Doc(WIDTH, 360, f"{p.name}：{p.slogan_zh} {p.slogan_en}")
    bg, ink = panel_tone(p.color_hex)
    x, right = 44, 520 - 40
    span = right - x
    tag = f"{p.color_name} {p.color_hex}"
    tag_w = measure(tag, "mono", 15)
    left = [f'<rect width="520" height="360" fill="{bg}"/>',
            doc.text(f"№ {p.no} · {p.kind_en}", "mono", 15, x, 58, fill=ink, tracking=.12),
            f'<rect x="{fmt(right - tag_w - 24)}" y="44" width="16" height="16" fill="{p.color_hex}"/>' if bg != p.color_hex else "",
            doc.text(tag, "mono", 15, right, 58, fill=ink, anchor="end"),
            doc.text(p.name, "bold", fit(p.name, "bold", 50, span), x, 134, fill=ink),
            doc.text(p.slogan_zh, "medium", fit(p.slogan_zh, "medium", 23, span), x, 178, fill=ink),
            doc.text(p.slogan_en, "serif", fit(p.slogan_en, "serif", 22, span), x, 212, fill=ink)]
    sx = x
    for value, label in p.stats:
        label = label.upper()
        left.append(doc.text(value, "bold", 40, sx, 298, fill=ink))
        left.append(doc.text(label, "mono", 14, sx, 324, fill=ink, tracking=.08))
        sx += max(measure(value, "bold", 40), measure(label, "mono", 14, .08)) + 32
    assert sx - 32 <= right, f"{p.repo} stats overflow the left panel ({sx - 32:.0f} > {right})"
    scene = SCENES[p.scene](doc, p)
    doc.defs.append('<clipPath id="scene"><rect x="520" width="780" height="360"/></clipPath>')
    body = (f'<rect width="{WIDTH}" height="360" fill="{INK}"/>{"".join(left)}'
            f'<g clip-path="url(#scene)"><g transform="translate(520 0)">{scene}</g></g>{hairline(360)}')
    return doc.render(body)


LIGHT = {"text": "#1F2328", "muted": "#59636E", "line": "#D1D9E0"}
DARK = {"text": "#F0F6FC", "muted": "#9198A1", "line": "#3D444D"}


def theme_css(c, inverse):
    return (f".t{{fill:{c['text']}}}.m{{fill:{c['muted']}}}.l{{stroke:{c['line']}}}"
            f".bg{{fill:{c['text']}}}.inv{{fill:{inverse['text']}}}")


THEME_CSS = theme_css(LIGHT, DARK) + "@media (prefers-color-scheme:dark){" + theme_css(DARK, LIGHT) + "}"


def themed_doc(w, h, title):
    """Transparent SVG whose ink follows the viewer's light or dark scheme."""
    doc = Doc(w, h, title)
    doc.css.append(THEME_CSS)
    return doc


def breathing_squares(doc, x_end, y, size=10, gap=8):
    """The six project colors, lit one after another, ending at x_end."""
    n = len(PROJECTS)
    x0 = x_end - n * size - (n - 1) * gap
    step, cycle = 1.2, 1.2 * n + 2.4
    out = []
    for i, p in enumerate(PROJECTS):
        t = i * step
        glow = doc.animate(cycle, [(0, "opacity:.35"), (t, "opacity:.35"), (t + .5, "opacity:1"), (t + 1.6, "opacity:1"),
                                   (t + 2.4, "opacity:.35"), (cycle, "opacity:.35")])
        out.append(f'<rect class="{glow}" x="{fmt(x0 + i * (size + gap))}" y="{fmt(y)}" width="{size}" height="{size}" '
                   f'fill="{both_themes_tone(p.color_hex)}"/>')
    return "".join(out)


def header():
    h = 236
    doc = themed_doc(WIDTH, h, f"{PROFILE['name']} {PROFILE['name_en']} · {PROFILE['slogan_zh']} {PROFILE['slogan_en']}")
    label = f"{PROFILE['name']}  {PROFILE['name_en'].upper()}  ·  {PROFILE['handle'].upper()}"
    out = [doc.text(label, "mono", 20, 0, 34, cls="m", tracking=.12),
           doc.text(PROFILE["slogan_zh"], "bold", fit(PROFILE["slogan_zh"], "bold", 64, WIDTH), 0, 124, cls="t"),
           doc.text(PROFILE["slogan_en"], "serif", fit(PROFILE["slogan_en"], "serif", 32, WIDTH), 0, 176, cls="m"),
           f'<path class="l" d="M0 220.5H{WIDTH - 140}"/>',
           breathing_squares(doc, WIDTH, 215)]
    return doc.render("".join(out))


def footer():
    h = 180
    doc = themed_doc(WIDTH, h, f"{PROFILE['thanks_zh']} {PROFILE['thanks_en']}")
    n = len(PROJECTS)
    out = [breathing_squares(doc, WIDTH / 2 + (n * 10 + (n - 1) * 8) / 2, 30),
           doc.text(PROFILE["thanks_zh"], "medium", fit(PROFILE["thanks_zh"], "medium", 34, WIDTH), WIDTH / 2, 106,
                    cls="t", anchor="middle"),
           doc.text(PROFILE["thanks_en"], "serif", 26, WIDTH / 2, 150, cls="m", anchor="middle")]
    return doc.render("".join(out))


def button(zh, en, arrow="→", accent=None, filled=False):
    h, pad = 40, 16
    fg, sub = ("inv", "inv") if filled else ("t", "m")
    x = pad
    square = ""
    if accent:
        square = f'<rect x="{x}" y="15" width="10" height="10" fill="{both_themes_tone(accent)}"/>'
        x += 20
    zh_x, x = x, x + measure(zh, "medium", 15) + 10
    en_x, x = x, x + measure(en, "mono", 11, .12) + 12
    arrow_x, x = x, x + measure(arrow, "mono", 14)
    w = round(x + pad)
    doc = themed_doc(w, h, f"{zh} {en}")
    box = (f'<rect class="bg" width="{w}" height="{h}"/>' if filled
           else f'<rect class="l" x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none"/>')
    return doc.render(box + square + doc.text(zh, "medium", 15, zh_x, 25.5, cls=fg)
                      + doc.text(en, "mono", 11, en_x, 24.5, cls=sub, tracking=.12)
                      + doc.text(arrow, "mono", 14, arrow_x, 25, cls=fg))


def link_img(href, src, alt, width=None):
    w = f' width="{width}"' if width else ""
    return f'<a href="{href}"><img src="{src}"{w} alt="{escape(alt)}"></a>'


def has_site(p):
    return not p.cta_url.startswith(p.url)


def readme():
    lines = [
        link_img(PROFILE["site"], "assets/header.svg",
                 f"{PROFILE['name']} {PROFILE['name_en']} · {PROFILE['slogan_zh']} {PROFILE['slogan_en']}", "100%"),
        "",
        f"{PROFILE['intro_zh']}<br>",
        PROFILE["intro_en"],
        "",
    ]
    for p in PROJECTS:
        buttons = [link_img(p.cta_url, f"assets/button-{p.repo}.svg", f"{p.cta_zh} {p.cta_en}")]
        if has_site(p):
            buttons.append(link_img(p.url, "assets/button-source.svg", f"{p.name} 源码 GitHub"))
        lines += [
            f"## {p.name}",
            "",
            link_img(p.url, f"assets/card-{p.repo}.svg", f"{p.name}：{p.slogan_zh} {p.slogan_en}", "100%"),
            "",
            f"<b>{p.lead_zh}</b>{p.body_zh}<br>",
            f"<b>{p.lead_en}</b> {p.body_en}",
            "",
            "\n".join(buttons),
            "",
            "<br>",
            "",
        ]
    lines += ["## 更多 · More", ""]
    lines += [f"- [{name}]({url}) {zh} · {en}" for name, url, zh, en in MORE]
    lines += [
        "",
        "<br>",
        "",
        link_img(PROFILE["x"], "assets/footer.svg", f"{PROFILE['thanks_zh']} {PROFILE['thanks_en']}", "100%"),
        "",
        '<p align="center">',
        link_img(PROFILE["x"], "assets/button-x.svg", f"在 X 上关注我 {PROFILE['x_handle']}"),
        link_img(PROFILE["site"], "assets/button-site.svg", f"网站 {PROFILE['site_label']}"),
        "</p>",
        "",
        f'<p align="center"><sub>微信 / WeChat <code>{PROFILE["wechat"]}</code></sub></p>',
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
    for p in PROJECTS:
        yield ASSETS / f"card-{p.repo}.svg", lambda p=p: card(p)
        yield ASSETS / f"button-{p.repo}.svg", lambda p=p: button(p.cta_zh, p.cta_en, accent=p.color_hex)
    yield ASSETS / "button-source.svg", lambda: button("源码", "GITHUB", arrow="↗")
    yield ASSETS / "footer.svg", footer
    yield ASSETS / "button-x.svg", lambda: button("在 X 上关注我", PROFILE["x_handle"].upper(), filled=True)
    yield ASSETS / "button-site.svg", lambda: button("网站", PROFILE["site_label"].upper(), arrow="↗")
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
