"""Render Your Birth Chart's Wealth Story.

render_pdf(reading)  -> bytes: white cover with purple edges, a clickable contents page, the reading,
                        and PDF bookmarks (the navigation pane in any PDF viewer).
render_web(reading)  -> str: an HTML fragment for the reading page, with a section menu that stays
                        beside the text on desktop and folds into a "Jump to a section" menu on phones.
Colors match the site: purple #4b2a7b, lilac #efe7fb / #dccdf3, gold #c9a24d, ink #2e2340.
"""
from __future__ import annotations

import html
import io
import os
import subprocess
import tempfile

PURPLE = "#4b2a7b"
LILAC = "#efe7fb"
LILAC2 = "#dccdf3"
GOLD = "#c9a24d"
INK = "#2e2340"
SOFT = "#6d5a8c"


def esc(s):
    return html.escape(str(s))


def _offers_html(s):
    items = "".join(f'<div class="offer"><a href="{esc(o["url"])}">{esc(o["title"])}</a><p>{esc(o["why"])}</p></div>'
                    for o in s.get("offers", []))
    return f'<div class="offers">{items}</div>' if items else ""


def _practice_html(s, for_pdf=True):
    pr = s.get("practice")
    if not pr:
        return ""
    lines = '<div class="wl"></div>' * (3 if for_pdf else 0)
    box = f'<div class="practice"><p class="plabel">{esc(pr["label"])}</p><p>{esc(pr["try"])}</p></div>'
    if not pr["prompts"]:
        return f'<div class="pblock">{box}</div>'
    lab = "Journal Prompt" if len(pr["prompts"]) == 1 else "Journal Prompts"
    first, rest = pr["prompts"][0], pr["prompts"][1:]
    # the box always travels with the first prompt; later prompts can start a new page on their own
    out = [f'<div class="pblock">{box}<div class="journal"><div class="jp"><p class="plabel">{lab}</p><p>{esc(first)}</p>{lines}</div></div></div>']
    for q in rest:
        out.append(f'<div class="journal"><div class="jp"><p>{esc(q)}</p>{lines}</div></div>')
    return "".join(out)


def _body_html(r, for_pdf=True, breaks=(), lines=True):
    out = []
    for s in r["sections"]:
        tag = "h1" if s["level"] == 1 else "h2"
        cls = ' class="newpage"' if s["id"] in breaks else ""
        out.append(f'<section id="{esc(s["id"])}"{cls}>')
        paras = list(s["paragraphs"])
        lead = f"<{tag}>{esc(s['heading'])}</{tag}>"
        if s.get("greeting"):
            lead += f'<p class="greet">{esc(s["greeting"])}</p>'
        # keep each heading with its opening paragraph so a heading never sits alone at the foot of a page
        if paras:
            lead += f"<p>{esc(paras.pop(0))}</p>"
        out.append(f'<div class="keep">{lead}</div>')
        for p in paras:
            out.append(f"<p>{esc(p)}</p>")
        out.append(_practice_html(s, lines))
        out.append(_offers_html(s))
        if s["id"] == "final":
            sign = esc(r["signoff"]).replace("\n", "<br>")
            out.append(f'<p class="signoff">{sign}</p>')
        out.append("</section>")
    out.append(f'<p class="site">sagereality11.com</p><div class="disc">{esc(r["disclaimer"])}</div>')
    return "".join(out)


