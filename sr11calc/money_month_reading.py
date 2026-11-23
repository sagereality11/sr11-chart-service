"""Build Your Monthly Money Forecast (same reading structure as the Wealth Story, so the same renderer works).

Depth pass (Nov 23):
  * Every activation is scored by how closely it ties to the person's own money points (income ruler,
    career ruler, Midheaven, Part of Fortune, Lot of Assets, eighth and eleventh rulers) and by the
    technique (slow transit, solar arc, progression, lunation, fast day). The score sets how many
    paragraphs it gets.
  * Themes that repeat across techniques (profection, transits, progressed Moon, solar arcs, lunations)
    are found and told as one story instead of being explained again in every section.
  * Each natal point is introduced once, in full, and referred to briefly after that.
  * Natal patterns, this month, and the longer chapter are kept in their own sections.
"""
from __future__ import annotations

import hashlib
import random
from collections import defaultdict

from . import money_month_deep as D
from . import money_month_text as T
from . import wealth as W
from .wealth_reading import Writer, explain_terms
from .wealth_text import HOUSE_TOPIC, ORD

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

CLASSIC = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")
ROLE_WEIGHT = {"both": 8, "second": 5, "career": 4, "mc": 4, "fortune": 3, "assets": 3, "eighth": 2, "eleventh": 2,
               "venus": 2, "jupiter": 2, "sun": 1, "other": 0}
THEME_ORDER = ["income", "career", "freedom", "structure", "growth", "power", "security", "value", "vision", "identity",
               "drive", "voice"]
ARC_VERB = {0: "conjoining", 90: "squaring", 180: "opposing"}
ASPECT_NOUN = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
ADJ = {"uranus": "a disruptive Uranian", "saturn": "a testing Saturnian", "jupiter": "an expansive Jupiterian",
       "neptune": "a dissolving Neptunian", "pluto": "a transforming Plutonian"}


def _date(d):
    return f"{W.MONTHS[d.month - 1]} {d.day}"


def _join(xs):
    xs = [x for x in xs if x]
    if not xs:
        return ""
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + (", and " if len(xs) > 2 else " and ") + xs[-1]


def _cap(s):
    return s[0].upper() + s[1:] if s else s


