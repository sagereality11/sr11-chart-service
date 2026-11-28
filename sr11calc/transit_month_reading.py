"""Your Monthly Transit Forecast: turns month_facts into the reading (the JSON the PDF and web view render).

Output shape matches the approved samples: name, month, birthLabel, tagline, letter, parts[ {title, intro,
opening, sections[ {title, eyebrow, sub, paras, octave, close, prompt, table, grid, natal, image, ...} ]} ],
finalSub, final, more, method, fine, affirmations.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random

from . import transit_text as T
from .transit_month import RULER, SIGNS, NAME, house_of, sep

TZ_LABEL = {"America/New_York": "Eastern", "America/Chicago": "Central", "America/Denver": "Mountain",
            "America/Phoenix": "Arizona", "America/Los_Angeles": "Pacific", "America/Anchorage": "Alaska",
            "Pacific/Honolulu": "Hawaii", "Europe/London": "UK", "Europe/Dublin": "Irish", "Australia/Sydney": "Sydney",
            "Europe/Paris": "Central European", "Europe/Berlin": "Central European", "America/Toronto": "Eastern",
            "America/Vancouver": "Pacific"}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SLOWP = ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node")
TRAD = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")

NATAL_SIGN = {
    "sun": "Your Sun in {sign} shines brightest through {need}.",
    "moon": "Your Moon in {sign} finds safety through {need}.",
    "mercury": "Your Mercury in {sign} thinks and speaks {style}.",
    "venus": "Your Venus in {sign} loves {style} and values {need}.",
    "mars": "Your Mars in {sign} ties your drive to {need}.",
    "jupiter": "Your Jupiter in {sign} grows through {need}.",
    "saturn": "Your Saturn in {sign} builds {style} and takes {world} seriously.",
    "uranus": "Your Uranus in {sign} is shared by your whole generation, so it's its place in your {h} house that makes it personal.",
    "neptune": "Your Neptune in {sign} is shared by your whole generation, so its place in your {h} house is what makes it yours.",
    "pluto": "Your Pluto in {sign} belongs to your generation, and its place in your {h} house shows where that deep power lives in your own life.",
    "chiron": "Your Chiron in {sign} carries a tender place around {world}.",
    "north_node": "Your North Node in {sign} asks you to grow toward {nn}.",
    "south_node": "Your South Node in {sign} carries the familiar pull of {sn}.",
    "asc": "Your {sign} rising meets the world {style}.",
    "mc": "Your Midheaven in {sign} points your life direction toward {world}.",
}
FINAL_ASK = {
    "jupiter": "Jupiter's contact with your {np} invites you to grow on purpose",
    "saturn": "Saturn's contact with your {np} asks you to be more intentional with your strength",
    "uranus": "Uranus's contact with your {np} asks you to make room for a freer, truer life",
    "neptune": "Neptune's contact with your {np} reminds you that what you love can grow out of what you believe",
    "pluto": "Pluto's contact with your {np} asks you to take your power back from what you've outgrown",
    "chiron": "Chiron's contact with your {np} invites you to meet an old tender place with compassion",
    "north_node": "the nodes crossing your {np} point you toward your soul's next step",
}
OCT_SHORT = {"jupiter": "growth without overwhelm", "saturn": "commitment without self-sacrifice",
             "uranus": "freedom without chaos", "neptune": "vision without losing yourself",
             "pluto": "power without control", "chiron": "healing without shame", "north_node": "direction without fear"}
CLOSERS = ["The deeper invitation of this month is to stop postponing the experience of your own life in the name of preparing for it. You're allowed to create, explore, rest and receive while you're still building your future.",
           "You don't have to diminish your previous chapter to recognize that you're ready for another one. Everything you've learned can come with you, even as the roles around it change.","The greatest sign of your strength isn't how much more you can carry. It's choosing, on purpose, what comes with you into your next chapter.",
           "You don't have to have it all figured out. You only have to keep choosing what is true for you, one day at a time.",
           "Trust the pace of your own becoming. Everything this month asks of you, you already have inside you."]
WINDOW_GUIDE = {
    "saturn": ["Let your choices come from clarity rather than built-up frustration.", "Decide from clarity, not from pressure."],
    "jupiter": ["Say yes to what genuinely excites you, and let the rest wait.", "Choose the opportunity that feels most like you."],
    "uranus": ["Notice where you feel restless, because that restlessness is pointing at what wants to change.", "Leave room for surprises, and don't rush to fill it."],
    "neptune": ["Give yourself room to dream, and be gentle with any uncertainty.", "Trust what you sense even before you can explain it."],
    "pluto": ["Let yourself go deeper than usual, and trust that what surfaces is ready to be released.", "Be honest with yourself about what you want."],
    "chiron": ["Treat yourself with the tenderness you'd offer someone you love.", "Go gently with old tender places."],
    "north_node": ["Pay attention to what feels fated, and take one small step toward it.", "Notice which familiar roles you step into, and whether you still want them."],
    "new": ["It's a good stretch for setting intentions and beginning gently.", "Begin small and let it grow."],
    "full": ["It's a good stretch for finishing, releasing and seeing clearly.", "Let something finish so something else can begin."],
    "sun": ["Let yourself be seen in the area of life the Sun is lighting up.", "Notice where your attention naturally goes."],
    "mercury": ["Choose your words with care, and say what needs to be said.", "Write things down before you decide."],
    "venus": ["Make room for pleasure and connection.", "Let yourself enjoy what you love."],
    "mars": ["Put your energy where it matters most, and rest when you can.", "Act on one priority at a time."],
    "quiet": ["Use these quieter days to rest and let everything settle.", "Let these days be spacious."],
}


def cls(asp):
    return {0: "conj", 180: "opp", 90: "sq"}.get(asp, "soft")


def ocls(asp):
    return {0: "conj", 180: "hard", 90: "hard"}.get(asp, "soft")


def when(iso, year=None):
    d = dt.date.fromisoformat(iso)
    s = f"{T_MONTHS[d.month - 1]} {d.day}"
    if year is not None and d.year != year:
        s += f", {d.year}"
    return s


T_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
            "November", "December"]


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def join(items, word="and"):
    items = [i for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {word} " + items[-1]


class Pick:
    def __init__(self, seed):
        self.r = random.Random(int(hashlib.md5(seed.encode()).hexdigest()[:8], 16))
        self.used = set()

    def one(self, opts):
        if isinstance(opts, str):
            return opts
        fresh = [o for o in opts if (o if isinstance(o, str) else repr(o)) not in self.used]
        o = self.r.choice(fresh or list(opts))
        self.used.add(o if isinstance(o, str) else repr(o))
        return o


def hname(h):
    return f"{T.ORD[h]} house"


def an(word):
    w = word.lower()
    return "an" if w[:1] in "aeiou" or w.startswith(("8", "11th", "18")) else "a"


def pn(pid, capital=False):
    """Planet name as a subject: the Sun, the Moon, the North Node, otherwise the bare name."""
    n = {"sun": "the Sun", "moon": "the Moon", "north_node": "the North Node", "south_node": "the South Node"}.get(pid, NAME.get(pid, pid))
    return cap(n) if capital else n


class Builder:
    def __init__(self, f, name, birth_label, pron="she", pair_mode=False):
        self.f, self.name, self.birth_label = f, name, birth_label
        self.pron = pron
        self.P = f["natal"]["points"]
        self.cusps = f["natal"]["cusps"]
        self.timed = f["natal"]["timed"]
        self.year, self.month = f["year"], f["month"]
        self.M = f["month_name"]
        self.pk = Pick(f"{name}|{birth_label}|{self.year}-{self.month}")
        self.prof = f["profection"]
        self.sections_used = set()
        self.done = []
        self._cyc = {}
        self.groups_told = {}
        self.oct_used = set()

    def cyc(self, key, opts):
        """Each call for the same key takes the next option, so a phrase pattern isn't reused until all are used."""
        i = self._cyc.get(key)
        if i is None:
            i = self.pk.r.randrange(len(opts))
        self._cyc[key] = i + 1
        return opts[i % len(opts)]

    def mhouse(self):
        sh = self.prof["month_shift"]
        return sh["house"] if sh else self.prof["month_house"]

    def top_theme(self):
        if not hasattr(self, "_tt"):
            conv = self.part_converge()
            self._tt = conv["sections"][0]["table"]["rows"][0][0].lower() if conv else ""
        return self._tt

    def octave(self, tp, oc, tg):
        base = T.OCTAVE.get((tp, oc), T.OCTAVE[("saturn", "hard")])
        seen = base[0] in self.oct_used
        if seen:
            alt = [T.OCTAVE[(tp, k)] for k in ("hard", "conj", "soft") if (tp, k) in T.OCTAVE and T.OCTAVE[(tp, k)][0] not in self.oct_used]
            if alt:
                base, seen = alt[0], False
        self.oct_used.add(base[0])
        for t in ([tg] if isinstance(tg, str) else list(tg)):
            if t in T.TGT_OCT and t not in self.oct_used:
                self.oct_used.add(t)
                lo, hi = T.TGT_OCT[t]
                if seen:
                    return [lo.replace("that can look like", "the shadow can look like"), hi.replace("it looks like", "the gift looks like")]
                return [base[0] + " " + lo, base[1] + " " + hi]
        return list(base)

    # ---------------------------------------------------------- helpers
    def H(self, lon):
        return house_of(lon, self.cusps)

    def dt_(self, iso):
        return when(iso, self.year)

    def rules(self, pid):
        """Houses (by cusp sign) a traditional planet rules."""
        if pid not in TRAD:
            return []
        return [i + 1 for i, s in enumerate(self.f["natal"]["cusp_signs"]) if RULER[SIGNS.index(s)] == pid]

    def natal_line(self, pid):
        p = self.P[pid]
        s = T.SIGN[p["sign"]]
        nn = T.NODE_SIGN.get(p["sign"], ("", ""))
        if pid in T.PSIGN:
            return T.PSIGN[pid][p["sign"]]
        return T_NATAL(pid).format(sign=p["sign"], need=s["need"], style=s["style"], world=T.SIGN_WORLD[p["sign"]],
                                   h=T.ORD[p["house"]], nn=nn[0], sn=nn[1])

    def pt(self, pid):
        return T.PT[pid]

    def nm(self, pid):
        return T.PT[pid]["n"] if pid in T.PT else NAME.get(pid, pid)

    def tname(self, pid):
        return T.TNAME.get(pid, NAME.get(pid, pid))

    def is_year_lord(self, pid):
        return pid == self.prof["lord"]

    # ---------------------------------------------------------- events
    def events(self):
        """Every dated event in the month, with a weight, a long phrase and a short grid label."""
        f, ev = self.f, []
        for s in f["stations"]:
            on = s["on"][0] if s["on"] else None
            lab = f"{self.tname(s['planet']).replace('the ', '').capitalize() if False else NAME[s['planet']]} {'retrograde' if s['kind'] == 'retrograde' else 'direct'}"
            long = f"{NAME[s['planet']]} turns {s['kind']} in your {hname(s['house'])}"
            if on:
                long += f", {T.ASP_WORD[on['aspect']]} your {self.nm(on['target'])}"
                lab += f", {T.ASP_WORD[on['aspect']]} your {self.nm(on['target'])}"
            w = {"mercury": 4, "venus": 5, "mars": 5}.get(s["planet"], 7) + (3 if self.is_year_lord(s["planet"]) else 0) + (2 if on else 0)
            ev.append(dict(date=s["date"], w=w, long=long, lab=lab, key=s["planet"], kind="station", asp=on["aspect"] if on else None,
                           att=self.pt(on["target"])["short"] if on else T.HOUSE[s["house"]]["short"],
                           sent=cap(long.replace(" turns ", " turns ", 1)) + " on {d}",
                           mean=f"That station touches {T.PT[on['target']]['ess']}." if on else f"That station turns your attention to {T.HOUSE[s['house']]['area']}."))
        for s in f["slow"]:
            for d in s["exact"]:
                long = f"{NAME[s['planet']]} {T.ASP_WORD[s['aspect']]} your natal {self.nm(s['target'])}, exact"
                ev.append(dict(date=d, w=s["weight"] / 2 + 2, long=long, asp=s["aspect"],
                               lab=f"{NAME[s['planet']]} {T.ASP_WORD[s['aspect']]} your {self.nm(s['target'])}",
                               key=s["planet"], kind="slow", att=self.pt(s["target"])["short"],
                               sent=f"{pn(s['planet'], True)} makes an exact {T.ASP_NOUN[s['aspect']]} to your natal {self.nm(s['target'])} on {{d}}",
                               mean=f"That contact touches {T.PT[s['target']]['ess']}."))
        for l in f["lunations"]:
            nm = "New Moon" if l["kind"] == "new" else "Full Moon"
            ecl = f", {l['eclipse']}" if l["eclipse"] else ""
            ev.append(dict(date=l["date"], w=8 + (3 if l["eclipse"] else 0),
                           long=f"{nm} at {l['deg']}° {l['sign']}{ecl}, {l['time']}",
                           lab=f"{nm} {l['deg']}° {l['sign']}, {T.ORD[l['house']]} house",
                           key=l["kind"], kind="lunation", att=T.HOUSE[l["house"]]["short"],
                           sent=f"The {nm} in {l['sign']} arrives on {{d}}" + (f" as {an(l['eclipse'])} {l['eclipse']}" if l["eclipse"] else "") + f", lighting up your {hname(l['house'])}",
                           mean=f"It brings {T.HOUSE[l['house']]['area']} into focus."))
        for i in f["ingresses"]:
            if i["planet"] in ("uranus", "neptune", "pluto", "chiron") and i["kind"] == "house":
                continue
            if i["kind"] == "sign":
                long = f"{NAME[i['planet']]} enters {i['sign']}"
                if i["planet"] == "sun" and i["sign"] in ("Capricorn", "Cancer", "Aries", "Libra"):
                    long += {"Capricorn": " (winter solstice)", "Cancer": " (summer solstice)", "Aries": " (equinox)",
                             "Libra": " (equinox)"}[i["sign"]] if self.f["tz"].startswith(("America", "Europe")) else ""
                lab = f"{NAME[i['planet']]} into {i['sign']}"
                att = T.SIGN_WORLD[i["sign"]].split(",")[0]
            else:
                long = f"{NAME[i['planet']]} enters your {hname(i['house'])}"
                lab = f"{NAME[i['planet']]} into your {T.ORD[i['house']]}"
                att = T.HOUSE[i["house"]]["short"]
            w = 3 if i["planet"] in ("sun", "mercury", "venus", "mars") else 5
            sent = (f"{pn(i['planet'], True)} moves into {i['sign']} on {{d}}" if i["kind"] == "sign"
                    else f"{pn(i['planet'], True)} crosses into your {hname(i['house'])} on {{d}}")
            ev.append(dict(date=i["date"], w=w, long=long, lab=lab, key=i["planet"], kind="ingress", att=att, sent=sent,
                           mean=f"That turns attention toward {T.SIGN_WORLD[i['sign']]}." if i["kind"] == "sign" else f"That turns attention toward {T.HOUSE[i['house']]['area']}."))
        seen = set()
        for h in f["fast"]:
            if h["target"] == "north_node" and h["aspect"] == 180 and any(
                    x["planet"] == h["planet"] and x["target"] == "south_node" and x["date"] == h["date"] for x in f["fast"]):
                continue
            k = (h["planet"], h["target"], h["aspect"], h["date"])
            if k in seen:
                continue
            seen.add(k)
            tgt = "your nodes" if h["target"] == "south_node" and h["aspect"] == 0 else f"your {self.nm(h['target'])}"
            verb = {0: "on", 180: "opposite", 90: "square", 120: "trine"}[h["aspect"]]
            long = f"{NAME[h['planet']]} {'crosses' if verb == 'on' else verb} {tgt}" if h["target"] != "south_node" else \
                f"{NAME[h['planet']]} crosses your South Node and opposes your North Node"
            w = 2 + (1 if h["target"] in ("sun", "moon", "asc", "mc") else 0) + (1 if h["planet"] == "mars" else 0)
            vb = {"on": "crosses", "opposite": "opposes", "square": "squares", "trine": "trines"}[verb]
            sent = (f"{pn(h['planet'], True)} {vb} {tgt} on {{d}}" if h["target"] != "south_node"
                    else f"{pn(h['planet'], True)} crosses your South Node on {{d}}")
            ev.append(dict(date=h["date"], w=w, long=long, lab=f"{NAME[h['planet']]} {verb} {tgt}", key=h["planet"], asp=h["aspect"],
                           kind="fast", att=self.pt(h["target"])["short"] if h["target"] in T.PT else "", sent=sent,
                           mean="It " + T.FAST_HIT.get((h["planet"], h["aspect"]), "touches {ess}").format(ess=T.PT[h["target"]]["short"]) + "."))
        sh = self.prof["month_shift"]
        if sh:
            ev.append(dict(date=sh["date"], w=5, long=f"Your monthly profection moves into {sh['sign']}",
                           lab=f"Month turns to {sh['sign']}", key="profection", kind="profection",
                           att=f"your {hname(sh['house'])}", sent=f"Your monthly profection moves into {sh['sign']} on {{d}}",
                           mean=f"The month {T.MONTH_HOUSE[sh['house']]}."))
        for e in ev:
            e.setdefault("act", "")
        ev.sort(key=lambda e: (e["date"], -e["w"]))
        return ev

    # ---------------------------------------------------------- the big currents
    def currents(self):
        f = self.f
        out, per = [], {}
        st_by = {s["planet"]: s for s in f["stations"] if s["planet"] in SLOWP}
        for s in f["slow"]:
            if per.get(s["planet"], 0) >= 2:
                continue
            if s["planet"] == "north_node" and s["target"] in ("north_node", "south_node"):
                continue
            # the same planet on one end of the nodal axis is one story, not two
            if s["target"] in ("north_node", "south_node") and any(o["planet"] == s["planet"] and o["target"] in ("north_node", "south_node") for o in out):
                continue
            # skip a planet aspecting itself here, cycles cover it
            if s["planet"] == s["target"] and s["aspect"] in (0, 90, 180):
                continue
            if any(s is g for o in out for g in o.get("group_items", [])):
                continue
            partners = self.conj_partners(s["target"])
            grp = [x for x in f["slow"] if x is not s and x["planet"] == s["planet"] and x["aspect"] == s["aspect"]
                   and x["target"] in partners]
            if grp:
                s = dict(s)
                s["group_items"] = grp
            out.append(s)
            per[s["planet"]] = per.get(s["planet"], 0) + 1
            if len(out) >= 6:
                break
        return out, st_by

    def conj_partners(self, pid):
        out = []
        for c in self.f["natal"].get("conjunctions", []):
            if c["a"] == pid:
                out.append(c["b"])
            elif c["b"] == pid:
                out.append(c["a"])
        return out

    def group_name(self, pids):
        order = sorted(pids, key=lambda k: ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node", "south_node", "asc", "mc").index(k))
        return "-".join(self.nm(k) for k in order) + " Conjunction"

    def current_section(self, s, st_by, idx):
        pk, P = self.pk, self.P
        tp, tg, asp = s["planet"], s["target"], s["aspect"]
        c, oc = cls(asp), ocls(asp)
        np_ = self.nm(tg)
        st = st_by.get(tp)
        st_here = st and any(o["target"] == tg and o["aspect"] == asp for o in st["on"])
        grp = s.get("group_items") or []
        tnm = np_ if not grp else self.group_name([tg] + [g["target"] for g in grp])
        title = f"{NAME[tp] if tp != 'north_node' else 'The North Node'} {T.ASP_WORD[asp].capitalize()} Your Natal {tnm}"
        if st_here:
            title = f"{NAME[tp]} Turns {st['kind'].capitalize()}, {T.ASP_WORD[asp].capitalize()} Your Natal {tnm}"
        if s["exact"]:
            eyebrow = join([self.dt_(d) for d in s["exact"]]) if len(s["exact"]) <= 2 else f"Exact {len(s['exact'])} times"
            if st_here:
                eyebrow = self.dt_(st["date"])
        elif st_here:
            eyebrow = self.dt_(st["date"])
        else:
            hi = max(s["orb_start"], s["orb_end"])
            eyebrow = (f"All month, within {s['orb']:.1f}° to {hi:.1f}° of exact" if hi <= 1.0
                       else f"Closest {self.dt_(s['closest'])}, within {s['orb']:.1f}° of exact")
        sub = T.SUB.get((tp, oc if oc != "hard" else "hard"), "")
        if sub and sub in self.oct_used:
            sub = f"What {pn(tp)} asks of {T.PT[tg]['short']}."
        self.oct_used.add(sub)
        tpos = f"{s['pos'].split('°')[0]}° {s['sign']}"
        npos = P[tg]
        paras = []
        orbw = "exactly" if s["exact"] else ("less than a degree from" if s["orb"] < 1 else "about a degree from")
        art = "" if orbw == "exactly" else an(T.ASP_NOUN[asp]) + " "
        so = next((o["orb"] for o in (st["on"] if st_here else []) if o["target"] == tg and o["aspect"] == asp), None)
        st_phrase = ("in an almost exact" if so is not None and so < 0.1 else "in a close" if so is not None and so < 0.5
                     else "within a degree of " + an(T.ASP_NOUN[asp]))
        lead = f"{NAME[tp] if tp != 'north_node' else 'The North Node'} is at {tpos} in your {hname(s['house'])} this month, "
        if s["exact"]:
            lead += f"and it makes an exact {T.ASP_NOUN[asp]} to your natal {np_} in {npos['sign']} in your {hname(npos['house'])}"
            lead += f" on {join([self.dt_(d) for d in s['exact']])}." if len(s["exact"]) <= 2 else " more than once this month."
        else:
            lead += f"and it comes within {s['orb']:.1f}° of {art}{T.ASP_NOUN[asp]} to your natal {np_} in {npos['sign']} in your {hname(npos['house'])}, closest around {self.dt_(s['closest'])}."
        if st_here:
            lead = (f"{NAME[tp]} stations {st['kind']} on {self.dt_(st['date'])} at {tpos} in your {hname(st['house'])}, "
                    f"{st_phrase} {T.ASP_NOUN[asp]} to your natal {np_} in {npos['sign']} in your {hname(npos['house'])}. "
                    + pk.one(T.STATION_NOTE))
        if grp:
            g = grp[0]
            lead += (f" It's also {an(T.ASP_NOUN[asp])} {T.ASP_NOUN[asp]} to your natal {self.nm(g['target'])}, which sits right beside your {np_}. "
                     + self.pk.one(["Although these are two separate aspects, I read them as one combined pattern, because the planets they touch work together in your chart.",
                                    "I read these together rather than as two separate transits, because those two planets act as a team in your chart.",
                                    "So this is really one experience touching a pair of planets that already move together."]))
        if self.is_year_lord(tp):
            lead += " " + pk.one([f"Because {NAME[tp]} rules your year, this isn't a passing moment. It's one of the main threads of {self.yr()}.",
                                  f"{NAME[tp]} is the ruler of your year, so this contact belongs to the heart of {self.yr()}.",
                                  f"As the planet in charge of your year, {NAME[tp]} gives this contact more weight than it would have in another year."])
        elif self.is_year_lord(tg):
            lead += " " + pk.one([f"Your {np_} rules your year, so anything that touches it this month carries extra weight.",
                                  f"Because your {np_} is the ruler of your year, this contact reaches into everything the year is about.",
                                  f"Your {np_} is in charge of your year, which makes this one of the contacts I'd watch most closely."])
        paras.append(lead)
        p2 = []
        first = tg not in self.sections_used
        self.sections_used.add(tg)
        if tg in T.PT and first:
            p2.append(T.PT[tg]["role"])
        if tg in NATAL_SIGN and first:
            p2.append(self.natal_line(tg))
        dg = self.dignity(tg, npos["sign"]) if first else None
        if dg and tg in T.PSIGN and any(w in T.PSIGN[tg][npos["sign"]] for w in ("fall", "exalted", "at home", "detriment")):
            dg = None
        if dg:
            p2.append(T.DIGNITY_TEXT[dg].format(lord=np_, sign=npos["sign"]).replace("this year asks you", "this contact asks you").replace("gives this year", "gives it"))
        if first and npos.get("retro") and tg in TRAD:
            p2.append(T.RETRO_NOTE.format(np=np_))
        for st_ in self.f["natal"].get("stelliums", []):
            if tg in st_["points"] and first:
                p2.append(f"It's part of your {st_['sign']} stellium with your {join([self.nm(k) for k in st_['points'] if k != tg])}, so this contact stirs that whole group.")
        if first and tg in T.PIH and self.timed:
            p2.append(T.PIH[tg].format(h=T.ORD[npos["house"]], focus=T.FOCUS[npos["house"]]))
        elif first and tg in T.PIH:
            p2.append(f"In your solar chart it falls in your {hname(npos['house'])}, among {T.FOCUS[npos['house']]}.")
        rh = self.rules(tg)
        if rh and first:
            cs = self.f["natal"]["cusp_signs"]
            hs = [f"your {cs[h - 1]} {hname(h)}" for h in rh[:2]]
            sh = join([T.HOUSE_ONE[h] for h in rh[:2]])
            pl = len(rh[:2]) > 1
            p2.append(self.cyc("rules", [f"It also rules {join(hs)}, so {sh} {'feel' if pl else 'feels'} this contact too.",
                                         f"Because it rules {join(hs)}, {sh} {'are' if pl else 'is'} part of this story as well.",
                                         f"It's also the ruler of {join(hs)}, which brings {sh} into the picture."]))
        br = self.bridge(s)
        if not first and not br and not (grp and frozenset((tg, grp[0]["target"])) in self.groups_told):
            prev = next((d for d in self.done if d["target"] == tg or tg in [g["target"] for g in d.get("group_items", [])]), None)
            if prev:
                p2 = [f"You met your {np_} earlier in this reading, with {pn(prev['planet'])}. This time {pn(tp)} reaches it from your {hname(s['house'])}, "
                      f"so two planets are working on {T.PT[tg]['short']} at once this month."]
        if p2:
            paras.append(" ".join(p2))
        if grp and frozenset((tg, grp[0]["target"])) in self.groups_told:
            g2 = grp[0]["target"]
            pv = self.groups_told[frozenset((tg, g2))]
            paras.append(f"Because your {self.nm(g2)} sits beside your {np_}, {pn(tp)} reaches both of them, the same pair {pn(pv)} is touching this month. "
                         f"That's a sign of how much attention this part of your chart is getting right now.")
            grp_done = True
        else:
            grp_done = False
        if grp and not grp_done:
            g2 = grp[0]["target"]
            self.groups_told[frozenset((tg, g2))] = tp
            gp = self.P[g2]
            t = (f"Your {self.nm(g2)} sits with your {np_} in {gp['sign']}, so {T.PT[g2]['short']} and {T.PT[tg]['short']} have always worked as one story in your life. "
                 + self.pk.one(["When one of them is touched, the other answers.", "You rarely feel one without the other.", "What moves one tends to move both."]))
            if self.is_year_lord(g2):
                t += f" Your {self.nm(g2)} also rules your year, which gives this pattern even more weight right now."
            rh2 = self.rules(g2)
            if rh2:
                t += f" It rules your {join([hname(h) for h in rh2[:2]])} too, so {join([T.HOUSE_ONE[h] for h in rh2[:2]])} {'are' if len(rh2[:2]) > 1 else 'is'} part of this story as well."
            paras.append(t)
        key = (tp, c) if (tp, c) in T.ASPECT_TEXT else (tp, "sq" if c == "opp" else c)
        txt = pk.one(T.ASPECT_TEXT.get(key, T.ASPECT_TEXT[("saturn", "sq")]))
        paras.append(txt.format(np=np_, ess=T.PT[tg]["ess"], short=T.PT[tg]["short"], short_cap=cap(T.PT[tg]["short"]),
                                asp=T.ASP_NOUN[asp]))
        th = T.TRANSIT_HOUSE.get(tp)
        p4 = []
        if th:
            h = s["house"]
            p4.append(pk.one(th).format(h=T.ORD[h], area=T.HOUSE[h]["area"], ask=T.HOUSE[h]["ask"]))
            nh = npos["house"]
            if tp in T.VERB and nh != h:
                p4.append(self.cyc("hlink", [f"Your {np_} answers from your {hname(nh)}, the realm of {T.FOCUS[nh]}, so the story runs between those two parts of your life.",
                                             f"Meanwhile your {np_} lives in your {hname(nh)}, so what changes in {T.HOUSE[h]['short']} is felt in {T.HOUSE[nh]['short']} too.",
                                             f"And because your {np_} sits in your {hname(nh)}, this reaches {T.FOCUS[nh]} as well.",
                                             f"Your {np_} carries the conversation back to your {hname(nh)}, to {T.FOCUS[nh]}."]))
        passes = [d for d in s["passes"]]
        near = s.get("near") or []
        if len(passes) >= 2:
            ds = [when(d, None) + (f", {d[:4]}" if int(d[:4]) != self.year else "") for d in passes]
            p4.append(f"This contact is exact {T.NUM.get(len(passes), str(len(passes)))} times in all, on {join(ds)}, so {self.M} is one chapter of a longer story.")
        elif len(passes) == 1 and not s["exact"]:
            d = passes[0]
            dd = dt.date.fromisoformat(d)
            past = dd < dt.date(self.year, self.month, 1)
            t = f"It {'was' if past else 'becomes'} exact on {when(d, self.year)}"
            if near:
                t += f", and {pn(tp)} comes back within a whisker of exact when it stations around {when(near[0]['date'], self.year)}, so this is a theme to finish rather than begin."
            else:
                if past and st_here:
                    t += (f", and this station brings {pn(tp)} back to the same degree, so the lesson of that first pass returns at full strength. "
                          f"Expect the days around {self.dt_(st['date'])} to feel like the heart of it.")
                else:
                    t += ", so you may already be feeling it settle." if past else ", so you'll feel it building."
            p4.append(t)
        elif near and not passes:
            p4.append(f"{pn(tp, True)} never quite perfects this aspect. It stations within a whisker of exact around {when(near[0]['date'], self.year)}, which makes the near miss just as strong as an exact pass.")
        if p4:
            paras.append(" ".join(p4))
        if br and not grp_done:
            paras.append(br)
        self.done.append(s)
        stage = self.stage(s)
        if stage:
            paras.append(stage)
        layer = self.layer(tp, tg)
        if layer:
            paras.append(layer)
        if tp in T.EVOLVE:
            paras.append(pk.one(T.EVOLVE[tp]).format(ess=T.PT[tg]["ess"]))
        sec = {"title": title, "eyebrow": eyebrow, "sub": sub, "paras": paras,
               "octave": self.octave(tp, oc, [tg] + [g["target"] for g in grp])}
        if idx % 2 == 0:
            sec["close"] = pk.one(T.CLOSE[tp])
        sec["prompt"] = pk.one(T.PROMPT.get(tg, T.PROMPT["sun"]))
        return sec

    def bridge(self, s):
        for d in self.done:
            if d["target"] == s["target"] and d["planet"] != s["planet"]:
                k = frozenset([d["planet"], s["planet"]])
                if k in T.SAME_TARGET:
                    return (f"What makes this especially meaningful is that {pn(d['planet'])} is touching the same natal {self.nm(s['target'])} this month. "
                            + T.SAME_TARGET[k].format(short=T.PT[s["target"]]["short"]))
                return f"{pn(d['planet'], True)} is touching your {self.nm(s['target'])} this month too, so {T.PT[s['target']]['ess']} are getting attention from two directions at once."
        for d in self.done:
            if d["planet"] == s["planet"]:
                continue
            if self.P[d["target"]]["house"] == self.P[s["target"]]["house"]:
                return (f"This lands in the same part of your chart as {pn(d['planet'])}'s contact with your {self.nm(d['target'])}, your {hname(self.P[s['target']]['house'])}. "
                        f"{pn(d['planet'], True)} asks {T.VOICE.get(d['planet'], '')}, and {pn(s['planet'])} asks {T.VOICE.get(s['planet'], '')}, and both questions land in {T.FOCUS[self.P[s['target']]['house']]}.")
            disp = RULER[SIGNS.index(self.P[s["target"]]["sign"])] if s["target"] in TRAD else None
            if disp and disp == d["target"]:
                return (f"There's a thread connecting this to {pn(d['planet'])}'s contact with your {self.nm(d['target'])}. Your {self.nm(s['target'])} sits in {self.P[s['target']]['sign']}, ruled by your {self.nm(d['target'])}, so what happens there flows into this story too.")
        return ""

    def stage(self, s):
        ms = f"{self.year}-{self.month:02d}"
        ps = sorted(s["passes"])
        if not ps:
            return ""
        first = when(ps[0], self.year)
        here = [i for i, d in enumerate(ps) if d[:7] == ms]
        if here:
            i = here[0]
            key = "first" if i == 0 and len(ps) > 1 else "last" if i == len(ps) - 1 and len(ps) > 1 else "middle" if len(ps) > 1 else None
            return self.pk.one(T.PASS_STAGE[key]).format(first=first) if key else ""
        nxt = [d for d in ps if d[:7] > ms]
        if nxt and not [d for d in ps if d[:7] < ms]:
            return self.pk.one(T.PASS_STAGE["coming"]).format(next=when(nxt[0], self.year))
        return ""

    def layer(self, tp, tg):
        """Rulership links between the transit, the natal point and the year and month rulers."""
        prof = self.prof
        bits = []
        tsign = self.f["sky"][tp]["sign"] if tp in self.f["sky"] else None
        if tsign and RULER[SIGNS.index(tsign)] == tg:
            bits.append(f"{NAME[tp] if tp != 'north_node' else 'The North Node'} is moving through {tsign}, a sign ruled by {NAME[tg]}, the same planet it's touching in your chart. " + self.pk.one(["That doubles the conversation between them.", "So the two planets are already in dialogue before the aspect even forms.", "That makes the connection between them stronger than the aspect alone would."]))
        if tg in TRAD:
            disp = RULER[SIGNS.index(self.P[tg]["sign"])]
            if disp == prof["month_lord"] and disp != tg:
                bits.append(f"Your natal {self.nm(tg)} is ruled by your {NAME[disp]}, which is also the ruler of your month. So {T.PT[disp]['ess']} sit at the center of this story too.")
            elif disp == prof["lord"] and disp != tg:
                bits.append(f"Your natal {self.nm(tg)} is ruled by your {NAME[disp]}, the ruler of your year, which ties this contact to the bigger work of {self.yr()}.")
        cr = self.f["natal"].get("chart_ruler")
        if self.timed and tg == cr:
            bits.append(f"Your {self.nm(tg)} is also your chart ruler, the planet that rules your {self.f['natal']['rising_sign']} rising, so this contact reaches into your whole sense of self.")
        if tg == prof["month_lord"] and tg != prof["lord"]:
            bits.append(f"Your {self.nm(tg)} is also the ruler of your month, so this contact speaks for much of {self.M}.")
        return " ".join(bits)

    def yr(self):
        return f"the year that began on your {self.prof['age']}{self.suf(self.prof['age'])} birthday"

    def suf(self, a):
        return "th" if 10 <= a % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(a % 10, "th")

    def ordinal_age(self):
        a = self.prof["age"] + 1
        suf = "th" if 10 <= a % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(a % 10, "th")
        return f"{a}{suf}"

    def station_section(self, s):
        h = s["house"]
        txt = T.STATION[(s["planet"], s["kind"])].format(date=self.dt_(s["date"]), pos=f"{s['pos'].split('°')[0]}° {s['sign']}",
                                                         h=T.ORD[h], area=T.HOUSE[h]["area"])
        paras = [txt + " " + self.pk.one(T.STATION_NOTE)]
        nat = [k for k, v in self.P.items() if v["house"] == h and k not in ("asc", "mc")]
        if not hasattr(self, "st_houses"):
            self.st_houses = {}
        prev = self.st_houses.get(h)
        self.st_houses.setdefault(h, s)
        if prev:
            paras.append(f"This is the same house {pn(prev['planet'])} turned in on {self.dt_(prev['date'])}, so two stations land in {T.HOUSE[h]['short']} within days of each other. "
                         f"When that happens I read it as one turning point told twice, and it's worth giving this part of your life some real attention this month.")
        elif nat:
            t = (f"Your natal {join([self.nm(k) for k in nat[:3]])} live{'s' if len(nat) == 1 else ''} in this house, so the station wakes up {'that part' if len(nat) == 1 else 'those parts'} of you too. "
                 + T.HOUSE[h]["long"].split(". ")[0].rstrip(".") + ".")
            k0 = next((k for k in nat if k in T.PIH and k not in self.sections_used), None)
            if k0 and self.timed:
                self.sections_used.add(k0)
                t += " " + T.PIH[k0].format(h=T.ORD[h], focus=T.FOCUS[h])
            paras.append(t)
        else:
            t = T.HOUSE[h]["long"].split(". ")[0].rstrip(".") + "."
            if h == self.prof["house"]:
                t += " " + T.HOUSE[h]["long"].split(". ")[1].rstrip(".") + ", and it's the house of your year, so this station speaks directly to the year you're in."
            paras.append(t)
        if self.is_year_lord(s["planet"]):
            paras.append(f"Because {NAME[s['planet']]} rules your year, its station carries extra weight. The choices you're turning over right now are part of a much bigger change unfolding through {self.yr()}.")
        return {"title": f"{NAME[s['planet']]} Turns {s['kind'].capitalize()} in Your {T.ORD[h]} House", "eyebrow": self.dt_(s["date"]),
                "sub": f"{'Another' if prev else 'A'} turning point for {T.HOUSE[h]['short']}.", "paras": paras,
                "octave": self.octave(s["planet"], "hard", [k for k in nat if k in T.TGT_OCT]) if s["planet"] in SLOWP else None}

    def midpoint_section(self, m):
        a, b = m["pair"]
        tp = m["planet"]
        mean = T.MIDPOINT.get((a, b), f"the story your {self.nm(a)} and {self.nm(b)} tell together")
        paras = [self.pk.one(T.MID_INTRO),
                 f"{NAME[tp]} {T.ASP_WORD[m['aspect']]}s the midpoint of your {self.nm(a)} and {self.nm(b)} at {m['pos'].split('°')[0]}° {m['pos'].split(' ')[-1]}, closest around {self.dt_(m['closest'])}. "
                 .replace("conjuncts", "sits on").replace("opposites", "opposes")
                 + f"This point is {mean}, and {NAME[tp]} {T.MID_VERB[tp]} it this month.",
                 f"Your {self.nm(a)} brings {T.PT[a]['ess']}, and your {self.nm(b)} brings {T.PT[b]['ess']}. " + self.pk.one([
                     "When a slow planet touches the point between them, they start working as one theme, and you may notice them showing up together in your life.",
                     "With this point activated, the two can't be separated this month. What affects one tends to stir the other.",
                     "For now they move as a pair, so pay attention to moments where both show up at once."])]
        mh = m.get("house")
        extra = []
        if mh and self.timed:
            extra.append(f"In your chart this point falls in your {hname(mh)}, so it plays out through {T.FOCUS[mh]}.")
        also = [c for c in getattr(self, "cur", []) if c["target"] in (a, b) and c["planet"] != tp and (c["planet"], c["target"]) not in self.oct_used]
        if also:
            self.oct_used.add((also[0]["planet"], also[0]["target"]))
            c0 = also[0]
            extra.append(f"{pn(c0['planet'], True)} is also making {an(T.ASP_NOUN[c0['aspect']])} {T.ASP_NOUN[c0['aspect']]} to your {self.nm(c0['target'])} this month, so this midpoint adds another layer to that story rather than starting a new one.")
        if extra:
            paras.append(" ".join(extra))
        return {"title": f"{NAME[tp]} {T.ASP_WORD[m['aspect']].capitalize()} Your {self.nm(a)} and {self.nm(b)} Midpoint",
                "eyebrow": f"Closest {self.dt_(m['closest'])}", "sub": f"Where your {self.nm(a)} and {self.nm(b)} meet.", "paras": paras,
                "octave": self.octave(tp, ocls(m["aspect"]), (a, b))}

    # ---------------------------------------------------------- parts
    def build(self):
        f, pk, M = self.f, self.pk, self.M
        cur, st_by = self.currents()
        self.cur = cur
        lead = cur[0] if cur else None
        theme_key = (lead["planet"], ocls(lead["aspect"])) if lead else ("none", "none")
        theme = pk.one(T.THEME.get(theme_key) or T.THEME[("none", "none")])
        self.theme = theme
        ev = self.events()
        self.ev = ev
        parts = [self.part_theme(cur, theme), self.part_season(), self.part_converge()]
        parts.append(self.part_currents(cur, st_by))
        parts.append(self.part_nodes())
        parts.append(self.part_personal())
        parts.append(self.part_lunar())
        parts.append(self.part_windows(ev))
        parts.append(self.part_calendar(ev))
        parts.append(self.part_charts())
        parts.append(self.part_ahead())
        parts.append(self.part_living(cur))
        parts = [p for p in parts if p and p.get("sections")]
        return {
            "name": self.name, "month": f"{M} {self.year}", "birthLabel": self.birth_label, "tagline": theme[0][:1] + theme[0][1:].lower(),
            "letter": self.letter(cur), "parts": parts, "finalSub": "Your Soul's Invitation", "final": self.final(cur),
            "more": T.MORE, "method": self.method(), "fine": T.FINE, "affirmations": self.affirmations(cur),
            "charts": {"a": wheel_chart(f, "natal"), "t": wheel_chart(f, "transit")},
        }

    def letter(self, cur):
        M, pr = self.M, self.prof
        hard = bool(cur) and ocls(cur[0]["aspect"]) in ("hard", "conj")
        p1 = f"Hey {self.name},"
        bd = dt.date.fromisoformat(pr["since"])
        if cur and cur[0]["planet"] in T.LETTER_HOOK:
            p2 = T.LETTER_HOOK[cur[0]["planet"]].format(M=M, short=T.PT[cur[0]["target"]]["short"])
        else:
            p2 = ("There are months when life asks you to build something new, and months when it asks you to reconsider what you've already built. "
                  + (f"{M} feels much more like the second kind, not because what you've created has lost its value, but because the person you're becoming is beginning to outgrow some of the shapes your life has taken."
                     if hard else f"{M} feels more like the first kind. Doors are opening, and the invitation is to walk through the ones that are truly yours."))
        acts = []
        for s in cur[:3]:
            verb = {0: "sits on", 180: "opposes", 90: "squares", 120: "trines", 60: "sextiles"}[s["aspect"]]
            st = next((x for x in self.f["stations"] if x["planet"] == s["planet"] and any(o["target"] == s["target"] for o in x["on"])), None)
            lead = f"{pn(s['planet'])} {('stations ' + st['kind'] + ' as it ') if st else ''}{verb} your natal {self.nm(s['target'])}"
            if self.is_year_lord(s["planet"]):
                lead = f"{pn(s['planet'])}, the ruler of your year, {('stations ' + st['kind'] + ' as it ') if st else ''}{verb} your natal {self.nm(s['target'])}"
            acts.append(lead)
        p3 = (f"Since your birthday in {T_MONTHS[bd.month - 1]}, you've been moving through {an(T.ORD[pr['house']])} {hname(pr['house'])} profection year, a year that brings {T.FOCUS[pr['house']]} into focus. "
              + (f"{M} sharpens that focus as {join(acts)}. " if acts else "")
              + self.letter_stations())
        focus = [T.PT[cur[0]["target"]]["short"]] if cur else []
        mh = self.mhouse()
        if T.HOUSE_ONE[mh] not in focus:
            focus.append(T.HOUSE_ONE[mh])
        p4 = (f"In the pages that follow I'll walk you through the season you're in, the big currents of {M}, the karmic pattern underneath them and the days that matter most. "
              f"As you read, notice what comes up around {join(focus)}: what feels familiar, what stirs something in you and what suddenly feels heavier or lighter than it used to. Those reactions are part of the message.")
        return [p1, p2, p3, p4]

    def letter_stations(self):
        sts = sorted(self.f["stations"], key=lambda x: x["date"])
        out = ""
        if len(sts) >= 2:
            d0, d1 = dt.date.fromisoformat(sts[0]["date"]), dt.date.fromisoformat(sts[-1]["date"])
            span = (d1 - d0).days
            out = (f"{cap(T.NUM.get(len(sts), str(len(sts))))} planets stand still this month"
                   + (f", all within {T.NUM.get(span + 1, str(span + 1))} days of each other" if span <= 5 else "")
                   + ", and a station is where a planet's energy is at its loudest.")
        elif len(sts) == 1:
            out = f"{pn(sts[0]['planet'], True)} stands still on {self.dt_(sts[0]['date'])}, and a station is where a planet's energy is at its loudest."
        th = self.top_theme()
        if th:
            out += (" " if out else "") + f"When I bring in your progressions and solar arcs, the theme they keep returning to is {th}."
        return out or "When I bring these movements together with your progressions and solar arcs, I see a larger transition unfolding."

    def headline(self, s):
        return (f"{NAME[s['planet']] if s['planet'] != 'north_node' else 'The North Node'} {T.ASP_WORD[s['aspect']]} your natal {self.nm(s['target'])} is the strongest current, "
                f"and it asks you to look at {T.PT[s['target']]['short']} with fresh eyes.")

    def part_theme(self, cur, theme):
        pk = self.pk
        paras = []
        OPEN = {"saturn": "the very qualities that have helped you succeed may need to be expressed differently for you to keep growing",
                "uranus": "a part of you that has waited a long time for room is asking to be let out",
                "neptune": "old definitions are softening before the new ones are fully clear",
                "jupiter": "life is offering you more room than you may be used to taking",
                "pluto": "something that has quietly held power in your life is ready to change shape",
                "chiron": "an old tender place is ready to be met in a new way",
                "north_node": "your soul's direction is coming into clearer view"}
        NOTBUT = {"saturn": ("become less capable", "become more selective about where you invest that capability"),
                  "jupiter": ("do more", "grow in the direction that is truly yours"),
                  "uranus": ("throw away the life you've built", "let more of your real self into it"),
                  "neptune": ("give up on what's practical", "let meaning guide what you build"),
                  "pluto": ("lose what you love", "stop holding it out of fear"),
                  "chiron": ("relive old pain", "meet it with the care you didn't receive then"),
                  "north_node": ("abandon what you know", "use it in service of where you're going")}
        for i, s in enumerate(cur[:3]):
            tp, tg = s["planet"], s["target"]
            noun = T.ASP_NOUN[s["aspect"]]
            th, nh = s["house"], self.P[tg]["house"]
            if i == 0:
                paras.append(f"{self.M} brings you to an interesting place in your evolution, where {OPEN[tp]}. "
                             f"Your {hname(self.prof['house'])} year has been asking you to look at {T.HOUSE[self.prof['house']]['ask']}, and this month that question becomes personal.")
                t = (f"{pn(tp, True)}'s {noun} to your natal {self.nm(tg)} in {self.P[tg]['sign']} brings this directly into {T.FOCUS[nh]}. "
                     f"{pn(tp, True)} asks {T.VOICE[tp]}, and your {self.nm(tg)} holds {T.PT[tg]['ess']}. "
                     f"{pn(tp, True)} isn't asking you to {NOTBUT[tp][0]}. It's asking you to {NOTBUT[tp][1]}.")
                if self.is_year_lord(tp) or self.is_year_lord(tg):
                    t += f" Because this is tied to the ruler of your year, it belongs to the bigger story of {self.yr()}."
            elif i == 1:
                t = (f"Meanwhile, {pn(tp)}'s {noun} to your natal {self.nm(tg)} opens another doorway. "
                     + (f"With {pn(tp)} moving through your {hname(th)} and your {self.nm(tg)} in your {hname(nh)}, the connection between {T.HOUSE_ONE[th]} and {T.HOUSE_ONE[nh]} becomes more important. " if th != nh else f"It all happens in your {hname(nh)}, among {T.FOCUS[nh]}. ")
                     + f"Where {pn(cur[0]['planet'])} asks {T.VOICE[cur[0]['planet']]}, {pn(tp)} asks {T.VOICE[tp]}.")
            else:
                t = (f"{pn(tp, True)}'s {noun} to your natal {self.nm(tg)} adds an even deeper dimension. It invites you to explore {T.PT[tg]['ess']}, "
                     f"and the way {T.FOCUS[nh]} have shaped them.")
            paras.append(t)
        if len(cur) >= 2:
            a = cur[0]["planet"]
            c1, c2 = T.CENTRAL[a]
            hs = []
            for s_ in cur[:3]:
                h_ = self.P[s_["target"]]["house"]
                if h_ not in hs:
                    hs.append(h_)
            reach = (f"Between them, these contacts reach into your {join([T.ORD[h] for h in hs])} houses, so {join([T.HOUSE_ONE[h] for h in hs])} are all being asked the same question from different sides. "
                     if len(hs) >= 2 else f"All of them come back to your {hname(hs[0])}, so {T.HOUSE_ONE[hs[0]]} is where this month really lives. ")
            paras.append(f"What makes {self.M} significant is that these aren't isolated experiences. {reach}"
                         f"The central question of {self.M} isn't {c1}. It's {c2}.")
        if not paras:
            paras.append(f"{self.M} is a quieter month in the big picture, with no slow planet making a close contact to your chart. That makes it a month of integration, a chance to let what you've learned settle into who you are, while the faster planets and the Moon mark the days that matter.")
        sec1 = {"title": theme[0], "paras": paras, "story": theme[1]}
        rows, seen = [], {}
        def add(h, why):
            seen.setdefault(h, [])
            if why not in seen[h]:
                seen[h].append(why)
        add(self.prof["month_house"], "Monthly profection")
        for s in self.f["stations"]:
            add(s["house"], f"{NAME[s['planet']]} turning {s['kind']}")
        for s in cur:
            add(self.P[s["target"]]["house"], f"{NAME[s['planet']] if s['planet'] != 'north_node' else 'North Node'} {T.ASP_WORD[s['aspect']]} your {self.nm(s['target'])}")
        for l in self.f["lunations"]:
            add(l["house"], ("New Moon" if l["kind"] == "new" else "Full Moon") + (" (eclipse)" if l["eclipse"] else ""))
        for h in sorted(seen):
            rows.append([T.ORD[h], cap(T.HOUSE[h]["area"]), cap(join(seen[h][:3]))])
        sec2 = {"title": f"Where {self.M} Lands in Your Chart",
                "paras": [f"Your chart holds twelve areas of life, but not every area gets the same attention each month. In {self.M} the energy gathers around the houses below."
                          + (lambda b: f" Your {hname(b)} is the busiest, with {T.NUM.get(len(seen[b]), str(len(seen[b])))} things touching it, so {T.HOUSE_ONE[b]} is where you're most likely to feel the month." if len(seen[b]) >= 2 else " What matters most isn't how many are lit up. It's how they talk to each other.")(max(seen, key=lambda h: len(seen[h])))
                          + ("" if self.timed else " Because your birth time isn't known, I'm reading your houses from your Sun sign, which still tells a true story about where the month's energy lands.")],
                "table": {"head": ["House", "Area of life", "What is touching it"], "widths": [0.16, 0.42, 0.42], "rows": rows}}
        return {"title": "Your Month's Soul Theme", "intro": f"What {self.M} is asking of you, and where it lands in your chart.",
                "sections": [sec1, sec2]}

    def part_season(self):
        pr, P, pk = self.prof, self.P, self.pk
        secs = []
        lord = pr["lord"]
        rising = "Sun sign" if not self.timed else "rising sign"
        p = [f"When you turned {pr['age']} on {when(pr['since'], None)}, {dt.date.fromisoformat(pr['since']).year}, your profection year moved into your {hname(pr['house'])}. "
             f"Counting by whole sign houses from your {self.f['natal']['rising_sign']} {rising.split()[0] if not self.timed else 'rising'}, that's {pr['sign']}, which makes {NAME[lord]} the planet in charge of your year until your next birthday.",
             T.HOUSE[pr["house"]]["long"],
             f"To see how this year works for you personally, I follow {NAME[lord]} back into your birth chart. Your {NAME[lord]} is in {pr['lord_sign']} in your {hname(pr['lord_house'])}. That ties this year's inner work to {T.LORD_HOUSE[pr['lord_house']]}."]
        dig = self.dignity(lord, pr["lord_sign"])
        self.sections_used.add(lord)
        if dig:
            p.append(T.DIGNITY_TEXT[dig].format(lord=NAME[lord], sign=pr["lord_sign"]))
        lord_hits = [s for s in self.f["slow"] if s["planet"] == lord or s["target"] == lord][:2]
        lord_st = [s for s in self.f["stations"] if s["planet"] == lord]
        if lord_st:
            p.append(f"{NAME[lord]} stations {lord_st[0]['kind']} on {self.dt_(lord_st[0]['date'])}, and because it rules your year, that station carries extra weight this month.")
        elif lord_hits:
            s = lord_hits[0]
            p.append(f"This month {('your year ruler ' + NAME[lord]) if s['planet'] == lord else pn(s['planet'])} makes {an(T.ASP_NOUN[s['aspect']])} {T.ASP_NOUN[s['aspect']]} to {'your natal ' + self.nm(s['target']) if s['planet'] == lord else 'your ' + NAME[lord]}, so the theme of your year is especially loud in {self.M}.")
        secs.append({"title": f"Your Year of the {T.ORD[pr['house']]} House", "eyebrow": "Annual profection", "paras": p})
        # monthly
        mp = []
        sh = pr["month_shift"]
        if sh:
            prev_sign = SIGNS[(SIGNS.index(sh["sign"]) - 1) % 12]
            mp.append(f"Around {self.dt_(sh['date'])}, your monthly profection moves from {prev_sign} into {sh['sign']}, your {hname(sh['house'])}, and {pn(sh['lord'])} becomes the planet in charge of your month. "
                      f"The early days of {self.M} still carry the {prev_sign} tone, and once {sh['sign']} takes over, the month {T.MONTH_HOUSE[sh['house']]}.")
            ml, mh = sh["lord"], sh["house"]
        else:
            mp.append(f"Through {self.M} your monthly profection is in {pr['month_sign']}, your {hname(pr['month_house'])}, with {pn(pr['month_lord'])} in charge of the month. That {T.MONTH_HOUSE[pr['month_house']]}.")
            ml, mh = pr["month_lord"], pr["month_house"]
        mlp = P[ml]
        self.sections_used.add(ml)
        mp.append(f"Your natal {NAME[ml]} is in {mlp['sign']} in your {hname(mlp['house'])}. {T.PT[ml]['role']} {self.natal_line(ml)}")
        if ml != lord:
            mp.append(f"The relationship between your year and your month tells an important story. {pn(lord, True)} asks {T.VOICE[lord]}, while {pn(ml)} asks {T.VOICE[ml]}. "
                      f"{pn(lord, True)} holds {T.PT[lord]['ess']}, and {pn(ml)} reminds you that {T.PT[ml]['ess']} belong in every decision too. The question isn't which one wins. It's whether the life you've built leaves room for both.")
        else:
            mp.append(f"{pn(ml, True)} rules both your year and your month right now, which makes this a concentrated time for {T.PT[ml]['short']}. Whatever it touches this month speaks for the whole year.")
        lun = [l for l in self.f["lunations"] if l["sign"] == (sh["sign"] if sh else pr["month_sign"])]
        if lun:
            l = lun[0]
            mp.append(f"The {'New' if l['kind'] == 'new' else 'Full'} Moon on {self.dt_(l['date'])} falls in {l['sign']}, the sign of your month, so the ruler of your month is literally lit up. Watch what it shows you about {T.HOUSE[l['house']]['short']}.")
        ch = self.chain_text()
        if ch:
            mp.append(ch)
        secs.append({"title": f"Your Month of {self.month_title(mh)}", "eyebrow": "Monthly profection", "paras": mp})
        # cycles
        for c in self.f["cycles"]:
            k = (c["planet"], c["aspect"])
            if k not in T.CYCLE:
                continue
            ttl, eb, paras = T.CYCLE[k]
            ps = c["passes"]
            pstr = join([when(d, None) + f", {d[:4]}" for d in ps[:4]]) if ps else "dates beyond this window"
            pp = [paras[0], paras[1].format(passes=pstr)]
            pid = c["planet"]
            if pid in P:
                h1, h2 = P[pid]["house"], self.f["sky"][pid]["house"]
                ax = (f"That lights up the axis between your {hname(h1)} and your {hname(h2)}, between {T.HOUSE[h1]['short']} and {T.HOUSE[h2]['short']}." if h1 != h2
                      else f"Both sit in your {hname(h1)}, so {T.HOUSE[h1]['short']} is where this cycle does its work.")
                pp.insert(1, f"Your natal {NAME[pid]} is in {P[pid]['sign']} in your {hname(h1)}, and transiting {NAME[pid]} is in {self.f['sky'][pid]['sign']} in your {hname(h2)}. " + ax)
            secs.append({"title": ttl, "eyebrow": eb, "paras": pp})
        # solar arcs
        sa = [x for x in self.f["solar_arcs"]["contacts"] if x["from"] in T.PT and x["target"] in T.PT][:3]
        if sa:
            pp = [pk.one(T.SA_INTRO)]
            for i, x in enumerate(sa):
                a, b = x["from"], x["target"]
                state = "exactly" if x["orb"] < 0.15 else ("approaching" if x["applying"] else "just past")
                verb = {0: "on", 90: "square", 180: "opposite"}[x["aspect"]]
                t = f"Your solar arc {self.nm(a)} is {state} {verb if state != 'exactly' else verb} your natal {self.nm(b)}"
                t += f", exact around {x['exact']}." if state != "exactly" else " right now."
                t += f" That connects {T.PT[a]['ess']} with {T.PT[b]['ess']}."
                if i == 0:
                    t += f" With your {self.nm(b)} in your {hname(P[b]['house'])}, this reaches into {T.HOUSE[P[b]['house']]['area']}, and it describes a change that unfolds over a year or more rather than in one month."
                pp.append(t)
            if len(sa) >= 2:
                pp.append("Together these arcs tell me the changes you're considering aren't a reaction to a hard month. They belong to a much longer season where your inner identity and your outer life are being brought into line.")
            secs.append({"title": "Your Solar Arcs", "eyebrow": "The slow turns of your life", "paras": pp})
        secs.append(self.progressions())
        opening = [f"Your monthly transits don't happen on their own. They sit inside much larger cycles that describe where you are in your life, and when several of those cycles point to the same theme, I pay closer attention. "
                   f"Here is the season {self.M} belongs to."]
        return {"title": "The Season You're In", "intro": "The bigger cycles holding this month.", "opening": opening, "sections": secs}

    def month_title(self, h):
        return {1: "Returning to Yourself", 2: "Remembering Your Worth", 3: "Finding Your Words", 4: "Coming Home",
                5: "Letting Joy In", 6: "Tending Your Days", 7: "Meeting Each Other", 8: "Letting Go",
                9: "Widening Your View", 10: "Stepping Forward", 11: "Finding Your People", 12: "Rest and Renewal"}[h]

    def dignity(self, pid, sign):
        if pid not in T.DOMICILE:
            return None
        if sign in T.DOMICILE[pid]:
            return "domicile"
        if T.EXALT.get(pid) == sign:
            return "exalted"
        if any(SIGNS[(SIGNS.index(s) + 6) % 12] == sign for s in T.DOMICILE[pid]):
            return "detriment"
        if T.EXALT.get(pid) and SIGNS[(SIGNS.index(T.EXALT[pid]) + 6) % 12] == sign:
            return "fall"
        return None

    def progressions(self):
        pg = self.f["progressed"]
        pm = pg["planets"]["moon"]
        ps = pg["planets"]["sun"]
        pp = []
        pp.append(f"Your progressed Moon is moving through {pm['sign']} in your {hname(pm['house'])}, {T.PMOON_SIGN[pm['sign']]}. It entered {pm['sign']} in {self.mname(pm['entered'])} and moves on in {self.mname(pm['leaves'])}. "
                  f"In your {hname(pm['house'])}, it keeps {T.HOUSE[pm['house']]['area']} in the foreground.")
        if pm["sign_change"]:
            pp.append(f"This month your progressed Moon changes sign, moving into {pm['end'].split(' ')[-1]}. Emotional shifts like this can feel subtle at first and then unmistakable.")
        pp.append(T.PHASE_TEXT[pg["phase"]] + f" The cycle began with your progressed New Moon in {pg['last_new_sign']} around {dt.date.fromisoformat(pg['last_new']).year}.")
        pc = [x for x in pg["contacts"] if x["from"] != "moon" and x["target"] in T.PT][:2]
        mc = [x for x in pg["contacts"] if x["from"] == "moon" and x["target"] in T.PT][:1]
        for x in pc + mc:
            verb = {0: "meeting", 90: "square", 180: "opposite", 120: "trine", 60: "sextile"}[x["aspect"]]
            pp.append(f"Your progressed {self.nm(x['from'])} is {verb} your natal {self.nm(x['target'])}, within {x['orb']:.1f}°. "
                      f"That brings {T.PT[x['from']]['ess']} into conversation with {T.PT[x['target']]['ess']}"
                      + (" for the next few months." if x["from"] == "moon" else ", a theme that builds slowly over the coming year."))
        pp.append(f"Your progressed Sun is at {ps['pos'].split('°')[0]}° {ps['sign']} in your {hname(ps['house'])}, so the slow story of who you're becoming runs through {T.HOUSE[ps['house']]['area']}.")
        return {"title": "Your Progressions", "eyebrow": "Your inner timing", "paras": pp}

    def mname(self, iso):
        d = dt.date.fromisoformat(iso)
        return f"{T_MONTHS[d.month - 1]} {d.year}"

    def part_currents(self, cur, st_by):
        secs = []
        covered = set()
        for i, s in enumerate(cur[:5]):
            secs.append(self.current_section(s, st_by, i))
            covered.add(s["planet"])
        for s in self.f["stations"]:
            if s["planet"] in SLOWP and s["planet"] not in covered:
                sec = self.station_section(s)
                if not sec["octave"]:
                    sec.pop("octave")
                secs.append(sec)
                covered.add(s["planet"])
        for m in self.f["midpoints"][:2]:
            if len(secs) >= 7:
                break
            secs.append(self.midpoint_section(m))
        if not secs:
            return None
        return {"title": f"The Big Currents of {self.M}", "intro": "The slow planets shaping the month.", "sections": secs}

    def part_nodes(self):
        P = self.P
        if "north_node" not in P:
            return None
        nn, sn = P["north_node"], P["south_node"]
        sr = RULER[SIGNS.index(sn["sign"])]
        snp = T.NODE_SIGN[sn["sign"]]
        nnp = T.NODE_SIGN[nn["sign"]]
        paras = [f"Your South Node is in {sn['sign']} in your {hname(sn['house'])}. In my work, the South Node describes the patterns your soul already knows so well they feel instinctive, the gifts and habits that have been reinforced again and again. "
                 f"With {sn['sign']} here, your familiar pull is toward {snp[1]}. In the {hname(sn['house'])}, all of that gets tied to {T.HOUSE[sn['house']]['area']}.",
                 f"When I follow the ruler of your South Node, I land on {NAME[sr]}, in {P[sr]['sign']} in your {hname(P[sr]['house'])}. "
                 + (f"That doubles the focus on {T.HOUSE[sn['house']]['area']} and tells me these themes are a big part of the pattern you came in with." if P[sr]["house"] == sn["house"]
                    else f"That links your familiar patterns to {T.HOUSE[P[sr]['house']]['area']}, so the gifts you came in with tend to show up there too.")
                 + " The gifts here are real. They only become confining when your sense of who you are depends on using them all the time.",
                 f"Your North Node in {nn['sign']} in your {hname(nn['house'])} points somewhere different. {nn['sign']} asks for {nnp[0]}, and the {hname(nn['house'])} asks you to grow into {T.HOUSE[nn['house']]['area']}. "
                 f"Moving from {sn['sign']} to {nn['sign']} is a lifelong journey, not something you finish in a month."]
        acts = []
        for h in self.f["fast"]:
            if h["target"] in ("south_node", "north_node") and h["aspect"] == 0:
                acts.append(f"{pn(h['planet'])} crosses your {'South' if h['target'] == 'south_node' else 'North'} Node on {self.dt_(h['date'])}")
        for s in self.f["slow"]:
            if s["target"] in ("north_node", "south_node") or s["target"] == sr:
                acts.append(f"{pn(s['planet'])} {s['aspect'] and 'makes ' + an(T.ASP_NOUN[s['aspect']]) + ' ' + T.ASP_NOUN[s['aspect']] + ' to' or 'sits on'} your {self.nm(s['target'])}"
                            + (", the ruler of your South Node" if s["target"] == sr else ""))
        for l in self.f["lunations"]:
            if l["house"] in (nn["house"], sn["house"]):
                acts.append(f"the {'New' if l['kind'] == 'new' else 'Full'} Moon lands in your {hname(l['house'])}")
        tn = self.f["sky"]["north_node"]
        acts.append(f"the transiting North Node is moving through your {hname(tn['house'])}")
        paras.append(f"{self.M} lights up this axis in a few ways. {cap(join(acts[:4]))}. All of this gives you a chance to notice where old patterns are running the show, and where you're ready to choose something new.")
        paras.append(f"You're not being asked to give up {snp[1]}. You're being invited to let it come from choice rather than habit, and to give {nnp[0]} a little more room.")
        return {"title": "The Karmic Pattern You're Invited to Transform", "intro": "Your nodes and the soul pattern underneath the month.",
                "sections": [{"title": f"Your Nodes and the {self.node_title(sn['house'])}", "paras": paras,
                              "close": f"When your {sn['sign']} gifts become an expression of who you are rather than proof of your worth, everything changes.",
                              "prompt": self.pk.one(T.PROMPT["south_node"])}]}

    def node_title(self, h):
        return {1: "Self You Know by Heart", 2: "Security You Know by Heart", 3: "Words You Know by Heart",
                4: "Home You Know by Heart", 5: "Joy You Know by Heart", 6: "Work You Know by Heart",
                7: "Partnerships You Know by Heart", 8: "Depths You Know by Heart", 9: "Wisdom You Know by Heart",
                10: "Ambition You Know by Heart", 11: "Circles You Know by Heart", 12: "Solitude You Know by Heart"}[h]

    def part_personal(self):
        secs = []
        sky = self.f["sky"]
        for pid in ("sun", "mercury", "venus", "mars"):
            s = sky[pid]
            h = s["house"]
            title = f"{'The ' if pid == 'sun' else ''}{NAME[pid]}, " + self.pk.one(T.PERSONAL_TITLE[pid]).format(short=cap(T.HOUSE[h]["short"]).replace("Your ", "Your "))
            p1 = [T.PERSONAL_HOUSE[pid].format(month=self.M, sign=s["sign"], h=T.ORD[h], area=T.HOUSE[h]["area"])]
            nat = [k for k, v in self.P.items() if v["house"] == h and k not in ("asc", "mc", "south_node", "north_node")]
            if nat:
                p1.append(f"Your natal {join([self.nm(k) for k in nat[:3]])} live{'s' if len(nat) == 1 else ''} in this house, so {pn(pid)} moving through it wakes up {'that part' if len(nat) == 1 else 'those parts'} of you as well.")
            ing = [i for i in self.f["ingresses"] if i["planet"] == pid]
            for i in ing[:2]:
                if i["kind"] == "sign":
                    ih = self.H(SIGNS.index(i["sign"]) * 30 + 15)
                    p1.append(f"{'The Sun' if pid == 'sun' else NAME[pid]} moves into {i['sign']} on {self.dt_(i['date'])}, turning your attention toward {T.SIGN_WORLD[i['sign']]}"
                              + (f", and in your chart toward {T.HOUSE[ih]['short']}." if ih != h else "."))
                else:
                    p1.append(f"On {self.dt_(i['date'])} it crosses into your {hname(i['house'])}, bringing {T.HOUSE[i['house']]['area']} into focus.")
            st = [x for x in self.f["stations"] if x["planet"] == pid]
            if st:
                p1.append(T.STATION[(pid, st[0]["kind"])].format(date=self.dt_(st[0]["date"]), pos=f"{st[0]['pos'].split('°')[0]}° {st[0]['sign']}",
                                                                  h=T.ORD[st[0]["house"]], area=T.HOUSE[st[0]["house"]]["area"]))
            elif s["retro"]:
                p1.append(f"{NAME[pid]} is retrograde this month, so this is a time to revisit and review rather than push ahead.")
            else:
                soon = [i for a_ in self.f.get("ahead", [])[:1] for i in a_["items"] if i.get("station") == pid]
                if soon:
                    p1.append(f"{NAME[pid]} is slowing down ahead of its {soon[0]['kind']} station on {when(soon[0]['date'], self.year)}, so you may feel your {'energy' if pid == 'mars' else 'attention'} turning inward before then.")
            for c in self.cur[:5]:
                if self.P[c["target"]]["house"] == h:
                    soft = pid in ("venus", "jupiter")
                    p1.append(f"This is the same part of your chart that {pn(c['planet'])}'s {T.ASP_NOUN[c['aspect']]} to your {self.nm(c['target'])} is reshaping, so {pn(pid)} "
                              + ("brings a softer influence into it, a reminder that this area can also be a source of restoration." if soft else
                                 "gives you everyday moments to notice that bigger work as it happens."))
                    break
            paras = [" ".join(p1)]
            hits = [x for x in self.f["fast"] if x["planet"] == pid and x["target"] in T.PT]
            hs, seen = [], set()
            for x in hits:
                if x["target"] == "north_node" and x["aspect"] == 180:
                    continue
                k = (x["target"], x["aspect"])
                if k in seen:
                    continue
                seen.add(k)
                verb = {0: "crosses", 180: "opposes", 90: "squares", 120: "trines"}[x["aspect"]]
                tgt = "your South Node and opposes your North Node" if x["target"] == "south_node" else f"your natal {self.nm(x['target'])}"
                mean = T.FAST_HIT.get((pid, x["aspect"]), "touches {ess}").format(ess=T.PT[x["target"]]["short"])
                hs.append(f"On {self.dt_(x['date'])} {'the Sun' if pid == 'sun' else NAME[pid]} {verb} {tgt}, which {mean}.")
                if len(hs) >= 4:
                    break
            if hs:
                paras.append(" ".join(hs))
            secs.append({"title": title, "paras": paras})
        return {"title": "Your Personal Planets This Month", "intro": "The Sun, Mercury, Venus and Mars, and the days they touch you.",
                "opening": ["The slow planets set the tone for the month, and the personal planets mark the days. They move quickly enough to touch your chart on specific dates, and those dates are where you're most likely to feel the bigger themes in everyday life."],
                "sections": secs}

    def part_lunar(self):
        secs = []
        tzl = TZ_LABEL.get(self.f["tz"], "")
        for l in self.f["lunations"]:
            new = l["kind"] == "new"
            h = l["house"]
            nm = "New Moon" if new else "Full Moon"
            eyebrow = f"{self.dt_(l['date'])}, {l['time']}{(' ' + tzl) if tzl else ''}, your {hname(h)}"
            paras = []
            flavor = (T.NM_SIGN if new else T.FM_SIGN)[l["sign"]]
            p1 = f"The {l['sign']} {nm} is {flavor}, and it falls in your {hname(h)}, the area of {T.HOUSE[h]['area']}."
            if not new:
                p1 += f" The Sun sits opposite in your {hname(l['sun_house'])}, so this Full Moon asks you to balance {T.HOUSE[l['sun_house']]['short']} with {T.HOUSE[h]['short']}."
            nat = [k for k, v in self.P.items() if v["house"] == h and k not in ("asc", "mc")]
            if nat:
                p1 += f" With your natal {join([self.nm(k) for k in nat[:3]])} in this house, this {'New' if new else 'Full'} Moon touches a big part of the pattern you were born with."
            paras.append(p1)
            r = l["ruler"]
            rp = self.P[r]
            rs = [s for s in self.f["stations"] if s["planet"] == r]
            p2 = f"{pn(r, True)} rules this {nm}, and in your chart it lives in {rp['sign']} in your {hname(rp['house'])}, so what happens here ties into {T.HOUSE[rp['house']]['area']}."
            if rs:
                p2 += f" {NAME[r]} also turns {rs[0]['kind']} on {self.dt_(rs[0]['date'])}, which makes this lunation part of a bigger turning point."
            roles = []
            if self.timed and r == self.f["natal"]["chart_ruler"]:
                roles.append("your chart ruler")
            if r == self.prof["lord"]:
                roles.append("the ruler of your year")
            if r == (self.prof["month_shift"]["lord"] if self.prof["month_shift"] else self.prof["month_lord"]):
                roles.append("the ruler of your month")
            if roles:
                p2 += f" {pn(r, True)} is also {join(roles)}, so following it back into your chart connects this lunation directly to the bigger story of your year."
            paras.append(p2)
            msign = self.prof["month_shift"]["sign"] if self.prof["month_shift"] else self.prof["month_sign"]
            if self.timed and l["sign"] == msign:
                wh = (SIGNS.index(l["sign"]) - SIGNS.index(self.f["natal"]["rising_sign"])) % 12 + 1
                if wh != h:
                    paras.append(f"Counted by whole sign houses, {l['sign']} is your {hname(wh)}, the house of your monthly profection, while in Placidus houses this lunation falls in your {hname(h)}. "
                                 f"I work with both. The whole sign house shows the bigger theme, and the Placidus house shows where the experience actually unfolds.")
            hits = [x for x in l["hits"] if x["target"] in T.PT][:2]
            if hits:
                hx = join([f"{T.ASP_WORD[x['aspect']]} your natal {self.nm(x['target'])}" if x["aspect"] else f"right on your natal {self.nm(x['target'])}" for x in hits])
                paras.append(f"This {nm} falls {hx}, so {T.PT[hits[0]['target']]['ess']} is personally in the light. "
                             + ("What you begin around it now has real staying power." if new else "Feelings around it may come to the surface so you can see them clearly."))
            near = [e for e in self.ev if e["kind"] in ("station", "slow", "profection") and e["w"] >= 5
                    and 0 < (dt.date.fromisoformat(e["date"]) - dt.date.fromisoformat(l["date"])).days <= 5]
            if near:
                near = sorted(near, key=lambda e: e["date"])[:3]
                paras.append(f"The timing is meaningful. In the days that follow, " + join([e["sent"].format(d=self.dt_(e["date"]))[:1].lower() + e["sent"].format(d=self.dt_(e["date"]))[1:] if not e["sent"].startswith(("Saturn", "Jupiter", "Neptune", "Uranus", "Pluto", "Chiron", "Venus", "Mars", "Mercury")) else e["sent"].format(d=self.dt_(e["date"])) for e in near])
                             + f". Intentions and insights from this {nm} feed directly into those turning points.")
            if l["eclipse"]:
                paras.append(T.ECLIPSE_NOTE["solar" if new else "lunar"].format(ecl=l["eclipse"]))
            if self.prof["month_sign"] == l["sign"] or (self.prof["month_shift"] and self.prof["month_shift"]["sign"] == l["sign"]):
                paras.append(f"It falls in the sign of your month, so the ruler of your month is literally lit up.")
            q = T.LUN_Q[h]
            secs.append({"title": f"{nm} at {l['deg']}° {l['sign']}", "eyebrow": eyebrow,
                         "sub": (T.LUN_SUB_NM if new else T.LUN_SUB_FM)[h], "paras": paras,
                         "practice": (T.LUN_PRACTICE_NM if new else T.LUN_PRACTICE_FM)[h], "questions": q})
        return {"title": "Your Lunar Journey", "intro": "The New Moon and Full Moon, and where they fall for you.",
                "opening": [f"The Moon's cycle gives every month a rhythm of beginning, building, seeing and releasing. Here is where {self.M}'s lunations fall in your chart, with a practice and a few questions for each."],
                "sections": secs}

    def part_windows(self, ev):
        import calendar
        last = calendar.monthrange(self.year, self.month)[1]
        cuts = [(1, 7), (8, 14), (15, 21), (22, 28), (29, last)] if last > 28 else [(1, 7), (8, 14), (15, 21), (22, 28)]
        secs = []
        used_titles = set()
        for a, b in cuts:
            es = [e for e in ev if a <= int(e["date"][8:10]) <= b and e["date"][:7] == f"{self.year}-{self.month:02d}"]
            es.sort(key=lambda e: -e["w"])
            top = es[0] if es else None
            key = top["key"] if top else "quiet"
            if key in ("profection",):
                key = es[1]["key"] if len(es) > 1 else "quiet"
            opts = [t for t in T.WINDOW_TITLE.get(key, T.WINDOW_TITLE["quiet"]) if t not in used_titles]
            if not opts:
                alt = [e for e in es[1:] if any(t not in used_titles for t in T.WINDOW_TITLE.get(e["key"], []))]
                if alt:
                    key = alt[0]["key"]
                    opts = [t for t in T.WINDOW_TITLE[key] if t not in used_titles]
            title_word = opts[0] if opts else "Moving Forward"
            used_titles.add(title_word)
            dates = f"{self.M} {a} to {b}" if a != b else f"{self.M} {a}"
            if es:
                chosen = sorted(es[:3], key=lambda e: e["date"])
                bits = [e["sent"].format(d=f"{self.M} {int(e['date'][8:10])}") for e in chosen]
                bits = [bits[0]] + [b[:4].replace("The ", "the ") + b[4:] for b in bits[1:]]
                big = len([e for e in es if e["w"] >= 7])
                opener = ""
                if big >= 3:
                    opener = self.cyc("wbig", T.WINDOW_OPEN_BIG).format(M=self.M)
                elif not [e for e in es if e["w"] >= 5]:
                    opener = self.cyc("wgentle", T.WINDOW_OPEN_GENTLE)
                atts = []
                for e in es[:3]:
                    a = e.get("att") or ""
                    if a and a not in atts:
                        atts.append(a)
                mean = (f"Together they touch {join(atts[:2])}. " if len(atts) >= 2 else (f"This touches {atts[0]}. " if atts else ""))
                txt = opener + (", ".join(bits[:-1]) + ", and " + bits[-1] if len(bits) > 1 else bits[0]) + ". " + mean
                g = self.pk.one(WINDOW_GUIDE.get(key, WINDOW_GUIDE["quiet"]))
                txt += g
            else:
                txt = "These are quieter days in your chart. " + self.pk.one(WINDOW_GUIDE["quiet"])
            secs.append({"eyebrow": dates, "title": f"Chapter {T.CHAPTER[len(secs)]}, {title_word}", "paras": [txt]})
        return {"title": f"Your {self.M}, Window by Window", "intro": "The month in five short chapters.",
                "opening": ["Here is the month told as five chapters of the same story, so you can see how the energy moves from week to week and how each part builds on the one before."],
                "sections": secs}

    def part_calendar(self, ev):
        grid_items = []
        ev_m = [e for e in ev if e["date"][:7] == f"{self.year}-{self.month:02d}"]
        per_day = {}
        for e in ev_m:
            d = int(e["date"][8:10])
            per_day.setdefault(d, []).append(e)
        top_w = sorted([e["w"] for e in ev_m], reverse=True)
        thr = top_w[min(5, len(top_w) - 1)] if top_w else 99
        for d in sorted(per_day):
            for e in sorted(per_day[d], key=lambda e: -e["w"])[:2]:
                grid_items.append([d, e["lab"], "a", e["w"] >= thr])
        rows = []
        for d in sorted(per_day):
            es = sorted(per_day[d], key=lambda e: -e["w"])[:3]
            rows.append([f"{MON[self.month - 1]} {d}", "; ".join(cap(e["long"]) for e in es[:2]), self.action(es[0])])
        imp = sorted(ev_m, key=lambda e: -e["w"])
        imp_rows, seen = [], set()
        for e in imp:
            d = int(e["date"][8:10])
            if d in seen:
                continue
            seen.add(d)
            imp_rows.append([f"{self.M} {d}", cap(e["long"]) + "."])
            if len(imp_rows) >= 6:
                break
        imp_rows.sort(key=lambda r: int(r[0].split()[-1]))
        return {"title": f"Your {self.M} Calendar", "intro": "A page to keep and come back to all month.",
                "opening": ["Use this calendar as a quick reference. The bold days are the ones I'd circle."],
                "sections": [{"title": f"{self.M} {self.year} at a Glance", "paras": [],
                              "grid": {"year": self.year, "month": self.month, "title": f"{self.M} {self.year} at a Glance",
                                       "sub": "A page to keep and come back to all month.", "legend": None, "items": grid_items}},
                             {"title": "Key Dates", "paras": [], "table": {"head": ["Date", "What happens", "How to work with it"],
                                                                          "widths": [0.13, 0.5, 0.37], "rows": rows}},
                             {"title": "Your Most Important Days", "paras": [], "table": {"head": ["Date", "Why it matters"], "widths": [0.22, 0.78], "rows": imp_rows}}]}

    def part_charts(self):
        houses = "Placidus houses" if self.timed else "solar houses from your Sun sign (your birth time isn't known)"
        return {"title": "Your Charts", "intro": "Your birth chart and this month's sky.",
                "sections": [{"title": "Your Birth Chart", "paras": [f"Your chart with {houses}, the major aspects drawn in the center and every placement listed below."],
                              "natal": {"key": "a"}},
                             {"title": f"Your Chart and {self.M}'s Sky",
                              "paras": [f"Here is your birth chart in the inner ring, with your houses, and the planets as they stand on {self.M} 15 in the outer ring. The lines in the center connect a transiting planet to one of yours when they're within 1° of an exact aspect."],
                              "image": {"kind": "biwheel", "inner": "a", "outer": "t", "w": 430,
                                        "caption": f"Inner ring your birth chart   ·   Outer ring {self.M} 15 transits"}}]
                + ([self.chart_pattern()] if self.chart_pattern() else [])}

    def part_ahead(self):
        rows = []
        for c in self.f["cycles"]:
            k = (c["planet"], c["aspect"])
            if k in T.CYCLE:
                nxt = [d for d in c["passes"] if d > f"{self.year}-{self.month:02d}-31"]
                rows.append([T.CYCLE[k][0].replace("Your ", ""), "Active now", self.mname(nxt[0]) if nxt else "Completing"])
        for s in self.cur[:4]:
            nxt = [d for d in s["passes"] if d > f"{self.year}-{self.month:02d}-31"]
            if nxt:
                rows.append([f"{NAME[s['planet']] if s['planet'] != 'north_node' else 'North Node'} {T.ASP_WORD[s['aspect']]} your {self.nm(s['target'])}",
                             "Exact this month" if s["exact"] else "In orb", self.mname(nxt[0])])
        for x in [x for x in self.f["solar_arcs"]["contacts"] if x["applying"] and x["from"] in T.PT and x["target"] in T.PT][:2]:
            rows.append([f"Solar arc {self.nm(x['from'])} {T.ASP_WORD[x['aspect']]} your {self.nm(x['target'])}", "Building slowly", x["exact"]])
        secs = []
        if rows:
            secs.append({"title": "Your Developing Cycles", "paras": [], "table": {"head": ["Cycle", "Where it is now", "Next big moment"],
                                                                                   "widths": [0.48, 0.28, 0.24], "rows": rows[:7]}})
        for a in self.f.get("ahead", []):
            items = a["items"]
            st = [i for i in items if "station" in i]
            ex = [i for i in items if "planet" in i and i["target"] in T.PT]
            bits = []
            for i in st[:3]:
                bits.append(f"{NAME[i['station']]} turns {i['kind']} on {when(i['date'], None)} in your {hname(i['house'])}, turning attention to {T.HOUSE[i['house']]['area']}.")
            for i in ex[:3]:
                bits.append(f"{NAME[i['planet']] if i['planet'] != 'north_node' else 'The North Node'} {T.ASP_WORD[i['aspect']]} your natal {self.nm(i['target'])} on {when(i['date'], None)}, touching {T.PT[i['target']]['short']}.")
            for l in a["lunations"]:
                if l["eclipse"]:
                    bits.append(f"The {l['eclipse']} on {when(l['date'], None)} falls in {l['sign']} in your {hname(l['house'])}, opening a new chapter around {T.HOUSE[l['house']]['area']}.")
            if not bits:
                l = a["lunations"][0] if a["lunations"] else None
                bits.append(f"{a['month_name']} is quieter in the big picture"
                            + (f", and the {'New' if l['kind'] == 'new' else 'Full'} Moon in {l['sign']} lights up your {hname(l['house'])}." if l else "."))
            tw = self.ahead_title(st, ex)
            secs.append({"title": f"{a['month_name']} {a['year']}, {tw}", "paras": [" ".join(bits[:4])]})
        return {"title": "What's Quietly Building", "intro": "The cycles still unfolding, and a look ahead.",
                "opening": [f"Some of what you feel in {self.M} is the beginning of something bigger. Here is what is still developing and what the next two months bring."],
                "sections": secs}

    def ahead_title(self, st, ex):
        if st:
            return {"mercury": "Reviewing and Rethinking", "venus": "Revisiting What You Value", "mars": "Turning Your Energy Inward",
                    "jupiter": "Growing From the Inside", "saturn": "Reconsidering Your Foundations", "uranus": "Preparing for Change",
                    "neptune": "Listening for the Next Dream", "pluto": "Going Deeper"}.get(st[0]["station"], "A New Rhythm")
        if ex:
            return {"jupiter": "Opening New Doors", "saturn": "Building Carefully", "uranus": "Making Room for Change",
                    "neptune": "Trusting the Unseen", "pluto": "Deepening", "chiron": "Healing Forward",
                    "north_node": "Following Your Path"}.get(ex[0]["planet"], "Moving Forward")
        return "A Gentler Rhythm"

    def part_living(self, cur):
        planets = []
        for s in cur:
            if s["planet"] not in planets:
                planets.append(s["planet"])
        if not planets:
            planets = ["north_node"]
        lean = join([T.LEAN[p] for p in planets[:4]])
        gentle = join([T.GENTLE[p] for p in planets[:3]])
        mh = self.mhouse()
        moon = self.P["moon"]["sign"]
        lp = (f"{self.M} supports {lean}. Give your attention to what is already working in {T.HOUSE[mh]['short']}, and let each step be one you've chosen rather than one you feel pushed into. "
              f"Your {moon} Moon is restored by {T.SIGN[moon]['need']}, so let yourself have that without making it earn its place.")
        tg0 = cur[0]["target"] if cur else "moon"
        gp = (f"Be gentle with {gentle}. When you notice them, especially around {T.PT[tg0]['short']}, pause before you react, and ask what you actually need. "
              f"Not every feeling this month is an instruction. Some of them are simply showing you what has been asking for your care.")
        ints = [T.INTENTION[p] for p in planets[:2]] + [T.INTENTION["year"]]
        qs, used = [], set()
        for s in cur[:4]:
            for q in T.PROMPT.get(s["target"], []):
                if q not in self.pk.used and q not in used:
                    qs.append(q)
                    used.add(q)
                    break
        nxt = T_MONTHS[self.month % 12]
        snp, nnp = T.NODE_SIGN[self.P["south_node"]["sign"]], T.NODE_SIGN[self.P["north_node"]["sign"]]
        extra = [f"What has {self.M} shown me about {T.HOUSE[self.prof['house']]['area']}?",
                 f"Where did I catch myself reaching for {snp[1]} out of habit?",
                 f"What would it look like to give {nnp[0]} a little more room?",
                 f"What am I willing to leave behind as I move into {nxt}?",
                 "Which parts of my future can I already begin to live?"]
        for q in extra:
            if len(qs) >= 6:
                break
            if q not in used:
                qs.append(q)
        return {"title": "Living With This Month", "intro": "How to work with the energy, day to day.",
                "opening": [f"Astrology is most useful when it changes how you live. Here is how I'd carry {self.M} with you."],
                "sections": [{"title": "What to Lean Into", "paras": [lp]}, {"title": "What to Be Gentle With", "paras": [gp]},
                             {"title": f"Your Three Intentions for {self.M}", "paras": ints, "italic": True},
                             {"title": "Your End of Month Reflection", "paras": [f"Come back to these questions at the end of {self.M} and notice how your answers have shifted over the month."],
                              "questions": qs[:6]}]}


    def action(self, e):
        k = e.get("kind")
        hmatch = None
        if k == "lunation":
            l = next((x for x in self.f["lunations"] if x["date"] == e["date"]), None)
            if l:
                return T.ACTION[l["kind"]].format(area=T.HOUSE[l["house"]]["short"]) + "."
        if k == "profection" and self.prof["month_shift"]:
            return T.ACTION["profection"].format(area=T.HOUSE[self.prof["month_shift"]["house"]]["short"]) + "."
        if k == "ingress":
            return T.ACTION["ingress"].format(area=e["att"]) + "."
        key = e.get("key")
        asp = e.get("asp")
        if asp is not None:
            c = ocls(asp)
            if key in ("venus",) and asp == 120:
                c = "soft"
            a = T.ACTION.get((key, c)) or T.ACTION.get((key, "hard" if c != "conj" else "conj"))
            if a:
                return a + "."
        if k == "station":
            return T.ACTION["station"] + "."
        return cap(e["att"]) + "." if e["att"] else ""

    def indicators(self):
        """Every technique's contribution, tagged with the themes it speaks to."""
        PT_TH = {"uranus": ["freedom"], "saturn": ["responsibility"], "jupiter": ["voice"], "neptune": ["healing"],
                 "chiron": ["healing"], "pluto": ["power"], "north_node": ["karmic"], "south_node": ["karmic"],
                 "sun": ["freedom"], "moon": ["responsibility"], "mercury": ["voice"], "venus": ["love"], "mars": ["power"],
                 "asc": ["freedom"], "mc": ["direction"]}
        H_TH = {1: "freedom", 2: "responsibility", 3: "voice", 4: "responsibility", 5: "love", 6: "direction", 7: "love",
                8: "power", 9: "voice", 10: "direction", 11: "freedom", 12: "healing"}
        out = []
        pr = self.prof
        out.append((f"{T.ORD[pr['house']]} house profection year", {H_TH[pr["house"]]} | set(PT_TH.get(pr["lord"], []))))
        mh = pr["month_shift"]["house"] if pr["month_shift"] else pr["month_house"]
        out.append((f"{T.ORD[mh]} house monthly profection", {H_TH[mh]}))
        for s in self.cur[:5]:
            th = set(PT_TH.get(s["planet"], [])) | set(PT_TH.get(s["target"], []))
            out.append((f"{pn(s['planet'], True)} {T.ASP_WORD[s['aspect']]} {self.nm(s['target'])}", th))
        for c in self.f["cycles"]:
            if (c["planet"], c["aspect"]) in T.CYCLE:
                out.append((T.CYCLE[(c["planet"], c["aspect"])][0].replace("Your ", ""), set(PT_TH.get(c["planet"], []))))
        for x in [x for x in self.f["solar_arcs"]["contacts"] if x["from"] in T.PT and x["target"] in T.PT][:3]:
            out.append((f"Solar arc {self.nm(x['from'])} {T.ASP_WORD[x['aspect']]} {self.nm(x['target'])}",
                        set(PT_TH.get(x["from"], [])) | set(PT_TH.get(x["target"], []))))
        pg = self.f["progressed"]
        out.append((f"Progressed Moon in the {T.ORD[pg['planets']['moon']['house']]}", {H_TH[pg["planets"]["moon"]["house"]]}))
        out.append((f"Progressed Sun in the {T.ORD[pg['planets']['sun']['house']]}", {H_TH[pg["planets"]["sun"]["house"]]}))
        for x in [x for x in pg["contacts"] if x["from"] != "moon" and x["target"] in T.PT][:2]:
            out.append((f"Progressed {self.nm(x['from'])} {T.ASP_WORD[x['aspect']]} {self.nm(x['target'])}",
                        set(PT_TH.get(x["from"], [])) | set(PT_TH.get(x["target"], []))))
        for st in self.f["stations"]:
            if st["planet"] in SLOWP:
                out.append((f"{NAME[st['planet']]} {'retrograde' if st['kind'] == 'retrograde' else 'direct'} in the {T.ORD[st['house']]}",
                            {H_TH[st["house"]]} | set(PT_TH.get(st["planet"], []))))
        for h in self.f["fast"]:
            if h["target"] == "south_node" and h["aspect"] == 0 and h["planet"] in ("sun", "mercury"):
                out.append((f"{NAME[h['planet']]} on your South Node", {"karmic"}))
        for l in self.f["lunations"]:
            out.append((f"{'New' if l['kind'] == 'new' else 'Full'} Moon in the {T.ORD[l['house']]}", {H_TH[l["house"]]}))
        sr = RULER[SIGNS.index(self.P["south_node"]["sign"])] if "south_node" in self.P else None
        for s in self.cur[:5]:
            if s["target"] == sr:
                out.append((f"{pn(s['planet'], True)} on your South Node ruler", {"karmic"}))
        return out

    def part_converge(self):
        ind = self.indicators()
        by = {}
        for lab, th in ind:
            for t in th:
                by.setdefault(t, []).append(lab)
        ranked = sorted([(k, v) for k, v in by.items() if len(v) >= 3], key=lambda kv: -len(kv[1]))[:4]
        if not ranked:
            return None
        rows = [[T.CONVERGE[k][0], f"{len(v)} indicators", join(v[:5])] for k, v in ranked]
        top = ranked[0]
        p1 = (f"When several timing techniques point to the same theme at the same time, I pay closer attention, because that's where a month stops being a list of transits and starts telling a story. "
              f"In {self.M} the strongest convergence is around {T.CONVERGE[top[0]][0].lower()}. {T.CONVERGE[top[0]][1]}")
        paras = [p1]
        if len(ranked) > 1:
            sec = ranked[1]
            shared = [x for x in top[1] if x in sec[1]]
            paras.append(f"Close behind it is {T.CONVERGE[sec[0]][0].lower()}. "
                         + (f"{cap(join(shared[:2]))} {'speaks' if len(shared[:2]) == 1 else 'speak'} to both, which is why I read them as two sides of the same transition rather than two separate experiences. "
                            if shared else "When I see these two themes together, I read them as two sides of the same transition rather than two separate experiences. ")
                         + f"What changes around {T.CONVERGE[top[0]][0].lower()} is likely to ask for change around {T.CONVERGE[sec[0]][0].lower()} too.")
        return {"title": "Where Your Cycles Converge", "intro": f"The themes {self.M} keeps repeating.",
                "sections": [{"title": f"The Themes Your Chart Keeps Repeating", "paras": paras,
                              "table": {"head": ["Theme", "Strength", "Indicators"], "widths": [0.3, 0.16, 0.54], "rows": rows},
                              "after": ["This grouping shows where techniques agree. It isn't a probability or an intensity score, and some indicators speak to more than one theme."]}]}

    def chain_text(self):
        pr, P = self.prof, self.P
        yl = pr["lord"]
        ml = pr["month_shift"]["lord"] if pr["month_shift"] else pr["month_lord"]
        cr = self.f["natal"]["chart_ruler"] if self.timed else None
        names = []
        bits = []
        if cr and cr in (yl, ml):
            bits.append(f"{pn(cr, True)} is also your chart ruler, the planet of your {self.f['natal']['rising_sign']} rising, so this month's lessons land very close to home.")
        for a, b in ((yl, ml), (yl, cr), (ml, cr)):
            if not a or not b or a == b:
                continue
            o = sep(P[a]["lon"], P[b]["lon"])
            for asp in (0, 60, 90, 120, 180):
                if abs(o - asp) <= 6:
                    bits.append(f"In your birth chart your {NAME[a]} and {NAME[b]} are {'together' if asp == 0 else 'in ' + an(T.ASP_NOUN[asp]) + ' ' + T.ASP_NOUN[asp]}, so these rulers already know each other well.")
                    break
            if RULER[SIGNS.index(P[b]["sign"])] == a:
                bits.append(f"Your {NAME[b]} sits in {P[b]['sign']}, a sign ruled by {NAME[a]}, so {NAME[a]} has the final say over how {NAME[b]} expresses itself.")
        hit = [s for s in self.f["slow"] if s["target"] in (yl, ml, cr) or s["planet"] in (yl, ml)]
        if hit:
            s = hit[0]
            bits.append(f"This month {pn(s['planet'])}'s {T.ASP_NOUN[s['aspect']]} to your {self.nm(s['target'])} touches this chain of rulers directly, which is why I treat it as one of the month's main threads.")
        uniq = []
        for b in bits:
            if b not in uniq:
                uniq.append(b)
        return " ".join(uniq[:3])

    def chart_pattern(self):
        hs = []
        for s in self.cur[:5]:
            for h in (s["house"], self.P[s["target"]]["house"]):
                if h not in hs:
                    hs.append(h)
        hs = hs[:5]
        if len(hs) < 2:
            return None
        lst = join([f"your {hname(h)}, {T.HOUSE[h]['short']}" for h in hs])
        return {"title": "Understanding the Pattern in Your Chart",
                "paras": [f"When you look at your birth chart alongside {self.M}'s sky, notice how several areas of your life are being touched at once. This month the lines gather around {lst}.",
                          self.pattern_link()]}

    def pattern_link(self):
        c = self.cur
        t = "Rather than reading each line as a separate influence, notice how the planets connect these areas."
        if len(c) >= 2:
            a, b = c[0], c[1]
            t += (f" {pn(a['planet'], True)} reaches your {self.nm(a['target'])} from your {hname(a['house'])} while {pn(b['planet'])} reaches your {self.nm(b['target'])} from your {hname(b['house'])}, "
                  f"so a change you make around {T.PT[a['target']]['short']} may be inseparable from what is developing around {T.PT[b['target']]['short']}.")
        return t

    def final(self, cur):
        pr = self.prof
        SPACE = {"saturn": ("mastery", "liberation"), "jupiter": ("what is enough", "what is possible"),
                 "uranus": ("stability", "freedom"), "neptune": ("what you know", "what you sense"),
                 "pluto": ("holding on", "letting go"), "chiron": ("protection", "healing"), "north_node": ("the familiar", "the new")}
        lead = cur[0]["planet"] if cur else "north_node"
        sp = SPACE[lead]
        out = [f"When I bring together your transits, profections, progressions, solar arcs and nodes, I see a soul moving through the space between {sp[0]} and {sp[1]}. "
               f"Your {hname(pr['house'])} year has kept {T.FOCUS[pr['house']]} at the heart of everything, and {self.M} adds a chapter where that work becomes personal."]
        asks = []
        for s in cur[:3]:
            asks.append(FINAL_ASK[s["planet"]].format(np=self.nm(s["target"])))
        if asks:
            out.append(f"Your {hname(pr['house'])} year asks you to look at {T.HOUSE[pr['house']]['ask']}, while {asks[0]}. "
                       + (cap(asks[1]) + "." if len(asks) > 1 else "") + (f" And {asks[2]}." if len(asks) > 2 else ""))
        if self.f["solar_arcs"]["contacts"] or self.f["progressed"]["contacts"]:
            conv = self.part_converge()
            th = conv["sections"][0]["table"]["rows"][0][0].lower() if conv else ""
            out.append("Your progressions and solar arcs tell me this isn't only about one month. Your inner world has been developing in a direction your outer life may now need to make room for"
                       + (f", and the theme they keep returning to is {th}." if th else "."))
        nn, sn = self.P["north_node"], self.P["south_node"]
        out.append(f"Your nodes tell the same story from another angle. You're learning to move from {T.NODE_SIGN[sn['sign']][1]} toward {T.NODE_SIGN[nn['sign']][0]}, and what you give feels truer when it comes from freedom rather than habit.")
        if self.f["cycles"]:
            ck = [T.CYCLE[(c["planet"], c["aspect"])][0] for c in self.f["cycles"] if (c["planet"], c["aspect"]) in T.CYCLE]
            nm_ = ck[0].replace("Your ", "your ") if ck else "the bigger cycles you're living through"
            out.append(f"{cap(nm_)} tells me this month is part of a real turning point. You don't have to rush that chapter, and you don't have to leave the person you've been behind to step into it.")
        octs = []
        for s in cur:
            o = OCT_SHORT[s["planet"]]
            if o not in octs:
                octs.append(o)
        if len(octs) < 3:
            octs += [x for x in ("rest without guilt", "love without losing yourself", "growth without overwhelm") if x not in octs]
        out.append({"bold": f"The higher octave of {self.M} is {join(octs[:3])}."})
        out.append(self.pk.one(CLOSERS))
        return out

    def method(self):
        node = "True Node" if self.f["node"] == "true" else "Mean Node"
        houses = "Placidus houses" if self.timed else "solar houses counted from your Sun sign, because your birth time isn't known"
        return [f"Your chart is calculated for {self.birth_label}, using the Swiss Ephemeris, the tropical zodiac, {houses} and the {node}. Monthly positions are calculated the same way for {self.M} {self.year}, with times shown in your local time zone.",
                f"Annual and monthly profections use whole sign houses counted from your {'rising sign' if self.timed else 'Sun sign'}, with traditional rulers. Transits from Jupiter outward are included when they come within 1° of an aspect to your chart, with their exact dates, and stations are included when they fall within 1° of an aspect. Exact aspects from the Sun, Mercury, Venus and Mars are listed on the day they happen.",
                "Secondary progressions use the day for a year method. Solar arcs use the true solar arc, measured by the progressed Sun. Both are included only within 1°. Midpoints use the short-way rule, hard aspects only, within 1°. Lunations and eclipses are read by the house they fall in, their ruler and any close contacts to your chart.",
                "I give the most weight to stations, the planets ruling your year and month, the angles of your chart, and themes repeated by more than one technique. An exact date is when a contact is mathematically exact, not a promise of an outer event. A transit can be felt before it's exact and after it passes, especially when retrograde motion brings it back more than once. Every reading here is built on my own research and methodology, and you're always welcome to use your own."]

    def affirmations(self, cur):
        out = []
        for s in cur:
            for a in T.AFFIRM[s["planet"]]:
                if a not in out:
                    out.append(a)
                    break
        for a in T.AFFIRM["any"]:
            if len(out) >= 8:
                break
            if "woman" in a and self.pron != "she":
                continue
            if a == "I honor who I am becoming." and self.pron == "she":
                continue
            if a not in out:
                out.append(a)
        return out[:8]


TITLE = {"sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars", "jupiter": "Jupiter",
         "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto", "chiron": "Chiron",
         "north_node": "North Node", "asc": "Ascendant", "mc": "Midheaven"}


def wheel_chart(f, which):
    w = f["wheel"]
    src = w["natal"] if which == "natal" else w["transit"]
    rr = w["natal_retro"] if which == "natal" else w["transit_retro"]
    return {"planets": {TITLE[k]: v for k, v in src.items() if k in TITLE},
            "retro": {TITLE[k]: True for k in rr if k in TITLE}, "cusps": w["cusps"], "solar": not w["timed"]}


def T_NATAL(pid):
    return NATAL_SIGN[pid]


def build_solo(f, name, birth_label, pron="she"):
    return Builder(f, name, birth_label, pron).build()
