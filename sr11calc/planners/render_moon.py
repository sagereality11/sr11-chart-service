import copy, io, json, os, sys, math, calendar
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import addMapping
from .moon_content import *
from . import nav

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
for n, f in [("Serif","Cormorant-SemiBold"),("SerifM","Cormorant-Medium"),("Sans","Lato-Regular"),("SansB","Lato-Bold"),("SansI","Lato-Italic")]:
    pdfmetrics.registerFont(TTFont(n, F+f+".ttf"))
addMapping("Sans",0,0,"Sans"); addMapping("Sans",1,0,"SansB"); addMapping("Sans",0,1,"SansI"); addMapping("Sans",1,1,"SansB")

PURPLE = HexColor("#5B2A86"); DEEP = HexColor("#3B1D5C"); LILAC = HexColor("#E7DAF5")
SOFT = HexColor("#F6F0FC"); LINE = HexColor("#D9C9EC"); INK = HexColor("#2E2438"); MUTED = HexColor("#7A6A8C")
GREY = HexColor("#B9B0C2")

W, H = letter
M = 54
CW = W - 2*M

body = ParagraphStyle("b", fontName="Sans", fontSize=10.5, leading=15.5, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=9, leading=13, textColor=MUTED)
callout = ParagraphStyle("c", parent=body, fontSize=10, leading=14.5)



