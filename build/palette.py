import colorsys
from pathlib import Path

DATA = Path(__file__).parent / "data"

INK = "#1D1B1C"
PAPER = "#F9F4DC"
WHITE = "#FFFFFF"
GITHUB_LIGHT_BG = "#FFFFFF"
GITHUB_DARK_BG = "#0D1117"


def read_named(path):
    pairs = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        name, _, hex_ = line.strip().rpartition(" ")
        if name and hex_.startswith("#"):
            pairs.append((name, hex_.upper()))
    return pairs


TRADITIONAL = dict(read_named(DATA / "colors.txt"))


def rgb(hex_):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(r, g, b):
    return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in (r, g, b))


def luminance(hex_):
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ink_on(bg):
    return max((WHITE, INK), key=lambda fg: contrast(fg, bg))


def mix(a, b, t):
    return to_hex(*(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def lift_on(hex_, bg=INK, min_ratio=4.5):
    """Mix toward white (or ink on a light bg) until the colour reads on bg."""
    toward = WHITE if luminance(bg) < 0.5 else INK
    for step in range(41):
        out = mix(hex_, toward, step / 40)
        if contrast(out, bg) >= min_ratio:
            return out
    return toward


def both_themes_tone(hex_, min_ratio=2.0):
    """The same hue at the nearest lightness that shows on GitHub light and dark."""
    def score(c):
        return min(contrast(c, GITHUB_LIGHT_BG), contrast(c, GITHUB_DARK_BG))
    if score(hex_) >= min_ratio:
        return hex_
    h, l, s = colorsys.rgb_to_hls(*rgb(hex_))
    cands = [(i / 100, to_hex(*colorsys.hls_to_rgb(h, i / 100, s))) for i in range(101)]
    passing = [(abs(li - l), c) for li, c in cands if score(c) >= min_ratio]
    if passing:
        return min(passing)[1]
    return max((c for _, c in cands), key=score)


def hls(hex_):
    return colorsys.rgb_to_hls(*rgb(hex_))
