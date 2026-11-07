"""Calendar files (.ics) for the planners: one color-coded calendar per planner, all-day events
with a reminder at 9:00 AM on the day. Works with Apple Calendar (iPhone, iPad, Mac), Outlook and
Google Calendar. Per-event colors use the standard COLOR property and CATEGORIES (shown by apps that
support them); the calendar itself carries the planner's color."""

from __future__ import annotations

import datetime as dt
import hashlib

from . import moon_content as MC
from . import money_content as MO
from . import transit_content as TC

ORD = MC.ORD
CAL_COLOR = {"moon": "#5B2A86", "money": "#4E8B5F", "transits": "#3B5BA5"}
CAL_NAME = {"moon": "Moon Cycles", "money": "Money & Business", "transits": "Transits"}

AFFIRMATIONS = [
    "Money flows to me with ease, and I receive it with gratitude.",
    "I am worthy of being paid well for my gifts.",
    "I make clear, confident decisions about my money.",
    "Every dollar I spend and save is in line with what I value.",
    "My income grows as I grow.",
    "I am allowed to rest and still be abundant.",
    "I trust myself to build wealth slowly and steadily.",
    "I release old stories about not having enough.",
    "There is room for my success, and there is room for everyone's.",
    "I charge what my work is worth, and the right people say yes.",
    "Abundance is my natural state, and I return to it today.",
    "I welcome new opportunities that feel aligned with my soul.",
    "I take care of my money, and my money takes care of me.",
    "I am open to receiving from expected and unexpected places.",
    "I give generously without emptying my own cup.",
    "My work makes a difference, and it is rewarded.",
    "I am calm and grounded when I look at my finances.",
    "I choose progress over perfection with my money.",
    "I am building a legacy my future self will thank me for.",
    "Money is a tool I use to create a life I love.",
    "I let go of guilt around wanting more.",
    "My boundaries protect my energy and my income.",
    "I am a good steward of what I have, and more comes to me.",
    "I am ready to be seen for what I offer.",
    "I celebrate every win, big or small.",
    "I trust the timing of my life and my money.",
    "I deserve financial peace.",
    "I attract clients and opportunities who value me.",
    "My bank account reflects the care I put into my work.",
    "I am grateful for what I have and open to what is coming.",
]


def _esc(s: str) -> str:
    return (s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n"))


def _fold(line: str) -> str:
    out, b = [], line.encode("utf-8")
    while len(b) > 74:
        cut = 73
        while cut > 0 and (b[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
            cut -= 1
        while cut > 1 and b[cut - 1:cut] == b"\\":  # don't split an escape like \n or \, (Apple's importer stops there)
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b" " + b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)


class _Cal:
    def __init__(self, product: str, name: str):
        self.product = product
        self.lines = []
        self.stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        title = f"{CAL_NAME[product]} Planner" + (f": {name}" if name and name != "Friend" else "")
        self.head = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Sage Reality 11//Planners//EN", "CALSCALE:GREGORIAN",
                     "METHOD:PUBLISH", f"X-WR-CALNAME:{_esc(title)}", f"NAME:{_esc(title)}",
                     f"X-APPLE-CALENDAR-COLOR:{CAL_COLOR[product]}", f"COLOR:{CAL_COLOR[product]}",
                     "X-WR-CALDESC:" + _esc("Your personal planner dates from Sage Reality 11, written for your birth chart.")]

    def add(self, day: dt.date, summary: str, desc: str, color: str, category: str, reminder: bool = True):
        uid = hashlib.sha1(f"{self.product}|{day}|{summary}".encode()).hexdigest()[:20] + "@sagereality11.com"
        ev = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{self.stamp}",
              f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + dt.timedelta(days=1):%Y%m%d}",
              f"SUMMARY:{_esc(summary)}", f"DESCRIPTION:{_esc(desc + chr(10) + chr(10) + 'Sage Reality 11 · sagereality11.com')}",
              f"CATEGORIES:{_esc(category)}", f"COLOR:{color}", "TRANSP:TRANSPARENT"]
        if reminder:
            ev += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(summary)}", "TRIGGER:PT9H", "END:VALARM"]
        ev.append("END:VEVENT")
        self.lines += ev

    def bytes(self) -> bytes:
        allx = self.head + self.lines + ["END:VCALENDAR"]
        return ("\r\n".join(_fold(l) for l in allx) + "\r\n").encode("utf-8")


