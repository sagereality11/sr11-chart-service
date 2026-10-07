"""Render a Your 2027 reading dict to branded HTML. render_html returns (cover_html, body_html);
render_single_html returns one printable document for browser-side PDF generation."""
import html
import json
import subprocess
import sys

PURPLE = "#4b2a7b"
DEEP = "#1d1033"
LILAC = "#efe7fb"
LILAC2 = "#dccdf3"
GOLD = "#c9a24d"
INK = "#2e2340"


def esc(s):
    return html.escape(str(s))


def paras(text, subheads=()):
    out = []
    for p in str(text).split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p in subheads:
            out.append(f'<h3>{esc(p)}</h3>')
        else:
            out.append(f"<p>{esc(p)}</p>")
    return "\n".join(out)


CSS = f"""
@page {{ margin: 0; }}
body {{ margin:0; font-family: 'Lora', 'DejaVu Serif', serif; color:{INK}; font-size:14.2pt; line-height:1.6; background:#fff; }}
.page {{ padding: 0 6px; page-break-after: always; position: relative; }}
.flow {{ page-break-after: auto; padding-bottom: 10px; }}
.flow h2 {{ page-break-after: avoid; }}
.page:last-child {{ page-break-after: auto; }}
h1,h2,h3,.sans {{ font-family:'Inter', 'DejaVu Sans', sans-serif; }}
h2 {{ color:{PURPLE}; font-size:23pt; font-weight:600; margin:0 0 14px 0; letter-spacing:.2px; }}
h2 .kicker {{ display:block; font-size:9pt; letter-spacing:3px; text-transform:uppercase; color:{GOLD}; font-weight:600; margin-bottom:4px; }}
h3 {{ color:{PURPLE}; font-size:15.5pt; font-weight:600; margin:22px 0 6px 0; }}
p {{ margin:0 0 12px 0; }}
.cover {{ margin:0; background:#fff; border-top:10px solid {PURPLE}; border-bottom:10px solid {PURPLE};
          color:{PURPLE}; height: 1300px; padding:0; text-align:center; overflow:hidden; }}
.cover .inner {{ padding-top: 400px; }}
.brand {{ font-family:'Inter'; letter-spacing:6px; font-size:11.5pt; font-weight:600; color:{PURPLE}; text-transform:uppercase; }}
.cover h1 {{ font-family:'Lora'; font-weight:400; font-size:58pt; margin:26px 0 6px 0; color:{PURPLE}; }}
.cover .sub {{ font-family:'Lora'; font-style:italic; font-size:20pt; color:#6d4fa0; }}
.cover .who {{ margin-top:70px; font-family:'Inter'; font-size:11pt; color:#5b4a75; line-height:1.8; }}
.cover .who b {{ font-size:14pt; color:{PURPLE}; font-weight:600; }}
.star {{ position:absolute; background:#fff; border-radius:50%; }}
.rule {{ width:70px; height:2px; background:{GOLD}; margin:26px auto; }}
.glance td {{ padding:9px 12px; border-bottom:1px solid {LILAC2}; vertical-align:top; font-size:13pt; }}
.glance td.k {{ font-family:'Inter'; font-size:9.5pt; text-transform:uppercase; letter-spacing:1.4px; color:{PURPLE}; width:34%; font-weight:600; }}
table {{ border-collapse:collapse; width:100%; }}
.card {{ background:{LILAC}; border-left:4px solid {PURPLE}; padding:14px 18px 6px 18px; margin:14px 0; page-break-inside: avoid; }}
.card .t {{ font-family:'Inter'; font-weight:600; color:{PURPLE}; font-size:12.5pt; }}
.card .s {{ font-family:'Inter'; font-size:10.5pt; color:#6d5a8c; margin:2px 0 8px 0; }}
.card p {{ font-size:13.2pt; }}
.bars td {{ text-align:center; vertical-align:bottom; padding:0 3px; }}
.bar {{ background:{LILAC2}; width:100%; }}
.bar.p {{ background:{PURPLE}; }}
.bars .lab {{ font-family:'Inter'; font-size:8.5pt; color:#6d5a8c; padding-top:6px; vertical-align:top; }}
.bars .lab.p {{ color:{PURPLE}; font-weight:700; }}
.month {{ margin: 0 0 18px 0; page-break-inside: avoid; border-top:1px solid {LILAC2}; padding-top:12px; }}
.month .mh {{ font-family:'Inter'; font-size:15pt; font-weight:600; color:{PURPLE}; }}
.month .hl {{ font-family:'Inter'; font-size:9.5pt; letter-spacing:1.6px; text-transform:uppercase; color:{GOLD}; font-weight:600; }}
.month .pw {{ background:{PURPLE}; color:#fff; font-family:'Inter'; font-size:8pt; letter-spacing:1.5px; padding:2px 8px; border-radius:10px; margin-left:8px; vertical-align:middle; }}
.ev td {{ padding:4px 0; vertical-align:top; font-size:12.8pt; }}
.ev td.d {{ font-family:'Inter'; font-size:9.5pt; color:{PURPLE}; font-weight:600; width:62px; padding-top:6px; }}
.power {{ background:{LILAC}; padding:16px 20px; margin:12px 0; page-break-inside: avoid; }}
.power .mh {{ font-family:'Inter'; font-size:16pt; font-weight:600; color:{PURPLE}; }}
.offer {{ border-left:3px solid {PURPLE}; padding:4px 0 2px 14px; margin:12px 0; page-break-inside:avoid; }}
.offer a {{ font-family:'Inter'; font-weight:700; color:{PURPLE}; text-decoration:none; font-size:12.5pt; }}
.offer p {{ margin:2px 0 0 0; font-size:12.4pt; }}
.signoff {{ font-style:italic; font-size:14pt; color:{PURPLE}; margin-top:24px; white-space:pre-line; }}
.disc {{ font-family:'Inter'; font-size:8.6pt; color:#7a6d8d; line-height:1.5; border-top:1px solid {LILAC2}; padding-top:12px; margin-top:34px; }}
.foot {{ font-family:'Inter'; font-size:8pt; color:#9a8db0; letter-spacing:2px; text-transform:uppercase; text-align:center; margin-top:22px; }}
"""