PDF_CSS = f"""
body {{ margin:0; font-family:'Lora','DejaVu Serif',serif; color:{INK}; font-size:13.6pt; line-height:1.62; background:#fff; }}
h1,h2,.kicker,.hint,.toc1,.toc2,.site,.disc {{ font-family:'Inter','DejaVu Sans',sans-serif; }}
h1 {{ color:{PURPLE}; font-size:21pt; font-weight:600; margin:30px 0 12px 0; padding-bottom:8px; border-bottom:1.5px solid {LILAC2}; page-break-after:avoid; }}
h2 {{ color:{PURPLE}; font-size:15pt; font-weight:600; margin:24px 0 8px 0; padding-left:12px; border-left:4px solid {GOLD}; page-break-after:avoid; }}
p {{ margin:0 0 11px 0; }}
.greet {{ font-style:italic; color:{PURPLE}; font-size:14.5pt; }}
.newpage {{ page-break-before:always; }}
.contents {{ page-break-after:always; padding-top:20px; }}
.contents .kicker {{ letter-spacing:3px; text-transform:uppercase; color:{GOLD}; font-size:9pt; font-weight:600; }}
.contents .ct {{ border:0; margin-top:4px; }}
.contents .hint {{ font-size:10.5pt; color:{SOFT}; margin-bottom:18px; }}
.contents ul {{ list-style:none; margin:0; padding:0; }}
.contents li a {{ color:{INK}; text-decoration:none; }}
.toc1 {{ font-size:12.5pt; font-weight:600; padding:9px 0; border-bottom:1px solid {LILAC2}; }}
.toc1 a {{ color:{PURPLE} !important; }}
.toc2 {{ font-size:11pt; padding:5px 0 5px 20px; color:{SOFT}; }}
.keep {{ page-break-inside:avoid; }}
.practice {{ background:{LILAC}; border-left:4px solid {PURPLE}; padding:12px 18px 4px 18px; margin:16px 0 14px 0; page-break-inside:avoid; }}
.plabel {{ font-family:'Inter','DejaVu Sans',sans-serif; font-size:9.5pt; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:{PURPLE}; margin:0 0 6px 0; }}
.pblock {{ page-break-inside:avoid; }}
.journal {{ margin:6px 0 4px 0; }}
.journal .plabel {{ color:{GOLD}; }}
.jp {{ page-break-inside:avoid; margin:0 0 14px 0; }}
.jp p:not(.plabel) {{ font-style:italic; margin:0 0 4px 0; }}
.wl {{ height:30px; border-bottom:1px solid {LILAC2}; }}
p {{ orphans:3; widows:3; }}
.offer {{ border-left:3px solid {PURPLE}; padding:2px 0 2px 14px; margin:12px 0; page-break-inside:avoid; }}
.offer a {{ font-family:'Inter','DejaVu Sans',sans-serif; font-weight:600; color:{PURPLE}; text-decoration:none; font-size:12pt; }}
.offer p {{ margin:3px 0 0 0; font-size:12.2pt; }}
.signoff {{ font-style:italic; color:{PURPLE}; font-size:14pt; margin-top:24px; }}
.site {{ font-size:9pt; letter-spacing:2px; text-transform:uppercase; color:{GOLD}; }}
.disc {{ font-size:8.6pt; color:#7a6d8d; line-height:1.5; border-top:1px solid {LILAC2}; padding-top:10px; margin-top:28px; }}
"""


