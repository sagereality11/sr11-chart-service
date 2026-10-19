"""Assemble Your Birth Chart's Wealth Story from the wealth analysis.

Output: {"title", "subtitle", "name", "birth", "sections": [{"id", "heading", "level", "paragraphs"}],
"snapshot": {...}, "signoff", "disclaimer"}. Level 1 sections are the navigation entries;
level 2 sections are nested under the section before them.
"""
from __future__ import annotations

import datetime as dt
import re

from . import wealth as W
from . import wealth_text as T

TITLE = "Your Birth Chart's Wealth Story"
HOUSE_SHORT = {1: "self", 2: "income", 3: "communication", 4: "home", 5: "creativity", 6: "daily work",
               7: "partnership", 8: "shared resources", 9: "knowledge", 10: "career", 11: "community",
               12: "quiet, behind-the-scenes work"}
RULE_SHORT = {**HOUSE_SHORT, 11: "gains", 8: "shared resources", 6: "daily work"}
VERB3 = {"conjunction": "sits with", "sextile": "sextiles", "square": "squares", "trine": "trines", "opposition": "opposes"}
NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
MALEFIC = {"mars", "saturn", "uranus", "neptune", "pluto", "chiron"}
BENEFIC = {"venus", "jupiter"}
PLANET_WEIGHT = {"pluto": 4.0, "neptune": 3.0, "uranus": 3.2, "saturn": 3.4, "jupiter": 2.4}


def the(pid):
    n = W.NAME[pid]
    if pid in ("north_node", "south_node"):
        return f"your {n}"
    return f"the {n}" if pid in ("sun", "moon") else n


def The(pid):
    return cap(the(pid))


def dg(n):
    return f"{n} degree" if n == 1 else f"{n} degrees"


def join(items, conj="and"):
    items = [i for i in items if i]
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"
    return ", ".join(items[:-1]) + f", {conj} " + items[-1]


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def degs(x):
    x = round(x, 1)
    if x < 1:
        return "less than a degree"
    if x < 2:
        return "less than two degrees"
    n = int(round(x))
    return f"about {NUM.get(n, n)} degrees"


def when(h, today):
    s, e = h["start"], h["end"]
    if h.get("ongoing_start") or s <= today + dt.timedelta(days=3):
        return f"from now through {W.month_year(e)}" if not h.get("ongoing_end") else "throughout the coming year"
    if (s.year, s.month) == (e.year, e.month):
        return f"in {W.part_of_month(s)} {W.month_year(s)}"
    if s.year == e.year:
        tail = " and beyond" if h.get("ongoing_end") else ""
        return f"from {W.MONTHS[s.month - 1]} through {W.month_year(e)}{tail}"
    tail = " and beyond" if h.get("ongoing_end") else ""
    return f"from {W.month_year(s)} through {W.month_year(e)}{tail}"


def prof_next(prof):
    """If the birthday that starts the next profection year is close, name it."""
    days = (prof["until"] - prof["today"]).days if prof.get("today") else 999
    if days > 75:
        return ""
    nh = prof["house"] % 12 + 1
    lord = prof["next_lord"]
    return (f"Your birthday in {W.month_year(prof['until'])} begins {T.PROFECTION[nh].split(',')[0].replace('a ', 'a new ', 1).replace('an ', 'a new ', 1)}, "
            f"with {the(lord)} taking over as lord of the year, so the second half of this window carries that new theme.")


class Writer:
    """Collects paragraphs and refuses to print the same sentence twice."""

    def __init__(self):
        self.seen = set()
        self.sections = []

    def section(self, sid, heading, level=1):
        self.sections.append({"id": sid, "heading": heading, "level": level, "paragraphs": []})

    def para(self, *parts):
        out = []
        for p in parts:
            if not p:
                continue
            for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", p.strip()):
                key = re.sub(r"\W+", " ", s.lower()).strip()
                if key and key not in self.seen:
                    self.seen.add(key)
                    out.append(s)
        if out:
            txt = re.sub(r"\b(1|one) degrees\b", r"\1 degree", " ".join(out))
            self.sections[-1]["paragraphs"].append(txt)


