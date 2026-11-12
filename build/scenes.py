import base64
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from palette import INK, PAPER, TRADITIONAL, hls, ink_on, lift_on, read_named
from svgdoc import fmt, measure

W, H = 780, 360
DIM = "rgba(249,244,220,.55)"
FAINT = "rgba(249,244,220,.14)"
HAIR = "rgba(255,255,255,.1)"
PANE = "#141213"
CACHE = Path(__file__).parent / ".cache"
DATA = Path(__file__).parent / "data"


def check(x, y, size, color, width=2.2, cls=None):
    """A tick drawn as a stroke, its box starting at (x, y)."""
    s = size / 12
    d = f"M{fmt(x + 1 * s)} {fmt(y + 6.5 * s)}L{fmt(x + 4.6 * s)} {fmt(y + 10 * s)}L{fmt(x + 11 * s)} {fmt(y + 2 * s)}"
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="square"/>'


def vps(doc, p):
    doc.phase = 4.6
    accent = lift_on(p.color_hex)
    cycle = 14
    out = [f'<rect x="28" y="28" width="420" height="304" fill="{PANE}" stroke="{HAIR}"/>',
           f'<path d="M28 60H448" stroke="{HAIR}"/>']
    out += [f'<rect x="{42 + i * 14}" y="40" width="8" height="8" fill="{FAINT}"/>' for i in range(3)]
    out.append(doc.text("codex", "mono", 13, 434, 49, fill=DIM, anchor="end"))
    out.append(doc.text("›", "mono", 16, 44, 92, fill=accent))
    out.append(doc.text("请按「小小东 VPS」方案配置我新买的服务器。", "regular", 16, 62, 92, fill=PAPER))
    steps = ["主、备两个节点", "HTTPS 证书", "分流规则 · 国内直连", "CLIProxyAPI 自动更新", "配置每日备份"]
    for i, label in enumerate(steps):
        y = 134 + i * 32
        cls = doc.appear(cycle, 1.0 + i * 1.1, 12.8)
        out.append(f'<g class="{cls}">{check(44, y - 12, 13, accent)}'
                   f'{doc.text(label, "regular", 16, 66, y, fill=PAPER, opacity=".9")}</g>')
    done = doc.appear(cycle, 6.8, 12.8)
    out.append(f'<g class="{done}">{doc.text("完成，订阅地址已写到桌面", "medium", 16, 44, 310, fill=accent)}</g>')

    devices = [("电脑", 106), ("手机", 180), ("路由器", 254)]
    nodes = {"主": 120, "备": 240}
    dx0, nx = 566, 676
    for name, cy in devices:
        out.append(f'<rect x="474" y="{cy - 20}" width="92" height="40" fill="{PANE}" stroke="{FAINT}"/>')
        out.append(doc.text(name, "medium", 15, 520, cy + 5.5, fill=PAPER, anchor="middle"))
        for ny in nodes.values():
            out.append(f'<path d="M{dx0} {cy}L{nx} {ny}" stroke="{FAINT}" stroke-width="1.2"/>')

    failover = (7.4, 13.4)
    main_off = doc.animate(cycle, [(0, "opacity:1"), (failover[0], "opacity:1"), (failover[0] + .4, "opacity:0"),
                                   (failover[1], "opacity:0"), (failover[1] + .4, "opacity:1"), (cycle, "opacity:1")])
    backup_on = doc.animate(cycle, [(0, "opacity:0"), (failover[0] + .3, "opacity:0"), (failover[0] + .7, "opacity:1"),
                                    (failover[1], "opacity:1"), (failover[1] + .4, "opacity:0"), (cycle, "opacity:0")])
    main_dim = doc.animate(cycle, [(0, "opacity:1"), (failover[0], "opacity:1"), (failover[0] + .4, "opacity:.28"),
                                   (failover[1], "opacity:.28"), (failover[1] + .4, "opacity:1"), (cycle, "opacity:1")])

    def route(ny):
        g = []
        for k, (_, cy) in enumerate(devices):
            g.append(f'<path d="M{dx0} {cy}L{nx} {ny}" stroke="{accent}" stroke-opacity=".7" stroke-width="1.6"/>')
            dot = doc.animate(1.8, [(0, "transform:translate(0,0);opacity:0"), (.2, "opacity:1"), (1.6, "opacity:1"),
                                    (1.8, f"transform:translate({nx - dx0}px,{ny - cy}px);opacity:0")],
                              delay=-k * 0.6)
            g.append(f'<rect class="{dot}" x="{dx0 - 3}" y="{cy - 3}" width="6" height="6" fill="{accent}"/>')
        return "".join(g)

    out.append(f'<g class="{main_off}">{route(nodes["主"])}</g>')
    out.append(f'<g class="{backup_on}" opacity="0">{route(nodes["备"])}</g>')
    for name, ny in nodes.items():
        cls = f' class="{main_dim}"' if name == "主" else ""
        caption = "PRIMARY" if name == "主" else "BACKUP"
        out.append(f'<g{cls}><rect x="{nx}" y="{ny - 32}" width="64" height="64" fill="{accent if name == "主" else PANE}" '
                   f'stroke="{accent}"/>'
                   f'{doc.text(name, "bold", 26, nx + 32, ny + 9, fill=ink_on(accent) if name == "主" else PAPER, anchor="middle")}'
                   f'{doc.text(caption, "mono", 12, nx + 32, ny + 52, fill=DIM, anchor="middle", tracking=.1)}</g>')
    down = doc.appear(cycle, failover[0] + .3, failover[1] - .2)
    out.append(f'<g class="{main_off}">{doc.text("主节点在线", "medium", 14, 760, 52, fill=DIM, anchor="end")}</g>')
    out.append(f'<g class="{down}" opacity="0">{doc.text("主节点不通 → 已切到备用", "medium", 14, 760, 52, fill=accent, anchor="end")}</g>')
    return "".join(out)