def render_cover_pdf(r) -> bytes:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    fdir = os.environ.get("SR11_FONT_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts"))
    if "SR11Lora" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SR11Lora", os.path.join(fdir, "Lora-Variable.ttf")))
        pdfmetrics.registerFont(TTFont("SR11LoraI", os.path.join(fdir, "Lora-Italic-Variable.ttf")))
    W, H = letter
    purple, soft, gold, ink, lilac = HexColor(PURPLE), HexColor(SOFT), HexColor(GOLD), HexColor("#5b4a75"), HexColor(LILAC)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(f"{r['title']} for {r['name']}")
    c.setAuthor("Sage Reality 11")
    c.setFillColor(purple)
    c.rect(0, H - 10, W, 10, stroke=0, fill=1)
    c.rect(0, 0, W, 10, stroke=0, fill=1)
    c.rect(0, 0, 10, H, stroke=0, fill=1)
    c.rect(W - 10, 0, 10, H, stroke=0, fill=1)
    c.setStrokeColor(lilac)
    c.setLineWidth(1)
    c.rect(26, 26, W - 52, H - 52, stroke=1, fill=0)

    def centered(text, y, font, size, color, space=0.0):
        w = pdfmetrics.stringWidth(text, font, size) + space * (len(text) - 1)
        t = c.beginText((W - w) / 2, y)
        t.setFont(font, size)
        t.setCharSpace(space)
        t.setFillColor(color)
        t.textOut(text)
        c.drawText(t)

    def rule(y):
        c.setStrokeColor(gold)
        c.setLineWidth(1.2)
        c.line(W / 2 - 28, y, W / 2 + 28, y)

    top = H * 0.66
    centered("SAGE REALITY 11", top, "SR11Lora", 10.5, purple, 4.2)
    rule(top - 18)
    centered("Your Birth Chart's", top - 76, "SR11Lora", 44, purple)
    centered("Wealth Story", top - 128, "SR11Lora", 44, purple)
    centered(r["subtitle"], top - 166, "SR11LoraI", 15, soft)
    rule(top - 192)
    b = r.get("birth") or {}
    if r.get("name"):
        centered(f"Prepared for {r['name']}", top - 232, "SR11Lora", 13, purple)
    line = "  ·  ".join(x for x in (b.get("date"), b.get("time")) if x)
    if line:
        centered(line, top - 252, "SR11Lora", 9.5, ink)
    if b.get("place"):
        centered(b["place"], top - 267, "SR11Lora", 9.5, ink)
    centered("With Love & Light, Tiff", 60, "SR11LoraI", 10, soft)
    c.showPage()
    c.save()
    return buf.getvalue()


def _norm(t):
    return " ".join(t.replace("\u2019", "'").replace("\u2018", "'").split()).lower()


def _find_pages(body_pdf, sections):
    """Page index (0-based, within the body) where each heading first appears, in reading order."""
    lines = [[_norm(x) for x in (pg.extract_text() or "").splitlines()] for pg in body_pdf.pages]
    out, start = {}, 0
    for s in sections:
        h = _norm(s["heading"])
        hit = next((i for i in range(start, len(lines)) if h in lines[i]), None)
        if hit is None:
            hit = next((i for i in range(start, len(lines)) if h in " ".join(lines[i])), start)
        out[s["id"]] = hit
        start = hit
    return out


def _stranded(body_pdf, sections, breaks, min_words=45):
    """Sections whose heading starts near the foot of a page with too little text under it."""
    out = set()
    pages = [[_norm(x) for x in (pg.extract_text() or "").splitlines()] for pg in body_pdf.pages]
    start = 0
    for s in sections:
        h = _norm(s["heading"])
        for i in range(start, len(pages)):
            if h in pages[i]:
                start = i
                k = pages[i].index(h)
                after = " ".join(pages[i][k + 1:])
                after = after.replace("sage reality 11", "")
                if len(after.split()) < min_words and i < len(pages) - 1 and s["id"] not in breaks and k > 2:
                    out.add(s["id"])
                break
    return out


def _fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fdir = os.environ.get("SR11_FONT_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts"))
    if "SR11Lora" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("SR11Lora", os.path.join(fdir, "Lora-Variable.ttf")))
        pdfmetrics.registerFont(TTFont("SR11LoraI", os.path.join(fdir, "Lora-Italic-Variable.ttf")))