def build_reading(a: dict, name: str, birth: dict) -> dict:
    P = a["planets"]
    R = a["rulers"]
    today = a["today"]
    r2 = R[2]
    rc = R[10]
    rf = W.RULER[P["fortune"]["sign"]]
    roles = a["roles"]
    w = Writer()
    described = {}      # planet -> section id where its full description lives
    used_contacts = set()

    def loc(pid):
        p = P[pid]
        return f"{p['sign']} in your {T.ORD[p['house']]} house"

    def contact_text(pid, kinds=("conj", "soft", "hard"), only=None, skip=None, limit=2, lead=True, subject=None):
        out = []
        for asp in P[pid]["aspects"]:
            o = asp["other"]
            if o in ("asc", "mc", "ic", "dsc", "fortune", "assets") or o == "south_node":
                continue
            cls = T.ASPECT_CLASS[asp["type"]]
            if cls not in kinds or (only and o not in only) or (skip and o in skip):
                continue
            key = tuple(sorted((pid, o)))
            if key in used_contacts or o not in T.CONTACT:
                continue
            txt = T.CONTACT[o][cls]
            first = re.split(r"(?<=[.!?])\s+", txt)[0]
            if re.sub(r"\W+", " ", first.lower()).strip() in w.seen:
                continue
            used_contacts.add(key)
            if cls == "conj":
                txt = re.sub(r"\bit\b", (subject.rstrip(",") + ",") if subject else the(pid), txt, count=1)
            elif lead:
                txt = f"{subject or The(pid)} {VERB3[asp['type']]} {the(o)}. " + txt
            out.append(txt)
            if len(out) >= limit:
                break
        return " ".join(out)

    def stars_for(point):
        lines = []
        hits = [s for s in a["stars"] if s["point"] == point and not s.get("used")]
        for s in hits:
            s["used"] = True
            ep, txt = T.STAR.get(s["star"], (None, None))
            if not ep:
                continue
            others = [x for x in a["stars"] if x["star"] == s["star"] and not x.get("used")]
            pt = T.STAR_PT.get(point) or W.NAME[point]
            orb = "about {} minutes of arc".format(int(round(s["orb"] * 60))) if s["orb"] < 1 else "a degree"
            line = T.STAR_LINE.format(pt=pt, star=T.STAR_NAME.get(s["star"], s["star"]), epithet=ep, orb=orb, txt=txt)
            for x in others:
                x["used"] = True
                line += " " + T.STAR_ALSO.format(star=T.STAR_NAME.get(s["star"], s["star"]),
                                                 pt=T.STAR_PT.get(x["point"]) or W.NAME[x["point"]])
            lines.append(line)
        return " ".join(lines)

    # ------------------------------------------------------------------ Where it begins
    w.section("begins", "Where Your Wealth Story Begins")
    money_roles = [r for r in ("asc", "second", "fortune", "assets") if r in roles.get(r2, [])]
    label = {"asc": "Ascendant", "second": "second house", "fortune": "Part of Fortune", "assets": "Lot of Assets"}
    companions = [o for o in a["occupants"][P[r2]["house"]] if o != r2 and o in W.TRAD]
    near = [o for o in a["occupants"][P[r2]["house"]] if o != r2 and abs(W.sep(P[o]["lon"], P[r2]["lon"])) <= 8]
    share = [o for o in companions if o not in near]
    if len(money_roles) >= 3:
        names = join([f"your {label[r]}" for r in money_roles])
        with_ = (f" with {join([the(c) for c in near[:3]])} close beside it" if near else
                 f", sharing that house with {join([the(c) for c in share[:3]])}" if share else "")
        stand = T.STAND["concentrated"].format(roles=names[5:] if names.startswith("your ") else names,
                                               R=the(r2), S=P[r2]["sign"], ord=T.ORD[P[r2]["house"]], with_=with_)
        stand = stand.replace("Your your ", "Your ")
        concentrated = True
    elif len([o for o in a["occupants"][2] if o in W.ALL]) >= 3:
        stand = T.STAND["stellium"].format(names=cap(join([the(o) for o in a["occupants"][2]])))
        concentrated = False
    else:
        stand = T.STAND["split"].format(R=The(r2), S=P[r2]["sign"], ord=T.ORD[P[r2]["house"]], C=the(rc),
                                        CS=P[rc]["sign"], cord=T.ORD[P[rc]["house"]])
        stand = cap(stand) if False else stand
        concentrated = False
    w.sections[-1]["greeting"] = f"Hey {name}," if name and name != "Friend" else "Hey there,"
    w.para(T.OPENING.format(stand=stand, close=""))
    w.para(T.CONCENTRATED_NOTE if concentrated else "", T.OPENING_CLOSE)

    # ------------------------------------------------------------------ How you create value
    w.section("value", "How You Create Value")
    s1, s2 = a["house_sign"][1], a["house_sign"][2]
    p2 = P[r2]
    if R[1] == r2 and s1 == s2:
        lead = (f"{s2} rules both your first and second houses, which links your identity directly with your income and the "
                f"resources you build. {The(r2)} rules both, and it sits in {loc(r2)}.")
    elif R[1] == r2:
        lead = (f"{The(r2)} rules both your first and second houses, which links your identity directly with your income. "
                f"It sits in {loc(r2)}.")
    else:
        lead = f"Your second house begins in {s2}, so {the(r2)} rules your income. {The(r2)} sits in {loc(r2)}."
    dig = p2.get("dignity")
    w.para(lead, T.DIGNITY[dig].format(P=The(r2), S=p2["sign"]) if dig in ("domicile", "exaltation") else "",
           T.MONEY_IN_HOUSE[p2["house"]])
    w.para(T.PLANET_EARN[r2], T.SIGN_EARN[p2["sign"]])
    described[r2] = "value"
    extra = []
    for o in a["occupants"][2]:
        if o != r2:
            extra.append(f"{The(o)} sits in your second house, bringing {T.KEYWORD.get(o, 'its energy')} directly into how you earn.")
    ang = []
    for asp in p2["aspects"]:
        if asp["other"] == "asc" and asp["type"] == "conjunction":
            ang.append(T.ANGLE_CONTACT["asc"]["conj"])
        if asp["other"] == "mc" and asp["type"] == "conjunction":
            ang.append(T.ANGLE_CONTACT["mc"]["conj"])
    friendly = contact_text(r2, kinds=("conj", "soft"), skip=MALEFIC | set(companions), limit=2)
    w.para(" ".join(extra), " ".join(ang), friendly, T.RETRO.get(r2, "") if p2["retro"] else "")
    # Mars or another planet sitting on the Ascendant shapes how this person earns
    for o in a["occupants"][1]:
        if o in ("mars", "saturn", "jupiter", "venus", "mercury", "sun") and o != r2:
            for asp in P[o]["aspects"]:
                if asp["other"] == "asc" and asp["type"] == "conjunction" and o not in described:
                    rules = [h for h, rr in R.items() if rr == o and h in (2, 5, 6, 8, 10, 11)]
                    rtxt = f", and it rules your {join([f'{T.ORD[h]} house of {RULE_SHORT[h]}' for h in rules])}" if rules else ""
                    w.para(f"{The(o)} at {P[o]['deg']} degrees {P[o]['sign']} sits {degs(asp['orb'])} from your Ascendant{rtxt}. "
                           f"You likely move quickly when something needs doing.",
                           T.DIGNITY[P[o]["dignity"]].format(P=The(o), S=P[o]["sign"]) if P[o]["dignity"] in ("fall", "detriment") else "",
                           "Financially, that can look like taking on more because you're the one who can, then wondering why the extra effort didn't change the numbers."
                           if P[o]["dignity"] in ("fall", "detriment") else "")
                    described[o] = "value"
    st = stars_for(r2) + " " + stars_for("asc")
    w.para(st.strip())
    if companions:
        cs = [c for c in companions if c not in described]
        if any(c in ("sun", "mercury") for c in cs) and "sun" in cs and "mercury" in cs and abs(W.sep(P["sun"]["lon"], P["mercury"]["lon"])) < 2:
            w.para(f"Your Sun and Mercury at {P['sun']['deg']} degrees {P['sun']['sign']} complete this {T.ORD[P[r2]['house']]} house gathering. "
                   "Mercury is less than a degree from the Sun, so your thinking and your sense of self move almost as one. "
                   "When you understand something, you tend to own it. You explain from experience rather than from a script, and people can feel the difference."
                   if abs(W.sep(P["sun"]["lon"], P["mercury"]["lon"])) < 1 else
                   f"Your Sun and Mercury in {P['sun']['sign']} complete this gathering, so your thinking and your sense of self travel together.")
            described["sun"] = described["mercury"] = "value"

    # ------------------------------------------------------------------ Fortune and Assets
    w.section("fortune", "Your Part of Fortune and Lot of Assets")
    F = P["fortune"]
    w.para(T.FORTUNE_INTRO.format(deg=F["deg"], sign=F["sign"], ord=T.ORD[F["house"]]), T.FORTUNE_HOUSE[F["house"]])
    d_fr = abs(W.sep(F["lon"], P[rf]["lon"]))
    ruler_bits = []
    if d_fr <= 3 and rf == r2:
        ruler_bits.append(f"It sits {degs(d_fr)} from its ruler, {the(rf)}, which is also the planet that rules your income. "
                          "When Fortune and the second house answer to one planet, the message is consistent. "
                          "Your opportunities and your earning power grow from the same source.")
    elif d_fr <= 3:
        ruler_bits.append(T.FORTUNE_RULER_CLOSE.format(orb=degs(d_fr), R=the(rf)))
    elif rf == r2:
        ruler_bits.append(T.FORTUNE_RULER_SAME.format(R=the(rf)))
    elif d_fr > 3:
        ruler_bits.append(T.FORTUNE_RULER_OTHER.format(R=The(rf), S=P[rf]["sign"], ord=T.ORD[P[rf]["house"]],
                                                       topic=T.HOUSE_TOPIC[P[rf]["house"]]))
        if P[rf].get("dignity"):
            ruler_bits.append(T.DIGNITY[P[rf]["dignity"]].format(P=The(rf), S=P[rf]["sign"]))
        described.setdefault(rf, "fortune")
    w.para(*ruler_bits)
    A = P["assets"]
    ra = W.RULER[A["sign"]]
    w.para(T.ASSETS_LINE.format(sign=A["sign"], ord=T.ORD[A["house"]], same=T.ASSETS_SAME if ra == rf else ""),
           T.ASSETS_MEANING["same"] if ra == r2 else T.ASSETS_MEANING["other"].format(R=the(ra)))
    if concentrated or F["house"] == 1 or P[r2]["house"] == 1:
        w.para(T.CARRY_FORWARD)
    w.para(stars_for("fortune"))

    # ------------------------------------------------------------------ What can block the flow
    w.section("blocks", "What Can Block the Flow")
    blocks = []
    for pid in dict.fromkeys([r2, rf]):
        pp = P[pid]
        if pp.get("solar") in ("combust", "beams", "cazimi"):
            d = abs(W.sep(pp["lon"], P["sun"]["lon"]))
            blocks.append(T.SOLAR[pp["solar"]].format(P=The(pid), d=("five and a half" if 5.25 <= d < 5.75 else NUM.get(int(round(d)), int(round(d))))))
        if pp.get("dignity") in ("detriment", "fall"):
            blocks.append(T.DIGNITY[pp["dignity"]].format(P=The(pid), S=pp["sign"]))
    phase_txt = T.PHASE[a["moon_phase"]] if "moon" in (r2, rf) else ""
    if "moon" in (r2, rf) and a["moon_phase"] == "balsamic" and P["moon"].get("solar") == "combust":
        phase_txt = ("Your Moon is about {} degrees behind the Sun and moving toward it, in the final phase of the lunar cycle. ".format(
            "five and a half" if 5.25 <= (360 - a["moon_elong"]) < 5.75 else int(round(360 - a["moon_elong"])))
            + "That's a balsamic Moon. It's still strong in its sign, but it can have a harder time being seen, including by you. "
            "Your own needs can get absorbed into whatever you're working toward. You handle the urgent thing, then the next one, "
            "and the moment you planned to rest keeps moving further away.")
        blocks = [b for b in blocks if not b.startswith("The Moon is about")]
    w.para(phase_txt if phase_txt.startswith("Your Moon is about") else "", " ".join(blocks))
    if not w.sections[-1]["paragraphs"]:
        w.para(T.BLOCK_INTRO)
    hard = contact_text(r2, kinds=("conj", "hard"), only=MALEFIC, limit=2)
    if not hard and rf != r2:
        hard = contact_text(rf, kinds=("conj", "hard"), only=MALEFIC, limit=1,
                            subject=f"{the(rf)}, the ruler of your Part of Fortune,")
        hard = cap(hard)
    w.para(hard)
    w.para(T.BLOCK_EMOTIONAL[r2])
    if P[r2]["house"] == 12:
        w.para(T.BLOCK_CADENT_12)
    elif P[r2]["house"] == 6:
        w.para(T.BLOCK_CADENT_6)
    if phase_txt and not phase_txt.startswith("Your Moon is about"):
        w.para(phase_txt)
    elif "moon" in (r2, rf) and a["moon_phase"] == "balsamic":
        w.para("The balsamic phase also carries a quieter gift. It belongs to the end of a cycle, when something has matured enough "
               "to be distilled. You may do your best financial work when you stop starting over and refine what you already know works.")
    if not w.sections[-1]["paragraphs"]:
        w.para(T.BLOCK_EMPTY)

    # ------------------------------------------------------------------ Midheaven and career
    w.section("career", "Your Midheaven and Career Path")
    mc = a["lon"]["mc"]
    pc = P[rc]
    rdeg = pc["deg"]
    if rc == r2:
        w.para(f"Your Midheaven sits at {dg(W.deg_of(mc))} {W.sign_of(mc)}, which makes {the(rc)} the traditional ruler of your career as well.",
               T.CAREER_BRIDGE_SAME, T.MC_SIGN[W.sign_of(mc)])
    else:
        dig = pc.get("dignity")
        w.para(T.CAREER_RULER.format(deg=W.deg_of(mc), sign=W.sign_of(mc), R=the(rc), Rc=The(rc), ds="" if W.deg_of(mc) == 1 else "s", rdeg=rdeg, rs="" if rdeg == 1 else "s",
                                     rsign=pc["sign"], rord=T.ORD[pc["house"]]).replace(f". {The(rc)} is at", f". {The(rc)} is at"),
               (T.DIGNITY_SHORT[dig] if dig else "") if rc not in described else "",
               T.PLANET_CAREER[rc], T.RETRO.get(rc, "") if pc["retro"] else "")
        w.para(T.CAREER_IN_HOUSE[pc["house"]],
               contact_text(rc, kinds=("conj",), limit=1).replace("sits with it", f"is about {int(round(next((x['orb'] for x in pc['aspects'] if x['type']=='conjunction'), 0)))} degrees away in the same house", 1)
               if rc not in described else "")
        described[rc] = "career"
    tens = []
    for asp in pc["aspects"]:
        if asp["other"] == "mc" and asp["type"] in ("square", "opposition"):
            tens.append(f"There's tension here too. {The(rc)} {T.ASPECT_WORD[asp['type']]}s your Midheaven, so the ruler of your career pulls at an angle to the career itself. "
                        "The daily work and the public role don't always ask for the same thing.")
    hard_c = contact_text(rc, kinds=("hard",), limit=2)
    w.para(" ".join(tens), hard_c)
    w.para(" ".join(T.TENTH_OCCUPANT.format(P=The(o), kw=T.KEYWORD.get(o, "its energy")) for o in a["occupants"][10] if o != rc))
    mc_aspects = []
    on_ic = []
    for pid in W.ALL:
        if pid == rc or pid not in P:
            continue
        for asp in P[pid]["aspects"]:
            if asp["other"] == "mc":
                if asp["type"] == "opposition":
                    on_ic.append(pid)
                elif asp["type"] in ("trine", "sextile") and pid in ("saturn", "jupiter", "venus", "sun", "moon", "mercury", "mars"):
                    mc_aspects.append((pid, asp["type"]))
    mcs = []
    if mc_aspects:
        names = join([the(p) for p, _ in mc_aspects])
        types = {t for _, t in mc_aspects}
        verb = ("trine" if types == {"trine"} else "sextile" if types == {"sextile"} else "support")
        mcs.append(f"{cap(names)} {verb}{'s' if len(mc_aspects) == 1 else ''} your Midheaven, lending "
                   f"{join([T.KEYWORD[p] for p, _ in mc_aspects])} to the way you're seen.")
    for p in on_ic:
        mcs.append(f"{The(p)} sits directly opposite your Midheaven at the base of your chart, which ties {T.KEYWORD.get(p, 'its energy')} "
                   "to home and foundations as much as to career.")
    w.para(T.MC_SIGN[W.sign_of(mc)] if rc != r2 else "", " ".join(mcs))
    if rc != r2:
        link = next((x for x in pc["aspects"] if x["other"] == r2), None)
        if link:
            w.para(T.CAREER_BRIDGE_ASPECT.format(asp=T.ASPECT_WORD[link["type"]] + ("s" if link["type"] in ("square", "trine", "sextile") else ""),
                                                 R2=the(r2), txt=T.BRIDGE_SOFT if T.ASPECT_CLASS[link["type"]] != "hard" else T.BRIDGE_HARD)
                   .replace("conjunct ", "sits with ").replace("opposite ", "opposes "))
        else:
            w.para(T.CAREER_BRIDGE_NONE.format(R=The(rc), R2=the(r2)))
    w.para(stars_for(rc) + " " + stars_for("mc"))

    # ------------------------------------------------------------------ Fifth, eighth, eleventh
    def house_section(h, sid, heading, OPEN, IN, OCC, extra_fn=None):
        w.section(sid, heading)
        rr = R[h]
        opener = OPEN.format(sign=a["house_sign"][h], R=the(rr))
        if rr in described:
            where = {"value": "in how you create value", "fortune": "as the ruler of your Part of Fortune",
                     "career": "as the ruler of your career", "fifth": f"in your fifth house",
                     "eighth": "in your eighth house", "eleventh": "in your eleventh house"}[described[rr]]
            if P[rr]["house"] == 1 and any(x["other"] == "asc" and x["type"] == "conjunction" for x in P[rr]["aspects"]):
                where = "on your Ascendant"
            cond = {"exaltation": ", where it's exalted", "domicile": ", where it's strong in its own sign",
                    "fall": ", where it's in its fall", "detriment": ", where it's in its detriment"}.get(P[rr].get("dignity"), "")
            w.para(opener, f"We've already met {the(rr)} {where}{cond if described[rr] != 'value' else ''}, and here it takes on another role.",
                   IN[P[rr]["house"]])
        else:
            dig = P[rr].get("dignity")
            w.para(opener, f"{The(rr)} sits at {P[rr]['deg']} degrees {P[rr]['sign']} in your {T.ORD[P[rr]['house']]} house.",
                   IN[P[rr]["house"]])
            w.para(stars_for(rr))
            w.para(T.DIGNITY[dig].format(P=The(rr), S=P[rr]["sign"]) if dig else "",
                   contact_text(rr, kinds=("conj", "soft", "hard"), skip=set(a["occupants"][h]), limit=2))
            described[rr] = sid
        occ = [o for o in a["occupants"][h] if o in W.ALL]
        if occ:
            lines = []
            for o in occ:
                if o in described:
                    continue
                lines.append(OCC.format(P=The(o), kw=T.KEYWORD.get(o, "its energy")))
                if P[o].get("dignity"):
                    lines.append(T.DIGNITY[P[o]["dignity"]].format(P=The(o), S=P[o]["sign"]))
                described[o] = sid
            w.para(" ".join(lines))
        if extra_fn:
            extra_fn(rr, occ)

    def fifth_extra(rr, occ):
        if "saturn" in occ and "pluto" in occ:
            w.para(T.FIFTH_SATURN_PLUTO)
        done = False
        for o in occ:
            if done:
                break
            for asp in P[o]["aspects"]:
                if asp["other"] == rr and T.ASPECT_CLASS[asp["type"]] == "soft":
                    done = True
                    w.para(f"{The(rr)} and {the(o)} form a {asp['type']}, so the ruler of your fifth house and the planet inside it are "
                           "cooperating. That gives your creativity a workable relationship with discipline."
                           if o == "saturn" else
                           f"{The(rr)} and {the(o)} form a {asp['type']}, so the ruler of your fifth house and the planet inside it are cooperating.")
                    break

    def eighth_extra(rr, occ):
        if R[7] == rr:
            w.para(f"{The(rr)} also rules your seventh house, so partners, clients, and collaborators come through this planet as well.",
                   T.EIGHTH_STRUCTURE)
        else:
            w.para(T.EIGHTH_STRUCTURE)
        nh = a["now_houses"].get("pluto")
        if nh and nh[0] == 8:
            w.para(T.PLUTO_8TH)

    def eleventh_extra(rr, occ):
        if P[rr].get("dignity") in ("fall", "detriment"):
            w.para(T.FALL_CAUTION.get(rr, ""), T.RECEIVE)

    house_section(5, "fifth", "Creativity, Pleasure, and Enterprise", T.FIFTH_OPEN, T.FIFTH_IN, T.FIFTH_OCC, fifth_extra)
    house_section(8, "eighth", "Shared Resources and Agreements", T.EIGHTH_OPEN, T.EIGHTH_IN, T.EIGHTH_OCC, eighth_extra)
    house_section(11, "eleventh", "Support, Networks, and Gains", T.ELEVENTH_OPEN, T.ELEVENTH_IN, T.ELEVENTH_OCC, eleventh_extra)
    # any star on the IC or DSC not yet told
    leftover = stars_for("ic") + " " + stars_for("dsc")
    if leftover.strip():
        w.para(leftover.strip())

    # ------------------------------------------------------------------ Nodes
    w.section("pattern", "The Pattern You're Learning to Change")
    sn, nn = P["south_node"], P["north_node"]
    conj = [o for o in W.ALL if o in P and abs(W.sep(P[o]["lon"], sn["lon"])) <= 5 and o in T.SN_CONJ]
    sn_head = f"Your South Node is in {sn['sign']} in your {T.ORD[sn['house']]} house" + (f", conjunct {join([the(c) for c in conj])}." if conj else ".")
    sn_house = T.SN_HOUSE[sn["house"]]
    w.para(sn_head, T.SN_SIGN[sn["sign"]], sn_house, " ".join(T.SN_CONJ[c] for c in conj))
    w.para(f"Your North Node in {nn['sign']} sits in your {T.ORD[nn['house']]} house.", T.NN_SIGN[nn["sign"]], T.NN_HOUSE[nn["house"]])
    soft = [x for x in nn["aspects"] if x["type"] in ("trine", "sextile") and x["other"] in W.TRAD]
    if soft:
        names = [the(x["other"]) for x in soft]
        hs = {P[x["other"]]["house"] for x in soft}
        where = f" in your {T.ORD[hs.pop()]} house" if len(hs) == 1 else ""
        types = {x["type"] for x in soft}
        verb = (soft[0]["type"] + "s") if len(types) == 1 else "forms supportive aspects to"
        if len(soft) > 1 and len(types) == 1:
            verb = f"{soft[0]['type']}s both" if len(soft) == 2 else verb
        w.para(T.NN_TRINE.format(asp=verb, names=join(names) + where), T.NODE_CLOSE)

    # ------------------------------------------------------------------ Thresholds
    w.section("thresholds", "The Thresholds Ahead")
    w.para(T.THRESH_INTRO)
    active_now = {h["target"] for h in a["transits"] if h["planet"] == "jupiter" and h["aspect"] == 0 and h.get("ongoing_start")}
    rec = [k for k in a["recent_jupiter"] if k not in active_now]
    if rec:
        nice_names = {"asc": "Ascendant", "fortune": "Part of Fortune", "mc": "Midheaven"}
        names = [nice_names.get(k, W.NAME[k]) for k in rec]
        w.para(T.RECENT_JUPITER.format(names=join(names)))
    target_weight = {"fortune": 1.8, "mc": 1.5, "asc": 1.4, "ic": 1.1, "assets": 1.0, "sun": 1.3, "moon": 1.3,
                     "venus": 1.2, "jupiter": 1.0, "saturn": 1.0}

    def tw(k):
        x = target_weight.get(k, 1.0)
        if k == r2:
            x = max(x, 2.0)
        if k == rc:
            x = max(x, 1.6)
        return x

    def tname(k):
        return {"asc": "Ascendant", "mc": "Midheaven", "ic": "IC", "fortune": "Part of Fortune", "assets": "Lot of Assets"}.get(k, W.NAME[k])

    def tmeaning(k):
        if k == r2:
            return T.TARGET_MEANING["second"]
        if k == rc:
            return T.TARGET_MEANING["career"]
        if k == rf:
            return T.TARGET_MEANING["fortune"]
        if k == "fortune":
            return T.TARGET_MEANING["point_fortune"]
        return T.TARGET_MEANING.get(k, "")

    by_planet = {}
    for h in a["transits"]:
        cyc = h["target"] == h["planet"] and (h["planet"], h["aspect"]) in T.CYCLE
        if h["target"] == h["planet"] and not cyc:
            continue
        h["weight"] = PLANET_WEIGHT[h["planet"]] * (1.6 if cyc else tw(h["target"])) * (0.6 if h["class"] == "soft" else 1.0)
        h["cycle"] = cyc
        by_planet.setdefault(h["planet"], []).append(h)
    for g in a["ingresses"]:
        by_planet.setdefault(g["planet"], [])
    groups = []
    for pl, hs in by_planet.items():
        ing = [g for g in a["ingresses"] if g["planet"] == pl]
        score = sum(h["weight"] for h in hs) + (2.0 * len(ing))
        groups.append((score, pl, hs, ing))
    groups.sort(key=lambda g: -g[0])
    groups = groups[:5]
    groups.sort(key=lambda g: min([h["start"] for h in g[2]] + [i["start"] for i in g[3]]))
    prof = a["profection"]
    prof_used = False
    if prof["lord"] not in [g[1] for g in groups]:
        lp = prof["lord"]
        w.para(f"Your annual profection adds one more layer. At {prof['age']}, you're in {T.PROFECTION[prof['house']]}. "
               f"{The(lp)} is the lord of your year until {W.MONTHS[prof['until'].month - 1]} {prof['until'].year}, so watch "
               f"your {T.ORD[P[lp]['house']]} house, where {the(lp)} sits in your chart, for where the year's story concentrates.",
               prof_next(prof))
        prof_used = True
    ecl_used = set()
    active_planets = [g[1] for g in groups]
    if not groups:
        w.para(T.QUIET_YEAR)
    for score, pl, hs, ing in groups:
        normal = sorted([h for h in hs if not h["cycle"]], key=lambda h: h["start"])
        cycles = [h for h in hs if h["cycle"]]
        main_cls = None
        for cls in ("conj", "hard", "soft"):
            if any(h["class"] == cls for h in normal):
                main_cls = cls
                break
        if main_cls and (pl, main_cls) in T.VERB:
            tg = [h for h in normal if h["class"] == main_cls]
            seen_t, tnames = set(), []
            for h in sorted(tg, key=lambda h: -h["weight"]):
                n = tname(h["target"])
                if n not in seen_t:
                    seen_t.add(n)
                    tnames.append(n)
            title = f"{pl.title()} {T.VERB[(pl, main_cls)]} Your {join(tnames[:2])}"
        elif cycles:
            title = T.CYCLE[(pl, cycles[0]["aspect"])][0]
        elif ing:
            title = f"{pl.title()} Reaches Your {T.ORD_TITLE[ing[0]['house']]} House"
        else:
            title = f"{pl.title()} Moves Through Your Chart"
        w.section(f"t-{pl}", title, level=2)
        # timing sentences, per class
        # an IC conjunction and a Midheaven opposition are the same moment on one axis
        ic_conj = [h for h in normal if h["target"] == "ic" and h["aspect"] == 0]
        mc_conj = [h for h in normal if h["target"] == "mc" and h["aspect"] == 0]
        if ic_conj:
            normal = [h for h in normal if not (h["target"] == "mc" and h["aspect"] == 180)]
        if mc_conj:
            normal = [h for h in normal if not (h["target"] == "ic" and h["aspect"] == 180)]
        for cls in ("conj", "hard", "soft"):
            items = [h for h in normal if h["class"] == cls]
            if not items:
                continue
            cap_n = 3 if cls == "soft" else 4
            if len(items) > cap_n:
                items = sorted(sorted(items, key=lambda h: -h["weight"])[:cap_n], key=lambda h: h["start"])
            # merge contacts that share an aspect and a time window
            merged = []
            for h in items:
                ww = when(h, today)
                if merged and merged[-1]["aspect"] == h["aspect"] and merged[-1]["when"] == ww:
                    merged[-1]["names"].append(tname(h["target"]))
                else:
                    merged.append({"aspect": h["aspect"], "when": ww, "names": [tname(h["target"])]})
            bits = []
            for i, m in enumerate(merged):
                verb = {0: "crosses", 90: "squares", 180: "opposes", 120: "trines", 60: "sextiles"}[m["aspect"]]
                tgt = "your " + join(m["names"])
                if i == 0:
                    bits.append(f"{pl.title()} {verb} {tgt} {m['when']}")
                elif merged[i - 1]["aspect"] == m["aspect"]:
                    bits.append(f"{tgt} {m['when']}")
                else:
                    bits.append(f"{verb} {tgt} {m['when']}")
            sentence = join(bits) + "."
            if cls == "conj" and ic_conj and any(h["target"] == "ic" for h in items):
                sentence = sentence[:-1] + ", while opposing your Midheaven."
            elif cls == "conj" and mc_conj and any(h["target"] == "mc" for h in items) and len(items) == 1:
                sentence = sentence[:-1] + ", while opposing your IC."
            if len(items) >= 3 and cls == "hard" and pl == "saturn":
                sentence += " That's a long, steady pressure on the exact points that carry your money story."
            means = []
            for h in items:
                m = tmeaning(h["target"])
                if m and h["target"] in (r2, rc, rf) and h["target"] not in ("fortune",):
                    means.append(f"your {tname(h['target'])} is {m}")
            mtxt = f"Remember that {join(list(dict.fromkeys(means)))}." if means else ""
            w.para(sentence, T.TRANSIT_CORE.get((pl, cls), ""), mtxt)
            # eclipses on the same points
            for e in a["eclipses"]:
                k = ("ruler" if e["point"] == r2 else "cruler" if e["point"] == rc else e["point"])
                if any(h["target"] == e["point"] or (e["point"] in ("mc", "ic") and h["target"] in ("mc", "ic")) for h in items) and e["jd"] not in ecl_used:
                    ecl_used.add(e["jd"])
                    if e["date"] < today:
                        w.para(T.ECLIPSE_PAST.format(kind=e["type"], date=W.month_year(e["date"]),
                                                     pt=tname(e["point"]), topic=T.ECLIPSE_TOPIC.get(k, "money")))
                    else:
                        w.para(T.ECLIPSE_LINE.format(kind=e["type"], date=W.month_year(e["date"]),
                                                     pt=tname(e["point"]), topic=T.ECLIPSE_TOPIC.get(k, "money")))
        for h in cycles:
            nm, txt = T.CYCLE[(pl, h["aspect"])]
            lead = {("saturn", 180): f"{cap(when(h, today))}, Saturn opposes its natal position.",
                    }.get((pl, h["aspect"]), f"This window also includes {nm.replace('Your ', 'your ')}, {when(h, today)}.")
            parts_ = re.split(r"(?<=[.!?])\s+", txt, maxsplit=1)
            if normal and (pl, h["aspect"]) == ("saturn", 180) and len(parts_) > 1:
                txt = parts_[1]
            w.para(lead if normal else "", txt)
        for g in ing:
            ww = when({**g, "ongoing_start": g["start"] <= today}, today)
            w.para(f"{cap(ww)}, {T.INGRESS[g['house']].format(P=pl.title())}",
                   T.INGRESS_PLANET[pl] if not normal else "")
        if pl == prof["lord"] and not prof_used:
            prof_used = True
            lordname = ("a " + pl.title()) if pl != "uranus" else "a Uranus"
            w.para(T.PROF_LINE.format(lordname=lordname, age=prof["age"], ord=T.ORD[prof["house"]], desc=T.PROFECTION[prof["house"]],
                                      Lord=The(pl), until=W.MONTHS[prof["until"].month - 1] + " " + str(prof["until"].year))
                   .replace("last birthday until", "last birthday through"),
                   "Agreements, debts, shared resources, and long-term commitments deserve careful attention right now." if prof["house"] == 8 else "",
                   prof_next(prof))
    # move a trailing profection paragraph out of a level-2 section if needed (handled by renderer order)

    # ------------------------------------------------------------------ Overall
    w.section("overall", "Your Overall Wealth Story")
    strengths, comps = [], []
    p = P[r2]
    if p.get("dignity") in ("domicile", "exaltation"):
        strengths.append("dignified")
    if p["angularity"] == "angular":
        strengths.append("angular")
    if abs(W.sep(P["fortune"]["lon"], P[rf]["lon"])) <= 3:
        strengths.append(f"closely tied to your Part of Fortune" if rf == r2 else "")
    if p.get("solar") == "combust":
        comps.append(f"{the(r2)} sits close enough to the Sun that its own needs can get lost")
    if p.get("dignity") in ("detriment", "fall"):
        comps.append(f"{the(r2)} works from a sign that doesn't come naturally to it")
    for asp in p["aspects"]:
        if asp["other"] in ("mars", "saturn") and T.ASPECT_CLASS[asp["type"]] in ("conj", "hard"):
            o = asp["other"]
            word = {"mars": "Mars", "saturn": "Saturn"}[o]
            fall = " in its fall" if P[o].get("dignity") == "fall" else ""
            comps.append(f"{word}{fall} {'beside it' if asp['type'] == 'conjunction' else 'in tension with it'} can push hard and still lose track of what you need")
            break
    s_txt = join([s for s in strengths if s])
    first = f"Your chart centers money on {the(r2)}" + (f", and {the(r2)} is {s_txt}." if s_txt else ".")
    second = ("That gives you real agency. Your earning power comes from " +
              {"moon": "your instincts, your care, and your ability to recognize what people need.",
               "sun": "your confidence, your leadership, and your willingness to be seen.",
               "mercury": "your mind, your words, and your ability to connect ideas.",
               "venus": "your taste, your relationships, and your sense of what people value.",
               "mars": "your courage, your effort, and your willingness to act.",
               "jupiter": "your knowledge, your generosity, and your sense of the bigger picture.",
               "saturn": "your patience, your discipline, and your ability to build over time."}[r2])
    third = ""
    if comps:
        third = "The complications come from the same place. " + " ".join(cap(c) + "." for c in comps)
        if p.get("solar") == "combust":
            third += " Income can come in while your energy goes out faster."
    w.para(first, second, third)
    pc = P[rc]
    cdesc = "a dignified " + W.NAME[rc] if pc.get("dignity") in ("domicile", "exaltation") else the(rc)
    r5, r8, r11 = R[5], R[8], R[11]
    strong = lambda pid: P[pid].get("dignity") in ("domicile", "exaltation")
    seen_p, seen_h = {rc}, {pc["house"]}

    def desc(pid):
        h = P[pid]["house"]
        if pid in seen_p:
            return f"the same {W.NAME[pid]}"
        seen_p.add(pid)
        adj = ("an exalted " if P[pid].get("dignity") == "exaltation" else "a strong " if P[pid].get("dignity") == "domicile" else "")
        nm = (adj + W.NAME[pid]) if adj else the(pid)
        if h in seen_h:
            return f"{nm}, also in your {T.ORD[h]} house"
        seen_h.add(h)
        return f"{nm} in your {T.ORD[h]} house of {HOUSE_SHORT[h]}"
    sentence2 = (f"Your career runs through {cdesc} in the house of {HOUSE_SHORT[pc['house']]}" +
                 (", which favors knowledge, guidance, and steady service while asking you to be intentional about how much of that service you give away."
                  if rc == "jupiter" and pc["house"] == 6 else "."))
    if r5 == r8:
        bits = [f"your fifth and eighth houses share {desc(r5)}, linking creative work with agreements and long-term structures"]
    else:
        bits = [f"creativity reaches money through {desc(r5)}", f"shared resources run through {desc(r8)}"]
    bits.append(f"your eleventh house brings gains through {'your own outreach' if P[r11]['house'] == 1 else RULE_SHORT[P[r11]['house']]}")
    tail = ""
    star_bits = [s_ for s_ in a["stars"] if s_["point"] in ("venus", "ic", "mc", r2)]
    if any(s_["star"] == "Regulus" for s_ in star_bits) and any(x["other"] == "ic" and x["type"] == "conjunction" for x in P["venus"]["aspects"]):
        tail = "Venus at your IC with Regulus ties much of this back to home, comfort, and dignity."
    w.para(sentence2, cap(join(bits)) + ".", tail)
    h2 = P[r2]["house"]
    kind = {1: "personal", 2: "personal", 7: "partner", 8: "partner", 10: "career", 5: "creative", 12: "quiet",
            3: "knowledge", 9: "knowledge"}.get(h2, "steady")
    w.para(T.OVERALL_CLOSE[kind])

    # ------------------------------------------------------------------ Final thoughts
    w.section("final", "Final Thoughts")
    w.para(T.FINAL_OPEN[r2])
    asks, lines = [], []
    for pl in active_planets[:3] if False else [g[1] for g in sorted(groups, key=lambda g: -g[0])][:3]:
        if pl in T.TRANSIT_ASK:
            asks.append(T.TRANSIT_ASK[pl][0])
            lines.append(T.TRANSIT_ASK[pl][1])
    picks = []
    if P[r2]["house"] in (1, 2) or concentrated:
        picks.append(T.FINAL_LINES["build"])
    if any(x["other"] in ("mars", "jupiter", "neptune") for x in P[r2]["aspects"]) or P[R[11]].get("dignity") in ("fall", "detriment"):
        picks.append(T.FINAL_LINES["overgive"])
    if nn["house"] == 12 or P[r2]["house"] == 12:
        picks.append(T.FINAL_LINES["quiet"])
    elif P[r2]["house"] in (7, 8):
        picks.append(T.FINAL_LINES["partner"])
    elif P[rc]["house"] == 10 or P[r2]["house"] == 10:
        picks.append(T.FINAL_LINES["seen"])
    if len(picks) < 3:
        picks.append(T.FINAL_LINES["steady"])
    if len(picks) < 3:
        picks.append(T.FINAL_LINES["trust"])
    picks = picks[:3]
    if not picks[-1].startswith("And"):
        picks[-1] = "And " + picks[-1][0].lower() + picks[-1][1:]
    if asks:
        w.para(f"The transits ahead ask for {join(asks)}. " + " ".join(lines) + " " + " ".join(picks))
    else:
        w.para(" ".join(picks))

    # ------------------------------------------------------------------ Where to go from here
    w.section("next", "Where to Go From Here")
    w.para(T.NEXT_INTRO)
    offers = [T.OFFER["timing"]]
    sign2 = a["house_sign"][2]
    offers.append((f"The Essence of {sign2}", "https://sagereality11.com/shop/" + T.ESSENCE[sign2] + "/",
                   T.ESSENCE_WHY.format(sign=sign2)))
    star = next((x for x in a["stars"] if x["star"] in T.STAR_GUIDE), None)
    if star:
        title, slug = T.STAR_GUIDE[star["star"]]
        pt = T.STAR_PT.get(star["point"]) or W.NAME[star["point"]]
        offers.append((title, "https://sagereality11.com/shop/" + slug + "/", T.STAR_GUIDE_WHY.format(star=star["star"], pt=pt)))
    offers.append(T.OFFER["manifest"])
    offers.append(T.OFFER["karmic"])
    offers.append(T.OFFER["transit_free"])
    offers.append(T.OFFER["hub"])
    w.sections[-1]["offers"] = [{"title": t, "url": u, "why": y} for t, u, y in offers]

    snap = snapshot(a, w, r2, rc, rf)
    return {"title": TITLE, "subtitle": "How your chart builds, holds, and grows your resources", "name": name,
            "birth": birth, "sections": w.sections, "signoff": T.SIGNOFF, "disclaimer": T.DISCLAIMER,
            "snapshot": snap}