def _t(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso)


def _clock(d: dt.datetime, tzl: str) -> str:
    return d.strftime("%I:%M %p").lstrip("0") + " " + tzl


def _first_sentences(text: str, n: int = 2) -> str:
    parts = text.split(". ")
    return ". ".join(parts[:n]).rstrip(".") + "."


def moon(data: dict, name: str, tzl: str) -> bytes:
    cal = _Cal("moon", name)
    for e in data["events"]:
        d = _t(e["dt"])
        src = MC.NEW if e["kind"] == "New Moon" else MC.FULL
        title = f"{e['eclipse'] or e['kind']} in {e['sign']} · your {ORD[e['house']]} house"
        desc = f"{_clock(d, tzl)} · {e['deg']}\n\n" + src[e["house"]]["text"] + "\n\nTry this: " + src[e["house"]]["try_this"]
        for k, _, _ in e.get("contacts", []):
            desc += "\n\n" + MC.CONTACT[k]
        if e["eclipse"]:
            desc += "\n\n" + (MC.ECLIPSE_SOLAR if e["kind"] == "New Moon" else MC.ECLIPSE_LUNAR)
        color = "black" if e["eclipse"] else ("indigo" if e["kind"] == "New Moon" else "orchid")
        cat = "Eclipse" if e["eclipse"] else e["kind"]
        cal.add(d.date(), title, desc, color, cat)
    for q in data["quarters"]:
        d = _t(q["dt"])
        cal.add(d.date(), f"{q['kind']} Moon · check in", f"{_clock(d, tzl)} · {q['deg']}, your {ORD[q['house']]} house\n\n"
                + MC.QUARTER_PROMPT[q["kind"]], "thistle", "Quarter Moon", reminder=False)
    return cal.bytes()


def money(data: dict, name: str, tzl: str) -> bytes:
    cal = _Cal("money", name)
    i = 0
    for dd in data["days"]:
        day = dt.date.fromisoformat(dd["date"])
        aff = AFFIRMATIONS[i % len(AFFIRMATIONS)]
        if dd["status"] == "green":
            i += 1
            why = ", ".join(dd.get("why") or [])
            cal.add(day, "Green day for money moves", f"Affirmation: {aff}\n\nA supportive day to launch, sign, pitch, send invoices, ask "
                    f"for a raise or make a planned purchase." + (f" ({why})" if why else ""), "seagreen", "Green day")
        elif dd["status"] == "caution":
            i += 1
            why = ", ".join(dd.get("why") or [])
            cal.add(day, "Caution day: pause big money decisions", f"Affirmation: {aff}\n\nEnergy is unpredictable today"
                    + (f" ({why})" if why else "") + ". Review and plan instead of committing if you can.", "indianred", "Caution day")
    for e in data["events"]:
        d = _t(e["dt"])
        if e["type"] == "aspect":
            if e["planet"] == "Sun" and e["aspect"] not in ("conjunct", "opposite"):
                continue
            pt = "your Midheaven" if e["point"] == "Midheaven" else f"your natal {e['point']}"
            title = f"{e['planet']} {e['aspect']} {pt}"
            desc = MO.PLANET_ASPECT[(e["planet"], e["flow"])]
            tip = MO.TIPS.get(e["planet"])
        elif e["type"] == "ingress":
            title = f"{e['planet']} enters your {ORD[e['house']]} house"
            desc = MO.INGRESS[e["planet"]].format(h=ORD[e["house"]], k=MO.HOUSE_KEY[e["house"]])
            tip = MO.TIPS.get(e["planet"])
        else:
            title = f"{e['planet']} stations {e['direction']}"
            desc = MO.STATION[(e["planet"], e["direction"])].format(h=ORD[e["house"]], k=MO.HOUSE_KEY[e["house"]])
            tip = MO.TIPS.get(e["planet"])
        if tip:
            desc += f"\n\nFor your personal money: {tip['personal']}\nFor your business: {tip['business']}"
        color = "goldenrod" if e["type"] == "aspect" else ("slategray" if e["type"] == "station" else "darkseagreen")
        cal.add(d.date(), title, desc, color, "Money transit", reminder=e["type"] == "station" or e.get("planet") in ("Jupiter", "Saturn"))
    for l in data["lunations"]:
        if l["house"] not in MO.MONEY_MOON and not l["eclipse"]:
            continue
        d = _t(l["dt"])
        nf = 0 if l["kind"] == "New Moon" else 1
        txt = MO.MONEY_MOON.get(l["house"], MO.OTHER_MOON)[nf]
        cal.add(d.date(), f"Money {l['eclipse'] or l['kind']} · your {ORD[l['house']]} house", f"{_clock(d, tzl)} · {l['deg']}\n\n{txt}",
                "black" if l["eclipse"] else "mediumpurple", "Money moon")
    return cal.bytes()