def _contents_pdf(sections, pages, first_body_page):
    """Contents page drawn directly. Returns (pdf bytes, [(rect, section id)])."""
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfgen import canvas
    _fonts()
    W, H = letter
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    purple, soft, gold, ink, lilac2 = HexColor(PURPLE), HexColor(SOFT), HexColor(GOLD), HexColor(INK), HexColor(LILAC2)
    x0, x1 = 72, W - 72
    y = H - 96
    c.setFillColor(gold)
    c.setFont("SR11Lora", 9)
    c.drawString(x0, y, "INSIDE YOUR READING")
    y -= 34
    c.setFillColor(purple)
    c.setFont("SR11Lora", 28)
    c.drawString(x0, y, "Contents")
    y -= 24
    c.setFillColor(soft)
    c.setFont("SR11LoraI", 10.5)
    c.drawString(x0, y, "Tap any section to jump straight to it. Your PDF viewer's bookmarks list every section too.")
    y -= 30
    links = []
    for s in sections:
        lvl1 = s["level"] == 1
        size = 12.5 if lvl1 else 10.5
        font = "SR11Lora"
        indent = 0 if lvl1 else 18
        num = str(pages[s["id"]] + 1)
        c.setFont(font, size)
        c.setFillColor(purple if lvl1 else ink)
        c.drawString(x0 + indent, y, s["heading"])
        c.drawRightString(x1, y, num)
        tw = pdfmetrics.stringWidth(s["heading"], font, size)
        nw = pdfmetrics.stringWidth(num, font, size)
        c.setFillColor(lilac2)
        dots_x = x0 + indent + tw + 8
        while dots_x < x1 - nw - 8:
            c.circle(dots_x, y + 3, 0.7, stroke=0, fill=1)
            dots_x += 5
        links.append(((x0 + indent - 2, y - 5, x1 + 2, y + size), s["id"]))
        if lvl1:
            c.setStrokeColor(lilac2)
            c.setLineWidth(0.6)
        y -= 25 if lvl1 else 19
    c.showPage()
    c.save()
    return buf.getvalue(), links


def _footer_pdf(n_pages, first_number=1):
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    _fonts()
    W, H = letter
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for i in range(n_pages):
        c.setFont("SR11Lora", 7.5)
        c.setFillColor(HexColor("#9a8db0"))
        c.drawCentredString(W / 2, 26, f"Sage Reality 11  \u00b7  Your Birth Chart's Wealth Story  \u00b7  {i + first_number}")
        c.showPage()
    c.save()
    return buf.getvalue()


def render_pdf(r) -> bytes:
    from pypdf import PdfReader, PdfWriter
    from pypdf.annotations import Link
    from pypdf.generic import Fit

    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    breaks = set()
    with tempfile.TemporaryDirectory() as td:
        hp, pp = os.path.join(td, "body.html"), os.path.join(td, "body.pdf")
        for _ in range(5):
            body = f'<!doctype html><html><head><meta charset="utf-8"><style>{PDF_CSS}</style></head><body>{_body_html(r, False, breaks)}</body></html>'
            with open(hp, "w", encoding="utf-8") as f:
                f.write(body)
            subprocess.run(["wkhtmltopdf", "-q", "--page-size", "Letter", "--disable-local-file-access", "--disable-javascript",
                            "--dpi", "110", "-T", "16mm", "-B", "18mm", "-L", "19mm", "-R", "19mm", hp, pp],
                           check=False, env=env, timeout=90, capture_output=True)
            body_pdf = PdfReader(pp)
            stranded = _stranded(body_pdf, r["sections"], breaks)
            # a final page holding only the closing lines reads as a stray page: start the links on a fresh page instead
            last = (body_pdf.pages[-1].extract_text() or "")
            if len(body_pdf.pages) > 1 and len(last.split()) < 120 and "where to go from here" not in _norm(last) \
                    and "next" not in breaks and any(x["id"] == "next" for x in r["sections"]):
                stranded.add("next")
            if not stranded:
                break
            breaks |= stranded
        n = len(body_pdf.pages)
        pages = _find_pages(body_pdf, r["sections"])
        footer = PdfReader(io.BytesIO(_footer_pdf(n)))
        for i, pg in enumerate(body_pdf.pages):
            pg.merge_page(footer.pages[i])
        contents, links = _contents_pdf(r["sections"], pages, 2)
        w = PdfWriter()
        w.append(PdfReader(io.BytesIO(render_cover_pdf(r))))
        w.append(PdfReader(io.BytesIO(contents)))
        for pg in body_pdf.pages:
            w.add_page(pg)
        offset = 2
        parent = None
        for s in r["sections"]:
            target = pages[s["id"]] + offset
            if s["level"] == 1:
                parent = w.add_outline_item(s["heading"], target)
            else:
                w.add_outline_item(s["heading"], target, parent=parent)
        w.add_outline_item("Contents", 1)
        for rect, sid in links:
            w.add_annotation(page_number=1, annotation=Link(rect=rect, target_page_index=pages[sid] + offset, fit=Fit.fit()))
        w.page_mode = "/UseOutlines"
        w.add_metadata({"/Title": f"{r['title']} for {r['name']}", "/Author": "Sage Reality 11"})
        out = io.BytesIO()
        w.write(out)
        return out.getvalue()