def ticker_colors(count=24):
    vivid = [(n, h) for n, h in TRADITIONAL.items() if hls(h)[2] >= 0.35 and 0.3 <= hls(h)[1] <= 0.72]
    picked = []
    for b in range(count):
        lo, hi = b / count, (b + 1) / count
        in_bin = [(n, h) for n, h in vivid if lo <= hls(h)[0] < hi]
        if in_bin:
            picked.append(min(in_bin, key=lambda c: abs(hls(c[1])[1] - 0.52) - 0.3 * hls(c[1])[2]))
    return picked


def colors(doc, p):
    strips = ticker_colors()
    w, gap, top, h = 64, 8, 30, 300
    pitch = w + gap
    loop = pitch * len(strips)
    cells = []
    for i, (name, hex_) in enumerate(strips * 2):
        x = 14 + i * pitch
        ink = ink_on(hex_)
        chars = "".join(doc.text(ch, "medium", 18, x + w / 2, top + 34 + k * 22, anchor="middle") for k, ch in enumerate(name))
        cells.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{hex_}"/>'
                     f'<g fill="{ink}">{chars}{doc.text(hex_, "mono", 11, x + w / 2, top + h - 14, anchor="middle")}</g>')
    slide = doc.animate(48, [(0, "transform:translateX(0)"), (48, f"transform:translateX(-{loop}px)")])
    return f'<g class="{slide}">{"".join(cells)}</g>'


LAYOUT_THUMBS = [
    "01-composition-logic/001-三分法构图.jpg", "02-visual-principles/087-放射平衡原则.jpg",
    "03-editorial-advertising/132-单栏版式.jpg", "04-type-grid-cjk/180-强制两端对齐.jpg",
    "05-web-ui/228-子网格布局.jpg", "06-film-frame/301-单人构图.jpg",
    "07-chinese-composition/315-高远法.jpg", "08-presentation/347-流程页幻灯片版式.jpg",
    "01-composition-logic/013-负空间构图.jpg", "02-visual-principles/099-尺度对比原则.jpg",
    "03-editorial-advertising/138-满出血版式.jpg", "04-type-grid-cjk/192-垂直文字排版.jpg",
    "05-web-ui/252-横向卷轴.jpg", "06-film-frame/313-横向调度.jpg",
    "07-chinese-composition/327-计白当黑构图.jpg", "01-composition-logic/037-S 形构图.jpg",
    "02-visual-principles/123-裁切构图.jpg", "03-editorial-advertising/162-栏目开启页.jpg",
    "04-type-grid-cjk/204-极坐标网格.jpg", "05-web-ui/264-底部导航布局.jpg",
]
LAYOUT_RAW = "https://raw.githubusercontent.com/nevertoday/350-layout-compositions/main/v2/thumbnails/"


