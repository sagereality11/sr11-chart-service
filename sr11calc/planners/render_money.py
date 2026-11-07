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
from .money_content import *
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
    EV = D["events"]; LUN = D["lunations"]; DAYS = {d["date"]: d for d in D["days"]}
    for e in EV + LUN: e["dtobj"] = datetime.fromisoformat(e["dt"])
    BP = D["blueprint"]

    state = {"page": 0, "links": False, "month": None}
    def link(dest, x1, y1, x2, y2): c.linkAbsolute("", dest, Rect=(x1, y1, x2, y2), Border="[0 0 0]")
    def frame(num=None):
        c.setFillColor(white); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(LILAC); c.setLineWidth(10); c.rect(14,14,W-28,H-28,fill=0,stroke=1)
        c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
        if num:
            c.setFont("Sans",8); c.setFillColor(MUTED)
            c.drawString(M, 34, "Sage Reality 11  ·  Your Money & Business Planner"); c.drawRightString(W-M, 34, str(num))
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

    # ---------- event text ----------
    PRIO = {"Jupiter":0, "Saturn":1, "Mars":2, "Venus":3, "Mercury":4, "Sun":5}
    def keep(e):
        if e["type"] == "aspect" and e["planet"] == "Sun" and e["aspect"] not in ("conjunct","opposite"): return False
        return True
    def ev_title(e):
        if e["type"] == "aspect":
            pt = "your Midheaven" if e["point"] == "Midheaven" else f"your natal {e['point']}"
            return f"{e['planet']} {e['aspect']} {pt}"
        if e["type"] == "ingress": return f"{e['planet']} enters your {ORD[e['house']]} house"
        return f"{e['planet']} stations {e['direction']}"
    def ev_text(e):
        if e["type"] == "aspect":
            return f"Transiting {e['planet']} {'meets' if e['aspect']=='conjunct' else 'makes a ' + e['aspect'] + ' to'} {POINT_MEANING[e['point']]}. " + PLANET_ASPECT[(e["planet"], e["flow"])]
        if e["type"] == "ingress": return INGRESS[e["planet"]].format(h=ORD[e["house"]], k=HOUSE_KEY[e["house"]])
        return STATION[(e["planet"], e["direction"])].format(h=ORD[e["house"]], k=HOUSE_KEY[e["house"]])
    EVK = [e for e in EV if keep(e)]

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle("Your Money & Business Planner"); c.setAuthor("Sage Reality 11")

    # ---------- COVER ----------
    newpage()
    c.setFillColor(SOFT); c.rect(24,24,W-48,H-48,fill=1,stroke=0)
    c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
    for i, r in enumerate([10, 14, 18, 22, 18, 14, 10]):
        x = W/2 + (i-3)*50; y = H-190
        c.setFillColor(LILAC if i % 2 else DEEP); c.setStrokeColor(PURPLE); c.circle(x, y, r, fill=1, stroke=1)
        c.setFillColor(white if i % 2 == 0 else PURPLE); c.setFont("Serif", r*1.1); c.drawCentredString(x, y - r*0.38, "$")
    eyebrow("Sage Reality 11", H-280, center=True)
    c.setFont("Serif", 46); c.setFillColor(DEEP)
    c.drawCentredString(W/2, H-345, "Your Money & Business"); c.drawCentredString(W/2, H-397, "Planner")
    c.setFont("SerifM", 18); c.setFillColor(PURPLE)
    c.drawCentredString(W/2, H-437, "Twelve months of money timing,"); c.drawCentredString(W/2, H-459, "written for your birth chart")
    c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(W/2-60, H-497, W/2+60, H-497)
    c.setFont("Sans", 11); c.setFillColor(INK)
    c.drawCentredString(W/2, H-527, f"Prepared for {NAME}"); c.drawCentredString(W/2, H-547, f"{START} to {END}")
    c.setFont("Sans", 9); c.setFillColor(MUTED); c.drawCentredString(W/2, 70, "sagereality11.com")

    # ---------- CONTENTS ----------

    NAV_BEFORE = [("Welcome", "welcome"), ("Using Your Planner", "using"), ("Your Money Blueprint", "blueprint"), ("Your Money Year", "moneyyear"), ("Green and Caution Days", "guide"), ("Your Money Year at a Glance", "glance")]

    NAV_AFTER = [("Looking Back on Your Money Year", "lookback"), ("Continue Your Journey", "journey")]

    newpage("contents")

    nav.contents_page(c, link, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF, _pm or {}, M, W, H)


    # ---------- WELCOME ----------
    newpage("welcome")
    eyebrow("A letter before you begin", H-80); heading("Welcome to Your Money Planner", H-112)
    y = H-140
    for t in [f"Hey {NAME},"] + WELCOME + [f"Your planner runs from {START} through {END}, and every date and time is shown for the location you entered."]:
        y = para(t, ParagraphStyle("l", parent=body, fontSize=11.5, leading=18), M, y) - 12
    c.setFont("SerifM", 17); c.setFillColor(DEEP); c.drawString(M, y-14, "With Love & Light,"); c.drawString(M, y-36, "Tiff")

    # ---------- USING ----------
    newpage("using")
    eyebrow("Print it or go digital", H-80); heading("Using Your Planner", H-112)
    y = para("Your planner is a PDF, so you can print it and write by hand, or use it on a tablet with a digital pen. It also has clickable links: tap a month on your Year at a Glance page to jump straight to it.", body, M, H-130) - 14
    y0 = y + 4
    y = box(None, "<b>How to Use Your Planner</b>, with step-by-step pictures:  <font color='#5B2A86'><b>sagereality11.com/planner-guide</b></font>", y0, LILAC)
    c.linkURL("https://sagereality11.com/planner-guide/", (M, y, W-M, y0), relative=0)
    y -= 12
    sub("To print your planner", y-4, 19); y = numbered(APP_PRINT[:1] + ["Print it on US Letter paper at 100% or actual size, so nothing gets cut off."] + APP_PRINT[2:], y-14) - 10
    sub("To use it on an iPad with GoodNotes", y-4, 19)
    ipad = [t.replace("Tap any moon on your Year at a Glance page or your monthly calendars to jump straight to that moon's pages", "Tap a month on your Year at a Glance page to jump straight to it") for t in APP_IPAD]
    y = numbered(ipad, y-14) - 10
    if y < 120: newpage(); y = H-80
    sub("Other tablets and computers", y-4, 19); y = numbered(APP_OTHER, y-14)


    # ---------- BLUEPRINT ----------
    newpage("blueprint")
    eyebrow("Where your wealth lives in your chart", H-80); heading("Your Money Blueprint", H-112)
    y = para("These are the core money placements in your birth chart. Every transit in this planner is read against them, so this page is your foundation.", body, M, H-130) - 14
    s2 = BP["second"]; mc = BP["mc"]
    items = [
     (f"Your 2nd house of money is in {s2['sign']}", MONEY_SIGN[s2["sign"]]),
     (f"Its ruler, {s2['ruler']}, sits in your {ORD[s2['ruler_house']]} house", "Your money flows through " + MONEY_HOUSE[s2["ruler_house"]]),
     (f"Venus in {BP['venus']['sign']} in your {ORD[BP['venus']['house']]} house", "Venus shows what you value and attract. Yours points to " + MONEY_HOUSE[BP["venus"]["house"]]),
     (f"Jupiter in {BP['jupiter']['sign']} in your {ORD[BP['jupiter']['house']]} house", "Jupiter shows where abundance grows. Yours grows through " + MONEY_HOUSE[BP["jupiter"]["house"]]),
     (f"Your Midheaven is in {mc['sign']}", MONEY_SIGN[mc["sign"]].replace("You earn", "In your career, you earn").replace("You make", "In your career, you make").replace("You build", "In your career, you build") + f" Its ruler, {mc['ruler']}, sits in your {ORD[mc['ruler_house']]} house."),
    ]
    for t, d in items:
        y = box(t, d, y) - 10
    y0 = y - 4
    y = box(None, "Want the full story? <b>Your Wealth Story Reading</b> goes much deeper into your money placements, aspects and thresholds. <font color='#5B2A86'><b>sagereality11.com/shop/wealth-story-reading</b></font>", y0, LILAC)
    c.linkURL("https://sagereality11.com/shop/wealth-story-reading/", (M, y, W-M, y0), relative=0)

    # ---------- MONEY YEAR ----------
    newpage("moneyyear")
    eyebrow("The theme of your money year", H-80); heading("Your Money Year", H-112)
    y = para("In traditional astrology, each year of your life activates a different house of your chart, beginning at your birthday. This is called an annual profection. The ruler of that house becomes your Lord of the Year, the planet whose transits matter most for you this year.", body, M, H-130) - 14
    for pr in D["prof"]:
        frm = date.fromisoformat(pr["frm"]); to = date.fromisoformat(pr["to"])
        sub(f"{frm.strftime('%B')} {frm.day}, {frm.year} to {to.strftime('%B')} {to.day}, {to.year}", y-4, 18); y -= 12
        x = pill(f"Age {pr['age']}", M, y-12); x = pill(f"{ORD[pr['house']]} House Year", x, y-12, LILAC, DEEP)
        pill(f"Lord of the Year: {pr['lord']}", x, y-12, SOFT, DEEP); y -= 28
        y = para(PROF_HOUSE[pr["house"]], body, M, y) - 8
        y = para(f"Your Lord of the Year is {pr['lord']}, which sits in {pr['lord_sign']} in your {ORD[pr['lord_house']]} house natally. That connects this year's money story to " + MONEY_HOUSE[pr["lord_house"]] + f" Pay extra attention to the months when {pr['lord']} is active in your monthly pages.", body, M, y) - 22

    # ---------- DAY GUIDE ----------
    newpage("guide")
    eyebrow("How to read your calendar", H-80); heading("Green and Caution Days", H-112)
    y = para("Each month begins with a calendar marking the days that support money moves and the days to slow down. These are guides, not rules. Life does not always wait for a green day, and that is okay.", body, M, H-130) - 16
    for (t, d), (f, tc) in zip(DAY_GUIDE, [(GREEN, GREENT), (ROSE, ROSET), (SOFT, MUTED), (SOFT, PURPLE)]):
        y = box(t, d, y, f, tc) - 10
    y = box("About the calculations", "Your planner uses Placidus houses from your birth date, time and city, traditional rulerships, and whole sign profections. Transit dates are when an aspect is exact, and you will usually feel it building a few days before. All times are in " + TZLABEL + ".", y - 6)
    y = box("Other factors to keep in mind", "This planner shows the big picture of your money timing. It does not include every factor an astrologer may look at, such as midpoints, fixed stars, the Lot of Fortune and Lot of Assets, progressions, your solar return or planetary hours. These can add detail or shift the timing of a specific day. If you are planning something important, like a launch, a big purchase or signing a contract, a deeper look at your chart can help you choose the best moment.", y - 10, LILAC)
    if y < 60: print("OVERFLOW guide", y)

    # ---------- YEAR AT A GLANCE ----------
    newpage("glance"); state["links"] = True
    eyebrow(f"{START} to {END}", H-80); heading("Your Money Year at a Glance", H-112)
    para("Your biggest money dates of the year. Tap any month to open it.", small, M, H-120)
    big = [e for e in EVK if e["type"] == "station" or e["planet"] in ("Jupiter","Saturn")]
    big += [dict(dtobj=l["dtobj"], title=f"{l['eclipse']} in your {ORD[l['house']]} house") for l in LUN if l["eclipse"]]
    big += [dict(dtobj=l["dtobj"], title=f"Money {l['kind']} in your {ORD[l['house']]} house") for l in LUN if not l["eclipse"] and l["house"] in (2, 10)]
    big.sort(key=lambda e: e["dtobj"])
    y = H-150; c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(M, y, W-M, y)
    for i, e in enumerate(big):
        if y < 82: break
        y -= 20
        if i % 2 == 0: c.setFillColor(SOFT); c.rect(M, y-6, CW, 20, fill=1, stroke=0)
        c.setFont("Sans", 9.5); c.setFillColor(INK); c.drawString(M+6, y, e["dtobj"].strftime("%b ") + str(e["dtobj"].day))
        c.setFont("SansB", 9.5); c.setFillColor(DEEP); c.drawString(M+70, y, e.get("title") or ev_title(e))
        link(f"m{e['dtobj']:%Y%m}", M, y-6, W-M, y+14)

    # ---------- MONTHS ----------
    def month_pages(yr, mo):
        mid = f"m{yr}{mo:02d}"; state["month"] = mid
        first = date(yr, mo, 1); mname = first.strftime("%B %Y")
        # calendar
        newpage(mid)
        eyebrow("Your Money Calendar", H-80); heading(mname, H-112)
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(yr, mo)
        cw = CW/7; rh = 58 if len(weeks) == 6 else 66; top = H-135
        c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
        for i, dn in enumerate(["SUN","MON","TUE","WED","THU","FRI","SAT"]): c.drawCentredString(M+i*cw+cw/2, top, dn)
        top -= 8
        lmap = {l["dtobj"].date(): l for l in LUN}
        for r, wk in enumerate(weeks):
            for i, d in enumerate(wk):
                x = M + i*cw; yb = top - (r+1)*rh
                if d.month != mo:
                    c.setFillColor(SOFT); c.setStrokeColor(LINE); c.rect(x, yb, cw, rh, fill=1, stroke=1); continue
                dd = DAYS[d.isoformat()]; st = dd["status"]
                c.setFillColor({"green": GREEN, "caution": ROSE}.get(st, white)); c.setStrokeColor(LINE); c.setLineWidth(0.6)
                c.rect(x, yb, cw, rh, fill=1, stroke=1)
                c.setFont("SansB", 9); c.setFillColor(INK); c.drawString(x+5, yb+rh-12, str(d.day))
                phase(x+cw-12, yb+rh-12, 6, dd["elong"])
                c.setFont("Sans", 6.6); c.setFillColor(MUTED); c.drawString(x+5, yb+5, f"Moon in your {ORD[dd['moon_house']]}")
                tags = []
                if st == "green": tags.append(("Green day", GREENT))
                if st == "caution": tags.append(("Caution", ROSET))
                if st == "void": tags.append(("Void Moon", MUTED))
                if d in lmap: tags.append((lmap[d]["eclipse"] or lmap[d]["kind"], PURPLE))
                if dd["merc_rx"]: tags.append(("Mercury Rx", PURPLE))
                yy = yb + rh - 26
                for t, col in tags[:3]:
                    c.setFont("SansB", 6.8); c.setFillColor(col); c.drawString(x+5, yy, t); yy -= 9
        y = top - len(weeks)*rh - 14
        lx = M
        for t, f, tc in [("Green day", GREEN, GREENT), ("Caution day", ROSE, ROSET)]:
            c.setFillColor(f); c.setStrokeColor(LINE); c.rect(lx, y-2, 10, 10, fill=1, stroke=1)
            c.setFont("Sans", 8); c.setFillColor(tc); c.drawString(lx+14, y, t); lx += 90
        c.setFont("SansI", 8); c.setFillColor(MUTED)
        c.drawString(lx, y, "Each day shows the house the Moon moves through in your chart at noon.")
        y -= 26
        sub("Key Money Dates", y, 17); y -= 6
        mev = sorted([e for e in EVK if e["dtobj"].year == yr and e["dtobj"].month == mo], key=lambda e: e["dtobj"])
        for l in LUN:
            if l["dtobj"].year == yr and l["dtobj"].month == mo:
                mev.append(dict(dtobj=l["dtobj"], title=f"{l['eclipse'] or l['kind']} in your {ORD[l['house']]} house"))
        mev.sort(key=lambda e: e["dtobj"])
        for e in mev:
            if y < 70: break
            y -= 15; c.setFont("Sans", 9); c.setFillColor(INK); c.drawString(M, y, short(e["dtobj"]))
            c.setFont("SansB", 9); c.setFillColor(DEEP); c.drawString(M+48, y, e.get("title") or ev_title(e))

        # money month page
        newpage()
        eyebrow(mname, H-80); heading("Your Money Month", H-112)
        y = H-128
        def prio(e):
            if e["type"] == "station": return 2
            if e["type"] == "ingress": return 5
            return {"Jupiter":0, "Saturn":1, "Mars":3, "Venus":4, "Sun":6}[e["planet"]]
        mt = sorted([e for e in EVK if e["dtobj"].year == yr and e["dtobj"].month == mo], key=lambda e: (prio(e), e["dtobj"]))
        theme = mt[0]["planet"] if mt and PRIO[mt[0]["planet"]] <= 3 else ("Mercury" if any(e["planet"]=="Mercury" and e["type"]=="station" for e in mt) else "Quiet")
        shown = 0; rest = []
        top6 = sorted(mt[:6], key=lambda e: e["dtobj"]); mt_rest = mt[6:]
        for e in top6 + mt_rest:
            if e in mt_rest: rest.append(e); continue
            p = Paragraph(f"<font name='SansB' color='#3B1D5C'>{short(e['dtobj'])}  ·  {ev_title(e)}</font><br/>{ev_text(e)}", item)
            _, h = p.wrap(CW, 1000)
            if y - h < 330: rest.append(e); continue
            p.drawOn(c, M, y-h); y -= h + 9; shown += 1
        if not mt:
            y = para("No major money transits this month. That is a gift. Use it to rest, review and plan.", body, M, y) - 8
        if rest:
            y = para("<font name='SansB'>Also this month:</font> " + "; ".join(f"{short(e['dtobj'])} {ev_title(e)}" for e in sorted(rest, key=lambda e: e["dtobj"])) + ".", small, M, y) - 10
        y -= 6; sub("Money Moons", y, 17); y -= 6
        for l in [l for l in LUN if l["dtobj"].year == yr and l["dtobj"].month == mo]:
            nf = 0 if l["kind"] == "New Moon" else 1
            t = MONEY_MOON.get(l["house"], OTHER_MOON)[nf]
            if l["eclipse"]: t += " Because this is an eclipse, notice what arrives rather than forcing big moves."
            y = para(f"<font name='SansB' color='#3B1D5C'>{short(l['dtobj'])}  ·  {l['eclipse'] or l['kind']} at {l['deg']}, your {ORD[l['house']]} house</font><br/>{t}", item, M, y-6) - 4
        y -= 10
        tp = TIPS[theme]
        y = box("For your personal money", tp["personal"], y, SOFT) - 8
        y = box("For your business", tp["business"], y, LILAC)
        if y < 60: print("OVERFLOW money month", mname, y)

        # goals
        newpage()
        eyebrow(mname, H-80); heading("Goals and Progress", H-112)
        top = H-140; seg = (top-64)/len(GOAL_PROMPTS)
        for i, pr in enumerate(GOAL_PROMPTS):
            yy = top - i*seg; c.setFont("SerifM", 15); c.setFillColor(PURPLE); c.drawString(M, yy-15, pr)
            lines(yy-42, yy-seg+14)
        # check-in
        newpage()
        eyebrow(mname, H-80); heading("Money Check-In", H-112)
        y = H-140; bw = (CW-12)/2
        for i, t in enumerate(CHECKIN):
            x = M + (i % 2)*(bw+12); yy = y - (i//2)*86
            c.setFillColor(SOFT); c.setStrokeColor(LINE); c.roundRect(x, yy-74, bw, 74, 8, fill=1, stroke=1)
            c.setFont("SansB", 9); c.setFillColor(PURPLE); c.drawString(x+12, yy-18, t.upper())
            c.setFont("Serif", 20); c.setFillColor(DEEP); c.drawString(x+12, yy-52, "$")
            c.setStrokeColor(LINE); c.line(x+26, yy-54, x+bw-14, yy-54)
        y -= 2*86 + 14
        seg = (y-64)/len(CHECKIN_PROMPTS)
        for i, pr in enumerate(CHECKIN_PROMPTS):
            yy = y - i*seg; c.setFont("SerifM", 15); c.setFillColor(PURPLE); c.drawString(M, yy-15, pr)
            lines(yy-42, yy-seg+14)
        # decisions
        newpage()
        eyebrow(mname, H-80); heading("Pricing and Big Decisions", H-112)
        para("Use this page for raising your prices, taking or leaving a job, a big purchase, or any money choice that deserves a clear head. Check your calendar for green days before you act.", small, M, H-120)
        top = H-160; seg = (top-64)/len(DECISION)
        for i, pr in enumerate(DECISION):
            yy = top - i*seg; c.setFont("SerifM", 14); c.setFillColor(PURPLE); c.drawString(M, yy-14, pr)
            lines(yy-38, yy-seg+12)

    yr, mo = START_D.year, START_D.month
    while date(yr, mo, 1) <= END_D:
        month_pages(yr, mo); mo += 1
        if mo == 13: yr, mo = yr+1, 1
    state["month"] = None

    # ---------- CLOSING ----------
    newpage("lookback")
    eyebrow("As your twelve months close", H-80); heading("Looking Back on Your Money Year", H-112)
    prs = ["What was my biggest money win this year?", "What money pattern did I break or begin to heal?", "What do I want my money story to be next year?"]
    top = H-140; seg = (top-64)/3
    for i, pr in enumerate(prs):
        yy = top - i*seg; c.setFont("SerifM", 15); c.setFillColor(PURPLE); c.drawString(M, yy-15, pr); lines(yy-42, yy-seg+14)
    newpage("journey")
    eyebrow("Keep going", H-80); heading("Continue Your Journey", H-112)
    y = H-130
    for t, dsc, url in [
     ("Your Wealth Story Reading", "Your full money reading: your money placements, aspects and the thresholds transits activate for you over the next year.", "sagereality11.com/shop/wealth-story-reading"),
     ("Your Moon Cycles Planner", "Twelve months of New and Full Moons, eclipses and intentions, written for your chart.", "sagereality11.com/shop/moon-cycles-planner"),
     ("Free Astrology Calculators", "Explore your chart with my free tools, including the money calculators.", "sagereality11.com/astrology-calculators"),
    ]:
        y0 = y
        y = box(None, f"<font name='Serif' size='15' color='#3B1D5C'>{t}</font><br/>{dsc}<br/><font color='#5B2A86'><b>{url}</b></font>", y) - 12
        c.linkURL("https://" + url + "/", (M, y+12, W-M, y0), relative=0)
    y -= 14; sub("A note from me", y); y -= 10
    y = para("This planner is based on my own research, methodology and intuitive abilities. It is meant for reflection and planning, and it is not financial, investment, tax, legal or medical advice. Please talk with a licensed professional before making financial decisions. You are always the one who decides what is right for your life and your business.", small, M, y) - 8
    y = para("Because this planner is a personalized digital download, all sales are final.", small, M, y) - 20
    c.setFont("SerifM", 17); c.setFillColor(DEEP); c.drawString(M, y-8, "With Love & Light,"); c.drawString(M, y-30, "Tiff")
    nav.outline(c, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF)
    c.save()
    if _pm is None:
        return render(D_original, NAME, TZLABEL, _pm=pm)
    return buf.getvalue()

