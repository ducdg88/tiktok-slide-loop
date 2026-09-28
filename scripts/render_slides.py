"""Dựng bộ ảnh slide TikTok 9:16 (1080x1920) từ file kịch bản JSON.

Cách dùng:
    python render_slides.py <kich_ban.json> [--out <thu_muc>]

Kiểu slide hỗ trợ: hook, text, versus, fix, list, cta.
Trong chữ, bọc **đoạn** để tô màu nhấn.
"""
import argparse
import html
import json
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

W, H = 1080, 1920

THEMES = {
    "terminal": {
        "bg": "#0b0f14", "panel": "#131a22", "text": "#f2f5f7", "muted": "#8a97a6",
        "ai": "#3ddc84", "truth": "#ff5c5c", "fix": "#ffd23f", "accent": "#3ddc84",
    },
    "light": {
        "bg": "#f7f4ee", "panel": "#ffffff", "text": "#15191e", "muted": "#6b7280",
        "ai": "#0f9d58", "truth": "#d93025", "fix": "#b8860b", "accent": "#1a73e8",
    },
}

ROBOT_SVG = """<svg viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg">
<rect x="92" y="4" width="16" height="26" rx="6" fill="{c}"/><circle cx="100" cy="6" r="10" fill="{t}"/>
<rect x="30" y="30" width="140" height="110" rx="28" fill="#dfe6ee" stroke="#1d2530" stroke-width="6"/>
<rect x="50" y="55" width="100" height="55" rx="16" fill="#1d2530"/>
<rect x="66" y="74" width="24" height="8" rx="4" fill="{c}"/><rect x="110" y="74" width="24" height="8" rx="4" fill="{c}"/>
<path d="M78 98 Q100 92 122 98" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M160 50 q10 14 0 22 q-10 -8 0 -22z" fill="#6fc3ff"/>
<rect x="45" y="146" width="110" height="68" rx="20" fill="#dfe6ee" stroke="#1d2530" stroke-width="6"/>
<rect x="118" y="120" width="70" height="86" rx="6" fill="#fff" stroke="#1d2530" stroke-width="5" transform="rotate(8 150 160)"/>
<text x="152" y="172" font-size="20" font-weight="900" fill="{c}" text-anchor="middle" transform="rotate(8 150 160)" font-family="Arial">DONE</text>
</svg>"""


def rich(s):
    s = html.escape(s or "")
    s = re.sub(r"\*\*(.+?)\*\*", r'<span class="hl">\1</span>', s)
    return s.replace("\n", "<br>")


def logo_html(brand):
    """ducpt.com: phần tên đậm, phần đuôi tên miền tô màu nhấn."""
    name, dot, tld = brand.partition(".")
    return f"{html.escape(name)}<em>{html.escape(dot + tld)}</em>" if dot else html.escape(brand)


def slide_body(sl, th):
    t = sl.get("type", "text")
    if t == "hook":
        robot = ROBOT_SVG.format(c=th["accent"], t=th["truth"]) if sl.get("robot", True) else ""
        return f"""<div class="hook"><h1>{rich(sl.get('headline'))}</h1>
<p class="sub">{rich(sl.get('sub'))}</p><div class="robot">{robot}</div></div>"""
    if t == "versus":
        label = rich(sl.get("label", ""))
        return f"""<div class="vs">{f'<div class="tag">{label}</div>' if label else ''}
<div class="bubble ai"><b>AI nói</b><p>{rich(sl.get('ai'))}</p></div>
<div class="bubble truth"><b>Sự thật</b><p>{rich(sl.get('truth'))}</p></div></div>"""
    if t == "fix":
        return f"""<div class="fixbox"><div class="tag fixtag">{rich(sl.get('label', 'CÁCH TRỊ'))}</div>
<h2>{rich(sl.get('headline'))}</h2><p>{rich(sl.get('body'))}</p></div>"""
    if t == "list":
        items = "".join(f"<li><span>{i+1}</span>{rich(x)}</li>" for i, x in enumerate(sl.get("items", [])))
        return f"""<div class="listbox"><h2>{rich(sl.get('headline'))}</h2><ol>{items}</ol></div>"""
    if t == "cta":
        kw = sl.get("keyword")
        return f"""<div class="cta"><h2>{rich(sl.get('headline'))}</h2>
{f'<div class="kw">Bình luận <b>{html.escape(kw)}</b></div>' if kw else ''}
<p>{rich(sl.get('body'))}</p><div class="site logo" style="font-size:72px">{logo_html(sl.get('link', ''))}</div></div>"""
    return f"""<div class="textbox"><h2>{rich(sl.get('headline'))}</h2><p>{rich(sl.get('body'))}</p></div>"""


def build_html(spec, idx, th):
    sl = spec["slides"][idx]
    total = len(spec["slides"])
    bg_img = sl.get("image")
    if bg_img:
        uri = pathlib.Path(bg_img).resolve().as_uri()
        bg_css = f"background-image:linear-gradient(rgba(0,0,0,.55),rgba(0,0,0,.8)),url('{uri}');background-size:cover;background-position:center;"
    else:
        bg_css = f"background-image:radial-gradient(circle at 85% 10%, {th['accent']}22, transparent 45%);"
    brand = spec.get("brand", "")
    wm_op = spec.get("watermark_opacity", 0.03)
    wm_rows = "".join(f'<div style="top:{y}px">{html.escape(brand)} &nbsp; {html.escape(brand)}</div>' for y in range(120, H, 420)) if brand and wm_op else ""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;700;800;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;background:{th['bg']};color:{th['text']};font-family:'Be Vietnam Pro','Segoe UI',Arial,sans-serif;overflow:hidden}}