def layout_thumb(rel, width=220, quality=62):
    src = CACHE / "layouts" / rel
    small = CACHE / "layouts-small" / f"{width}q{quality}" / rel
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        tmp = src.with_suffix(".part")
        urllib.request.urlretrieve(LAYOUT_RAW + urllib.parse.quote(rel), tmp)
        tmp.rename(src)
    if not small.exists():
        small.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["magick", str(src), "-resize", f"{width}x", "-strip", "-sampling-factor", "4:2:0",
                        "-interlace", "none", "-quality", str(quality), str(small)], check=True)
    return "data:image/jpeg;base64," + base64.b64encode(small.read_bytes()).decode()


def layouts(doc, p):
    cols, cw, gap = 5, 140, 14
    ch = cw * 1448 / 1086
    pitch = ch + gap
    per_col = len(LAYOUT_THUMBS) // cols
    loop = pitch * per_col
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2
    for i, rel in enumerate(LAYOUT_THUMBS):
        doc.defs.append(f'<image id="L{i}" width="{cw}" height="{fmt(ch)}" preserveAspectRatio="xMidYMid slice" '
                        f'href="{layout_thumb(rel)}"/>')
    out = []
    for c in range(cols):
        items = [i for i in range(len(LAYOUT_THUMBS)) if i % cols == c]
        x = x0 + c * (cw + gap)
        tiles = []
        for k, i in enumerate(items * 2):
            y = k * pitch
            tiles.append(f'<use href="#L{i}" x="{fmt(x)}" y="{fmt(y)}"/>'
                         f'<rect x="{fmt(x + .5)}" y="{fmt(y + .5)}" width="{cw - 1}" height="{fmt(ch - 1)}" fill="none" stroke="{HAIR}"/>')
        up = c % 2 == 0
        start, end = (0, -loop) if up else (-loop, 0)
        slide = doc.animate(40, [(0, f"transform:translateY({fmt(start)}px)"), (40, f"transform:translateY({fmt(end)}px)")],
                            delay=-c * 6.5)
        out.append(f'<g class="{slide}" transform="translate(0 {fmt(-loop / 2 + c * 37)})"><g>{"".join(tiles)}</g></g>')
    fade = doc.uid("fade")
    doc.defs.append(f'<linearGradient id="{fade}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}"/>'
                    f'<stop offset=".09" stop-color="{INK}" stop-opacity="0"/><stop offset=".91" stop-color="{INK}" stop-opacity="0"/>'
                    f'<stop offset="1" stop-color="{INK}"/></linearGradient>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#{fade})"/>')
    return "".join(out)


def pstack(doc, p):
    doc.phase = 5.2
    accent = lift_on(p.color_hex)
    cycle = 13
    out = [f'<path d="M376 40V320" stroke="{HAIR}"/>',
           doc.text("以前 · BEFORE", "mono", 13, 32, 52, fill=DIM, tracking=.06),
           doc.text("用 pstack · WITH PSTACK", "mono", 13, 408, 52, fill=accent, tracking=.06)]
    bubbles = [("AI", "修好了。", 0.6, False), ("你", "……还是坏的。", 2.0, True), ("AI", "抱歉，我再改一处。", 3.4, False)]
    for k, (who, text, t, mine) in enumerate(bubbles):
        y = 78 + k * 66
        size = 18
        tw = measure(text, "medium", size)
        bw = tw + 36
        x = 344 - bw if mine else 32
        fill, ink = (PAPER, INK) if mine else ("rgba(255,255,255,.08)", PAPER)
        cls = doc.appear(cycle, t, 12.2)
        out.append(f'<g class="{cls}">{doc.text(who, "mono", 12, x if not mine else x + bw, y - 6, fill=DIM, anchor="end" if mine else "start")}'
                   f'<rect x="{fmt(x)}" y="{y}" width="{fmt(bw)}" height="44" fill="{fill}"/>'
                   f'{doc.text(text, "medium", size, x + 18, y + 28.5, fill=ink)}</g>')
    tail = doc.appear(cycle, 4.8, 12.2)
    out.append(f'<g class="{tail}">{doc.text("来回五轮，一个下午没了。", "regular", 14, 32, 300, fill=DIM)}</g>')

    items = ["复现问题", "找到根因", "改代码", "自己再试一遍", "给出修前修后证据"]
    for i, label in enumerate(items):
        y = 76 + i * 40
        t = 1.2 + i * 1.2
        tick = doc.appear(cycle, t, 12.2, fade=.25)
        lit = doc.animate(cycle, [(0, "opacity:.5"), (t, "opacity:.5"), (t + .25, "opacity:1"), (12.2, "opacity:1"),
                                  (12.45, "opacity:.5"), (cycle, "opacity:.5")])
        out.append(f'<rect x="408.5" y="{y + .5}" width="21" height="21" fill="none" stroke="{FAINT}"/>'
                   f'<g class="{tick}">{check(411, y + 3, 15, accent, 2.4)}</g>'
                   f'<g class="{lit}">{doc.text(label, "regular", 17, 446, y + 17, fill=PAPER)}</g>')
    final = doc.appear(cycle, 7.6, 12.2)
    out.append(f'<g class="{final}"><rect x="408" y="282" width="6" height="30" fill="{accent}"/>'
               f'{doc.text("真的修好了。", "bold", 24, 426, 306, fill=accent)}</g>')
    return "".join(out)


