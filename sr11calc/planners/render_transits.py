import copy, io, json, os, sys, math, calendar
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.fonts import addMapping
from .transit_content import *
from . import nav
from .moon_content import APP_PRINT, APP_IPAD, APP_OTHER

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
for n, f in [("Serif","Cormorant-SemiBold"),("SerifM","Cormorant-Medium"),("Sans","Lato-Regular"),("SansB","Lato-Bold"),("SansI","Lato-Italic")]:
    pdfmetrics.registerFont(TTFont(n, F+f+".ttf"))
addMapping("Sans",0,0,"Sans"); addMapping("Sans",1,0,"SansB"); addMapping("Sans",0,1,"SansI"); addMapping("Sans",1,1,"SansB")

PURPLE = HexColor("#5B2A86"); DEEP = HexColor("#3B1D5C"); LILAC = HexColor("#E7DAF5")
SOFT = HexColor("#F6F0FC"); LINE = HexColor("#D9C9EC"); INK = HexColor("#2E2438"); MUTED = HexColor("#7A6A8C"); GREY = HexColor("#B9B0C2")
GREEN = HexColor("#E2F0DC"); GREENT = HexColor("#2F6B3A"); ROSE = HexColor("#F9E3DA"); ROSET = HexColor("#9A4A2C")

W, H = letter; M = 54; CW = W - 2*M
body = ParagraphStyle("b", fontName="Sans", fontSize=10.5, leading=15.5, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=9, leading=13, textColor=MUTED)
callout = ParagraphStyle("c", parent=body, fontSize=10, leading=14.5)
item = ParagraphStyle("i", parent=body, fontSize=9.6, leading=13.4)