def render(data, NAME, TZLABEL, _pm=None):
    """Draw the planner and return the PDF bytes. Drawn twice: the first pass finds the page
    numbers for the Contents page, the second pass draws them."""
    data_original = data; data = copy.deepcopy(data); pm = {}
    EV = data["events"]; QU = data["quarters"]; DAYS = {d["date"]: d for d in data["days"]}
    for e in EV + QU: e["dtobj"] = datetime.fromisoformat(e["dt"])
    for i, e in enumerate(EV): e["id"] = f"lun{i}"

    START_D = date.fromisoformat(data["start"]); END_D = date.fromisoformat(data["end"])
    START = START_D.strftime("%B %Y"); END = END_D.strftime("%B %Y")
    NAV_MONTHS = nav.months_from(START_D); KEYF = lambda y, m: f"cal{y}{m:02d}"

    state = {"page": 0, "cal": None, "links": False}

    def link(dest, x1, y1, x2, y2):
        c.linkAbsolute("", dest, Rect=(x1, y1, x2, y2), Border="[0 0 0]")

    def frame(num=None):
        c.setFillColor(white); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(LILAC); c.setLineWidth(10); c.rect(14,14,W-28,H-28,fill=0,stroke=1)
        c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
        if num:
            c.setFont("Sans",8); c.setFillColor(MUTED)
            c.drawString(M, 34, "Sage Reality 11  ·  Your Moon Cycles Planner")
            c.drawRightString(W-M, 34, str(num))
            if state["links"]:
                c.setFont("SansB",8); c.setFillColor(PURPLE)
                t1 = "Year at a Glance"; w1 = c.stringWidth(t1,"SansB",8)
                x = W/2 - 10 - w1
                c.drawString(x, 34, t1); link("glance", x-2, 30, x+w1+2, 44)
                if state["cal"]:
                    t2 = "Back to Calendar"; w2 = c.stringWidth(t2,"SansB",8)
                    c.drawString(W/2 + 10, 34, t2); link(state["cal"], W/2+8, 30, W/2+12+w2, 44)

    def newpage(bookmark=None):
        if state["page"]: c.showPage()
        state["page"] += 1; frame(state["page"] if state["page"] > 1 else None)
        if state["links"]: nav.draw_tabs(c, link, NAV_MONTHS, KEYF, state["cal"], M, W, H)
        if bookmark: c.bookmarkPage(bookmark); pm[bookmark] = state["page"]

    def para(text, style, x, y, w=CW):
        p = Paragraph(text, style); _, h = p.wrap(w, 1000); p.drawOn(c, x, y-h); return y-h

    def heading(text, y, size=28):
        c.setFont("Serif", size); c.setFillColor(DEEP); c.drawString(M, y, text)

    def eyebrow(text, y, x=M, center=False):
        c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
        (c.drawCentredString(W/2, y, text.upper()) if center else c.drawString(x, y, text.upper()))

    def phase(x, y, r, el):
        """Draw the Moon as it looks at elongation el (degrees), northern hemisphere view."""
        c.setFillColor(DEEP); c.setStrokeColor(PURPLE); c.setLineWidth(0.8)
        c.circle(x, y, r, fill=1, stroke=0)
        el %= 360
        waxing = el < 180
        L = 1 if waxing else -1
        k = math.cos(math.radians(el)) if waxing else -math.cos(math.radians(el))
        p = c.beginPath(); N = 36
        for i in range(N+1):
            t = math.radians(-90 + 180*i/N)
            p.lineTo(x + L*r*math.cos(t), y + r*math.sin(t)) if i else p.moveTo(x + L*r*math.cos(t), y + r*math.sin(t))
        for i in range(N, -1, -1):
            t = math.radians(-90 + 180*i/N)
            p.lineTo(x + k*r*math.cos(t), y + r*math.sin(t))
        p.close()
        c.setFillColor(LILAC); c.drawPath(p, fill=1, stroke=0)
        c.circle(x, y, r, fill=0, stroke=1)

    def moon(x, y, r, kind):
        phase(x, y, r, {"New Moon":0, "First Quarter":90, "Full Moon":180, "Last Quarter":270}[kind])

    def pill(text, x, y, fill=PURPLE, fg=white, size=8.5):
        c.setFont("SansB", size); w = c.stringWidth(text,"SansB",size)+18
        c.setFillColor(fill); c.roundRect(x, y-5, w, 18, 9, fill=1, stroke=0)
        c.setFillColor(fg); c.drawString(x+9, y+1, text); return x+w+6

    def box(title, text, y, fill=SOFT):
        p = Paragraph(text, callout); _, h = p.wrap(CW-28, 1000)
        th = 16 if title else 0
        c.setFillColor(fill); c.setStrokeColor(LINE); c.setLineWidth(0.8)
        c.roundRect(M, y-h-th-22, CW, h+th+22, 8, fill=1, stroke=1)
        if title:
            c.setFont("SansB",9); c.setFillColor(PURPLE); c.drawString(M+14, y-20, title.upper())
        p.drawOn(c, M+14, y-11-th-h)
        return y-h-th-22

    def lines(y_top, y_bottom, gap=24):
        c.setStrokeColor(LINE); c.setLineWidth(0.6); y = y_top
        while y > y_bottom: c.line(M, y, W-M, y); y -= gap

    def fmtdate(d): return d.strftime("%A, %B ") + str(d.day) + d.strftime(", %Y")
    def fmttime(d): return d.strftime("%I:%M %p").lstrip("0") + " " + TZLABEL
    def ctime(d): return d.strftime("%I:%M").lstrip("0") + ("a" if d.hour < 12 else "p")
    def short(d): return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")

    def numbered(items, y, cont_title=None, floor=70):
        for i, t in enumerate(items, 1):
            p = Paragraph(t, body); _, h = p.wrap(CW-28, 1000)
            if y - h < floor:
                newpage(); y = H-90
            c.setFont("SansB", 10.5); c.setFillColor(PURPLE); c.drawString(M, y-11, f"{i}.")
            p.drawOn(c, M+22, y-h); y -= h + 5
        return y

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle("Your Moon Cycles Planner"); c.setAuthor("Sage Reality 11")

    # ---------- COVER ----------
    newpage()
    c.setFillColor(SOFT); c.rect(24,24,W-48,H-48,fill=1,stroke=0)
    c.setStrokeColor(PURPLE); c.setLineWidth(1); c.rect(24,24,W-48,H-48,fill=0,stroke=1)
    for i, el in enumerate([0, 45, 90, 135, 180, 225, 270, 315, 355]):
        phase(W/2 + (i-4)*52, H-190, 16, el if el else 0.01)
    eyebrow("Sage Reality 11", H-280, center=True)
    c.setFont("Serif", 50); c.setFillColor(DEEP)
    c.drawCentredString(W/2, H-345, "Your Moon Cycles"); c.drawCentredString(W/2, H-400, "Planner")
    c.setFont("SerifM", 18); c.setFillColor(PURPLE)
    c.drawCentredString(W/2, H-440, "Twelve months of intention and release,")
    c.drawCentredString(W/2, H-462, "written for your birth chart")
    c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(W/2-60, H-500, W/2+60, H-500)
    c.setFont("Sans", 11); c.setFillColor(INK)
    c.drawCentredString(W/2, H-530, f"Prepared for {NAME}")
    c.drawCentredString(W/2, H-550, f"{START} to {END}")
    c.setFont("Sans", 9); c.setFillColor(MUTED); c.drawCentredString(W/2, 70, "sagereality11.com")

    # ---------- CONTENTS ----------

    NAV_BEFORE = [("Welcome", "welcome"), ("Using Your Planner", "using"), ("Your Moon Rhythm and Houses", "rhythm"), ("The Eight Phases of the Moon", "phases"), ("Your Year at a Glance", "glance")] + ([("Your Eclipse Seasons", "eclipses")] if any(e["eclipse"] for e in EV) else [])

    NAV_AFTER = [("Looking Back on Your Year", "lookback"), ("Continue Your Journey", "journey")]

    newpage("contents")

    nav.contents_page(c, link, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF, _pm or {}, M, W, H)


    # ---------- WELCOME ----------
    newpage("welcome")
    eyebrow("A letter before you begin", H-80)
    heading("Welcome to Your Moon Cycles Planner", H-112)
    letter_text = [
     f"Hey {NAME},",
     "Every month the Moon moves through a full cycle, from the dark New Moon to the bright Full Moon and back again. Each phase has its own energy. There is a time to plant, a time to take action, a time to celebrate, and a time to let go and rest.",
     "But here is what most moon calendars leave out. Every New Moon and Full Moon lands in a different part of your birth chart. The same New Moon that asks one person to focus on money might be asking you to rest, or to fall in love with your creativity again. This planner was built from your birth chart, so every page shows where each moon lands for you, which part of your life it is lighting up, and when it touches a planet or point in your own chart.",
     "You do not need to know astrology to use it. You only need to show up, read your page, and write.",
     f"Your planner begins in {START} and runs for twelve full months, through {END}. Every time is shown for the location you entered.",
     "I hope this becomes a place you return to. A small ritual that helps you notice your own rhythm.... and trust it.",
    ]
    y = H-140
    for t in letter_text:
        y = para(t, ParagraphStyle("l", parent=body, fontSize=11.5, leading=18), M, y) - 12
    c.setFont("SerifM", 17); c.setFillColor(DEEP)
    c.drawString(M, y-14, "With Love & Light,"); c.drawString(M, y-36, "Tiff")

    # ---------- USING YOUR PLANNER ----------
    newpage("using")
    eyebrow("Print it or go digital", H-80)
    heading("Using Your Planner", H-112)
    y = para("Your planner is a PDF, so you can print it and write by hand, or use it on a tablet with a digital pen. It also has clickable links: tap a moon on your Year at a Glance page or your monthly calendar to jump straight to that moon's pages.", body, M, H-130) - 14
    y0 = y + 4
    y = box(None, "<b>How to Use Your Planner</b>, with step-by-step pictures:  <font color='#5B2A86'><b>sagereality11.com/planner-guide</b></font>", y0, LILAC)
    c.linkURL("https://sagereality11.com/planner-guide/", (M, y, W-M, y0), relative=0)
    y -= 12
    c.setFont("Serif", 19); c.setFillColor(DEEP); c.drawString(M, y-4, "To print your planner"); y -= 14
    y = numbered(APP_PRINT, y) - 10
    c.setFont("Serif", 19); c.setFillColor(DEEP); c.drawString(M, y-4, "To use it on an iPad with GoodNotes"); y -= 14
    y = numbered(APP_IPAD, y, floor=54) - 10
    if y < 110: newpage(); y = H-80
    c.setFont("Serif", 19); c.setFillColor(DEEP); c.drawString(M, y-4, "Other tablets and computers"); y -= 14
    y = numbered(APP_OTHER, y, floor=54)


    # ---------- MOON RHYTHM + HOUSES ----------
    newpage("rhythm")
    eyebrow("How this planner works", H-80)
    heading("Your Moon Rhythm", H-112)
    y = para("Each month starts with a calendar showing the Moon's phase every day and which of your houses the Moon is moving through. Then each New Moon and Full Moon gets two pages. The first tells you where the moon lands in your chart and what it is asking of you. The second is yours, with prompts and space to write.", body, M, H-130) - 14
    moon(M+14, y-14, 11, "New Moon")
    para("<b>New Moon pages</b> are for intentions. Plant one or two clear seeds rather than a long wish list. Intentions are strongest when set within about two days after the New Moon.", body, M+38, y)
    y -= 60
    moon(M+14, y-14, 11, "Full Moon")
    para("<b>Full Moon pages</b> are for release and reflection. Look at what has grown since the New Moon, notice what feels heavy, and let it go.", body, M+38, y)
    y -= 58
    heading("Your Twelve Houses", y, 22); y -= 14
    y = para("Your birth chart is divided into twelve houses, and each one holds a different area of your life. When the Moon moves through a house, that area of life is where you will feel it most.", body, M, y) - 10
    for h in range(1,13):
        yy = y - ((h-1)%6)*20; xx = M + (0 if h<=6 else CW/2)
        c.setFillColor(PURPLE); c.setFont("SansB",10); c.drawString(xx, yy-12, f"{ORD[h]} house")
        c.setFillColor(INK); c.setFont("Sans",9.5); c.drawString(xx+62, yy-12, HOUSE_KEY[h][0].upper()+HOUSE_KEY[h][1:])
    y -= 6*20 + 16
    box("About the calculations", "Your planner uses Placidus houses calculated from your birth date, time and city. A moon is marked as landing on one of your natal planets or points when it falls within 3 degrees, which is the orb I consider the epicenter. You may feel a moon at a wider orb too, just not as strongly. I use the True Node. All times are shown in " + TZLABEL + ".", y)

    # ---------- EIGHT PHASES ----------
    newpage("phases")
    eyebrow("The full cycle", H-80)
    heading("The Eight Phases of the Moon", H-112)
    y = para("The New Moon and Full Moon are the two big turning points, but the Moon is always somewhere in its cycle. Each phase carries its own energy, and you will see all eight on your monthly calendars.", body, M, H-130) - 14
    for i, (name, key, text) in enumerate(PHASES):
        el = i*45 if i else 0.01
        phase(M+16, y-16, 14, el)
        c.setFont("Serif", 16); c.setFillColor(DEEP); c.drawString(M+44, y-12, name)
        pill(key, M+44 + c.stringWidth(name, "Serif", 16) + 10, y-12, LILAC, DEEP, 8)
        y = para(text, ParagraphStyle("ph", parent=body, fontSize=9.8, leading=13.8), M+44, y-18, CW-44) - 13

    # ---------- YEAR AT A GLANCE ----------
    newpage("glance")
    state["links"] = True
    eyebrow(f"{START} to {END}", H-80)
    heading("Your Year at a Glance", H-112)
    para("Tap any row to jump to that moon's pages.", small, M, H-120)
    y = H-148
    cols = [M, M+92, M+170, M+272, M+340]
    c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
    for x,t in zip(cols, ["DATE","MOON","SIGN","YOUR HOUSE","WORTH NOTING"]): c.drawString(x, y, t)
    y -= 8; c.setStrokeColor(PURPLE); c.setLineWidth(0.8); c.line(M, y, W-M, y)
    seen = {}
    for e in EV:
        key = (e["kind"], e["sign"], e["house"]); e["full_circle"] = seen.get(key); seen.setdefault(key, e)
    for i,e in enumerate(EV):
        y -= 21
        if i % 2 == 0:
            c.setFillColor(SOFT); c.rect(M, y-6, CW, 21, fill=1, stroke=0)
        d = e["dtobj"]
        c.setFillColor(INK); c.setFont("Sans", 9.5); c.drawString(cols[0], y, short(d))
        moon(cols[1]+5, y+3, 4.5, e["kind"])
        c.setFillColor(INK); c.drawString(cols[1]+16, y, e["kind"])
        c.drawString(cols[2], y, e["deg"]); c.drawString(cols[3], y, ORD[e["house"]])
        notes = ([e["eclipse"]] if e["eclipse"] else []) + [f"on your {k}" for k,_,_ in e["contacts"]] + (["full circle moon"] if e["full_circle"] else [])
        c.setFont("SansI", 8.5); c.setFillColor(PURPLE); c.drawString(cols[4], y, ", ".join(notes)[:58])
        link(e["id"], M, y-6, W-M, y+15)

    PAIRS = {"Ascendant":"Asc","Descendant":"Asc","Midheaven":"MC","IC":"MC","North Node":"NN"}
    def eclipse_page(e):
        d = e["dtobj"]; h = e["house"]; oh = e["opp_house"]; solar = e["kind"] == "New Moon"
        newpage(e["id"]+"e")
        eyebrow("What this eclipse means for you", H-78)
        c.setFont("Serif", 27); c.setFillColor(DEEP); c.drawString(M, H-110, e["eclipse"])
        c.setFont("Sans", 10.5); c.setFillColor(MUTED); c.drawString(M, H-128, f"{fmtdate(d)}  ·  {fmttime(d)}")
        moon(W-M-26, H-100, 24, e["kind"])
        x = pill(e["deg"], M, H-152)
        x = pill(f"Your {ORD[h]} House", x, H-152, LILAC, DEEP)
        pill(f"Axis to your {ORD[oh]} House", x, H-152, SOFT, DEEP)
        y = H-180
        src = ECL_SOLAR_HOUSE if solar else ECL_LUNAR_HOUSE
        c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y, "Where it lands in your chart"); y -= 10
        y = para(src[h]["text"], body, M, y) - 12
        y = para(f"Every eclipse falls on an axis. The other end of this one is in {e['opp_sign']}, in your {ORD[oh]} house of {HOUSE_KEY[oh]}, so what changes in one of these areas of your life often shows up in the other.", body, M, y) - 16
        seen_pairs = set(); shown = 0
        for k, asp, orb in sorted(e["axis"], key=lambda t: (t[2], t[1] != "on")):
            grp = PAIRS.get(k, k)
            if grp in seen_pairs: continue
            seen_pairs.add(grp)
            tight = orb <= 3
            if k in PAIRS: lead = "This eclipse activates "
            else: lead = "This eclipse lands right on " if asp == "on" else "This eclipse falls opposite "
            title = ("Eclipse epicenter: " if tight else "Felt more softly: ") + {"North Node":"your Nodes","Ascendant":"your Ascendant","Descendant":"your Descendant","Midheaven":"your Midheaven","IC":"your IC"}.get(k, "your natal " + k)
            extra = "" if tight else f" At {orb:.0f} degrees it sits outside the tighter orb I consider the epicenter, so you may feel it more gently."
            y = box(title, lead + ECL_POINT[k] + extra, y) - 10; shown += 1
        if not shown:
            y = box("Your natal planets", "This eclipse does not land on any of your natal planets or angles, so its story plays out mainly through the house it falls in and the opposite house across your chart.", y) - 10
        y = box("How to work with it", src[h]["work"] + " Remember that eclipse energy can be felt in the weeks before and after the exact date, and an eclipse story keeps unfolding for months.", y, LILAC)
        if y < 60: print("OVERFLOW eclipse", e["dt"], y)
        if y > 170:
            c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y-30, "What I Am Noticing")
            lines(y-58, 64)

    # ---------- ECLIPSES ----------
    ecl = [e for e in EV if e["eclipse"]]
    if ecl:
        newpage("eclipses")
        eyebrow("The bigger story of your year", H-80)
        heading("Your Eclipse Seasons", H-112)
        solar = [e for e in ecl if e["kind"]=="New Moon"]
        axis_signs = []
        for e in solar:
            if e["sign"] not in axis_signs: axis_signs.append(e["sign"])
        axis_houses = sorted({e["house"] for e in solar})
        y = para("Eclipses come in seasons, about twice a year, and they act like turning points in your story. An eclipse story usually unfolds over 12 to 18 months along one axis of the zodiac before it moves on to the next, so what begins at one eclipse often develops at the next ones on the same axis.", body, M, H-130) - 12
        if len(axis_signs) >= 2:
            hs = " and ".join(ORD[h] for h in axis_houses)
            y = box("Your eclipse axis", f"This year the solar eclipses fall in {axis_signs[0]} and {axis_signs[1]}, which in your chart is your {hs} house axis. That means the bigger changes of your year are moving through {HOUSE_KEY[axis_houses[0]]}, and {HOUSE_KEY[axis_houses[1]]}. Notice what begins, ends or shifts in these areas of your life over the coming months.", y) - 18
        for e in ecl:
            d = e["dtobj"]
            moon(M+12, y-6, 10, e["kind"])
            c.setFont("Serif", 16); c.setFillColor(DEEP); c.drawString(M+34, y-11, e["eclipse"])
            c.setFont("Sans", 9.5); c.setFillColor(MUTED)
            c.drawString(M+34, y-27, f"{fmtdate(d)}  ·  {e['deg']}  ·  your {ORD[e['house']]} house")
            link(e["id"]+"e", M, y-32, W-M, y+6)
            y -= 50
        para("Tap any eclipse to read what it means for you. Many astrologers suggest observing eclipses more than actively manifesting on them. Use your eclipse pages to notice, journal and release, and save your biggest intentions for the regular New Moons that follow.", small, M, y-4)
        for e in ecl: eclipse_page(e)

    # ---------- CALENDAR ----------
    def calendar_page(yr, mo):
        cal_id = f"cal{yr}{mo:02d}"; state["cal"] = cal_id
        newpage(cal_id)
        eyebrow("Your Moon Calendar", H-80)
        heading(date(yr,mo,1).strftime("%B %Y"), H-112)
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(yr, mo)
        cw = CW/7; rh = 58 if len(weeks) == 6 else 66
        top = H-135
        c.setFont("SansB", 8.5); c.setFillColor(PURPLE)
        for i, dn in enumerate(["SUN","MON","TUE","WED","THU","FRI","SAT"]):
            c.drawCentredString(M + i*cw + cw/2, top, dn)
        top -= 8
        marks = {}
        for e in EV + QU:
            marks.setdefault(e["dtobj"].date(), []).append(e)
        for r, wk in enumerate(weeks):
            for i, d in enumerate(wk):
                x = M + i*cw; yb = top - (r+1)*rh
                inmonth = d.month == mo
                inrange = START_D <= d <= END_D
                ev = marks.get(d, [])
                fill = LILAC if (ev and inrange and inmonth) else (white if (inmonth and inrange) else SOFT)
                c.setFillColor(fill); c.setStrokeColor(LINE); c.setLineWidth(0.6)
                c.rect(x, yb, cw, rh, fill=1, stroke=1)
                if not inmonth: continue
                c.setFont("SansB" if inrange else "Sans", 9); c.setFillColor(INK if inrange else GREY)
                c.drawString(x+5, yb+rh-12, str(d.day))
                if not inrange: continue
                dd = DAYS[d.isoformat()]
                phase(x+cw-14, yb+rh-14, 8, dd["elong"])
                c.setFont("Sans", 6.8); c.setFillColor(MUTED)
                sg, hs = (ev[0]["sign"], ev[0]["house"]) if ev else (dd["sign"], dd["house"])
                c.drawString(x+5, yb+17 if ev else yb+7, f"{sg} · {ORD[hs]}")
                if ev:
                    e = ev[0]
                    lab = {"New Moon":"New","Full Moon":"Full","First Quarter":"1st Qtr","Last Quarter":"Last Qtr"}[e["kind"]]
                    if e.get("eclipse"): lab = "Eclipse"
                    c.setFont("SansB", 7.2); c.setFillColor(PURPLE)
                    c.drawString(x+5, yb+6, f"{lab} {ctime(e['dtobj'])}")
                    if "id" in e: link(e["id"], x, yb, x+cw, yb+rh)
        y = top - len(weeks)*rh - 13
        c.setFont("SansI", 7.5); c.setFillColor(MUTED)
        c.drawString(M, y, "Each day shows the Moon's sign and your house at noon, or at the exact moment on a New, Full or Quarter Moon day.")
        c.drawString(M, y-10, "Tap a highlighted New or Full Moon to open its pages.")
        y -= 8
        y -= 24
        c.setFont("Serif", 17); c.setFillColor(DEEP); c.drawString(M, y, "This Month's Moons"); y -= 8
        for e in sorted([e for e in EV+QU if e["dtobj"].year==yr and e["dtobj"].month==mo and START_D <= e["dtobj"].date() <= END_D], key=lambda e: e["dt"]):
            d = e["dtobj"]; y -= 18
            moon(M+7, y+3, 6, e["kind"])
            c.setFont("SansB", 9.5); c.setFillColor(DEEP); c.drawString(M+20, y, e.get("eclipse") or e["kind"])
            c.setFont("Sans", 9.5); c.setFillColor(INK)
            c.drawString(M+150, y, f"{d.strftime('%a, %b')} {d.day}  ·  {ctime(d)}  ·  {e['deg']}  ·  your {ORD[e['house']]} house")
            if "id" in e:
                link(e["id"], M, y-4, W-M, y+12)
            else:
                y -= 13; c.setFont("SansI", 8.5); c.setFillColor(PURPLE)
                c.drawString(M+20, y, QUARTER_PROMPT[e["kind"]])

    # ---------- LUNATION PAGES ----------
    def lunation(e):
        d = e["dtobj"]; kind = e["kind"]; h = e["house"]
        newpage(e["id"])
        eyebrow(kind, H-78)
        c.setFont("Serif", 27); c.setFillColor(DEEP); c.drawString(M, H-110, fmtdate(d))
        c.setFont("Sans", 10.5); c.setFillColor(MUTED); c.drawString(M, H-128, fmttime(d))
        moon(W-M-26, H-100, 24, kind)
        x = pill(e["deg"], M, H-152)
        x = pill(f"Your {ORD[h]} House", x, H-152, LILAC, DEEP)
        if e["eclipse"]: pill(e["eclipse"], x, H-152, DEEP)
        y = H-180
        c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y, "Where it lands in your chart"); y -= 10
        src = NEW if kind=="New Moon" else FULL
        t = src[h]["text"]
        if kind == "Full Moon" and e["sun_house"] != h:
            t += f" With the Sun across the sky in your {ORD[e['sun_house']]} house, this Full Moon asks you to balance {HOUSE_KEY[h]} with {HOUSE_KEY[e['sun_house']]}."
        y = para(t, body, M, y) - 12
        y = para(SIGN[e["sign"]]["text"], body, M, y) - 16
        for k,_,_ in e["contacts"]:
            ttl = f"This moon lands on your {k}" if k in ("Ascendant","Midheaven","Descendant","IC") else f"This moon lands on your natal {k}"
            y = box(ttl, CONTACT[k], y) - 10
        if e["eclipse"]:
            t2 = (ECLIPSE_SOLAR if kind=="New Moon" else ECLIPSE_LUNAR) + (PENUMBRAL if "Penumbral" in e["eclipse"] else "")
            y0 = y
            y = box("Eclipse energy", t2 + " <font color='#5B2A86'><b>Tap here to read what this eclipse means for you.</b></font>", y)
            link(e["id"]+"e", M, y, W-M, y0); y -= 10
        if e["full_circle"]:
            y = box("A full circle moon", f"This {kind} returns to the same sign and the same house as the {kind} on {short(e['full_circle']['dtobj'])}, near the start of your planner. Before you write today, read what you wrote that day. Notice what has grown and how much has changed.", y) - 10
        y = box("Try this", src[h]["try_this"], y, LILAC)
        if y < 60: print("OVERFLOW", e["dt"], y)
        if y > 170:
            c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y-30, "Moon Notes")
            lines(y-58, 64)
        newpage()
        eyebrow(f"{kind}  ·  {short(d)}  ·  your {ORD[h]} house", H-78)
        heading("My Intentions" if kind=="New Moon" else "What I Am Releasing", H-110, 27)
        prompts = list(src[h]["prompts"])
        prompts.append(f"Looking back at what I wrote on {short(e['full_circle']['dtobj'])}, what has changed?" if e["full_circle"] else SIGN[e["sign"]]["new" if kind=="New Moon" else "full"])
        top = H-140; seg = (top-64)/len(prompts)
        for i,pr in enumerate(prompts):
            yy = top - i*seg
            p = Paragraph(pr, ParagraphStyle("p", fontName="SerifM", fontSize=15, leading=18, textColor=PURPLE))
            _, ph = p.wrap(CW, 200); p.drawOn(c, M, yy-ph)
            lines(yy-ph-24, yy-seg+14)

    yr, mo = START_D.year, START_D.month
    while date(yr, mo, 1) <= END_D:
        calendar_page(yr, mo)
        for e in EV:
            if e["dtobj"].year == yr and e["dtobj"].month == mo: lunation(e)
        mo += 1
        if mo == 13: yr, mo = yr+1, 1
    state["cal"] = None

    # ---------- CLOSING ----------
    newpage("lookback")
    eyebrow("As your twelve months close", H-80)
    heading("Looking Back on Your Year", H-112)
    prs = ["Which intention grew more than I expected?", "What did I release that I no longer miss?", "What did the Moon teach me about my own rhythm?"]
    top = H-140; seg = (top-64)/3
    for i,pr in enumerate(prs):
        yy = top - i*seg
        c.setFillColor(PURPLE); c.setFont("SerifM", 15); c.drawString(M, yy-15, pr)
        lines(yy-42, yy-seg+14)

    newpage("journey")
    eyebrow("Keep going", H-80)
    heading("Continue Your Journey", H-112)
    y = H-130
    for t, dsc, url in [
     ("What's Happening to Me Right Now? Your Personal Timing Reading", "Your moon cycles show the monthly rhythm. This reading shows the bigger timing of your life right now: the transits, eclipses and progressions shaping this chapter.", "sagereality11.com/shop/personal-timing-reading"),
     ("Your Transits Planner", "Twelve months of the transits touching your chart, with your big transits explained and monthly calendars.", "sagereality11.com/shop/transits-planner"),
     ("Soul Circle", "Monthly goddess guides, member readings and tools for your journey.", "sagereality11.com/soul-circle"),
    ]:
        y0 = y
        y = box(None, f"<font name='Serif' size='15' color='#3B1D5C'>{t}</font><br/>{dsc}<br/><font color='#5B2A86'><b>{url}</b></font>", y) - 12
        c.linkURL("https://" + url + "/", (M, y+12, W-M, y0), relative=0)
    y -= 14
    c.setFont("Serif", 18); c.setFillColor(DEEP); c.drawString(M, y, "A note from me"); y -= 10
    y = para("This planner is based on my own research, methodology and intuitive abilities. It is meant for reflection and personal growth, and it is not medical, legal or financial advice. You are always the one who decides what is right for your life.", small, M, y) - 8
    y = para("Because this planner is a personalized digital download, all sales are final.", small, M, y) - 20
    c.setFont("SerifM", 17); c.setFillColor(DEEP); c.drawString(M, y-8, "With Love & Light,"); c.drawString(M, y-30, "Tiff")

    nav.outline(c, NAV_BEFORE, NAV_AFTER, NAV_MONTHS, KEYF)
    c.save()
    if _pm is None:
        return render(data_original, NAME, TZLABEL, _pm=pm)
    return buf.getvalue()