def strip(doc, p):
    doc.phase = 4.0
    accent = lift_on(p.color_hex)
    cycle = 10
    pic = [f'<rect x="36" y="40" width="252" height="252" fill="{PANE}" stroke="{FAINT}"/>',
           f'<rect x="52" y="56" width="220" height="220" fill="{TRADITIONAL["乳白"]}"/>',
           f'<rect x="52" y="176" width="220" height="100" fill="{TRADITIONAL["靛青"]}"/>',
           f'<rect x="196" y="84" width="48" height="48" fill="{TRADITIONAL["胭脂红"]}"/>',
           f'<rect x="76" y="132" width="88" height="44" fill="{TRADITIONAL["藤黄"]}"/>',
           f'<rect x="52" y="226" width="220" height="10" fill="{TRADITIONAL["铜绿"]}"/>',
           doc.text("image.png", "mono", 12, 36, 316, fill=DIM)]
    gone = ["C2PA Content Credentials", "OpenAI gpt-image", "EXIF", "XMP", "IPTC DigitalSourceType", "Comment"]
    kept = ["保留 ICC 色彩配置", "保留修改时间", "像素不解码不重编码"]
    rows = []
    top, pitch = 58, 30
    scan_from, scan_to, t0, t1 = 40, top + 6 * pitch, 0.8, 5.6

    def passes(y):
        return t0 + (y - scan_from) / (scan_to - scan_from) * (t1 - t0)

    for i, label in enumerate(gone):
        y = top + i * pitch
        t = passes(y - 5)
        tw = measure(label, "mono", 14)
        fade = doc.animate(cycle, [(0, "opacity:1"), (t, "opacity:1"), (t + .4, "opacity:.34"), (9.2, "opacity:.34"),
                                   (9.6, "opacity:1"), (cycle, "opacity:1")])
        strike = doc.animate(cycle, [(0, "transform:scaleX(0)"), (t, "transform:scaleX(0)"), (t + .3, "transform:scaleX(1)"),
                                     (9.2, "transform:scaleX(1)"), (9.6, "transform:scaleX(0)"), (cycle, "transform:scaleX(0)")],
                             extra="transform-box:fill-box;transform-origin:left center")
        tag = doc.appear(cycle, t + .2, 9.2)
        rows.append(f'<g class="{fade}" opacity=".34"><rect x="332" y="{y - 9}" width="8" height="8" fill="{PAPER}"/>'
                    f'{doc.text(label, "mono", 14, 352, y, fill=PAPER)}'
                    f'<rect class="{strike}" x="350" y="{y - 5.5}" width="{fmt(tw + 4)}" height="1.6" fill="{PAPER}"/></g>'
                    f'<g class="{tag}">{doc.text("REMOVED", "mono", 11, 752, y, fill=DIM, anchor="end", tracking=.08)}</g>')
    rows.append(f'<path d="M332 {top + 6 * pitch - 14}H752" stroke="{HAIR}"/>')
    for i, label in enumerate(kept):
        y = top + 6 * pitch + 14 + i * pitch
        rows.append(f'{check(330, y - 12, 13, accent, 2.2)}{doc.text(label, "medium", 15, 352, y, fill=accent)}'
                    f'{doc.text("KEPT", "mono", 11, 752, y, fill=accent, anchor="end", tracking=.08)}')
    grad = doc.uid("scan")
    doc.defs.append(f'<linearGradient id="{grad}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}" stop-opacity="0"/>'
                    f'<stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>')
    scan = doc.animate(cycle, [(0, f"transform:translateY({scan_from}px);opacity:0"), (t0, f"transform:translateY({scan_from}px);opacity:0"),
                               (t0 + .2, "opacity:1"), (t1, f"transform:translateY({scan_to}px);opacity:1"),
                               (t1 + .3, f"transform:translateY({scan_to}px);opacity:0"), (cycle, f"transform:translateY({scan_to}px);opacity:0")])
    beam = f'<g class="{scan}" opacity="0"><rect x="20" y="-1" width="740" height="2" fill="url(#{grad})"/></g>'
    return "".join(pic) + "".join(rows) + beam