def render(D, NAME, TZLABEL, _pm=None):
    """Draw the planner and return the PDF bytes. Drawn twice: the first pass finds the page
    numbers for the Contents page, the second pass draws them."""
    D_original = D; D = copy.deepcopy(D); pm = {}
    START_D = date.fromisoformat(D["start"]); END_D = date.fromisoformat(D["end"])
    START = START_D.strftime("%B %Y"); END = END_D.strftime("%B %Y")
    NAV_MONTHS = nav.months_from(START_D); KEYF = lambda y, m: f"m{y}{m:02d}"
    DAYS = {d["date"]: d for d in D["days"]}

    state = {"page": 0, "links": False, "month": None}
    def link(dest, x1, y1, x2, y2): c.linkAbsolute("", dest, Rect=(x1, y1, x2, y2), Border="[0 0 0]")
    def frame(num=None):
        c.setFillColor(white); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(LILAC); c.setLineWidth(10); c.rect(14,14,W-28,H-28,fill=0,stroke=1)
        c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
        if num:
            c.setFont("Sans",8); c.setFillColor(MUTED)
            c.drawString(M, 34, "Sage Reality 11  ·  Your Transits Planner"); c.drawRightString(W-M, 34, str(num))
            if state["links"]:
                c.setFont("SansB",8); c.setFillColor(PURPLE)
                t1 = "Year at a Glance"; w1 = c.stringWidth(t1,"SansB",8); x = W/2 - w1 + 20
                c.drawString(x, 34, t1); link("glance", x-2, 30, x+w1+2, 44)
                if state["month"]:
                    t2 = "Back to Calendar"; w2 = c.stringWidth(t2,"SansB",8)
                    c.drawString(W/2 + 40, 34, t2); link(state["month"], W/2+38, 30, W/2+42+w2, 44)
    def newpage(bm=None):
        if state["page"]: c.showPage()
        state["page"] += 1; frame(state["page"] if state["page"] > 1 else None)
        if state["links"]: nav.draw_tabs(c, link, NAV_MONTHS, KEYF, state["month"], M, W, H)
        if bm: c.bookmarkPage(bm); pm[bm] = state["page"]
    def para(t, st, x, y, w=CW):
        p = Paragraph(t, st); _, h = p.wrap(w, 2000); p.drawOn(c, x, y-h); return y-h
    def heading(t, y, size=28): c.setFont("Serif", size); c.setFillColor(DEEP); c.drawString(M, y, t)
    def sub(t, y, size=18): c.setFont("Serif", size); c.setFillColor(DEEP); c.drawString(M, y, t)
    def eyebrow(t, y, center=False):
        c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
        (c.drawCentredString(W/2, y, t.upper()) if center else c.drawString(M, y, t.upper()))
    def pill(t, x, y, fill=PURPLE, fg=white, size=8.5):
        c.setFont("SansB", size); w = c.stringWidth(t,"SansB",size)+18
        c.setFillColor(fill); c.roundRect(x, y-5, w, 18, 9, fill=1, stroke=0)
        c.setFillColor(fg); c.drawString(x+9, y+1, t); return x+w+6
    def box(title, text, y, fill=SOFT, tcolor=PURPLE):
        p = Paragraph(text, callout); _, h = p.wrap(CW-28, 2000); th = 16 if title else 0
        c.setFillColor(fill); c.setStrokeColor(LINE); c.setLineWidth(0.8)
        c.roundRect(M, y-h-th-22, CW, h+th+22, 8, fill=1, stroke=1)
        if title: c.setFont("SansB",9); c.setFillColor(tcolor); c.drawString(M+14, y-20, title.upper())
        p.drawOn(c, M+14, y-11-th-h); return y-h-th-22
    def lines(y0, y1, gap=24, x0=M, x1=None):
        c.setStrokeColor(LINE); c.setLineWidth(0.6); y = y0
        while y > y1: c.line(x0, y, x1 or W-M, y); y -= gap
    def phase(x, y, r, el):
        c.setFillColor(DEEP); c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.circle(x, y, r, fill=1, stroke=0)
        el %= 360; wax = el < 180; L = 1 if wax else -1
        k = math.cos(math.radians(el)) if wax else -math.cos(math.radians(el))
        p = c.beginPath(); N = 30
        for i in range(N+1):
            t = math.radians(-90+180*i/N); pt = (x+L*r*math.cos(t), y+r*math.sin(t))
            p.lineTo(*pt) if i else p.moveTo(*pt)
        for i in range(N, -1, -1):
            t = math.radians(-90+180*i/N); p.lineTo(x+k*r*math.cos(t), y+r*math.sin(t))
        p.close(); c.setFillColor(LILAC); c.drawPath(p, fill=1, stroke=0); c.circle(x, y, r, fill=0, stroke=1)
    def short(d): return d.strftime("%b ") + str(d.day)
    def numbered(items, y):
        for i, t in enumerate(items, 1):
            p = Paragraph(t, body); _, h = p.wrap(CW-28, 1000)
            if y - h < 70: newpage(); y = H-90
            c.setFont("SansB", 10.5); c.setFillColor(PURPLE); c.drawString(M, y-11, f"{i}.")
            p.drawOn(c, M+22, y-h); y -= h + 5
        return y


    # ---------- data prep ----------
    ABBR = {"conjunct":"conj","square":"sq","opposite":"opp","trine":"tri","sextile":"sxt"}
    PABBR = {"Ascendant":"Asc","Midheaven":"MC","North Node":"Node"}
    def ptname(n): return {"Ascendant":"your Ascendant","Midheaven":"your Midheaven","North Node":"your North Node"}.get(n, f"your natal {n}")
    BIG = D["big"]
    for i, b in enumerate(BIG):
        b["id"] = f"bt{i}"
        b["major"] = (b["planet"] != "Jupiter" and b["aspect"] != "sextile") or (b["planet"] == "Jupiter" and b["aspect"] != "sextile")
        b["title"] = f"{b['planet']} {b['aspect']} {ptname(b['point'])}"
        b["exact_d"] = [datetime.fromisoformat(x) for x in b["exact"]]
    FASTT = D["fast"]
    for f in FASTT: f["dtobj"] = datetime.fromisoformat(f["dt"])
    STN = D["stations"]
    for s_ in STN: s_["dtobj"] = datetime.fromisoformat(s_["dt"])
    ECL = D["eclipses"]
    for e in ECL: e["dtobj"] = datetime.fromisoformat(e["dt"])
    MONTHS = {m["month"]: m for m in D["months"]}

    def fulld(d): return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")
    def when(b):
        a = date.fromisoformat(b["start"][:10]); z = date.fromisoformat(b["end"][:10])
        a_txt = "Active before your planner begins" if a < START_D else f"Active from {fulld(a)}"
        z_txt = f"through {fulld(z)}" if z <= END_D else "into next year"
        ex_in = [d for d in b["exact_d"] if START_D <= d.date() <= END_D]
        if ex_in: ex = "Exact on " + " and ".join(fulld(d) for d in ex_in)
        elif any(d.date() < START_D for d in b["exact_d"]) or not b["exact_d"]: ex = "Exact before your planner begins, now separating"
        else: ex = "Exact on " + fulld(min(d for d in b["exact_d"] if d.date() > END_D)) + ", after your planner ends"
        return f"{a_txt} {z_txt}.  {ex}."

    USE = {}
    def big_text(b):
        p, a, n = b["planet"], b["aspect"], b["point"]
        k = USE.setdefault(p, 0); USE[p] += 1
        b["vi"] = k
        t = PLANET_V[p][k % len(PLANET_V[p])] + " " + POINT[n] + " " + ASPECT[a]
        if (p, a, n) in SPECIAL: t = SPECIAL[(p, a, n)] + " " + t
        t += f" This transit moves through your {ORD[b['house']]} house of {HOUSE_KEY[b['house']]}, so that is where you are likely to notice it."
        lo, hi = OCTAVE[p]
        t += f" In its lower octave it can feel like {lo}. In its higher octave it becomes {hi}."
        return t

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle("Your Transits Planner"); c.setAuthor("Sage Reality 11")

    # ---------- COVER ----------
    newpage()
    c.setFillColor(SOFT); c.rect(24,24,W-48,H-48,fill=1,stroke=0)
    c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
    cx, cy = W/2, H-185
    for r in (62, 44, 26):
        c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.circle(cx, cy, r, fill=0, stroke=1)
    for r, ang, rad, fill in [(62, 30, 7, DEEP), (44, 200, 6, LILAC), (26, 110, 5, DEEP), (62, 250, 5, LILAC)]:
        x = cx + r*math.cos(math.radians(ang)); y = cy + r*math.sin(math.radians(ang))
        c.setFillColor(fill); c.setStrokeColor(PURPLE); c.circle(x, y, rad, fill=1, stroke=1)
    c.setFillColor(DEEP); c.circle(cx, cy, 9, fill=1, stroke=0)
    eyebrow("Sage Reality 11", H-280, center=True)
    c.setFont("Serif", 50); c.setFillColor(DEEP)
    c.drawCentredString(W/2, H-345, "Your Transits"); c.drawCentredString(W/2, H-400, "Planner")
    c.setFont("SerifM", 18); c.setFillColor(PURPLE)
    c.drawCentredString(W/2, H-440, "Twelve months of personal timing,"); c.drawCentredString(W/2, H-462, "written for your birth chart")
    c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(W/2-60, H-500, W/2+60, H-500)
    c.setFont("Sans", 11); c.setFillColor(INK)
    c.drawCentredString(W/2, H-530, f"Prepared for {NAME}"); c.drawCentredString(W/2, H-550, f"{START} to {END}")
    c.setFont("Sans", 9); c.setFillColor(MUTED); c.drawCentredString(W/2, 70, "sagereality11.com")

    # ---------- CONTENTS ----------

    NAV_BEFORE = [("Welcome", "welcome"), ("Using Your Planner", "using"), ("How Transits Work", "how"), ("Your Year", "year"), ("Your Big Transits at a Glance", "glance"), ("Your Big Transits", "bigtransits"), ("Retrogrades and Eclipses", "turning")]

    NAV_AFTER = [("Looking Back on Your Year", "lookback"), ("Continue Your Journey", "journey")]

    newpage("contents")

    nav.contents_page(c, link, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF, _pm or {}, M, W, H)


    # ---------- WELCOME ----------
    newpage("welcome")
    eyebrow("A letter before you begin", H-80); heading("Welcome to Your Transits Planner", H-112)
    y = H-140
    for t in [f"Hey {NAME},"] + WELCOME + [f"Your planner runs from {START} through {END}, and every date and time is shown for the location you entered."]:
        y = para(t, ParagraphStyle("l", parent=body, fontSize=11.5, leading=18), M, y) - 12
    c.setFont("SerifM", 17); c.setFillColor(DEEP); c.drawString(M, y-14, "With Love & Light,"); c.drawString(M, y-36, "Tiff")

    # ---------- USING ----------
    newpage("using")
    eyebrow("Print it or go digital", H-80); heading("Using Your Planner", H-112)
    y = para("Your planner is a PDF, so you can print it and write by hand, or use it on a tablet with a digital pen. It also has clickable links: tap a transit on your Big Transits page to read about it, or tap a month to jump to it.", body, M, H-130) - 18
    sub("To print your planner", y-4, 19); y = numbered(APP_PRINT[:1] + ["Print it on US Letter paper at 100% or actual size, so nothing gets cut off."] + APP_PRINT[2:], y-16) - 16
    sub("To use it on an iPad with GoodNotes", y-4, 19)
    ipad = [t.replace("Tap any moon on your Year at a Glance page or your monthly calendars to jump straight to that moon's pages", "Tap a transit or a month on your Year at a Glance page to jump straight to it") for t in APP_IPAD]
    y = numbered(ipad, y-16) - 16
    if y < 120: newpage(); y = H-80
    sub("Other tablets and computers", y-4, 19); numbered(APP_OTHER, y-16)

    # ---------- HOW TRANSITS WORK ----------
    newpage("how")
    eyebrow("Reading your transits", H-80); heading("How Transits Work", H-112)
    y = para("A transit happens when a planet moving through the sky today makes an angle, called an aspect, to a planet or point in your birth chart. The planet tells you what kind of energy arrives, the aspect tells you how it feels, and the house tells you where in your life it shows up.", body, M, H-130) - 14
    for t, d in PLANETS_GUIDE:
        y = para(f"<font name='SansB' color='#3B1D5C'>{t}</font>  {d}", body, M, y) - 7
    y -= 8; sub("The five aspects", y, 18); y -= 8
    for a in ["conjunct","sextile","square","trine","opposite"]:
        y = para(f"<font name='SansB' color='#3B1D5C'>{a.capitalize()}</font>  {ASPECT[a]}", body, M, y) - 6
    y = box("About the calculations", "Your planner uses Placidus houses from your birth date, time and city. Jupiter and Saturn transits are counted within 2 degrees and Uranus, Neptune and Pluto within 1.5 degrees, so the dates show when you will feel each one most. All times are in " + TZLABEL + ".", y - 10) - 10
    box("Other factors to keep in mind", "This planner follows the transits to your natal chart. It does not include progressions, solar arcs, your solar return, midpoints or fixed stars, which can add more layers to your timing. For the bigger picture of this chapter of your life, see my reading What's Happening to Me Right Now? Your Personal Timing Reading.", y, LILAC)

    # ---------- YOUR YEAR ----------
    newpage("year")
    eyebrow("The theme of your year", H-80); heading("Your Year", H-112)
    y = para("Each year of your life activates a different house of your chart, beginning at your birthday. This is called an annual profection. The ruler of that house becomes your Lord of the Year, and transits involving that planet tend to matter most for you.", body, M, H-130) - 14
    for pr in D["prof"]:
        frm = date.fromisoformat(pr["frm"]); to = date.fromisoformat(pr["to"])
        sub(f"{fulld(frm)} to {fulld(to)}", y-4); y -= 12
        x = pill(f"Age {pr['age']}", M, y-12); x = pill(f"{ORD[pr['house']]} House Year", x, y-12, LILAC, DEEP)
        pill(f"Lord of the Year: {pr['lord']}", x, y-12, SOFT, DEEP); y -= 28
        lt = [b for b in BIG if b["planet"] == pr["lord"] and b["major"]]
        extra = f" Watch your {pr['lord']} transits this year, including {lt[0]['title']}." if lt else ""
        y = para(f"This is a {ORD[pr['house']]} house year, so {HOUSE_KEY[pr['house']]} take center stage. Your Lord of the Year is {pr['lord']}, which sits in your {ORD[pr['lord_house']]} house of {HOUSE_KEY[pr['lord_house']]}." + extra, body, M, y) - 22

    # ---------- GLANCE ----------
    newpage("glance"); state["links"] = True
    eyebrow(f"{START} to {END}", H-80); heading("Your Big Transits at a Glance", H-112)
    para("The slower transits that shape your year. Tap any transit to read what it means for you.", small, M, H-120)
    y = H-150; c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(M, y, W-M, y)
    majors = [b for b in BIG if b["major"]]; minors = [b for b in BIG if not b["major"]]
    for i, b in enumerate(majors):
        y -= 20
        if i % 2 == 0: c.setFillColor(SOFT); c.rect(M, y-6, CW, 20, fill=1, stroke=0)
        ex_in = [d for d in b["exact_d"] if START_D <= d.date() <= END_D]
        c.setFont("Sans", 9); c.setFillColor(INK)
        c.drawString(M+6, y, ", ".join(short(d) for d in ex_in) if ex_in else "separating")
        c.setFont("SansB", 9.5); c.setFillColor(DEEP); c.drawString(M+110, y, b["title"])
        c.setFont("Sans", 8.5); c.setFillColor(MUTED); c.drawRightString(W-M-6, y, f"your {ORD[b['house']]} house")
        link(b["id"], M, y-6, W-M, y+14)
    y -= 30; sub("Gentle supports", y, 16); y -= 6
    para("Lighter Jupiter sextiles that open small doors when you take a step toward them: " + "; ".join(f"{b['title']} ({', '.join(short(d) for d in b['exact_d'] if START_D <= d.date() <= END_D) or 'active'})" for b in minors) + ".", small, M, y)

    # ---------- BIG TRANSIT WRITE-UPS ----------
    newpage("bigtransits")
    eyebrow("What they mean for you", H-80); heading("Your Big Transits", H-112)
    y = H-130
    for b in majors:
        t = big_text(b)
        p = Paragraph(t, callout); _, h = p.wrap(CW-28, 2000)
        need = h + 120
        if y - need < 60:
            newpage(); y = H-80
        c.bookmarkPage(b["id"], fit="XYZ", top=y+10)
        c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y-14, b["title"])
        c.setFont("SansI", 8.8); c.setFillColor(PURPLE); c.drawString(M, y-29, when(b))
        y -= 36
        y = box(None, t, y) - 6
        wk = WORK_V[b["planet"]][b["vi"] % len(WORK_V[b["planet"]])]
        if (b["planet"], b["aspect"], b["point"]) in SPECIAL_LINK:
            wk += f" Want to go deeper? Try my free calculator at <b>{SPECIAL_LINK[(b['planet'], b['aspect'], b['point'])]}</b>"
        y = box("How to work with it", wk, y, LILAC) - 18

    # ---------- RETROGRADES + ECLIPSES ----------
    newpage("turning")
    eyebrow("Turning points of your year", H-80); heading("Retrogrades and Eclipses", H-112)
    y = H-136; sub("Planets changing direction", y, 18); y -= 6
    for s_ in STN:
        y -= 16; c.setFont("Sans", 9.5); c.setFillColor(INK); c.drawString(M, y, short(s_["dtobj"]))
        c.setFont("SansB", 9.5); c.setFillColor(DEEP); c.drawString(M+50, y, f"{s_['planet']} stations {s_['direction']}")
        c.setFont("Sans", 9); c.setFillColor(MUTED); c.drawString(M+240, y, f"{s_['deg']}  ·  your {ORD[s_['house']]} house")
    y -= 30; sub("Eclipses", y, 18); y -= 6
    for e in ECL:
        y -= 16; c.setFont("Sans", 9.5); c.setFillColor(INK); c.drawString(M, y, short(e["dtobj"]))
        c.setFont("SansB", 9.5); c.setFillColor(DEEP); c.drawString(M+50, y, e["kind"])
        c.setFont("Sans", 9); c.setFillColor(MUTED); c.drawString(M+240, y, f"{e['deg']}  ·  your {ORD[e['house']]} house")
    y -= 20
    y1 = box(None, "Eclipses are turning points that unfold over months. For a personal page on every eclipse and all of your New and Full Moons, see <b>Your Moon Cycles Planner</b>. <font color='#5B2A86'><b>sagereality11.com/shop/moon-cycles-planner</b></font>", y, LILAC)
    c.linkURL("https://sagereality11.com/shop/moon-cycles-planner/", (M, y1, W-M, y), relative=0)

    # ---------- MONTHS ----------
    def tlabel(p, a, n): return f"{p} {ABBR[a]} {PABBR.get(n, n)}"
    def month_pages(yr, mo):
        mid = f"m{yr}{mo:02d}"; state["month"] = mid
        mname = date(yr, mo, 1).strftime("%B %Y"); key = f"{yr}-{mo:02d}"
        inm = lambda d: d.year == yr and d.month == mo
        newpage(mid)
        eyebrow("Your Transit Calendar", H-80); heading(mname, H-112)
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(yr, mo)
        cw = CW/7; rh = 60 if len(weeks) == 6 else 70; top = H-135
        c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
        for i, dn in enumerate(["SUN","MON","TUE","WED","THU","FRI","SAT"]): c.drawCentredString(M+i*cw+cw/2, top, dn)
        top -= 8
        marks = {}
        for f in FASTT: marks.setdefault(f["dtobj"].date(), []).append((1, tlabel(f["planet"], f["aspect"], f["point"])))
        for b in majors:
            for d in b["exact_d"]: marks.setdefault(d.date(), []).append((0, tlabel(b["planet"], b["aspect"], b["point"])))
        for s_ in STN: marks.setdefault(s_["dtobj"].date(), []).append((0, f"{s_['planet']} {'Rx' if s_['direction']=='retrograde' else 'direct'}"))
        for r, wk in enumerate(weeks):
            for i, d in enumerate(wk):
                x = M + i*cw; yb = top - (r+1)*rh
                if d.month != mo:
                    c.setFillColor(SOFT); c.setStrokeColor(LINE); c.rect(x, yb, cw, rh, fill=1, stroke=1); continue
                dd = DAYS[d.isoformat()]; mk = sorted(marks.get(d, []))
                c.setFillColor(LILAC if any(m[0] == 0 for m in mk) else white); c.setStrokeColor(LINE); c.setLineWidth(0.6)
                c.rect(x, yb, cw, rh, fill=1, stroke=1)
                c.setFont("SansB", 9); c.setFillColor(INK); c.drawString(x+5, yb+rh-12, str(d.day))
                phase(x+cw-12, yb+rh-12, 6, dd["elong"])
                yy = yb + rh - 25
                for pri, t in mk[:3]:
                    c.setFont("SansB" if pri == 0 else "Sans", 6.4); c.setFillColor(DEEP if pri == 0 else PURPLE)
                    c.drawString(x+4, yy, t); yy -= 8.5
                c.setFont("Sans", 6.2); c.setFillColor(MUTED)
                c.drawString(x+4, yb+4, f"Moon {ORD[dd['moon_house']]}")
                if "Mercury" in dd["rx"]:
                    c.setFont("SansB", 6.2); c.setFillColor(PURPLE); c.drawRightString(x+cw-4, yb+4, "Mercury Rx")
        y = top - len(weeks)*rh - 13
        c.setFont("SansI", 7.6); c.setFillColor(MUTED)
        c.drawString(M, y, "Highlighted days hold an exact big transit or a planet changing direction. Moon shows the house the Moon moves through at noon.")
        y -= 26
        sm = MONTHS[key]
        box(f"The Sun in your {ORD[sm['sun_house']]} house", SUN_MONTH[sm["sun_house"]], y)

        # transits page
        newpage()
        eyebrow(mname, H-80); heading("Your Month in Transits", H-112)
        y = H-138
        act = [b for b in majors if date.fromisoformat(b["start"][:10]) <= date(yr, mo, calendar.monthrange(yr, mo)[1]) and date.fromisoformat(b["end"][:10]) >= date(yr, mo, 1)]
        sub("Big transits active this month", y-4, 16); y -= 12
        if not act: y = para("No slow transits are active this month. A lighter month to catch your breath.", body, M, y) - 6
        for b in act:
            ex = [d for d in b["exact_d"] if inm(d)]
            t = f"<font name='SansB' color='#3B1D5C'>{b['title']}</font>" + (f"  ·  <font color='#5B2A86'>exact {', '.join(short(d) for d in ex)}</font>" if ex else "") + f"  ·  your {ORD[b['house']]} house"
            y0 = y; y = para(t, item, M, y) - 5; link(b["id"], M, y, W-M, y0)
        y -= 10; sub("This month's transits", y, 16); y -= 6
        ft = sorted([f for f in FASTT if inm(f["dtobj"])], key=lambda f: f["dtobj"])
        st = [s_ for s_ in STN if inm(s_["dtobj"])]
        items = [(f["dtobj"], f"<font name='SansB' color='#3B1D5C'>{short(f['dtobj'])}  ·  {f['planet']} {f['aspect']} {ptname(f['point'])}</font>  {FAST[(f['planet'], f['flow'])].capitalize()} around {FAST_POINT[f['point']]}.") for f in ft]
        items += [(s_["dtobj"], f"<font name='SansB' color='#3B1D5C'>{short(s_['dtobj'])}  ·  {s_['planet']} stations {s_['direction']}</font>  In your {ORD[s_['house']]} house of {HOUSE_KEY[s_['house']]}. " + STATION_X[s_["direction"]]) for s_ in st]
        items.sort(key=lambda t: t[0]); rest = 0
        for _, t in items:
            p = Paragraph(t, item); _, h = p.wrap(CW, 500)
            if y - h < 70: rest += 1; continue
            p.drawOn(c, M, y-h-4); y -= h + 7
        if rest: y = para(f"Plus {rest} more on your calendar.", small, M, y-4)
        if y > 200:
            sub("Notes", y-30, 16); lines(y-56, 64)
        if y < 45: print("OVERFLOW", mname)

        # journal
        newpage()
        eyebrow(mname, H-80); heading("Reflections", H-112)
        top = H-140; seg = (top-64)/len(JOURNAL)
        for i, pr in enumerate(JOURNAL):
            yy = top - i*seg
            p = Paragraph(pr, ParagraphStyle("p", fontName="SerifM", fontSize=15, leading=18, textColor=PURPLE)); _, ph = p.wrap(CW, 200); p.drawOn(c, M, yy-ph)
            lines(yy-ph-24, yy-seg+14)

    yr, mo = START_D.year, START_D.month
    while date(yr, mo, 1) <= END_D:
        month_pages(yr, mo); mo += 1
        if mo == 13: yr, mo = yr+1, 1
    state["month"] = None

    # ---------- CLOSING ----------
    newpage("lookback")
    eyebrow("As your twelve months close", H-80); heading("Looking Back on Your Year", H-112)
    prs = ["Which transit changed me the most this year?", "What did I build, release or awaken to?", "What am I carrying into my next year?"]
    top = H-140; seg = (top-64)/3
    for i, pr in enumerate(prs):
        yy = top - i*seg; c.setFont("SerifM", 15); c.setFillColor(PURPLE); c.drawString(M, yy-15, pr); lines(yy-42, yy-seg+14)
    newpage("journey")
    eyebrow("Keep going", H-80); heading("Continue Your Journey", H-112)
    y = H-130
    for t, dsc, url in [
     ("What's Happening to Me Right Now? Your Personal Timing Reading", "The deeper story of this chapter: your transits, eclipses, progressions and profections woven together.", "sagereality11.com/shop/personal-timing-reading"),
     ("Your Moon Cycles Planner", "Twelve months of New and Full Moons and a personal page for every eclipse.", "sagereality11.com/shop/moon-cycles-planner"),
     ("Your Money & Business Planner", "Your money transits, green and caution days and monthly money pages.", "sagereality11.com/shop/money-business-planner"),
    ]:
        y0 = y
        y = box(None, f"<font name='Serif' size='15' color='#3B1D5C'>{t}</font><br/>{dsc}<br/><font color='#5B2A86'><b>{url}</b></font>", y) - 12
        c.linkURL("https://" + url + "/", (M, y+12, W-M, y0), relative=0)
    y -= 14; sub("A note from me", y); y -= 10
    y = para("This planner is based on my own research, methodology and intuitive abilities. It is meant for reflection and personal growth, and it is not medical, legal or financial advice. You are always the one who decides what is right for your life.", small, M, y) - 8
    y = para("Because this planner is a personalized digital download, all sales are final.", small, M, y) - 20
    c.setFont("SerifM", 17); c.setFillColor(DEEP); c.drawString(M, y-8, "With Love & Light,"); c.drawString(M, y-30, "Tiff")
    nav.outline(c, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF)
    c.save()
    if _pm is None:
        return render(D_original, NAME, TZLABEL, _pm=pm)
    return buf.getvalue()