WEB_CSS = f"""
.sr-ws{{--p:{PURPLE};--l:{LILAC};--l2:{LILAC2};--g:{GOLD};--ink:{INK};color:var(--ink);max-width:1080px;margin:0 auto;font-family:'Source Serif 4',Georgia,serif;font-size:1.06rem;line-height:1.7}}
.sr-ws *{{box-sizing:border-box}}
.sr-ws .ws-grid{{display:grid;grid-template-columns:215px minmax(0,1fr);gap:1.8rem;align-items:start}}
@media (min-width:1200px){{.sr-ws .ws-grid{{grid-template-columns:250px minmax(0,1fr);gap:2.4rem}}}}
.sr-ws nav.ws-nav{{position:sticky;top:90px;max-height:calc(100vh - 110px);overflow:auto;border:1px solid var(--l2);border-top:5px solid var(--p);border-radius:4px;background:#fff;padding:1rem .9rem}}
.sr-ws nav .ws-navt{{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.25rem;color:var(--p);margin:0 0 .5rem}}
.sr-ws nav ol{{list-style:none;margin:0;padding:0}}
.sr-ws nav a{{display:block;padding:.38rem .5rem;border-radius:3px;color:var(--ink);text-decoration:none;font-size:.92rem;line-height:1.35}}
.sr-ws nav a.l2{{padding-left:1.3rem;font-size:.85rem;color:#6d5a8c}}
.sr-ws nav a:hover,.sr-ws nav a.on{{background:var(--l);color:var(--p)}}
.sr-ws nav select{{display:none}}
.sr-ws .ws-read section{{scroll-margin-top:90px}}
.sr-ws .ws-read h1{{line-height:1.2;font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;color:var(--p);font-size:2rem;margin:2.2rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid var(--l2)}}
.sr-ws .ws-read section:first-child h1{{margin-top:0}}
.sr-ws .ws-read h2{{line-height:1.25;font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;color:var(--p);font-size:1.45rem;margin:1.6rem 0 .5rem;padding-left:.8rem;border-left:4px solid var(--g)}}
.sr-ws .ws-read{{max-width:46rem}}
.sr-ws .ws-read p{{margin:0 0 1.05rem}}
.sr-ws .greet{{font-style:italic;color:var(--p);font-size:1.15rem}}
.sr-ws .signoff{{font-style:italic;color:var(--p);font-size:1.15rem;margin-top:1.6rem}}
.sr-ws .disc{{font-size:.82rem;color:#7a6d8d;border-top:1px solid var(--l2);padding-top:.8rem;margin-top:1.6rem}}
.sr-ws .practice{{background:var(--l);border-left:4px solid var(--p);padding:.9rem 1.1rem .2rem;margin:1.2rem 0;border-radius:3px}}
.sr-ws .plabel{{font-size:.78rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--p);margin:0 0 .4rem!important}}
.sr-ws .journal{{margin:0 0 1.4rem}}.sr-ws .journal .plabel{{color:#a07f2c}}
.sr-ws .jp p:not(.plabel){{font-style:italic;margin:0 0 .7rem!important}}
.sr-ws .offer{{border-left:3px solid var(--p);padding:.1rem 0 .1rem .9rem;margin:.9rem 0}}
.sr-ws .offer a{{font-weight:600;color:var(--p);text-decoration:none}}
.sr-ws .offer a:hover{{text-decoration:underline}}
.sr-ws .offer p{{margin:.2rem 0 0}}
.sr-ws .site{{font-size:.8rem;letter-spacing:2px;text-transform:uppercase;color:var(--g);margin-top:1.4rem}}
.sr-ws .totop{{display:inline-block;margin-top:.6rem;font-size:.85rem;color:var(--p)}}
@media (max-width:820px){{
 .sr-ws .ws-grid{{display:block}}
 .sr-ws nav.ws-nav{{position:sticky;top:0;z-index:30;max-height:none;border-radius:0;margin:0 -16px 1.2rem;padding:.6rem 16px;border-left:0;border-right:0}}
 .sr-ws nav .ws-navt,.sr-ws nav ol{{display:none}}
 .sr-ws{{font-size:1.04rem;line-height:1.75}}
 .sr-ws .ws-read section{{scroll-margin-top:175px}}
 .sr-ws .ws-read h1{{font-size:1.65rem;margin-top:1.8rem}}
 .sr-ws .ws-read h2{{font-size:1.3rem}}
 .sr-ws nav select{{display:block;width:100%;padding:.65rem .7rem;border:1px solid var(--l2);border-radius:3px;font-size:1rem;color:var(--ink);background:#fff}}
}}
"""