def stars():
    import random
    random.seed(11)
    out = []
    for _ in range(90):
        s = random.choice([1, 1, 1, 2, 2, 3])
        out.append(f'<div class="star" style="left:{random.randint(10, 780)}px;top:{random.randint(10, 890)}px;'
                   f'width:{s}px;height:{s}px;opacity:{random.uniform(.35, .95):.2f}"></div>')
    return "".join(out)


def offers_html(r):
    if not r.get("offers"):
        return ""
    items = "".join(f'<div class="offer"><a href="{esc(o["url"])}">{esc(o["title"])}</a><p>{esc(o["why"])}</p></div>'
                    for o in r["offers"])
    return f'<h3 style="margin-top:30px">Where to Go From Here</h3><p>{esc(r["next_intro"])}</p>{items}'


def render_single_html(r):
    cover, body = render_html(r)
    cbody = cover.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    return body.replace("<body>", "<body>" + cbody.replace('class="page cover"', 'class="page cover" style="page-break-after:always"'), 1)


def render_html(r):
    b = r["birth"]
    who = f"<b>{esc(r['name'])}</b><br>{esc(b['date'])}"
    if b["time"] and b["time"] != "unknown":
        who += f" · {esc(b['time'])}"
    if b["place"]:
        who += f"<br>{esc(b['place'])}"
    parts = [f"""<div class="page cover"><div class="inner">
<div class="brand">Sage Reality 11</div><div class="rule"></div>
<h1>{esc(r['title'])}</h1><div class="sub">{esc(r['subtitle'])}</div>
<div class="rule"></div><div class="who">{who}</div></div></div>"""]

    # at a glance + intensity strip
    rows = "".join(f'<tr><td class="k">{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in r["snapshot"].items())
    mx = max(m["score"] for m in r["months"]) or 1
    bars = "".join(
        f'<td><div class="bar{" p" if m.get("power") else ""}" style="height:{max(6, int(150 * m["score"] / mx))}px"></div></td>'
        for m in r["months"])
    labs = "".join(f'<td class="lab{" p" if m.get("power") else ""}">{m["month"][:3]}</td>' for m in r["months"])
    parts.append(f"""<div class="page"><h2><span class="kicker">At a Glance</span>Your 2027 in One Page</h2>
<table class="glance">{rows}</table>
<h3 style="margin-top:34px">How Much Is Moving, Month by Month</h3>
<p style="font-size:11pt;color:#6d5a8c">Taller bars mean more of your personal chart is being activated. Your power months are in deep purple.</p>
<table class="bars" style="height:170px"><tr style="height:150px">{bars}</tr><tr>{labs}</tr></table>
<div class="foot">Part One · The Story &nbsp;&nbsp;|&nbsp;&nbsp; Part Two · Your Calendar</div></div>""")

    # story
    for i, s in enumerate(r["sections"]):
        kicker = "Part One · The Story" if i == 0 else "The Story"
        cards = "".join(f'<div class="card"><div class="t">{esc(c["title"])}</div><div class="s">{esc(c["sub"])}</div>'
                        f'{paras(c["body"])}</div>' for c in s.get("cards", []))
        parts.append(f'<div class="page flow"><h2><span class="kicker">{kicker}</span>{esc(s["heading"])}</h2>'
                     f'{paras(s["body"], s.get("subheads", ()))}{cards}</div>')

    # power months
    pm = "".join(f'<div class="power"><div class="mh">{esc(p["month"])}</div><p>{esc(p["why"])}</p></div>'
                 for p in r["power_months"])
    parts.append(f'<div class="page" style="page-break-before:always"><h2><span class="kicker">Part Two · Your Calendar</span>The Months That Matter Most</h2>'
                 f'{paras(r["power_intro"])}{pm}</div>')

    # month by month
    blocks = []
    for m in r["months"]:
        evs = "".join(f'<tr><td class="d">{esc(e["date"])}</td><td>{esc(e["text"])}</td></tr>' for e in m["events"])
        badge = '<span class="pw">POWER MONTH</span>' if m.get("power") else ""
        hl = f'<div class="hl">{esc(m["headline"])}</div>' if m.get("headline") and not m.get("quiet") else ""
        quiet = f'<p style="font-size:11.2pt;margin-top:6px">{esc(m["quiet"])}</p>' if m.get("quiet") else ""
        blocks.append(f'<div class="month"><div class="mh">{esc(m["month"])} 2027{badge}</div>{hl}'
                      f'<table class="ev">{evs}</table>{quiet}</div>')
    parts.append('<div class="page"><h2><span class="kicker">Your Calendar</span>Month by Month</h2>'
                 + "".join(blocks) + "</div>")

    parts.append(f'<div class="page"><h2><span class="kicker">Closing</span>Final Thoughts</h2>{paras(r["final"])}'
                 f'<div class="signoff">{esc(r["signoff"])}</div>{offers_html(r)}<div class="disc">{esc(r["disclaimer"])}</div>'
                 f'<div class="foot">sagereality11.com</div></div>')
    wrap = lambda body: f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
    return wrap(parts[0]), wrap("".join(parts[1:]))


if __name__ == "__main__":
    r = json.load(open(sys.argv[1]))
    cover, body = render_html(r)
    open("cover.html", "w").write(cover)
    open(sys.argv[2], "w").write(body)
    common = ["wkhtmltopdf", "-q", "--page-size", "Letter", "--enable-local-file-access", "--dpi", "110"]
    subprocess.run(common + ["-T", "0", "-B", "0", "-L", "0", "-R", "0", "cover.html", "cover.pdf"], check=False)
    subprocess.run(common + ["-T", "16mm", "-B", "16mm", "-L", "18mm", "-R", "18mm",
                             "--footer-center", "Sage Reality 11  ·  Your 2027  ·  [page]", "--footer-font-name", "Inter",
                             "--footer-font-size", "7", "--footer-spacing", "6",
                             sys.argv[2], "body.pdf"], check=False)
    from pypdf import PdfWriter, PdfReader
    w = PdfWriter()
    w.add_page(PdfReader("cover.pdf").pages[0])
    for pg in PdfReader("body.pdf").pages:
        w.add_page(pg)
    w.add_metadata({"/Title": f"Your 2027 for {r['name']}", "/Author": "Sage Reality 11"})
    w.write(sys.argv[3])