.frame{{position:relative;width:{W}px;height:{H}px;padding:150px 80px 220px;display:flex;flex-direction:column;justify-content:center;{bg_css}}}
.top{{position:absolute;top:70px;left:80px;right:80px;display:flex;justify-content:space-between;font-weight:800;font-size:34px;letter-spacing:2px}}
.top .series{{color:{th['accent']}}} .top .ep{{color:{th['muted']}}}
.bottom{{position:absolute;bottom:90px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center;font-size:32px;color:{th['muted']};font-weight:700}}
.dots{{display:flex;gap:10px}} .dots i{{width:16px;height:16px;border-radius:50%;background:{th['muted']}55}} .dots i.on{{background:{th['accent']};width:44px;border-radius:8px}}
.hl{{color:{th['accent']}}}
.src{{position:absolute!important;bottom:170px;left:80px;right:80px;font-size:26px;color:{th['muted']};font-weight:500}}
.logo{{font-weight:900;font-size:40px;letter-spacing:-1px;color:{th['text']}}} .logo em{{font-style:normal;color:{th['accent']}}}
.wm{{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:0}}
.wm div{{position:absolute;left:-300px;right:-300px;text-align:center;font-weight:900;font-size:120px;letter-spacing:8px;color:{th['text']};opacity:{wm_op};transform:rotate(-24deg);white-space:nowrap}}
.frame>*:not(.wm){{position:relative;z-index:1}} .top,.bottom{{position:absolute!important}}
h1{{font-size:104px;line-height:1.12;font-weight:900}}
h2{{font-size:78px;line-height:1.15;font-weight:900;margin-bottom:40px}}
p{{font-size:50px;line-height:1.4;font-weight:500}}
.sub{{margin-top:40px;color:{th['muted']}}}
.robot{{width:420px;margin:70px auto 0}}
.tag{{display:inline-block;font-size:36px;font-weight:800;padding:12px 28px;border-radius:40px;background:{th['panel']};margin-bottom:40px;color:{th['muted']}}}
.bubble{{background:{th['panel']};border-radius:36px;padding:44px 50px;margin-bottom:44px;border-left:14px solid}}
.bubble b{{display:block;font-size:38px;letter-spacing:3px;text-transform:uppercase;margin-bottom:16px}}
.bubble p{{font-size:58px;font-weight:800;line-height:1.3}}
.ai{{border-color:{th['ai']}}} .ai b{{color:{th['ai']}}} .ai .hl{{color:{th['ai']}}}
.truth{{border-color:{th['truth']}}} .truth b{{color:{th['truth']}}} .truth .hl{{color:{th['truth']}}}
.fixbox h2{{color:{th['fix']}}} .fixtag{{color:{th['fix']};border:3px solid {th['fix']};background:transparent}}
.fixbox .hl{{color:{th['fix']}}}
ol{{list-style:none}} li{{font-size:52px;font-weight:700;line-height:1.3;margin-bottom:34px;display:flex;gap:28px}}
li span{{flex:none;width:74px;height:74px;border-radius:50%;background:{th['accent']};color:{th['bg']};display:flex;align-items:center;justify-content:center;font-weight:900;font-size:42px}}
.cta{{text-align:center}} .cta h2{{font-size:86px}}
.kw{{display:inline-block;margin:10px 0 50px;font-size:60px;font-weight:800;padding:30px 54px;border-radius:28px;background:{th['accent']};color:{th['bg']}}}
.site{{margin-top:50px;font-size:64px;font-weight:900;color:{th['accent']}}}
</style></head><body><div class="frame">
<div class="wm">{wm_rows}</div>
<div class="top"><span class="series">{html.escape(spec.get('series', ''))}</span><span class="ep">#{int(spec.get('episode', 0)):02d}</span></div>
{slide_body(sl, th)}
{f'<div class="src">Nguồn: {html.escape(sl["source"])}</div>' if sl.get("source") else ''}
<div class="bottom"><span class="logo">{logo_html(spec.get('brand', ''))}</span>
<div class="dots">{''.join('<i class="on"></i>' if i == idx else '<i></i>' for i in range(total))}</div>
<span>{idx+1}/{total}</span></div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    a = ap.parse_args()
    spec_path = pathlib.Path(a.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    th = THEMES.get(spec.get("theme", "terminal"), THEMES["terminal"])
    out = pathlib.Path(a.out) if a.out else spec_path.parent / spec_path.stem
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": W, "height": H})
        files = []
        for i in range(len(spec["slides"])):
            page.set_content(build_html(spec, i, th), wait_until="networkidle")
            f = out / f"slide_{i+1:02d}.png"
            page.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": W, "height": H})
            files.append(str(f))
        browser.close()
    print(json.dumps({"ok": True, "out": str(out), "files": files}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