def build_money_month(a: dict, f: dict, name: str, birth: dict, first_time: bool = True) -> dict:
    P = a["planets"]
    r2, rc, rf = f["r2"], f["rc"], f["rf"]
    rulers, hs = a["rulers"], a["house_sign"]
    r8, r11 = rulers[8], rulers[11]
    untimed = f["untimed"]
    MONTH = f["month_name"]
    month = f"{MONTH} {f['year']}"
    seed = hashlib.md5(f"{name}|{birth.get('date')}|{f['year']}-{f['month']}".encode()).hexdigest()
    rng = random.Random(int(seed, 16))
    w = Writer()
    occ = {h: [p for p in a["occupants"].get(h, []) if p in CLASSIC] for h in range(1, 13)}
    lord = f["monthly"]["lord"]

    # ------------------------------------------------------------------ names and roles
    def nm(k):
        return W.NAME.get(k, k)

    def the(k):
        return ("the " if k in ("sun", "moon") else "") + nm(k)

    def The(k):
        return _cap(the(k))

    def role(k):
        if k == r2 and k == rc:
            return "both"
        if k == r2:
            return "second"
        if k == rc:
            return "career"
        if k in ("mc", "fortune", "assets"):
            return k
        if k == r8:
            return "eighth"
        if k == r11:
            return "eleventh"
        if k in ("venus", "jupiter", "sun"):
            return k
        return "other"

    def weight(k):
        return ROLE_WEIGHT[role(k)] + (2 if k == lord else 0)

    ROLE_TAG = {"both": "which rules both your income and your career", "second": "the planet that rules your income",
                "career": "the ruler of your career", "fortune": "where opportunity tends to find you",
                "assets": "what you build and keep",
                "eighth": "the ruler of your shared resources", "eleventh": "the ruler of your gains"}
    tagged = set()

    def ref(k):
        """'your Jupiter, the ruler of your career' the first time, 'your Jupiter' after."""
        base = f"your {nm(k)}"
        r = role(k)
        if k in tagged or r not in ROLE_TAG:
            return base
        tagged.add(k)
        return f"{base}, {ROLE_TAG[r]}"

    introduced = set()

    def placed(k):
        p = P[k]
        rx = " retrograde" if p.get("retro") and k in CLASSIC else ""
        return f"sits{rx} in {p['sign']} in your {ORD[p['house']]} house"

    def intro_pt(k):
        """Natal description of a point, given once."""
        if k in introduced or k not in P:
            return ""
        introduced.add(k)
        tagged.add(k)
        p = P[k]
        if k == "mc":
            return (f"Your Midheaven is in {p['sign']}, and its traditional ruler, {the(rc)}, {placed(rc)}." if rc in P else "")
        if k in ("fortune", "assets"):
            if k == "fortune":
                return f"Your Part of Fortune {placed(k)}, connecting your material well-being with {T.SHORT_TOPIC[p['house']]}."
            same = P.get("fortune", {}).get("house") == p["house"]
            return f"Your Lot of Assets {placed(k)}{', right beside your Part of Fortune' if same else ''}, tying what you keep to {T.SHORT_TOPIC[p['house']]}."
        r = role(k)
        tag = {"both": ", the planet that rules both your income and your career",
               "second": ", the planet that rules your second house of income",
               "career": ", the ruler of your Midheaven and career",
               "eighth": ", the ruler of your eighth house of shared resources",
               "eleventh": ", the ruler of your eleventh house of gains"}.get(r, "")
        return f"Your natal {nm(k)}{tag}{',' if tag else ''} {placed(k)}."

    def natal_depth(k):
        """Retrograde or dignity note for a natal planet, once."""
        if k not in CLASSIC or ("depth", k) in introduced:
            return ""
        introduced.add(("depth", k))
        p = P[k]
        if p.get("retro") and k in D.RETRO_DEEP:
            return D.RETRO_DEEP[k]
        if p.get("dignity") in D.DIGNITY_DEEP:
            return D.DIGNITY_DEEP[p["dignity"]].format(P=The(k))
        return ""

    def role_deep(k):
        r = role(k)
        if ("role", k) in introduced or r not in D.ROLE_DEEP:
            return ""
        introduced.add(("role", k))
        return D.ROLE_DEEP[r].format(P=the(k))

    weaved = set()

    def weave(h, brief=False):
        """Who lives in this house, told once per house."""
        if h in weaved:
            return ""
        weaved.add(h)
        o = [p for p in occ[h] if p not in ("moon",) or not untimed]
        if o:
            signs = {P[p]["sign"] for p in o}
            names = _join(nm(p) for p in o)
            verb = "occupies" if len(o) == 1 else "occupy"
            sign = f" in {o and P[o[0]]['sign']}" if len(signs) == 1 else ""
            out = f"Your natal {names} {verb} this house{sign}."
            pl = [p for p in o if p in D.NATURE]
            if len(pl) >= 2 and not brief:
                out += f" {D.NATURE[pl[0]]}, while {D.NATURE[pl[1]]}."
            return out
        R = rulers[h]
        if brief or R not in P:
            return ""
        rx = " retrograde" if P[R].get("retro") else ""
        return D.EMPTY_HOUSE.format(ord=ORD[h], sign=hs[h], R=nm(R), rx=rx, rsign=P[R]["sign"], rord=ORD[P[R]["house"]])

    # ------------------------------------------------------------------ gather and score activations
    acts = []
    for c in f["currents"]:
        pl, cls = c["planet"], c["class"]
        base = 4 if (pl in ("uranus", "neptune", "pluto", "saturn") and cls in ("conj", "hard")) else 3 if (pl == "jupiter" and cls == "conj") else 2
        acts.append({"tech": "transit", "planet": pl, "target": c["target"], "aspect": c["aspect"], "cls": cls,
                     "date": c["exact"], "score": base + weight(c["target"])})
    for e in f["events"]:
        if e["kind"] != "day":
            continue
        asp = e["aspect"]
        cls = "conj" if asp == 0 else "soft" if asp in (60, 120) else "hard"
        acts.append({"tech": "day", "planet": e["planet"], "target": e["target"], "aspect": asp, "cls": cls,
                     "date": e["date"], "score": 1 + weight(e["target"])})
    for L in f["lunations"]:
        for hit in L["hits"][:1]:
            acts.append({"tech": "lunation", "planet": L["kind"], "target": hit["target"], "aspect": hit["aspect"],
                         "cls": "conj" if hit["aspect"] == 0 else "hard", "date": L["date"], "score": 2 + weight(hit["target"])})
    for x in f["solar_arcs"]:
        acts.append({"tech": "arc", "planet": x["planet"], "target": x["target"], "aspect": x["aspect"],
                     "cls": "conj" if x["aspect"] == 0 else "hard", "date": None, "score": 3 + weight(x["target"])})
    for x in f["slow_prog"]:
        acts.append({"tech": "prog", "planet": x["planet"], "target": x["target"], "aspect": x["aspect"],
                     "cls": "conj" if x["aspect"] == 0 else "soft" if x["aspect"] in (60, 120) else "hard",
                     "date": None, "score": 3 + weight(x["target"])})

    def depth(act):
        return 3 if act["score"] >= 8 else 2 if act["score"] >= 6 else 1

    # ------------------------------------------------------------------ themes that repeat across techniques
    def target_theme(k):
        r = role(k)
        if r in ("second", "both", "fortune", "assets"):
            return "income"
        if r in ("career", "mc"):
            return "career"
        return D.PLANET_THEME.get(k, "identity")

    src = defaultdict(set)
    lt = "income" if lord == r2 else "career" if lord == rc else D.PLANET_THEME.get(lord, "identity")
    src[lt].add("profection")
    for x in acts:
        if x["tech"] in ("transit", "arc", "prog") or x["score"] >= 5:
            src[target_theme(x["target"])].add(x["tech"])
        if x["tech"] in ("transit", "arc", "prog"):
            mover = "career" if x["planet"] == "mc" else "identity" if x["planet"] == "asc" else D.PLANET_THEME.get(x["planet"])
            if mover:
                src[mover].add(x["tech"])
    pm = f["pmoon"]
    src[D.SIGN_THEME[pm["sign"]]].add("pmoon")
    for L in f["lunations"]:
        if L["hits"]:
            src[D.SIGN_THEME[L["sign"]]].add("lunation")
    top = [t for t in sorted(src, key=lambda t: (-len(src[t]), THEME_ORDER.index(t))) if len(src[t]) >= 2][:3]

    def theme_nouns(ts):
        return _join(D.THEME[t]["noun"] for t in ts)

    # ------------------------------------------------------------------ 1. opening
    w.section("begins", "Your Money Month Begins")
    w.sections[-1]["greeting"] = f"Hey {name}," if name else "Hey there,"
    w.para(rng.choice(D.OPEN_FRAME),
           D.OPEN_THEMES.format(month=month, themes=theme_nouns(top)) if top else D.OPEN_QUIET.format(month=month))
    if untimed:
        w.para(D.OPEN_UNTIMED)

    # natal income
    p2 = P[r2]
    h2 = p2["house"]
    others = [nm(o) for o in occ[h2] if o != r2]
    if not untimed and P.get("fortune", {}).get("house") == h2:
        others.append("Part of Fortune")
    with_ = f" alongside your {_join(others)}" if others else ""
    rx = " retrograde" if p2.get("retro") else ""
    line = (D.INCOME_LINE_SOLAR if untimed else D.INCOME_LINE).format(R=the(r2), sign=p2["sign"], ord=ORD[h2], with_=with_)
    line = line.replace("your natal the ", "your natal ").replace(f"sits in {p2['sign']}", f"sits{rx} in {p2['sign']}")
    w.para(_cap(line), D.INCOME_HOUSE[h2], rng.choice(D.INCOME_ALIGN_V), D.STELLIUM[h2] if len(occ[h2]) >= 3 else "")
    introduced.add(r2)
    tagged.add(r2)
    for h in range(1, 13):
        if len(occ[h]) >= 3 and h == h2:
            weaved.add(h)

    # month lord
    mo = f["monthly"]
    lp = P[lord]
    lord_role = (D.LORD_SAME_R2.format(Lord=The(lord)) if lord == r2 else
                 D.LORD_SAME_RC.format(Lord=The(lord)) if lord == rc else
                 D.LORD_OTHER.format(lord=the(lord), sign=lp["sign"], ord=ORD[lp["house"]], topic=T.SHORT_TOPIC[lp["house"]]))
    w.para(T.MONTH_LORD_INTRO.format(ord=ORD[mo["house"]], hof=T.HOUSE_OF[mo["house"]], lord=the(lord)),
           T.LORD_FEEL[lord], lord_role, D.SIGN_LESSON[lp["sign"]])
    introduced.add(lord)

    # career
    pc = P[rc]
    rxc = " retrograde" if pc.get("retro") else ""
    career_hit = [x for x in acts if x["tech"] == "transit" and x["target"] in (rc, "mc") and x["planet"] in D.CAREER_HIT_THEME]
    w.para((D.CAREER_OPEN_SOLAR if untimed else D.CAREER_OPEN).format(
               mcsign=hs[10], R=the(rc), rx=rxc, sign=pc["sign"], ord=ORD[pc["house"]], hof=T.HOUSE_OF[pc["house"]]),
           "That's the same planet that rules your income, so your reputation and your earnings travel together." if rc == r2 else "",
           D.CAREER_IN[pc["house"]],
           D.CAREER_HIT.format(P=nm(career_hit[0]["planet"]), R=the(rc),
                               theme_line=D.CAREER_HIT_THEME[career_hit[0]["planet"]]) if career_hit else "",
           D.CAREER_CLOSE.format(month=MONTH))
    introduced.update({rc, "mc"})
    tagged.add(rc)

    # ------------------------------------------------------------------ 2. at a glance
    items = []
    for x in acts:
        if x["tech"] == "day" and x["score"] >= 3:
            verb = "crosses" if x["aspect"] == 0 else D.VERB[x["aspect"]]
            items.append((x["score"], x["date"], f"On {_date(x['date'])}, {the(x['planet'])} {verb} your {nm(x['target'])}, "
                                               f"{D.GLANCE_TARGET.get(role(x['target']), D.GLANCE_TARGET['other'])}."))
        elif x["tech"] == "transit" and x["date"]:
            items.append((x["score"], x["date"], f"On {_date(x['date'])}, {nm(x['planet'])}'s {ASPECT_NOUN[x['aspect']]} to "
                                               f"your {nm(x['target'])} is exact."))
    for L in f["lunations"]:
        h = L["h"] if "h" in L else L["house"]
        o = [nm(p) for p in occ[h]]
        where = f", where your natal {_join(o)} already {'lives' if len(o) == 1 else 'live'}" if o else ""
        ecl = "eclipse " if L["eclipse"] else ""
        items.append((9, L["date"], f"The {'New' if L['kind'] == 'new' else 'Full'} Moon {ecl}on {_date(L['date'])} falls in "
                                    f"{L['sign']}, turning attention toward your {ORD[h]} house of {T.HOUSE_OF[h]}{where}."))
    for s in f["stations"]:
        items.append((6, s["date"], f"On {_date(s['date'])}, Mercury turns {s['kind']} in {s['sign']}, so slow down on contracts and double-check the details."))
    for m in f["midpoints"][:1]:
        items.append((4, m["date"], f"On {_date(m['date'])}, {nm(m['planet'])} activates your {nm(m['pair'][0])} and {nm(m['pair'][1])} money midpoint."))
    items = sorted(sorted(items, key=lambda i: -i[0])[:8], key=lambda i: i[1])
    if items:
        w.section("glance", "Your Month at a Glance")
        thirds = [[i for i in items if i[1].day <= 10], [i for i in items if 10 < i[1].day <= 20], [i for i in items if i[1].day > 20]]
        part = max(range(3), key=lambda k: (sum(i[0] for i in thirds[k]), k))
        nw = ["one", "two", "three", "four", "five", "six", "seven", "eight"][len(items) - 1]
        w.para(D.GLANCE_SHAPE.format(month=MONTH, n=nw, part=D.GLANCE_PART[part])
               .replace(" one key financial and professional dates", " one key date"))
        for k, grp in enumerate(thirds):
            if grp:
                tail = D.GLANCE_TAIL if k == 2 and any("Full Moon" in g[2] for g in grp) and top else ""
                w.para(*[g[2] for g in grp], tail)

    # ------------------------------------------------------------------ 3. moving
    mv = f["moving"]
    w.section("moving", "Where the Money Planets Are Moving")
    w.para(D.MOVING_INTRO)
    hsun, hven, hmar = mv["sun"]["house"], mv["venus"]["house"], mv["mars"]["house"]
    w.para(D.SUN_SHINES.format(ord=ORD[hsun], noun=D.HOUSE_NOUN[hsun]), D.HOUSE_DEEP[hsun], weave(hsun), D.SUN_Q[hsun])
    w.para(D.VENUS_HOUSE_DEEP[hven], weave(hven), D.VENUS_REFRAME[hven])
    w.para(D.MARS_HOUSE_DEEP[hmar], weave(hmar), D.MARS_TENSION[hmar])
    if len({hsun, hven, hmar}) == 3:
        w.para(D.MOVING_SYNTH.format(a=D.HOUSE_NOUN[hsun], b=D.HOUSE_NOUN[hven], c=D.HOUSE_NOUN[hmar], month=MONTH), D.MOVING_SYNTH2)
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "Look at where Venus and Mars are in your chart this month and give each one an action. One thing to receive, and one thing to push forward.",
                                  "prompts": [T.PROMPT_MOVING.format(vord=ORD[hven], mord=ORD[hmar])]}

    # ------------------------------------------------------------------ helpers for transits
    def slow_block(x):
        """One to four paragraphs for a slow transit, scaled by its score."""
        d = depth(x)
        k, pl = x["target"], x["planet"]
        verb = D.VERB_SLOW[x["aspect"]]
        exact = f" The aspect is exact on {_date(x['date'])}." if x["date"] else ""
        first = f"This month {nm(pl)} {verb} {ref(k)}.{exact}"
        w.para(first, intro_pt(k), D.SLOW_MEAN.get((pl, x["cls"]), ""))
        if d >= 2:
            w.para(natal_depth(k), role_deep(k), D.SLOW_DEEP.get((pl, x["cls"]), ""))
        if d >= 3 and k in P and "house" in P[k]:
            h = P[k]["house"]
            w.para(f"Because {the(k)} sits in your {ORD[h]} house, this may bring attention to {HOUSE_TOPIC[h]}.",
                   D.HOUSE_DEEP[h] if h not in weaved else "", D.SLOW_PRACTICAL.get(pl, ""))
        return d

    def day_para(x, lead=True):
        k, pl = x["target"], x["planet"]
        verb = "crosses" if x["aspect"] == 0 else D.VERB[x["aspect"]]
        out = [f"On {_date(x['date'])}, {the(pl)} {verb} {ref(k)}." if lead else "", intro_pt(k)]
        r = role(k)
        if pl == "venus":
            out.append(D.VENUS_TO.get(r, D.FAST_MEAN.get(("venus", x["cls"]), "")))
        else:
            out.append(D.FAST_MEAN.get((pl, x["cls"]), ""))
            if pl == "mercury" and r in ("second", "career", "both"):
                out.append(D.MERCURY_TO_RULER.format(T=the(k)))
        if depth(x) >= 2:
            out += [role_deep(k), natal_depth(k)]
        return out

    # ------------------------------------------------------------------ 4. openings
    good = {("jupiter", "conj"), ("jupiter", "soft"), ("saturn", "soft"), ("uranus", "conj")}
    open_slow = sorted([x for x in acts if x["tech"] == "transit" and (x["planet"], x["cls"]) in good], key=lambda x: -x["score"])
    watch_slow = sorted([x for x in acts if x["tech"] == "transit" and (x["planet"], x["cls"]) not in good], key=lambda x: -x["score"])
    open_days = [x for x in acts if x["tech"] == "day" and x["cls"] in ("soft", "conj") and x["planet"] in ("venus", "sun", "mercury", "mars")]
    open_days = sorted(sorted(open_days, key=lambda x: -x["score"])[:5], key=lambda x: x["date"])
    w.section("open", "Openings This Month")
    w.para(D.OPEN_INTRO)
    for x in open_slow[:2]:
        slow_block(x)
    venus = [x for x in open_days if x["planet"] == "venus"]
    rest = [x for x in open_days if x["planet"] != "venus"]
    cluster = None
    best = []
    for i in range(len(venus)):
        grp = [v for v in venus[i:] if (v["date"] - venus[i]["date"]).days <= 7]
        if len(grp) > len(best):
            best = grp
    if len(best) >= 2:
        cluster = best
        venus = [v for v in venus if v not in best]
    for x in sorted(venus + rest, key=lambda x: x["date"]):
        w.para(*day_para(x))
    if cluster:
        w.para(D.VENUS_CLUSTER.format(d1=_date(cluster[0]["date"]), d2=_date(cluster[-1]["date"])))
        small = []
        for x in cluster:
            if x["score"] >= 4:
                w.para(*day_para(x))
            else:
                small.append(x)
        if small:
            w.para(*(f"On {_date(x['date'])}, Venus {'crosses' if x['aspect'] == 0 else D.VERB[x['aspect']]} {ref(x['target'])}." for x in small),
                   *(D.VENUS_TO.get(role(x["target"]), "") for x in small[:1]))
    n_open = len(open_slow[:2]) + len(open_days)
    if n_open >= 2:
        w.para(rng.choice(D.OPEN_SYNTH_V))
    elif not n_open:
        w.para(D.QUIET_OPEN)
    top_open = (open_slow[0]["planet"] if open_slow else open_days[0]["planet"] if open_days else None)
    w.sections[-1]["practice"] = {"label": "Try This", "try": T.TRY_OPEN.get(top_open or "quiet", T.TRY_OPEN["quiet"]),
                                  "prompts": [T.PROMPT_OPEN]}

    # ------------------------------------------------------------------ 5. watch
    w.section("watch", "What to Watch")
    w.para(D.WATCH_INTRO)
    watched = False
    pattern_done = False
    for x in watch_slow[:2]:
        d = slow_block(x)
        watched = True
        if d >= 3 and not pattern_done and "saturn" in P:
            ps = P["saturn"]
            mates = [nm(p) for p in occ[ps["house"]] if p != "saturn" and abs(W.sep(P[p]["lon"], ps["lon"])) <= 8]
            sat = "Your natal Saturn" + (f", joined by {_join(mates)}," if mates else "")
            w.para(D.WATCH_DEEPER.format(sat=sat, sign=ps["sign"], ord=ORD[ps["house"]],
                                         topic=T.SHORT_TOPIC[ps["house"]]),
                   D.SATURN_PATTERN[ps["house"]], D.SATURN_TURN.format(month=MONTH))
            pattern_done = True
    hard_days = sorted([x for x in acts if x["tech"] == "day" and x["cls"] == "hard" and x["planet"] in ("mars", "venus")], key=lambda x: x["date"])[:3]
    if hard_days:
        w.para(*(f"On {_date(x['date'])}, {the(x['planet'])} {D.VERB[x['aspect']]} {ref(x['target'])}." for x in hard_days),
               D.FAST_MEAN[("mars", "hard")] if any(x["planet"] == "mars" for x in hard_days) else D.FAST_MEAN[("venus", "hard")])
        watched = True
    if f["mercury_retro"]:
        mm = f["mercury_mid"]
        w.para(T.MERC_RX.format(ord=ORD[mm["house"]], topic=T.SHORT_TOPIC[mm["house"]]),
               " ".join(T.MERC_STATION[s["kind"]].format(date=_date(s["date"]), sign=s["sign"], ord=ORD[s["house"]]) for s in f["stations"]))
        watched = True
    if not watched:
        w.para(D.QUIET_WATCH)
    top_watch = watch_slow[0]["planet"] if watch_slow else ("mars" if hard_days else "mercury" if f["mercury_retro"] else None)
    w.sections[-1]["practice"] = {"label": "Try This", "try": T.TRY_WATCH.get(top_watch or "none", T.TRY_WATCH["none"]),
                                  "prompts": [T.PROMPT_WATCH]}

    # ------------------------------------------------------------------ 6. lunations
    w.section("moons", "The New Moon and Full Moon in Your Houses")
    w.para(D.LUN_INTRO)
    prompts = []
    lon = a["lon"]
    for L in f["lunations"]:
        h = L["house"]
        angle = ""
        if not untimed:
            for ang in ("asc", "mc", "ic", "dsc"):
                if ang in lon and abs(W.sep(L["lon"], lon[ang])) <= 5:
                    angle = D.LUN_ANGLE[ang]
                    break
        hit = L["hits"][0] if L["hits"] else None
        w.para(D.LUN_LINE[L["kind"]].format(date=_date(L["date"]), deg=L["deg"], sign=L["sign"], ord=ORD[h], hof=T.HOUSE_OF[h]),
               T.ECLIPSE_NOTE if L["eclipse"] else "",
               angle,
               D.LUN_SIGN_JOIN.format(flavor=D.LUN_SIGN[L["sign"]], ord=ORD[h], topic=HOUSE_TOPIC[h]),
               weave(h, brief=True),
               T.LUNATION_HIT[hit["aspect"]].format(t=ref(hit["target"])[5:]) if hit else "",
               (T.NEW_HOUSE if L["kind"] == "new" else T.FULL_HOUSE)[h])
        sr = W.RULER[L["sign"]]
        link = ""
        if sr in (r2, rc):
            link = D.LUN_RULER_LINK.format(sign=L["sign"], R=the(sr), what="income" if sr == r2 else "career", story="financial" if sr == r2 else "career")
        w.para((D.NEW_LESSON if L["kind"] == "new" else D.FULL_LESSON)[h], link,
               D.THEME["security"]["lesson"] if link and sr == r2 and L["kind"] == "full" else "")
        prompts.append((T.PROMPT_NEW if L["kind"] == "new" else T.PROMPT_FULL).format(ord=ORD[h], topic=T.SHORT_TOPIC[h]))
    news = [L for L in f["lunations"] if L["kind"] == "new"]
    fulls = [L for L in f["lunations"] if L["kind"] == "full"]
    if news and fulls:
        A, B = (news[0], fulls[0]) if news[0]["date"] < fulls[0]["date"] else (fulls[0], news[0])
        arc_of = lambda L: (D.NEW_ARC if L["kind"] == "new" else D.FULL_ARC)[L["house"]]
        w.para(D.LUN_SYNTH.format(a=arc_of(A), b=arc_of(B), tail=rng.choice(D.LUN_SYNTH_TAIL_V)))
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "On the New Moon, write one money intention in the present tense. On the Full Moon, read it again and write down what changed.",
                                  "prompts": prompts[:2]}

    # ------------------------------------------------------------------ 7. progressed Moon
    w.section("pmoon", "Your Progressed Moon This Month")
    w.para(D.PMOON_INTRO)
    w.para(f"With your progressed Moon in {pm['sign']} in your {ORD[pm['house']]} house, {D.PMOON_SIGN[pm['sign']]}.",
           f"{D.PMOON_SIGN_TRAIT[pm['sign']]}.", D.PMOON_HOUSE_DEEP[pm["house"]],
           T.PMOON_SIGN_CHANGE.format(sign=pm["sign_change"]) if pm["sign_change"] else "",
           T.PMOON_HOUSE_CHANGE.format(ord=ORD[pm["house_change"]], topic=T.SHORT_TOPIC[pm["house_change"]]) if pm["house_change"] else "")
    w.para(D.PMOON_MONEY[pm["sign"]])
    st = D.SIGN_THEME[pm["sign"]]
    echo = [x for x in watch_slow + open_slow if D.PLANET_THEME.get(x["planet"]) == st]
    w.para(D.PMOON_LESSON[pm["sign"]],
           D.PMOON_ECHO.format(what=f"{MONTH}'s {nm(echo[0]['planet'])} {ASPECT_NOUN[echo[0]['aspect']]} to your {nm(echo[0]['target'])}")
           if echo and st in top else "")
    for x in [x for x in pm["aspects"] if x["in_month"]][:2]:
        cls = "conj" if x["aspect"] == 0 else "soft" if x["aspect"] in (60, 120) else "hard"
        w.para(T.PMOON_ASPECT[x["aspect"]].format(t=ref(x["target"]), date=_date(x["date"])), T.PMOON_ASPECT_MEAN[cls])
    w.sections[-1]["practice"] = {"label": "Try This",
                                  "try": "Once this month, check in with how you feel about money before you check the numbers. Write one sentence about the feeling, then one about the facts.",
                                  "prompts": [T.PROMPT_PMOON.format(sign=pm["sign"], ord=ORD[pm["house"]])]}

    # ------------------------------------------------------------------ 8. bigger current
    arcs = [x for x in acts if x["tech"] == "arc"]
    progs = [x for x in acts if x["tech"] == "prog"]
    mids = f["midpoints"]
    if arcs or progs or mids:
        w.section("current", "The Bigger Current")
        if arcs:
            w.para(D.BIG_INTRO)
        elif progs:
            w.para(D.BIG_INTRO_PROG)
        said_not_event = False
        seen_asp, seen_tgt = set(), set()
        for x in sorted(arcs, key=lambda x: -x["score"])[:3]:
            k, m = x["target"], x["planet"]
            mover_txt = D.SA_MOVER.get(m, "")
            r = role(k)
            sa_t = D.SA_TARGET.get(r if r in D.SA_TARGET else ("sun" if k == "sun" else "other"), "").format(T=the(k))
            parts = [f"Your directed {nm(m)} is {ARC_VERB[x['aspect']]} your natal {nm(k)}.",
                     f"{mover_txt}." if mover_txt else "", intro_pt(k),
                     D.SA_ASPECT_AGAIN[x["aspect"]] if x["aspect"] in seen_asp else D.SA_ASPECT[x["aspect"]],
                     D.SA_SAME_TARGET.format(T=the(k)) if k in seen_tgt else sa_t]
            seen_asp.add(x["aspect"])
            seen_tgt.add(k)
            if depth(x) >= 2:
                parts.append(natal_depth(k))
            if not said_not_event and depth(x) <= 2:
                parts.append(D.SA_NOT_EVENT)
                said_not_event = True
            w.para(*parts)
        for x in progs[:1]:
            w.para(T.SLOWPROG_LINE.format(p=nm(x["planet"]), a=T.ASPECT_WORD[x["aspect"]], t=ref(x["target"])))
        if mids:
            m = mids[0]
            w.para(D.MIDPOINT_DEEP.format(a=nm(m["pair"][0]), b=nm(m["pair"][1]), mean=T.MIDPOINT_MEAN[m["pair"]],
                                          P=nm(m["planet"]), date=_date(m["date"])))
        if len(top) >= 2 and (arcs or progs):
            others = []
            if watch_slow or open_slow:
                x = (watch_slow or open_slow)[0]
                others.append(f"the {nm(x['planet'])} {ASPECT_NOUN[x['aspect']]} to your {nm(x['target'])}")
            others.append(f"your progressed Moon in {pm['sign']}")
            pair = D.PAIR.get(frozenset(top[:2])) or D.PAIR_GENERIC.format(A=_cap(D.THEME[top[0]]["noun"]), B=D.THEME[top[1]]["noun"])
            w.para(D.CONVERGE.format(others=_join(others), pair=pair), D.THEME[top[0]]["lesson"])

    # ------------------------------------------------------------------ 9. what the month is preparing you for
    w.section("prepare", D.PREP_HEAD.format(month=MONTH))
    parts = []
    if top:
        parts.append(D.PREP_OPEN.format(month=MONTH, themes=_join(D.THEME[t]["short"] for t in top)))
    parts.append(f"The monthly spotlight on {the(lord)} connects {D.THEME[lt]['noun']} with this month's choices"
                 + (f", while the transits highlight the relationship between {D.THEME[target_theme(watch_slow[0]['target'])]['noun']} "
                    f"and {D.THEME[D.PLANET_THEME[watch_slow[0]['planet']]]['noun']}." if watch_slow else "."))
    parts.append(f"Your progressed Moon in {pm['sign']} reinforces the importance of {D.THEME[st]['noun']}"
                 + (f", and your solar arc directions suggest that questions around "
                    f"{_join(sorted({D.THEME[target_theme(x['target'])]['short'] for x in arcs}))} are developing over a longer period." if arcs else "."))
    w.para(*parts)
    if news and fulls:
        A, B = (news[0], fulls[0]) if news[0]["date"] < fulls[0]["date"] else (fulls[0], news[0])
        w.para(D.PREP_LUN.format(a=(D.NEW_ARC if A["kind"] == "new" else D.FULL_ARC)[A["house"]],
                                 b=(D.NEW_ARC if B["kind"] == "new" else D.FULL_ARC)[B["house"]], tail=rng.choice(D.PREP_LUN_TAIL_V)))
    if f["next_new_moon"]:
        n = f["next_new_moon"]
        w.para(D.NEXT_LINE.format(nmonth=W.MONTHS[n["date"].month - 1], sign=n["sign"], ord=ORD[n["house"]], hof=T.HOUSE_OF[n["house"]]),
               D.NEXT_HOUSE[n["house"]])

    # ------------------------------------------------------------------ 10. final thoughts
    w.section("final", "Final Thoughts")
    sig = []
    sig.append("your income ruler is guiding the month" if lord == r2 else "your career ruler is guiding the month" if lord == rc
               else f"{the(lord)} is guiding the month")
    big = (watch_slow or open_slow)
    if big and big[0]["planet"] in ADJ:
        x = big[0]
        r = role(x["target"])
        who = {"second": "your income ruler", "career": "your career ruler", "both": "the ruler of your income and career",
               "mc": "your Midheaven", "fortune": "your Part of Fortune", "assets": "your Lot of Assets"}.get(r, f"your {nm(x['target'])}")
        sig.append(f"{who} is receiving {ADJ[x['planet']]} activation")
    sig.append(f"your progressed Moon is moving through a chapter of {D.THEME[st]['noun']}")
    if arcs:
        sig.append(f"your solar arc directions are emphasizing {_join(sorted({D.THEME[target_theme(x['target'])]['short'] for x in arcs}))}")
    sig_line = _cap(_join(sig)) + "."
    w.para((D.FINAL_CONVERGE if top else D.FINAL_SIMPLE).format(month=MONTH, list=sig_line))
    stel = [h for h in range(1, 13) if len(occ[h]) >= 3]
    a_bits = list(dict.fromkeys([T.SHORT_TOPIC[h2], T.SHORT_TOPIC[pc["house"]]] + [T.SHORT_TOPIC[h] for h in stel]))
    b_line = (f"With {the(r2)} ruling your income from your {ORD[h2]} house and {the(rc)} connecting your career to your "
              f"{ORD[pc['house']]} house, the way you earn is tied to who you are and how you spend your days."
              if rc != r2 else f"With {the(r2)} ruling both your income and your career from your {ORD[h2]} house, your money and "
                               f"your reputation move together.")
    disrupt = big and big[0]["planet"] in ("uranus", "pluto", "neptune") and D.PLANET_THEME[big[0]["planet"]] in top
    w.para(D.FINAL_NATAL.format(a=_join(a_bits + ["your material security"]), b=b_line, tail=rng.choice(D.FINAL_NATAL_TAIL_V)),
           D.FINAL_YET if disrupt else "", D.THEME[D.PLANET_THEME[big[0]["planet"]]]["final"] if disrupt else "")
    fin = [D.THEME[t]["final"] for t in top[:2] if not (disrupt and t == D.PLANET_THEME[big[0]["planet"]])]
    w.para(*(fin or [D.THEME[lt]["final"]]))

    # ------------------------------------------------------------------ offers
    w.section("next", "Where to Go From Here")
    w.para(T.OFFERS_INTRO)
    w.sections[-1]["offers"] = [{"title": OFFERS[k][0], "url": OFFERS[k][1], "why": OFFERS[k][2]} for k in ("wealth", "timing", "moon", "manifest")]

    explain_terms(w.sections, skip=("next", "glance", "begins", "current", "pmoon"))
    if untimed:
        for sec in w.sections:
            sec["paragraphs"] = [p.replace("your Midheaven and career", "your solar tenth house of career")
                                  .replace("rules your Midheaven", "rules your solar tenth house of career")
                                  .replace(" Your Midheaven is the very top of your chart, tied to career and reputation.", "")
                                  for p in sec["paragraphs"]]
    return {"title": "Your Monthly Money Forecast", "subtitle": f"Money and career for {month}", "name": name, "birth": birth,
            "cover_lines": ("Your Monthly", "Money Forecast"), "footer_title": f"Your Monthly Money Forecast  ·  {month}",
            "sections": w.sections, "signoff": T.SIGNOFF, "disclaimer": T.DISCLAIMER}