def rime(doc, p):
    doc.phase = 0.8
    brands = read_named(DATA / "rime-brand-colors.txt")
    slot = 1.6
    cycle = slot * len(brands)
    cands = [("1", "小小东"), ("2", "笑笑"), ("3", "小小"), ("4", "晓东"), ("5", "小东")]
    bars = [("浅色", 46, PAPER, INK, "rgba(29,27,28,.12)"), ("夜色", 176, "#121011", PAPER, HAIR)]
    out = []

    slots = [doc.slot(cycle, i * slot, (i + 1) * slot, fade=.05) for i in range(len(brands))]
    for label, y, bg, fg, stroke in bars:
        out.append(f'<rect x="40.5" y="{y + .5}" width="699" height="110" fill="{bg}" stroke="{stroke}"/>')
        out.append(doc.text("xiaoxiaodong", "regular", 16, 64, y + 34, fill=fg, opacity=".6"))
        out.append(doc.text(label, "medium", 13, 716, y + 30, fill=fg, opacity=".45", anchor="end"))
        x = 64
        first = None
        for n, word in cands:
            nw = measure(n, "regular", 15)
            ww = measure(word, "medium", 26)
            if first is None:
                first = (x, nw, ww)
            out.append(doc.text(n, "regular", 15, x, y + 82, fill=fg, opacity=".5"))
            out.append(doc.text(word, "medium", 26, x + nw + 8, y + 84, fill=fg))
            x += nw + 8 + ww + 34
        fx, nw, ww = first
        for i, (name, hex_) in enumerate(brands):
            ink = ink_on(hex_)
            out.append(f'<g class="{slots[i]}"{"" if i == 0 else " opacity=\"0\""}>'
                       f'<rect x="{fmt(fx - 12)}" y="{y + 52}" width="{fmt(nw + 8 + ww + 24)}" height="44" fill="{hex_}"/>'
                       f'{doc.text("1", "regular", 15, fx, y + 82, fill=ink, opacity=".7")}'
                       f'{doc.text("小小东", "medium", 26, fx + nw + 8, y + 84, fill=ink)}</g>')
    for i, (name, hex_) in enumerate(brands):
        out.append(f'<g class="{slots[i]}"{"" if i == 0 else " opacity=\"0\""}>'
                   f'<rect x="40" y="314" width="14" height="14" fill="{hex_}" stroke="{FAINT}"/>'
                   f'{doc.text(name, "medium", 15, 64, 327, fill=PAPER)}'
                   f'{doc.text(hex_, "mono", 13, 64 + measure(name, "medium", 15) + 12, 326.5, fill=DIM)}'
                   f'{doc.text(f"{i + 1:02d} / {len(brands)}", "mono", 12, 740, 326, fill=DIM, anchor="end")}</g>')
    return "".join(out)


SCENES = {
    "vps": vps,
    "colors": colors,
    "layouts": layouts,
    "pstack": pstack,
    "strip": strip,
    "rime": rime,
}
