"""Your Shared Soul Journey: the two-person monthly forecast, written from the relationship's lens."""
from __future__ import annotations

import datetime as dt

from . import transit_text as T
from . import transit_pair_text as X
from .transit_month import NAME, RULER, SIGNS, sep
from .transit_month_reading import (Builder, MON, T_MONTHS, TZ_LABEL, an, cap, hname, join, ocls, pn, wheel_chart, when)

SLOWP = ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node")


class PairBuilder:
    def __init__(self, fa, fb, pf, name_a, name_b, label_a, label_b, pron_a="she", pron_b="he", rel="parent_child"):
        self.fa, self.fb, self.pf = fa, fb, pf
        self.A = Builder(fa, name_a, label_a, pron_a)
        self.B = Builder(fb, name_b, label_b, pron_b)
        self.na, self.nb = name_a, name_b
        self.rel = rel if rel in T.REL else "parent_child"
        self.R = T.REL[self.rel]
        self.kind = X.LENS_KIND[self.rel]
        s, o, p, r = X.PRON.get(pron_b, X.PRON["they"])
        self.sub, self.obj, self.pos, self.refl = s, o, p, r
        self.M, self.year, self.month = fa["month_name"], fa["year"], fa["month"]
        self.pk = self.A.pk
        self.PA, self.PB = fa["natal"]["points"], fb["natal"]["points"]

    # ---------------------------------------------------------- helpers
    def nmA(self, k):
        return self.A.nm(k)

    def bpos(self, k):
        return f"{self.nb}'s {self.A.nm(k)}"

    def conv3(self, t):
        """Second person text rewritten about the other person."""
        import re
        they = self.sub == "they"
        v = (lambda base, s3: base if they else s3)
        rules = [(r"\byou're\b", f"{self.sub} {v('are', 'is')}"), (r"\byou'll\b", f"{self.sub}'ll"), (r"\byou've\b", f"{self.sub} {v('have', 'has')}"),
                 (r"\byourself\b", self.refl), (r"\byour\b", self.pos), (r"\bYour\b", cap(self.pos)),
                 (r"\byou love\b", f"{self.sub} {v('love', 'loves')}"), (r"\byou call\b", f"{self.sub} {v('call', 'calls')}"),
                 (r"\byou really are\b", f"{self.sub} really {v('are', 'is')}"), (r"\byou make\b", f"{self.sub} {v('make', 'makes')}"),
                 (r"\byou can\b", f"{self.sub} can"), (r"\byou will\b", f"{self.sub} will"),
                 (r"\byou find\b", f"{self.sub} {v('find', 'finds')}"), (r"\byou go\b", f"{self.sub} {v('go', 'goes')}"),
                 (r"\byou build\b", f"{self.sub} {v('build', 'builds')}"), (r"\byou hold\b", f"{self.sub} {v('hold', 'holds')}"),
                 (r"\byou want\b", f"{self.sub} {v('want', 'wants')}"), (r"\byou reach\b", f"{self.sub} {v('reach', 'reaches')}"),
] + [(rf"\byou {w}\b", f"{self.sub} {v(w, (w[:-1] + 'ies') if w.endswith('ry') else w + ('es' if w.endswith(('ch', 'sh', 'ss', 'o')) else 's'))}") for w in
       ("carry", "share", "show", "allow", "give", "need", "feel", "know", "learn", "see", "act", "meet", "live", "grow", "take", "keep")] + [
                 (r"\byou\b", self.obj)]
        for a, b in rules:
            t = re.sub(a, b, t)
        return t

    def ess3(self, k):
        return self.conv3(T.PT[k]["ess"])

    def short3(self, k):
        return self.conv3(T.PT[k]["short"])

    def fmt3(self, t):
        return t.format(N=self.nb, pos=self.pos, obj=self.obj)

    def deg(self, P, k):
        return f"{P[k]['deg']}° {P[k]['sign']}"

    # ---------------------------------------------------------- build
    def build(self):
        A, B = self.A, self.B
        A.cur, _ = A.currents()
        B.cur, _ = B.currents()
        A.ev, B.ev = A.events(), B.events()
        A.theme = A.pk.one(T.THEME.get((A.cur[0]["planet"], ocls(A.cur[0]["aspect"])) if A.cur else ("none", "none")) or T.THEME[("none", "none")])
        B.theme = B.pk.one(T.THEME.get((B.cur[0]["planet"], ocls(B.cur[0]["aspect"])) if B.cur else ("none", "none")) or T.THEME[("none", "none")])
        parts = [self.part_ask(), self.part_agreements(), self.part_wheels(), self.part_shared(), self.part_pattern(),
                 self.part_each(), self.part_lunar(), self.part_calendar(), self.part_belongs(), self.part_beyond(),
                 self.part_living(), self.part_charts()]
        parts = [p for p in parts if p and p.get("sections")]
        return {"pair": True, "name": self.na, "other": self.nb, "relation": self.R["label"], "month": f"{self.M} {self.year}",
                "title": "Your Shared Soul Journey", "titleSub": "Monthly Transit Forecast for Two",
                "coverQ": "WHAT IS THIS MONTH ASKING OF US?", "birthLabel": self.A.birth_label,
                "birthLabel2": f"{self.nb}, {self.B.birth_label}", "tagline": cap(self.R["hope"]),
                "letter": self.letter(), "parts": parts, "finalSub": "Your Shared Soul Invitation", "final": self.final(),
                "more": T.MORE, "method": self.method(), "fine": T.FINE, "affirmations": self.affirmations(),
                "charts": {"a": wheel_chart(self.fa, "natal"), "b": wheel_chart(self.fb, "natal"), "t": wheel_chart(self.fa, "transit")}}

    # ---------------------------------------------------------- shared activations
    def shared(self):
        out, seen = [], []
        for x in self.pf["shared"]:
            L = x["link"]
            dup = next((o for o in out if o["planet"] == x["planet"] and (o["link"]["b"] == L["b"] or o["link"]["a"] == L["a"])), None)
            if dup:
                dup.setdefault("also", []).append(x)
                continue
            out.append(dict(x))
        return out[:4]

    def sh_title(self, s):
        L = s["link"]
        tp = pn(s["planet"], True)
        both = f"Your {self.nmA(L['a'])} and {self.nb}'s {self.nmA(L['b'])}"
        if s["shape"] and s["shape"]["kind"] == "tsquare":
            return f"{tp} Completes a T-Square on {both}"
        return f"{tp} Touches {both}"

    def sh_section(self, s, i):
        L = s["link"]
        tp, a, b = s["planet"], L["a"], L["b"]
        pa, pb = self.PA[a], self.PB[b]
        paras = []
        lead = (f"Your {self.nmA(a)} at {self.deg(self.PA, a)} and {self.nb}'s {self.nmA(b)} at {self.deg(self.PB, b)} are already "
                f"{'joined' if L['aspect'] == 0 else 'in ' + an(T.ASP_NOUN[L['aspect']]) + ' ' + T.ASP_NOUN[L['aspect']]} between your charts. "
                f"Around {self.A.dt_(s['date'])}, {pn(tp)} at {s['pos'].split('°')[0]}° {s['pos'].split(' ')[-1]} makes {an(T.ASP_NOUN[s['asp_a']])} {T.ASP_NOUN[s['asp_a']]} to your {self.nmA(a)} "
                f"and {an(T.ASP_NOUN[s['asp_b']])} {T.ASP_NOUN[s['asp_b']]} to {self.pos} {self.nmA(b)}, both within {max(s['orb_a'], s['orb_b']):.1f}°.")
        sh = s["shape"]
        diag_pts = [{"lon": pa["lon"], "who": "a", "label": f"Your {self.nmA(a)}"},
                    {"lon": pb["lon"], "who": "b", "label": f"{self.nb}'s {self.nmA(b)}"},
                    {"lon": self.lon_of(s["pos"]), "who": "t", "label": f"{NAME[tp]}, {MON[self.month - 1]} {int(s['date'][8:10])}"}]
        lines = [[0, 1, L["aspect"]], [2, 0, s["asp_a"]], [2, 1, s["asp_b"]]]
        caption = f"{NAME[tp]} {T.ASP_WORD[s['asp_a']]} your {self.nmA(a)} and {T.ASP_WORD[s['asp_b']]} {self.nb}'s {self.nmA(b)}."
        if sh and sh["kind"] == "tsquare":
            apex = {"transit": f"{NAME[tp]} itself", "a": f"your {self.nmA(a)}", "b": f"{self.nb}'s {self.nmA(b)}"}[sh["apex"]]
            osign = SIGNS[int(sh["open"] // 30)]
            lead += (f" Rather than two separate transits, I read this as {pn(tp)} briefly completing a T-square across both of your charts, with {apex} at the focal point. "
                     f"That tells me the tension of these days is most likely to gather around {self.focal(sh, tp, a, b)}. "
                     f"The open point of the T-square falls in {osign}, which brings in {T.SIGN[osign]['need']}. " + self.pk.one(["That's the quality that helps release the tension.", "Reaching for that quality is how the pressure finds its way out.", "That's the medicine this configuration is asking for."]))
            diag_pts.append({"lon": sh["open"], "who": "open", "label": "Open point"})
            ai = {"transit": 2, "a": 0, "b": 1}[sh["apex"]]
            lines.append([3, ai, 180, 1])
            caption += f" The focal point is {apex}."
        for al in s.get("also", []):
            La = al["link"]
            if La["a"] != a:
                lead += f" It also reaches your {self.nmA(La['a'])}, which sits beside your {self.nmA(a)}, so I read them together as one experience."
            elif La["b"] != b:
                lead += f" It also reaches {self.nb}'s {self.nmA(La['b'])}, so I read them together as one experience."
        if sh and sh["kind"] == "stack":
            lead += " Because your two planets sit together, the transit lands on both of you at once, so you're likely to feel this at the same time."
        paras.append(lead)
        c = ocls(s["asp_a"])
        ca, cb = c if c != "hard" else "hard", ocls(s["asp_b"])
        blocks = [
            {"h": "What this stirs in you",
             "paras": [X.A_TEXT.get((tp, ca), X.A_TEXT[("saturn", "hard")]).format(np=self.nmA(a), ess=T.PT[a]["ess"], asp=T.ASP_NOUN[s["asp_a"]])
                       + " " + self.A.natal_line(a)]},
            {"h": f"What this stirs in {self.nb}",
             "paras": [X.B_TEXT.get((tp, cb), X.B_TEXT[("saturn", "hard")]).format(N=self.nb, pos=self.pos, obj=self.obj, np=self.nmA(b), ess=self.ess3(b), asp=T.ASP_NOUN[s["asp_b"]])
                       + f" {self.nb}'s {self.nmA(b)} is in {pb['sign']} in {self.pos} {hname(pb['house'])}, the area of {T.HOUSE[pb['house']]['area']}."]},
            {"h": "What it asks of the two of you",
             "paras": [X.TOGETHER[tp]]},
        ]
        octs = X.PAIR_OCT.get(tp, X.PAIR_OCT["saturn"])
        sec = {"title": self.sh_title(s), "eyebrow": self.A.dt_(s["date"]),
               "sub": f"{cap(T.VOICE[tp])} for both of you.", "paras": paras, "blocks": blocks,
               "diagram": {"data": {"rotate": round(diag_pts[2]["lon"] / 10) * 10, "center": "T-square" if sh and sh["kind"] == "tsquare" else "",
                                    "points": diag_pts, "lines": lines}, "caption": caption},
               "octTable": [list(x) for x in octs[:4]],
               "reflect": [["Your reflection", self.pk.one(T.PROMPT.get(a, T.PROMPT["sun"]))],
                           [f"A question {self.nb} might sit with", X.B_PROMPT[tp]]]}
        return sec

    def focal(self, sh, tp, a, b):
        if sh["apex"] == "a":
            return T.PT[a]["ess"]
        if sh["apex"] == "b":
            return self.ess3(b)
        return {"saturn": "responsibility and who carries what", "jupiter": "growth and generosity", "uranus": "freedom and change",
                "neptune": "trust, clarity and what goes unsaid", "pluto": "power and control", "chiron": "old hurts and how you talk about them",
                "north_node": "the direction each of you is growing"}[tp]

    def lon_of(self, pos):
        d, rest = pos.split("°")
        mnt, sign = rest.strip().split("' ")
        return SIGNS.index(sign) * 30 + int(d) + int(mnt) / 60

    # ---------------------------------------------------------- parts
    def letter(self):
        sh = self.shared()
        p1 = f"Hey {self.na},"
        p2 = (f"This reading looks at {self.M} through two charts at once, yours and {self.nb}'s. Every month the planets move through both of your charts, "
              f"but some months they land right on the places where your charts are tied to each other.")
        if sh:
            planets = []
            for s in sh:
                if NAME[s["planet"]] not in planets:
                    planets.append(NAME[s["planet"]])
            p2 += f" {self.M} is one of those months. {join(planets[:3])} {'are' if len(planets) > 1 else 'is'} pressing on threads between you within the same few weeks."
        p3 = (f"So this isn't only your month and {self.nb}'s month side by side. It's a month for the relationship itself, and for {self.R['us']}, that means looking at {self.R['lens']}. "
              f"In the pages that follow I'll walk you through the soul agreements between your charts, how {self.M} presses on each one, what belongs to you, what belongs to {self.nb} and what belongs to the two of you together.")
        return [p1, p2, p3]

    def part_ask(self):
        sh = self.shared()
        A, B = self.A, self.B
        paras = []
        if sh:
            s = sh[0]
            L = s["link"]
            paras.append(f"The strongest thread this month runs between your {self.nmA(L['a'])} and {self.nb}'s {self.nmA(L['b'])}. "
                         f"Your {self.nmA(L['a'])} holds {T.PT[L['a']]['ess']}, and {self.pos} {self.nmA(L['b'])} holds {self.ess3(L['b'])}. "
                         f"When {pn(s['planet'])} touches both at once, it asks each of you {T.VOICE[s['planet']]}, and it asks the same of the space between you.")
        if A.cur:
            a = A.cur[0]
            paras.append(f"Your own month centers on {pn(a['planet'])}'s {T.ASP_NOUN[a['aspect']]} to your {self.nmA(a['target'])}, a story about {A.theme[0].lower()}.")
        if B.cur:
            b = B.cur[0]
            paras.append(f"{self.nb}'s month centers on {pn(b['planet'])}'s {T.ASP_NOUN[b['aspect']]} to {self.pos} {self.nmA(b['target'])}, a story about {B.theme[0].lower()}.")
        paras.append(f"Put those together and the relationship is being invited to grow along with the two people in it. Neither of you has to grow at the other's expense. "
                     f"The hope for this month is {self.R['hope']}.")
        title = {"family": "The Love Stays, the Shape Changes", "love": "Growing Together, Growing Free", "peer": "Building on What You Share"}[self.kind]
        return {"title": f"What Is This Month Asking of the Two of You?", "intro": f"The heart of {self.M} for {self.R['us']}.",
                "sections": [{"title": title, "paras": paras,
                              "story": {"family": "The story becomes a month where our love stays the same while its shape grows up.",
                                        "love": "The story becomes a month where we choose each other again, as the people we are now.",
                                        "peer": "The story becomes a month where we choose our roles instead of falling into them."}[self.kind]}]}

    def part_agreements(self):
        links = [l for l in self.pf["links"] if l["a"] in T.PT and l["b"] in T.PT][:7]
        if not links:
            return None
        rows = []
        for l in links:
            rows.append([f"{self.nmA(l['a'])} {self.deg(self.PA, l['a'])}", f"{self.nmA(l['b'])} {self.deg(self.PB, l['b'])}",
                         T.ASP_NOUN[l["aspect"]].capitalize(), cap(T.PT[l["a"]]["short"]) + " and " + self.short3(l["b"])])
        over = []
        for l in links[:3]:
            over.append(f"Your {self.nmA(l['a'])} falls in {self.nb}'s {hname(l['a_in_b_house'])}, the area of {T.HOUSE[l['a_in_b_house']]['area']}")
        after = [f"When I flip the charts, a few placements stand out. {'. '.join(over)}. That shows where each of you is felt most strongly in the other's life."]
        secs = [{"title": "Your Shared Blueprint", "paras": [f"These are the closest connections between your two charts, within 2°. They're the soul agreements this month presses on."],
                 "table": {"head": ["Your placement", f"{self.nb}'s placement", "Connection", "What it holds"], "widths": [0.22, 0.24, 0.16, 0.38], "rows": rows},
                 "after": after}]
        used = set()
        for l in links[:5]:
            key = frozenset([l["a"], l["b"]]) if l["a"] != l["b"] else frozenset([l["a"]])
            NOUN = {"sun": "Identity", "moon": "Belonging", "mercury": "Understanding", "venus": "Love", "mars": "Courage", "jupiter": "Growth",
                    "saturn": "Responsibility", "uranus": "Freedom", "neptune": "Faith", "pluto": "Power", "chiron": "Healing",
                    "north_node": "Destiny", "south_node": "Old Familiar Ground", "asc": "Presence", "mc": "Direction"}
            ttl = T.AGREEMENT.get(frozenset([l["a"], l["b"]]))
            romantic = {frozenset(["venus", "mars"]), frozenset(["sun", "venus"]), frozenset(["mars", "pluto"]), frozenset(["venus", "uranus"])}
            if not ttl or (self.kind != "love" and frozenset([l["a"], l["b"]]) in romantic):
                ttl = f"Shared {NOUN[l['a']]}" if NOUN[l["a"]] == NOUN[l["b"]] else f"{NOUN[l['a']]} and {NOUN[l['b']]}"
            if ttl in used:
                continue
            used.add(ttl)
            pa, pb = self.PA[l["a"]], self.PB[l["b"]]
            sa, sb = T.SIGN[pa["sign"]], T.SIGN[pb["sign"]]
            p1 = (f"Your {self.nmA(l['a'])} in {pa['sign']} {T.LINK_VERB[l['aspect']]} {self.nb}'s {self.nmA(l['b'])} in {pb['sign']}, within {l['orb']:.1f}°. "
                  + (f"Your {pa['sign']} side wants {sa['wants']}, and {self.pos} {pb['sign']} side wants {self.conv3(sb['wants'])}. " if pa["sign"] != pb["sign"] else self.pk.one([f"You share {pa['sign']} here, so you recognize something of yourself in each other. ", f"Both of these sit in {pa['sign']}, which gives you a common language here. ", f"With both in {pa['sign']}, this is familiar ground for you both. "]))
                  + (T.LINK_TONE[l["aspect"]] if l["aspect"] not in getattr(self, "_tones", set()) else ""))
            self._tones = getattr(self, "_tones", set()) | {l["aspect"]}
            seen = getattr(self, "_seenpts", set())
            bits = []
            if ("a", l["a"]) not in seen:
                bits.append(f"Your {self.nmA(l['a'])} lives in your {hname(pa['house'])}, so for you this plays out through {T.HOUSE[pa['house']]['area']}.")
            if ("b", l["b"]) not in seen:
                bits.append(f"{self.nb}'s {self.nmA(l['b'])} lives in {self.pos} {hname(pb['house'])}, so for {self.obj} it plays out through {T.HOUSE[pb['house']]['area']}.")
            self._seenpts = seen | {("a", l["a"]), ("b", l["b"])}
            p2 = " ".join(bits)
            g, t = self.pk.one(X.LINK_GIFT[l["aspect"]])
            p3 = f"{g} {t}" + (f" In {self.R['bond']}, this thread lives in {self.R['lens']}." if not getattr(self, "_lens_said", False) else "")
            self._lens_said = True
            secs.append({"title": f"The Agreement of {ttl}", "eyebrow": f"Your {self.nmA(l['a'])} {T.ASP_WORD[l['aspect']]} {self.pos} {self.nmA(l['b'])}", "paras": [x for x in (p1, p2, p3) if x]})
            if len(secs) >= 6:
                break
        if len(secs) > 1:
            secs[-1]["close"] = "Every agreement between two souls can be renegotiated with love."
        return {"title": "The Soul Agreements Between You", "intro": "The threads that tie your charts together.", "sections": secs}

    def part_wheels(self):
        return {"title": "Your Tri-Wheels", "intro": f"Both charts under {self.M}'s sky.",
                "sections": [
                    {"title": "With You at the Center", "paras": [f"Your chart is in the inner ring in purple, with your houses. {self.nb}'s planets are in the middle ring in rose, and {self.M}'s planets are in the outer ring in teal. The lines in the center connect a transiting planet to one of yours within 1°."],
                     "image": {"kind": "triwheel", "inner": "a", "middle": "b", "outer": "t", "w": 410,
                               "caption": f"Inner ring {self.na}   ·   Middle ring {self.nb}   ·   Outer ring {self.M} 15 transits"}},
                    {"title": f"With {self.nb} at the Center", "paras": [f"Here the charts are flipped. {self.nb}'s chart and houses are in the inner ring, your planets are in the middle ring, and {self.M}'s planets are in the outer ring. This shows how the month lands in {self.pos} life."],
                     "image": {"kind": "triwheel", "inner": "b", "middle": "a", "outer": "t", "w": 410,
                               "caption": f"Inner ring {self.nb}   ·   Middle ring {self.na}   ·   Outer ring {self.M} 15 transits"}}]}

    def part_shared(self):
        sh = self.shared()
        secs = [self.sh_section(s, i) for i, s in enumerate(sh)]
        if not secs:
            for bth in self.pf["both"][:2]:
                a, b = bth["a"][0], bth["b"][0]
                secs.append({"title": f"{pn(bth['planet'], True)} in Both of Your Charts", "eyebrow": "All month",
                             "paras": [f"{pn(bth['planet'], True)} is active in both of your charts this month. For you, it {T.ASP_WORD[a['aspect']]}s your {self.nmA(a['target'])}. For {self.nb}, it {T.ASP_WORD[b['aspect']]}s {self.pos} {self.nmA(b['target'])}.".replace("conjuncts", "sits on").replace("opposites", "opposes"),
                                       X.TOGETHER[bth["planet"]]]})
        if not secs:
            return None
        return {"title": f"Where {self.M} Touches You Both", "intro": "The transits pressing on the threads between you.", "sections": secs}

    def part_pattern(self):
        links = [l for l in self.pf["links"] if l["a"] in T.PT and l["b"] in T.PT][:4]
        title, intro, t2, p2, close = X.PATTERN[self.kind]
        if not links:
            return None
        names = join([f"your {self.nmA(l['a'])} {T.ASP_WORD[l['aspect']]} {self.pos} {self.nmA(l['b'])}" for l in links[:4]])
        themes = []
        for l in links:
            for k in (l["a"], l["b"]):
                if T.VOICE.get(k) and T.VOICE[k] not in themes:
                    themes.append(T.VOICE[k])
        p1 = (f"When I bring together {names}, one theme keeps coming back. It's the relationship between {join(themes[:3])}, and how each of you holds them for the other.")
        sa = self.A.cur[0]["planet"] if self.A.cur else None
        p_you = (f"Your chart brings {T.LEAN.get(sa, 'its own strengths')}" + (f", and this month your own work is about {self.A.theme[0].lower()}." if sa else "."))
        sb = self.B.cur[0]["planet"] if self.B.cur else None
        p_b = (f"{self.nb}'s chart brings the other half. {cap(self.pos)} month is about {self.B.theme[0].lower()}." if sb else "")
        p3 = ("This isn't about blame or about who started a pattern. Patterns keep going through familiar responses, even when both people are fully able to respond differently.")
        return {"title": title, "intro": intro,
                "sections": [{"title": {"family": "When Love Becomes Responsibility", "love": "How You Reach for Each Other", "peer": "The Roles You've Taken On"}[self.kind],
                              "paras": [p1, p_you + " " + p_b, p3]},
                             {"title": t2, "paras": [p2, f"But a pattern showing up in two charts doesn't make it fate. Healing comes through awareness. You can see where a familiar reaction came from without repeating it the same way, and {self.nb} can build {self.pos} own way without rejecting what came before. {self.M} invites both of you into that."],
                              "close": close}]}

    def part_each(self):
        A, B = self.A, self.B
        def summary(bld, you=True):
            out = []
            pr = bld.prof
            who = "your" if you else self.pos
            foc = T.FOCUS[pr['house']] if you else self.conv3(T.FOCUS[pr['house']])
            out.append(f"{'You are' if you else self.nb + ' is'} in {an(T.ORD[pr['house']])} {hname(pr['house'])} profection year, with {pn(pr['lord'])} in charge, so {foc} sit at the center of {who} year.")
            for s in bld.cur[:2]:
                tgt = s["target"]
                ess = T.PT[tgt]["ess"] if you else self.ess3(tgt)
                out.append(f"{pn(s['planet'], True)}'s {T.ASP_NOUN[s['aspect']]} to {who} {self.nmA(tgt)} touches {ess}.")
            if bld.cur:
                c1, c2 = T.CENTRAL[bld.cur[0]["planet"]]
                q = f"The central question for {'you' if you else self.obj} isn't {c1}. It's {c2}."
                out.append(q if you else self.conv3(q.replace(f"for {self.obj} isn't", "for THEM isn't")).replace("THEM", self.obj))
            return " ".join(out)
        sa = summary(A, True)
        sb = summary(B, False)
        rows = [[f"{A.theme[0]}", f"{B.theme[0]}", cap(self.R["hope"])]]
        return {"title": "Each of You This Month", "intro": "Your own journeys, side by side.",
                "sections": [{"title": f"Your {self.M}, {A.theme[0]}", "paras": [sa]},
                             {"title": f"{self.nb}'s {self.M}, {B.theme[0]}", "paras": [sb]},
                             {"title": "Where Your Journeys Meet", "paras": [],
                              "table": {"head": ["Your chapter", f"{self.nb}'s chapter", "What you share"], "widths": [0.33, 0.33, 0.34], "rows": rows},
                              "after": [f"Your timing is different, but the themes fit together. Neither of you has to grow at the other's expense. The relationship just needs enough room for both journeys."]}]}

    def part_lunar(self):
        secs = []
        tzl = TZ_LABEL.get(self.fa["tz"], "")
        for l in self.pf["lunations"]:
            new = l["kind"] == "new"
            nm = "New Moon" if new else "Full Moon"
            ha, hb = l["house_a"], l["house_b"]
            p1 = (f"For you, this {nm} falls in your {hname(ha)}, the area of {T.HOUSE[ha]['area']}. "
                  f"For {self.nb}, it falls in {self.pos} {hname(hb)}, the area of {T.HOUSE[hb]['area']}.")
            ha_hits = [x for x in l["hits_a"] if x["target"] in T.PT][:1]
            hb_hits = [x for x in l["hits_b"] if x["target"] in T.PT][:1]
            if ha_hits:
                p1 += f" It's close to your {self.nmA(ha_hits[0]['target'])}, which makes it personal for you."
            if hb_hits:
                p1 += f" It's close to {self.pos} {self.nmA(hb_hits[0]['target'])}, which gives it extra weight for {self.obj}."
            if l["eclipse"]:
                p1 += f" It's {an(l['eclipse'])} {l['eclipse']}, so what it opens or closes can echo for months."
            p2 = ("Rather than setting intentions for each other, try each setting your own, ones that honor the relationship and still leave each of you free." if new
                  else "Full Moons bring feelings to the surface. If something comes up between you, let it be a conversation rather than a verdict.")
            secs.append({"title": f"{nm} at {l['deg']}° {l['sign']}", "eyebrow": f"{self.A.dt_(l['date'])}, {l['time']}{(' ' + tzl) if tzl else ''}",
                         "sub": f"Your {hname(ha)} and {self.pos} {hname(hb)}.", "paras": [p1, p2],
                         "reflect": [[f"Your {nm} intention", X.LUN_INTENT[ha]], [f"An intention {self.nb} might choose", X.LUN_INTENT[hb]],
                                     ["To share together", "How can we cheer each other on without becoming responsible for each other's dreams?" if new else "What are we each ready to release, and how can we support that?"]]})
        return {"title": "Your Shared Lunar Journey", "intro": "Where the month's lunations fall for each of you.", "sections": secs}

    def part_calendar(self):
        A, B = self.A, self.B
        ym = f"{self.year}-{self.month:02d}"
        items, per = [], {}
        for who, bld in (("a", A), ("b", B)):
            for e in bld.ev:
                if e["date"][:7] != ym or e["w"] < 5:
                    continue
                d = int(e["date"][8:10])
                lab = e["lab"] if who == "a" else e["lab"].replace("your ", self.pos + " ").replace("Month turns", self.pos.capitalize() + " month turns")
                per.setdefault(d, {"a": [], "b": [], "both": []})[who].append((e["w"], lab, e))
        for s in self.shared():
            d = int(s["date"][8:10])
            L = s["link"]
            per.setdefault(d, {"a": [], "b": [], "both": []})["both"].append((20, f"{NAME[s['planet']]} on your {self.nmA(L['a'])} and {self.pos} {self.nmA(L['b'])}", None))
        for d in sorted(per):
            for who in ("both", "a", "b"):
                for w, lab, _ in sorted(per[d][who], key=lambda x: -x[0])[:1]:
                    items.append([d, lab, who, who == "both" or w >= 9])
        rows = []
        for d in sorted(per):
            pa = sorted(per[d]["a"], key=lambda x: -x[0])
            pb = sorted(per[d]["b"], key=lambda x: -x[0])
            pt = per[d]["both"]
            if not (pa or pb or pt):
                continue
            rows.append([f"{MON[self.month - 1]} {d}", cap(pa[0][2]["long"]) if pa else "", cap(pb[0][2]["long"].replace("your ", self.pos + " ")) if pb else "",
                         pt[0][1] if pt else ""])
        win = []
        for s in self.shared():
            L = s["link"]
            win.append([self.A.dt_(s["date"]), f"{pn(s['planet'], True)} touches your {self.nmA(L['a'])} and {self.pos} {self.nmA(L['b'])}. {X.TOGETHER[s['planet']].split('. ')[0].replace('Together, this', 'This').rstrip('.')}."])
        secs = [{"title": f"{self.M} {self.year} at a Glance", "paras": [],
                 "grid": {"year": self.year, "month": self.month, "title": f"{self.M} {self.year} at a Glance",
                          "sub": "A page to keep, with the key dates for both of you.",
                          "legend": [["a", "For you"], ["b", f"For {self.nb}"], ["both", "For both of you"]], "items": items}},
                {"title": f"{self.M}, Side by Side", "paras": [f"Times are {TZ_LABEL.get(self.fa['tz'], 'local')}. The together column shows when a transit touches a thread between your charts."],
                 "table": {"head": ["Date", "For you", f"For {self.nb}", "Together"], "widths": [0.11, 0.3, 0.3, 0.29], "rows": rows}}]
        if win:
            secs.append({"title": "Your Most Important Shared Windows", "paras": [], "table": {"head": ["When", "What it holds"], "widths": [0.2, 0.8], "rows": win}})
        return {"title": "Your Shared Calendar", "intro": "Both of your months on one page.", "sections": secs}

    def part_belongs(self):
        A, B = self.A, self.B
        ya, yb = [], []
        for s in A.cur[:3]:
            for t in X.SOUL_WORK[s["planet"]]:
                if t not in ya:
                    ya.append(t)
        for s in B.cur[:3]:
            for t in X.B_SOUL_WORK[s["planet"]]:
                t = self.fmt3(t)
                if t not in yb:
                    yb.append(t)
        if not ya:
            ya = ["Resting in what you've built", "Letting the month be gentle"]
        if not yb:
            yb = [f"Trusting {self.pos} own timing", f"Growing at {self.pos} own pace"]
        return {"title": f"What Belongs to You, What Belongs to {self.nb}", "intro": "Sorting out whose work is whose.",
                "sections": [{"title": "Your Soul Work", "sub": "Living as fully yourself.", "paras": [], "bullets": ya[:5]},
                             {"title": f"{self.nb}'s Soul Work", "sub": f"{self.nb} becoming more fully {self.refl}.", "paras": [], "bullets": yb[:5]},
                             {"title": "Your Shared Soul Work", "sub": "What belongs to the relationship.",
                              "paras": [f"The work that belongs to both of you is {self.R['hope']}. That means honest conversations, agreements that fit who you both are now, and enough trust to let each other grow."]}]}

    def part_beyond(self):
        rows = []
        for who, bld in (("You", self.A), (self.nb, self.B)):
            for s in bld.cur[:3]:
                nxt = [d for d in s["passes"] if d[:7] > f"{self.year}-{self.month:02d}"]
                if nxt:
                    tgt = f"{'your' if who == 'You' else self.pos} {self.nmA(s['target'])}"
                    rows.append([who, f"{pn(s['planet'], True)} {T.ASP_WORD[s['aspect']]} {tgt}", bld.mname(nxt[0])])
        paras = []
        for a in self.fa.get("ahead", [])[:2]:
            st = [i for i in a["items"] if "station" in i][:2]
            bits = [f"{NAME[i['station']]} turns {i['kind']} on {when(i['date'], None)}" for i in st]
            if bits:
                paras.append(f"In {a['month_name']}, {join(bits)}. Watch how that lands for each of you.")
        secs = []
        if rows:
            secs.append({"title": "Your Shared Timeline", "paras": [], "table": {"head": ["Who", "Cycle", "Next big moment"], "widths": [0.18, 0.56, 0.26], "rows": rows[:7]}})
        if paras:
            secs.append({"title": "The Months Ahead", "paras": paras})
        return {"title": f"Beyond {self.M}", "intro": "What keeps unfolding for both of you.", "sections": secs}

    def part_living(self):
        planets = []
        for s in self.shared() + self.A.cur[:2] + self.B.cur[:2]:
            if s["planet"] not in planets:
                planets.append(s["planet"])
        lean = join([T.LEAN[p] for p in planets[:3]]) or "honest conversation and steady care"
        gentle = join([T.GENTLE[p] for p in planets[:3]]) or "old habits"
        qs = []
        for s in self.A.cur[:4]:
            q = T.PROMPT.get(s["target"], [None])[0]
            if q and q not in qs:
                qs.append(q)
        bq = []
        for s in self.B.cur[:4]:
            q = X.B_PROMPT[s["planet"]]
            if q not in bq:
                bq.append(q)
        return {"title": "Living With This Month Together", "intro": "How to carry the month, day to day.",
                "sections": [{"title": "What to Lean Into", "paras": [f"{self.M} supports {lean}. Lean into the conversations that clear the air and the small gestures that say you see each other as you are now."]},
                             {"title": "What to Be Gentle With", "paras": [f"Be gentle with {gentle}. When things feel tense between you, pause before you react and ask what each of you actually needs."]},
                             {"title": "Your Reflections", "paras": ["Come back to these at the end of the month."], "questions": (qs + ["What am I carrying in this relationship that isn't mine?", "What do I appreciate about who this person is becoming?"])[:5]},
                             {"title": f"Questions {self.nb} Might Sit With", "paras": [f"These are for {self.obj}, if {self.sub} would like them, not for you to answer on {self.pos} behalf."], "bullets": (bq + ["What am I ready to take more ownership of?"])[:4]},
                             {"title": "Questions to Ask Each Other", "paras": ["These are meant to be asked out loud, over coffee or on a drive, with no right answers and no rush."], "questions": X.ASK_EACH[self.rel]}]}

    def part_charts(self):
        return {"title": "Your Charts", "intro": "Both birth charts, side by side.",
                "sections": [{"title": f"{self.na}'s Birth Chart", "paras": ["Your chart with the major aspects drawn in the center and every placement listed."], "natal": {"key": "a"}},
                             {"title": f"{self.nb}'s Birth Chart", "paras": [f"{self.nb}'s chart, drawn the same way."], "natal": {"key": "b"}}]}

    def final(self):
        sh = self.shared()
        out = [f"When I lay your chart and {self.nb}'s chart together under {self.M}'s sky, I see two journeys meeting at an important doorway. "
               f"Your relationship is being invited to grow along with the two people in it, instead of asking either of you to stay in a role you've outgrown."]
        if sh:
            bits = [f"{pn(s['planet'])} on your {self.nmA(s['link']['a'])} and {self.pos} {self.nmA(s['link']['b'])} asks {T.VOICE[s['planet']]}" for s in sh[:3]]
            out.append(cap(". ".join(bits)) + ".")
        if self.A.cur and self.B.cur:
            out.append(f"Your own month is about {self.A.theme[0].lower()}, and {self.nb}'s is about {self.B.theme[0].lower()}. "
                       f"As each of you does your own work, the relationship gets lighter and more honest.")
        out.append(f"Your bond doesn't have to become any less meaningful for this to happen. It can become more honest, more balanced and more able to hold both of you as you grow.")
        out.append({"bold": f"The higher octave of {self.M} is {self.R['hope']}."})
        out.append({"family": "You gave each other roots. Now both of you get to see what grows from them.",
                    "love": "Love grows strongest when both people are free to keep becoming themselves.",
                    "peer": "The best partnerships keep making room for both people to grow."}[self.kind])
        return out

    def method(self):
        node = "True Node" if self.fa["node"] == "true" else "Mean Node"
        return [f"Your chart is calculated for {self.A.birth_label}, and {self.nb}'s for {self.B.birth_label}, using the Swiss Ephemeris, the tropical zodiac, Placidus houses (solar houses when a birth time is unknown) and the {node}. Monthly positions are calculated for {self.M} {self.year}.",
                "Connections between your charts are included within 2°, including Chiron, the nodes and the angles, and I read each chart from both directions. A transit counts as touching a connection when it reaches both ends within 1.5°. When a transit squares both ends of an opposition, or completes a square, I read it as a temporary T-square with its focal point and open point.",
                "Each person's own month uses the same methods as the single reading. Profections, transits from Jupiter outward within 1°, stations, the personal planets on their exact days, lunations, progressions, solar arcs and midpoints. An exact date is when a contact is mathematically exact, not a promise of an outer event."]

    def affirmations(self):
        out = []
        for s in self.shared() + self.A.cur:
            for a in T.AFFIRM[s["planet"]]:
                if a not in out:
                    out.append(a)
                    break
        for a in ["We can love each other and still be free.", "I honor who we are becoming.", "Our bond can grow up without growing apart.",
                  "I listen to understand, not to fix.", "I trust the timing of both of our lives.", "Love and boundaries can live together."]:
            if len(out) >= 8:
                break
            if a not in out:
                out.append(a)
        return out[:8]


def build_pair(fa, fb, pf, name_a, name_b, label_a, label_b, pron_a="she", pron_b="he", rel="parent_child"):
    return PairBuilder(fa, fb, pf, name_a, name_b, label_a, label_b, pron_a, pron_b, rel).build()
