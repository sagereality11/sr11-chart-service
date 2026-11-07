"""Transits Planner data: slow transits with active periods and exact hits, monthly fast transits,
stations, the Sun's house each month, daily Moon phase and house, eclipses and profections."""

from __future__ import annotations

import datetime as dt
from datetime import timedelta

from .common import Ctx, fmt, sign


def compute(ctx: Ctx) -> dict:
    natal = {k: ctx.natal[k] for k in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
                                        "Neptune", "Pluto", "North Node", "Ascendant", "Midheaven"]}
    house, tojd, fromjd, pos = ctx.house, ctx.tojd, ctx.fromjd, ctx.pos
    J0, J1, start, end, tz = ctx.J0, ctx.J1, ctx.start, ctx.end, ctx.tz
    ASP={0:"conjunct",60:"sextile",90:"square",120:"trine",180:"opposite"}
    SLOW=["Jupiter","Saturn","Uranus","Neptune","Pluto"]; FAST=["Sun","Mercury","Venus","Mars"]
    ORB={"Jupiter":2,"Saturn":2,"Uranus":1.5,"Neptune":1.5,"Pluto":1.5}
    NATAL_ALL=list(natal.keys())
    NATAL_PERSONAL=["Sun","Moon","Mercury","Venus","Mars","Ascendant","Midheaven"]
    def adiff(t,n,a,s): return ((t-n-s*a+180)%360)-180

    # ---- slow transits: daily scan, active periods, exact hits ----
    slow={}
    jd=J0-60; prev={}
    while jd<=J1+60:
        for p in SLOW:
            tl,_=pos(p,jd)
            for n in NATAL_ALL:
                if p=="Pluto" and n=="Pluto": continue
                for a,nm in ASP.items():
                    if a in (60,) and p in ("Uranus","Neptune","Pluto"): pass
                    for s in ((1,) if a in (0,180) else (1,-1)):
                        v=adiff(tl,natal[n],a,s); key=(p,nm,n)
                        pv=prev.get((p,a,s,n))
                        if abs(v)<=ORB[p]:
                            slow.setdefault(key,dict(days=[],exact=[]))["days"].append(jd)
                        if pv is not None and abs(v)<3 and ((pv<0<=v) or (pv>0>=v)):
                            slow.setdefault(key,dict(days=[],exact=[]))["exact"].append(jd-1+abs(pv)/(abs(pv)+abs(v)))
                        prev[(p,a,s,n)]=v
        jd+=1
    big=[]
    for (p,nm,n),d in slow.items():
        days=[x for x in d["days"]]
        if not any(J0<=x<J1 for x in days): continue
        # passes = runs of consecutive days
        runs=[];
        for x in sorted(days):
            if runs and x-runs[-1][1]<=1.5: runs[-1][1]=x
            else: runs.append([x,x])
        runs=[r for r in runs if r[1]>=J0 and r[0]<J1]
        ex=[fromjd(e).isoformat() for e in sorted(d["exact"]) if J0-60<=e<=J1+60]
        big.append(dict(planet=p,aspect=nm,point=n,flow=nm in("sextile","trine") or (nm=="conjunct" and p=="Jupiter"),
            start=fromjd(min(r[0] for r in runs)).isoformat(), end=fromjd(max(r[1] for r in runs)).isoformat(),
            passes=[(fromjd(a).date().isoformat(),fromjd(b).date().isoformat()) for a,b in runs], exact=ex,
            house=house(pos(p,(runs[0][0]+runs[-1][1])/2)[0]), natal_house=house(natal[n]) if n not in("Ascendant","Midheaven") else None))
    PR={"Pluto":0,"Neptune":1,"Uranus":2,"Saturn":3,"Jupiter":4}
    big.sort(key=lambda b:b["start"])

    # ---- fast transits: 6-hour scan exact hits ----
    fast=[]; prev={}; ingress=[]; stations=[]; prevh={}; prevs={}
    jd=J0-1; STEP=0.25
    while jd<=J1:
        for p in FAST+SLOW:
            tl,sp=pos(p,jd)
            h=house(tl)
            if p in prevh and prevh[p]!=h and jd>=J0 and p in("Sun","Mars","Venus","Mercury","Jupiter","Saturn"):
                ingress.append(dict(planet=p,house=h,dt=fromjd(jd).isoformat(),retro=sp<0))
            prevh[p]=h
            if p!="Sun" and p in prevs and (prevs[p]>0)!=(sp>0) and jd>=J0:
                stations.append(dict(planet=p,direction="retrograde" if sp<0 else "direct",dt=fromjd(jd).isoformat(),deg=fmt(tl),house=h))
            prevs[p]=sp
            if p not in FAST: continue
            targets=NATAL_PERSONAL
            for n in targets:
                for a,nm in ASP.items():
                    if p in("Sun","Venus","Mercury") and a in (60,120) : continue
                    if p=="Mercury" and a!=0: continue
                    for s in ((1,) if a in (0,180) else (1,-1)):
                        v=adiff(tl,natal[n],a,s); k=(p,a,s,n); pv=prev.get(k)
                        if pv is not None and abs(v)<4 and ((pv<0<=v) or (pv>0>=v)) and jd>=J0:
                            t=jd-STEP+STEP*abs(pv)/(abs(pv)+abs(v))
                            fast.append(dict(planet=p,aspect=nm,point=n,dt=fromjd(t).isoformat(),flow=nm in("sextile","trine") or (nm=="conjunct" and p in("Venus","Sun")),house=house(tl)))
                        prev[k]=v
        jd+=STEP
    # dedupe ingress jitter
    ing=[]
    for e in ingress:
        if any(x["planet"]==e["planet"] and x["house"]==e["house"] and abs((dt.datetime.fromisoformat(e["dt"])-dt.datetime.fromisoformat(x["dt"])).days)<4 for x in ing): continue
        ing.append(e)
    ingress=ing

    # sun's house each month (at mid-month) and phases daily
    months=[]; d=start
    while d<end:
        mid=tojd(d.replace(day=15)); months.append(dict(month=d.strftime("%Y-%m"),sun_house=house(pos("Sun",mid)[0]),sun_sign=sign(pos("Sun",mid)[0])))
        d=(d.replace(day=28)+timedelta(days=4)).replace(day=1)
    days=[]; d=start.date()
    while d<end.date():
        jn=tojd(dt.datetime(d.year,d.month,d.day,12,tzinfo=tz))
        m,_=pos("Moon",jn); s,_=pos("Sun",jn)
        rx=[p for p in ["Mercury","Venus","Mars"] if pos(p,jn)[1]<0]
        days.append(dict(date=d.isoformat(),elong=(m-s)%360,moon_house=house(m),moon_sign=sign(m),rx=rx)); d+=timedelta(days=1)
    # eclipses
    ecl=[]
    for k, jj, _ in ctx.eclipses():
        ml=pos("Moon",jj)[0]
        ecl.append(dict(kind="Solar Eclipse" if k=="solar" else "Lunar Eclipse",dt=fromjd(jj).isoformat(),deg=fmt(ml),house=house(ml)))
    ecl.sort(key=lambda e:e["dt"])
    prof=ctx.profections()


    return dict(**ctx.window(), big=big, fast=fast, ingress=ingress, stations=stations, months=months, days=days,
                eclipses=ecl, prof=prof, natal={k: fmt(v) for k, v in natal.items()},
                natal_house={k: house(v) for k, v in natal.items()})
