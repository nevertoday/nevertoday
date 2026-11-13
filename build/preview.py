"""Render README.md the way GitHub does and screenshot it, plus seeked frames of every animated asset.

Frames: every animation's delay is shifted by -T and paused, so Chrome evaluates the real keyframes at time T.
Motion check: frames at T=1.5, 3 and 7 must differ from T=0. Loop check: T=0 and T=L (the LCM of all durations) must match.
"""
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / ".preview"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-{}.css"
THEMES = {"light": "#ffffff", "dark": "#0d1117"}
CONTENT_WIDTH = 846
ANIM = re.compile(r"animation:(k\d+) ([\d.]+)s (\S+) (-?[\d.]+)s infinite;")


def chrome(url, png, width, height, *flags):
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, "--headless=new", f"--user-data-dir={prof}", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={width},{height}", "--virtual-time-budget=6000", f"--screenshot={png}", *flags, url],
                       check=True, capture_output=True)


def github_html():
    res = subprocess.run(["gh", "api", "markdown", "-f", "mode=markdown", "-f", "context=nevertoday/nevertoday",
                          "-F", f"text=@{ROOT / 'README.md'}"], check=True, capture_output=True, text=True)
    html = res.stdout
    return re.sub(r'(src|srcset)="[^"]*?/?(assets/[\w.-]+\.svg)"', lambda m: f'{m[1]}="{(ROOT / m[2]).as_uri()}"', html)


def page(theme, html):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{CSS.format(theme)}">'
            f'<style>body{{margin:0;background:{THEMES[theme]}}}.markdown-body{{box-sizing:content-box;width:{CONTENT_WIDTH}px;'
            f'margin:0 auto;padding:24px}}</style></head><body><article class="markdown-body">{html}</article></body></html>')


def trim_height(png, bg):
    bbox = subprocess.run(["magick", str(png), "-bordercolor", bg, "-border", "1", "-fuzz", "2%", "-trim", "-format", "%@", "info:"],
                          check=True, capture_output=True, text=True).stdout
    w, h, x, y = map(int, re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", bbox).groups())
    bottom = y + h + 24
    subprocess.run(["magick", str(png), "-crop", f"x{bottom}+0+0", "+repage", str(png)], check=True)


def seek(svg_text, t):
    return ANIM.sub(lambda m: f"animation:{m[1]} {m[2]}s {m[3]} {float(m[4]) - t:.3f}s infinite;animation-play-state:paused;", svg_text)


def loop_length(svg_text):
    centis = {round(float(d) * 100) for d in re.findall(r"animation:k\d+ ([\d.]+)s", svg_text)}
    return math.lcm(*centis) / 100 if centis else None


def diff(a, b):
    res = subprocess.run(["magick", "compare", "-metric", "AE", "-fuzz", "3%", str(a), str(b), "null:"],
                         capture_output=True, text=True)
    return int(float(res.stderr.split()[0]))


def frames(svg, times):
    text = svg.read_text(encoding="utf-8")
    w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', text).groups())
    pngs = []
    work = OUT / "frames" / svg.stem
    work.mkdir(parents=True, exist_ok=True)
    for t in times:
        frame = work / f"t{t:g}.svg"
        frame.write_text(seek(text, t), encoding="utf-8")
        holder = work / f"t{t:g}.html"
        holder.write_text(f'<html><body style="margin:0;background:#888"><img src="{frame.name}" width="{w}"></body></html>')
        png = work / f"t{t:g}.png"
        chrome(holder.as_uri(), png, w, h)
        pngs.append(png)
    holder = work / "reduced.html"
    holder.write_text(f'<html><body style="margin:0;background:#888"><img src="{svg.as_uri()}" width="{w}"></body></html>')
    reduced = work / "reduced-motion.png"
    chrome(holder.as_uri(), reduced, w, h, "--force-prefers-reduced-motion")
    return pngs, reduced


def main():
    only = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    if not only or "page" in only:
        html = github_html()
        for theme, bg in THEMES.items():
            doc = OUT / f"readme-{theme}.html"
            doc.write_text(page(theme, html), encoding="utf-8")
            png = OUT / f"readme-{theme}.png"
            chrome(doc.as_uri(), png, CONTENT_WIDTH + 48, 7000, *(["--force-dark-mode"] if theme == 'dark' else []))
            trim_height(png, bg)
            print(f"page   {png.relative_to(ROOT)}")
    for svg in sorted((ROOT / "assets").glob("*.svg")):
        if only and svg.stem not in only and "all" not in only:
            continue
        text = svg.read_text(encoding="utf-8")
        loop = loop_length(text)
        if loop is None:
            continue
        times = [0, 1.5, 3, 7, loop]
        pngs, reduced = frames(svg, times)
        moved, looped = max(diff(pngs[0], f) for f in pngs[1:-1]), diff(pngs[0], pngs[-1])
        sheet = OUT / f"frames-{svg.stem}.png"
        subprocess.run(["magick", *map(str, pngs[:-1]), str(reduced), "-background", "#888", "-splice", "0x6", "-append", str(sheet)],
                       check=True)
        report[svg.stem] = {"loop_s": loop, "max_px_changed_vs_t0": moved, "px_changed_0_to_loop": looped,
                            "sheet": str(sheet.relative_to(ROOT))}
        print(f"frames {svg.stem:40s} loop {loop:7.1f}s  moved {moved:7d}px  after-loop {looped:5d}px")
        assert moved > 0, f"{svg.stem} does not move"
        assert looped == 0, f"{svg.stem} does not return to its first frame after {loop}s"
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for f in sorted((ROOT / "assets").glob("*.svg")):
        print(f"size   {f.stat().st_size / 1024:8.1f} KB  {f.name}")


if __name__ == "__main__":
    main()
