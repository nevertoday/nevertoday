from html import escape
from itertools import groupby

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT_FILES = {
    "b": ("/Users/admin/Library/Fonts/Alibaba-PuHuiTi-Bold.ttf", None),
    "m": ("/Users/admin/Library/Fonts/Alibaba-PuHuiTi-Medium.ttf", None),
    "r": ("/Users/admin/Library/Fonts/Alibaba-PuHuiTi-Regular.ttf", None),
    "s": ("/System/Library/Fonts/NewYorkItalic.ttf", {"opsz": 20}),
    "j": ("/Users/admin/Library/Fonts/JetBrainsMono-Medium.ttf", None),
}

FACES = {
    "bold": ["b"],
    "medium": ["m"],
    "regular": ["r"],
    "serif": ["s", "r"],
    "mono": ["j", "r"],
}

FALLBACKS = {}


def fmt(v, nd=1):
    s = f"{v:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


class Font:
    def __init__(self, tag):
        path, location = FONT_FILES[tag]
        self.tag = tag
        self.name = path.rsplit("/", 1)[-1]
        self.tt = TTFont(path)
        self.cmap = self.tt.getBestCmap()
        self.upem = self.tt["head"].unitsPerEm
        self.glyphs = self.tt.getGlyphSet(location=location) if location else self.tt.getGlyphSet()
        self._paths = {}

    def has(self, ch):
        return ord(ch) in self.cmap

    def advance(self, gname):
        return self.glyphs[gname].width

    def path(self, gname):
        if gname not in self._paths:
            pen = SVGPathPen(self.glyphs, ntos=lambda v: fmt(v, 0))
            self.glyphs[gname].draw(pen)
            self._paths[gname] = pen.getCommands()
        return self._paths[gname]


_FONTS = {}


def font(tag):
    if tag not in _FONTS:
        _FONTS[tag] = Font(tag)
    return _FONTS[tag]


def pick(face, ch):
    chain = FACES[face]
    for i, tag in enumerate(chain):
        f = font(tag)
        if f.has(ch):
            if i:
                FALLBACKS.setdefault((face, font(chain[0]).name, f.name), set()).add(ch)
            return f
    raise ValueError(f"no font in face {face!r} has {ch!r} (U+{ord(ch):04X})")


def shape(text, face, size, tracking=0):
    """Glyph placements [(font, glyph, x_px)] and the run width in px."""
    out, x = [], 0.0
    for ch in text:
        f = pick(face, ch)
        g = f.cmap[ord(ch)]
        out.append((f, g, x))
        x += f.advance(g) * size / f.upem + tracking * size
    if text:
        x -= tracking * size
    return out, x


def measure(text, face, size, tracking=0):
    return shape(text, face, size, tracking)[1]


def fit(text, face, size, max_width, tracking=0):
    w = measure(text, face, size, tracking)
    return size if w <= max_width else size * max_width / w


class Doc:
    """One SVG file: glyph defs written once, CSS animations, extra defs."""

    def __init__(self, width, height, title):
        self.width, self.height, self.title = width, height, title
        self.css = []
        self.defs = []
        self._glyphs = {}
        self._keyframes = {}
        self._classes = {}
        self._n = 0

    def uid(self, prefix):
        self._n += 1
        return f"{prefix}{self._n}"

    def glyph_id(self, f, gname):
        key = (f.tag, gname)
        if key not in self._glyphs:
            self._glyphs[key] = f"{f.tag}{f.tt.getGlyphID(gname):x}"
        return self._glyphs[key]

    def text(self, s, face, size, x, y, fill=None, anchor="start", tracking=0, cls=None, opacity=None):
        placed, width = shape(s, face, size, tracking)
        x0 = x - {"start": 0, "middle": width / 2, "end": width}[anchor]
        runs = []
        for f, items in groupby(placed, key=lambda p: p[0]):
            items = [p for p in items if f.path(p[1])]
            if not items:
                continue
            k = size / f.upem
            ox = items[0][2]
            uses = "".join(
                f'<use href="#{self.glyph_id(f, g)}"' + (f' x="{fmt((gx - ox) / k, 0)}"' if gx != ox else "") + "/>"
                for _, g, gx in items
            )
            runs.append(f'<g transform="translate({fmt(x0 + ox)} {fmt(y)}) scale({fmt(k, 5)} {fmt(-k, 5)})">{uses}</g>')
        attrs = "".join(
            f' {a}="{v}"' for a, v in (("fill", fill), ("class", cls), ("opacity", opacity)) if v is not None
        )
        return f"<g{attrs}>{''.join(runs)}</g>"

    def animate(self, dur, stops, ease="linear", delay=0, extra=""):
        """stops are (seconds, css declarations) across 0..dur. Returns a class name."""
        body = "".join(f"{fmt(100 * t / dur, 2)}%{{{decl}}}" for t, decl in stops)
        if body not in self._keyframes:
            self._keyframes[body] = f"k{len(self._keyframes)}"
            self.css.append(f"@keyframes {self._keyframes[body]}{{{body}}}")
        key = (self._keyframes[body], dur, ease, delay, extra)
        if key not in self._classes:
            cls = self._classes[key] = f"a{len(self._classes)}"
            self.css.append(f".{cls}{{animation:{key[0]} {fmt(dur, 2)}s {ease} {fmt(delay, 2)}s infinite;{extra}}}")
        return self._classes[key]

    def appear(self, cycle, t_in, t_out=None, fade=0.35, hidden="opacity:0", shown="opacity:1", extra=""):
        """Hidden, fades in at t_in, holds, fades out at t_out. The static state is `shown`."""
        t_out = cycle - fade if t_out is None else t_out
        stops = [(0, hidden), (t_in, hidden), (min(t_in + fade, cycle), shown), (t_out, shown),
                 (min(t_out + fade, cycle), hidden), (cycle, hidden)]
        return self.animate(cycle, stops, extra=extra)

    def render(self, body):
        glyph_defs = "".join(
            f'<path id="{gid}" d="{font(tag).path(g)}"/>' for (tag, g), gid in self._glyphs.items()
        )
        css = "".join(self.css) + "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img" aria-labelledby="t">'
            f'<title id="t">{escape(self.title)}</title><style>{css}</style>'
            f"<defs>{glyph_defs}{''.join(self.defs)}</defs>{body}</svg>\n"
        )