def snapshot(a, w, r2, rc, rf):
    P = a["planets"]
    first_para = w.sections[0]["paragraphs"][0]
    theme = first_para.replace("Thank you for letting me spend time with a bit of your wealth story. ", "")
    blocks = next((s for s in w.sections if s["id"] == "blocks"), None)
    watch = ""
    if blocks and blocks["paragraphs"]:
        paras = [p for p in blocks["paragraphs"] if not p.startswith(T.BLOCK_INTRO[:40])]
        concrete = [p for p in paras if p.startswith("Your Moon is about") or any(k in p for k in ("from the Sun", "detriment", "its fall"))]
        emotional = [p for p in paras if p.startswith("Because ")]
        pick = (concrete or emotional or paras or [""])[0]
        sents, words = [], 0
        for s_ in re.split(r"(?<=[.!?])\s+", pick):
            limit = 3 if pick.startswith("Your Moon is about") else 2
            if sents and (len(sents) >= limit or words + len(s_.split()) > 65):
                break
            sents.append(s_)
            words += len(s_.split())
        watch = " ".join(sents)
    rows = [
        ("The planet that rules your income", f"{W.NAME[r2]} in {P[r2]['sign']}, {T.ORD[P[r2]['house']]} house"),
        ("Your Part of Fortune", f"{P['fortune']['deg']}° {P['fortune']['sign']}, {T.ORD[P['fortune']['house']]} house"),
        ("The ruler of your career", f"{W.NAME[rc]} in {P[rc]['sign']}, {T.ORD[P[rc]['house']]} house"),
        ("Your Midheaven", f"{W.deg_of(a['lon']['mc'])}° {W.sign_of(a['lon']['mc'])}"),
        ("This year's profection", f"{T.ORD[a['profection']['house']].title()} house, ruled by {W.NAME[a['profection']['lord']]}"),
    ]
    thresholds = [s["heading"] for s in w.sections if s["level"] == 2]
    return {"theme": theme, "rows": rows, "watch": watch, "thresholds": thresholds,
            "contents": [s["heading"] for s in w.sections if s["level"] == 1 and s["id"] != "next"]}