WEB_JS = """
(function(){
  var root=document.currentScript&&document.currentScript.parentNode; if(!root) return;
  var links=root.querySelectorAll('nav.ws-nav a'), sel=root.querySelector('nav.ws-nav select');
  function go(id){ var el=document.getElementById(id); if(el){ el.scrollIntoView({behavior:'smooth',block:'start'}); } }
  links.forEach(function(a){ a.addEventListener('click',function(e){ e.preventDefault(); go(a.getAttribute('href').slice(1)); }); });
  var nav=root.querySelector('nav.ws-nav');
  function pin(){ if(!nav||window.innerWidth>820){ if(nav) nav.style.top=''; return; } var b=0;
    document.querySelectorAll('body *').forEach(function(el){ if(root.contains(el)) return; var cs=getComputedStyle(el);
      if((cs.position==='fixed'||cs.position==='sticky')&&cs.display!=='none'&&cs.visibility!=='hidden'){ var r=el.getBoundingClientRect(); if(r.top<=1&&r.bottom>b&&r.bottom<200&&r.width>window.innerWidth*0.6) b=r.bottom; } });
    nav.style.top=b+'px'; }
  pin(); window.addEventListener('resize',pin); window.addEventListener('scroll',function(){ if(!pin.d){ pin.d=1; setTimeout(function(){ pin.d=0; pin(); },400); } },{passive:true});
  if(sel){ sel.addEventListener('change',function(){ if(sel.value) go(sel.value); }); }
  if('IntersectionObserver' in window){
    var secs=root.querySelectorAll('.ws-read section');
    var io=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){
      links.forEach(function(a){ a.classList.toggle('on', a.getAttribute('href')==='#'+en.target.id); });
      if(sel){ sel.value=en.target.id; } } }); },{rootMargin:'-20% 0px -70% 0px'});
    secs.forEach(function(s){ io.observe(s); });
  }
})();
"""


JUMP = "if(this.value){var e=document.getElementById(this.value);if(e)e.scrollIntoView({behavior:&quot;smooth&quot;,block:&quot;start&quot;});}"


def render_web(r) -> str:
    nav = []
    opts = ['<option value="">Jump to a section…</option>']
    for s in r["sections"]:
        cls = "l1" if s["level"] == 1 else "l2"
        nav.append(f'<li><a class="{cls}" href="#{esc(s["id"])}">{esc(s["heading"])}</a></li>')
        opts.append(f'<option value="{esc(s["id"])}">{"  " if s["level"] == 2 else ""}{esc(s["heading"])}</option>')
    body = _body_html(r, for_pdf=False, lines=False)
    return (f'<div class="sr-ws"><style>{WEB_CSS}</style><div class="ws-grid">'
            f'<nav class="ws-nav" aria-label="Sections of your reading"><p class="ws-navt">Your Reading</p>'
            f'<ol>{"".join(nav)}</ol><select aria-label="Jump to a section" onchange="{JUMP}">{"".join(opts)}</select></nav>'
            f'<div class="ws-read">{body}</div></div></div>')
