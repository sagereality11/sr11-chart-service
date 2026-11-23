"""Build Your Monthly Money Forecast (same reading structure as the Wealth Story, so the same renderer works)."""
from __future__ import annotations

from . import money_month_text as T
from . import wealth as W
from .wealth_reading import Writer, explain_terms

SHOP = "https://sagereality11.com/shop/"
OFFERS = {
    "wealth": ("What Is My Birth Chart Saying About Money? Your Wealth Story Reading", SHOP + "wealth-story-reading/",
               "The full map behind this forecast, how you create value, what can block the flow, your career path, and the thresholds of the next twelve months."),
    "timing": ("What's Happening to Me Right Now? Your Personal Timing Reading", SHOP + "personal-timing-reading/",
               "Every major transit moving through your chart right now, not only the money ones, and how to move through it."),
    "manifest": ("When Are My Best Days to Manifest? Your Personal Manifestation Map", SHOP + "personal-manifestation-map/",
                 "Twelve months of your personal power days and pause days, so you know when to launch or ask."),
    "moon": ("What Is the Moon Asking of You This Month? Your Moon Calendar", SHOP + "moon-calendar/",
             "The inner side of the month, every Moon phase through your houses, with journal pages."),
}


def _date(d):
    return f"{W.MONTHS[d.month - 1]} {d.day}"