def transits(data: dict, name: str, tzl: str) -> bytes:
    cal = _Cal("transits", name)
    pname = lambda n: {"Ascendant": "your Ascendant", "Midheaven": "your Midheaven", "North Node": "your North Node"}.get(n, f"your natal {n}")
    for b in data["big"]:
        title = f"{b['planet']} {b['aspect']} {pname(b['point'])}"
        desc = TC.PLANET_V[b["planet"]][0] + " " + TC.POINT[b["point"]] + " " + TC.ASPECT[b["aspect"]]
        sp = TC.SPECIAL.get((b["planet"], b["aspect"], b["point"]))
        if sp:
            desc = sp + " " + desc
        desc += "\n\nHow to work with it: " + TC.WORK_V[b["planet"]][0]
        start, end = dt.date.fromisoformat(data["start"]), dt.date.fromisoformat(data["end"])
        for x in b["exact"]:
            d = _t(x)
            if start <= d.date() <= end:
                cal.add(d.date(), f"Exact today: {title}", desc, "rebeccapurple", "Big transit")
        bs = dt.date.fromisoformat(b["start"][:10])
        if start <= bs <= end and not (b["planet"] == "Jupiter" and b["aspect"] == "sextile"):
            cal.add(bs, f"Begins: {title}", desc, "mediumpurple", "Big transit", reminder=False)
    for f in data["fast"]:
        d = _t(f["dt"])
        phrase = TC.FAST[(f["planet"], f["flow"])]
        cal.add(d.date(), f"{f['planet']} {f['aspect']} {pname(f['point'])}",
                f"{phrase[0].upper() + phrase[1:]} around {TC.FAST_POINT[f['point']]}.", "plum", "Transit", reminder=False)
    for s in data["stations"]:
        d = _t(s["dt"])
        cal.add(d.date(), f"{s['planet']} stations {s['direction']} · your {ORD[s['house']]} house",
                f"{s['deg']}. {TC.STATION_X[s['direction']]}", "slategray", "Retrograde")
    for e in data["eclipses"]:
        d = _t(e["dt"])
        cal.add(d.date(), f"{e['kind']} · your {ORD[e['house']]} house", f"{_clock(d, tzl)} · {e['deg']}. Eclipses are turning points that unfold over months.",
                "black", "Eclipse")
    return cal.bytes()


BUILDERS = {"moon": moon, "money": money, "transits": transits}