def _join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def build_money_month(a: dict, f: dict, name: str, birth: dict, first_time: bool = True) -> dict:
    P = a["planets"]
    r2, rc, rf = f["r2"], f["rc"], f["rf"]
    untimed = f["untimed"]
    month = f"{f['month_name']} {f['year']}"
    w = Writer()

    def nm(k):
        return {"asc": "Ascendant", "mc": "Midheaven", "fortune": "Part of Fortune", "assets": "Lot of Assets"}.get(k, W.NAME.get(k, k))

    def the(k):
        return ("the " if k in ("sun", "moon") else "") + W.NAME[k]

    def The(k):
        x = the(k)
        return x[0].upper() + x[1:]

    rank = {k: i for i, k in enumerate([r2, rc, "fortune", "assets", "mc", "venus", "jupiter"])}

    role_said = set()

    def t(k):
        """'Jupiter, the ruler of your career' the first time, plain name after."""
        base = nm(k)
        if k in role_said:
            return base
        role_said.add(k)
        if k == r2 and k == rc:
            return f"{base}, which rules both your income and your career"
        if k == r2:
            return f"{base}, the planet that rules your income"
        if k == rc:
            return f"{base}, the ruler of your career"
        if k == "fortune":
            return f"{base}, where opportunity tends to find you"
        if k == "assets":
            return f"{base}, what you build and keep"
        if k == "mc":
            return f"{base}, your public reputation"
        if k == rf:
            return f"{base}, the ruler of your Part of Fortune"
        return base

    # ------------------------------------------------------------------ opening
    w.section("begins", "Your Money Month Begins")
    w.sections[-1]["greeting"] = f"Hey {name}," if name else "Hey there,"
    w.para(T.INTRO.format(month=month))
    if untimed:
        w.para(T.INTRO_UNTIMED)
    mo = f["monthly"]
    lord = mo["lord"]
    lp = P[lord]
    role = "both" if lord == r2 and lord == rc else "second" if lord == r2 else "career" if lord == rc else None
    w.para(T.MONTH_LORD_INTRO.format(ord=T.ORD[mo["house"]], hof=T.HOUSE_OF[mo["house"]], lord=the(lord)),
           T.LORD_FEEL[lord],
           T.LORD_NATAL.format(lord=the(lord), sign=lp["sign"], ord=T.ORD[lp["house"]], topic=T.SHORT_TOPIC[lp["house"]]),
           T.LORD_ROLE.get(role, ""))
    if role:
        role_said.add(lord)

    # ------------------------------------------------------------------ sort the month
    open_cur, watch_cur = [], []
    for c in f["currents"]:
        key = (c["planet"], c["class"])
        good = key in {("jupiter", "conj"), ("jupiter", "soft"), ("saturn", "soft"), ("uranus", "conj")}
        (open_cur if good else watch_cur).append(c)
    days = [e for e in f["events"] if e["kind"] == "day"]
    by_pl = {}
    for e in days:
        cls = "conj" if e["aspect"] == 0 else "soft" if e["aspect"] in (60, 120) else "opp" if (e["planet"] == "venus" and e["aspect"] == 180) else "hard"
        by_pl.setdefault((e["planet"], cls), []).append(e)

    # ------------------------------------------------------------------ at a glance
    w.section("glance", "Your Month at a Glance")
    w.para(T.GLANCE_INTRO)
    glance = []
    prio = {"lunation": 0, "station": 1, "mars": 2, "sun": 3, "venus": 4, "mercury": 5, "pmoon": 6, "midpoint": 7}
    for e in f["events"]:
        if e["kind"] == "day":
            if e["planet"] == "venus" and e["target"] not in (r2, rc, "fortune", "assets", "mc", "venus"):
                continue
            label = {"venus": T.VENUS_DAY, "mars": T.MARS_DAY}.get(e["planet"])
            txt = (label[e["aspect"]] if label else (T.SUN_DAY if e["planet"] == "sun" else T.MERCURY_DAY)).format(t=nm(e["target"]))
            glance.append((prio[e["planet"]], e["date"], txt))
        elif e["kind"] == "lunation" or e.get("kind") in ("new", "full"):
            pass
        elif e["kind"] == "station":
            glance.append((1, e["date"], f"Mercury turns {e['kind'] if e['kind'] != 'station' else ''}".strip()))
    for L in f["lunations"]:
        glance.append((0, L["date"], f"{'Eclipse ' if L['eclipse'] else ''}{'New' if L['kind'] == 'new' else 'Full'} Moon in {L['sign']}, your {T.ORD[L['house']]} house of {T.HOUSE_OF[L['house']]}"))
    for s in f["stations"]:
        glance.append((1, s["date"], f"Mercury turns {s['kind']} in {s['sign']}"))
    for x in f["pmoon"]["aspects"]:
        if x["in_month"]:
            glance.append((6, x["date"], f"Your progressed Moon {T.ASPECT_WORD[x['aspect']] if x['aspect'] else 'meets'} your natal {nm(x['target'])}".replace("sextile your", "sextiles your").replace("trine your", "trines your").replace("square your", "squares your").replace("opposite your", "opposes your")))
    for m in f["midpoints"]:
        glance.append((7, m["date"], f"{W.NAME[m['planet']]} activates your {nm(m['pair'][0])} and {nm(m['pair'][1])} midpoint"))
    glance = [g for g in glance if g[2]]
    keep = sorted(sorted(glance, key=lambda g: (g[0], g[1]))[:8], key=lambda g: g[1])
    merged = {}
    for _, d, txt in keep:
        merged.setdefault(d, []).append(txt)
    for d, txts in merged.items():
        line = txts[0] + "".join(", and " + x[0].lower() + x[1:] if x.startswith(("Venus", "Mars", "Mercury", "The Sun")) is False else ", and " + x for x in txts[1:])
        w.para(f"{_date(d)}. {line}.")

    # ------------------------------------------------------------------ where the money planets move
    mv = f["moving"]
    w.section("moving", "Where the Money Planets Are Moving")
    w.para(T.MOVING_INTRO)
    w.para(T.SUN_HOUSE[mv["sun"]["house"]])
    w.para(T.VENUS_HOUSE[mv["venus"]["house"]])
    w.para(T.MARS_HOUSE[mv["mars"]["house"]])
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "Look at where Venus and Mars are in your chart this month and give each one an action. One thing to receive, and one thing to push forward.",
                                  "prompts": [T.PROMPT_MOVING.format(vord=T.ORD[mv["venus"]["house"]], mord=T.ORD[mv["mars"]["house"]])]}

    # ------------------------------------------------------------------ openings
    w.section("open", "Openings This Month")
    w.para(T.OPEN_INTRO)
    opened = False
    for c in open_cur[:3]:
        w.para(T.CURRENT[(c["planet"], c["class"])].format(t=t(c["target"])),
               T.EXACT_ON.format(date=_date(c["exact"])).strip() if c["exact"] else "")
        opened = True
    top_open = open_cur[0]["planet"] if open_cur else None
    for (pl, cls) in (("venus", "conj"), ("venus", "soft"), ("venus", "opp"), ("sun", "conj"), ("mercury", "conj"), ("mars", "conj")):
        evs = by_pl.get((pl, cls), [])
        if not evs:
            continue
        evs = sorted(sorted(evs, key=lambda e: rank.get(e["target"], 9))[:3], key=lambda e: e["date"])
        verb = {("venus", "conj"): "crosses", ("venus", "soft"): "makes easy angles to", ("venus", "opp"): "opposes",
                ("sun", "conj"): "crosses", ("mercury", "conj"): "crosses", ("mars", "conj"): "crosses"}[(pl, cls)]
        items = _join(f"your {nm(e['target'])} on {_date(e['date'])}" for e in evs)
        mean = {"venus": T.VENUS_MEAN.get(cls, T.VENUS_MEAN["soft"]), "sun": T.SUN_MEAN, "mercury": T.MERCURY_MEAN, "mars": T.MARS_MEAN["conj"]}[pl]
        w.para(f"{The(pl)} {verb} {items}.", mean)
        opened = True
        top_open = top_open or pl
    if not opened:
        w.para(T.NO_OPEN)
    w.sections[-1]["practice"] = {"label": "Try This", "try": T.TRY_OPEN.get(top_open or "quiet", T.TRY_OPEN["quiet"]),
                                  "prompts": [T.PROMPT_OPEN]}

    # ------------------------------------------------------------------ watch
    w.section("watch", "What to Watch")
    w.para(T.WATCH_INTRO)
    watched = False
    for c in watch_cur[:3]:
        w.para(T.CURRENT[(c["planet"], c["class"])].format(t=t(c["target"])),
               T.EXACT_ON.format(date=_date(c["exact"])).strip() if c["exact"] else "")
        watched = True
    top_watch = watch_cur[0]["planet"] if watch_cur else None
    evs = sorted(by_pl.get(("mars", "hard"), []), key=lambda e: e["date"])[:3]
    if evs:
        w.para(f"Mars squares or opposes {_join(f'your {nm(e['target'])} on {_date(e['date'])}' for e in evs)}.", T.MARS_MEAN["hard"])
        watched = True
        top_watch = top_watch or "mars"
    if f["mercury_retro"]:
        mm = f["mercury_mid"]
        w.para(T.MERC_RX.format(ord=T.ORD[mm["house"]], topic=T.SHORT_TOPIC[mm["house"]]),
               " ".join(T.MERC_STATION[s["kind"]].format(date=_date(s["date"]), sign=s["sign"], ord=T.ORD[s["house"]]) for s in f["stations"]))
        watched = True
        top_watch = top_watch or "mercury"
    if not watched:
        w.para(T.NO_WATCH)
    w.sections[-1]["practice"] = {"label": "Try This", "try": T.TRY_WATCH.get(top_watch or "none", T.TRY_WATCH["none"]),
                                  "prompts": [T.PROMPT_WATCH]}

    # ------------------------------------------------------------------ lunations
    w.section("moons", "The New Moon and Full Moon in Your Houses")
    w.para(T.LUNATION_INTRO)
    prompts = []
    for L in f["lunations"]:
        hit = L["hits"][0] if L["hits"] else None
        w.para(T.LUNATION_LINE[L["kind"]].format(date=_date(L["date"]), deg=L["deg"], sign=L["sign"], ord=T.ORD[L["house"]]),
               (T.NEW_HOUSE if L["kind"] == "new" else T.FULL_HOUSE)[L["house"]],
               T.LUNATION_HIT[hit["aspect"]].format(t=t(hit["target"])) if hit else "",
               T.ECLIPSE_NOTE if L["eclipse"] else "")
        prompts.append((T.PROMPT_NEW if L["kind"] == "new" else T.PROMPT_FULL).format(ord=T.ORD[L["house"]], topic=T.SHORT_TOPIC[L["house"]]))
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "On the New Moon, write one money intention in the present tense. On the Full Moon, read it again and write down what changed.",
                                  "prompts": prompts[:2]}

    # ------------------------------------------------------------------ progressed Moon
    pm = f["pmoon"]
    w.section("pmoon", "Your Progressed Moon This Month")
    w.para(T.PMOON_INTRO)
    w.para(T.PMOON_SIGN[pm["sign"]], T.PMOON_HOUSE.format(ord=T.ORD[pm["house"]], topic=T.SHORT_TOPIC[pm["house"]]),
           T.PMOON_SIGN_CHANGE.format(sign=pm["sign_change"]) if pm["sign_change"] else "",
           T.PMOON_HOUSE_CHANGE.format(ord=T.ORD[pm["house_change"]], topic=T.SHORT_TOPIC[pm["house_change"]]) if pm["house_change"] else "")
    for x in [x for x in pm["aspects"] if x["in_month"]][:2]:
        cls = "conj" if x["aspect"] == 0 else "soft" if x["aspect"] in (60, 120) else "hard"
        w.para(T.PMOON_ASPECT[x["aspect"]].format(t=t(x["target"]), date=_date(x["date"])), T.PMOON_ASPECT_MEAN[cls])
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "Once this month, check in with how you feel about money before you check the numbers. Write one sentence about the feeling, then one about the facts.",
                                  "prompts": [T.PROMPT_PMOON.format(sign=pm["sign"], ord=T.ORD[pm["house"]])]}

    # ------------------------------------------------------------------ bigger current
    sa, sp, mids = f["solar_arcs"], f["slow_prog"], f["midpoints"]
    if sa or sp or mids:
        w.section("current", "The Bigger Current")
        if sa or sp:
            w.para(T.BIG_INTRO)
        for x in sa[:2]:
            w.para(T.SA_LINE[x["aspect"]].format(p=nm(x["planet"]), t=t(x["target"])), T.SA_MEAN[x["planet"]])
        for x in sp[:1]:
            w.para(T.SLOWPROG_LINE.format(p=nm(x["planet"]), a=T.ASPECT_WORD[x["aspect"]], t=t(x["target"])))
        if mids:
            m = mids[0]
            w.para(T.MIDPOINT_INTRO, T.MIDPOINT_MEAN[m["pair"]], T.MIDPOINT_HIT.format(P=W.NAME[m["planet"]], date=_date(m["date"])))

    # ------------------------------------------------------------------ final thoughts
    w.section("final", "Final Thoughts")
    bits = []
    if open_cur or by_pl.get(("venus", "soft")) or by_pl.get(("venus", "conj")):
        bits.append("The openings this month are real, and they work best when you use them on purpose.")
    if watch_cur:
        c = watch_cur[0]
        bits.append(f"The pressure on your {nm(c['target'])} is asking for a change, not a crisis.")
    bits.append(f"With {the(lord)} guiding the month, let {T.SHORT_TOPIC[mo['house']]} set the pace.")
    w.para(T.FINAL_INTRO, *bits)
    if f["next_new_moon"]:
        n = f["next_new_moon"]
        w.para(T.NEXT_TEASER.format(date=_date(n["date"]), sign=n["sign"], ord=T.ORD[n["house"]], hof=T.HOUSE_OF[n["house"]]))

    # ------------------------------------------------------------------ offers
    w.section("next", "Where to Go From Here")
    w.para(T.OFFERS_INTRO)
    w.sections[-1]["offers"] = [{"title": OFFERS[k][0], "url": OFFERS[k][1], "why": OFFERS[k][2]} for k in ("wealth", "timing", "moon", "manifest")]

    explain_terms(w.sections, skip=("next", "glance"))
    return {"title": "Your Monthly Money Forecast", "subtitle": f"Money and career for {month}", "name": name, "birth": birth,
            "cover_lines": ("Your Monthly", "Money Forecast"), "footer_title": f"Your Monthly Money Forecast  ·  {month}",
            "sections": w.sections, "signoff": T.SIGNOFF, "disclaimer": T.DISCLAIMER}
