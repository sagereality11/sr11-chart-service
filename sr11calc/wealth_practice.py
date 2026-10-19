"""Try This steps, journal prompts and 'How to Work With It' notes for the Wealth Story Reading.

Every line follows the reading's voice rules: warm second person, contractions, no em dashes,
no colons, and nothing that repeats a sentence used elsewhere in the reading.
"""
from . import wealth as W
from . import wealth_text as T

ELEMENT = {s: e for e, signs in {
    "fire": ("Aries", "Leo", "Sagittarius"), "earth": ("Taurus", "Virgo", "Capricorn"),
    "air": ("Gemini", "Libra", "Aquarius"), "water": ("Cancer", "Scorpio", "Pisces")}.items() for s in signs}

# ---------------------------------------------------------------- How You Create Value
VALUE_TRY = {
    "moon": "Make a list of the things people already come to you for, the ones you do without thinking. Circle the one that leaves you feeling most like yourself afterward, and put a price or a plan next to it this week.",
    "sun": "Write one sentence that says what you do and who it's for, then say it out loud to someone this week without softening it. Notice where you want to make it smaller, and leave it big.",
    "mercury": "Pick one thing you explain well and turn it into something people can buy or book, even a small version of it. A short guide, a single session, or a workshop all count. Your words are part of your currency, so let them work for you.",
    "venus": "Look at your prices or your pay and ask whether they match the quality you actually deliver. Raise one thing by a small, comfortable amount, or ask for one thing you've been hoping someone would offer.",
    "mars": "Choose one money task you've been circling and give it a single focused hour this week. You earn through action, and one finished step will do more for you than a week of planning.",
    "jupiter": "Write down three things you know that other people would happily learn from you. Choose one and share it publicly this month, as a post, a class, or a conversation with someone who could hire you.",
    "saturn": "Pick one small financial habit you can keep for thirty days, like moving a set amount to savings every payday or writing down every dollar that comes in. Your chart rewards the slow, steady things you actually keep doing.",
}
VALUE_PROMPT = {
    1: "Where in your life are you the product, and how do you feel about being seen that way?",
    2: "What did you learn growing up about what money is worth and what you're worth? Which of those beliefs still fits you?",
    3: "Which conversations, ideas, or skills with words have brought you the most opportunity so far?",
    4: "How do home, family, and your sense of belonging shape the way you earn and spend?",
    5: "What do you make or do for joy that someone has already offered to pay for, or could?",
    6: "Which parts of your daily work feel like your craft, and which ones drain you without paying you back?",
    7: "Which partnerships or clients have helped you earn the most, and what did those relationships have in common?",
    8: "How do you feel about receiving, whether it's a raise, a gift, an investment, or help? Where do you push it away?",
    9: "What do you know, teach, or believe that could become a source of income if you trusted it more?",
    10: "What do you want to be known for, and is your income connected to that yet?",
    11: "Who in your circle has opened a door for you, and whose door could you open?",
    12: "What work do you do behind the scenes that nobody sees? What would change if it were valued and paid?",
}
HOUSE_SHORT = {1: "self and initiative", 2: "income and worth", 3: "communication and learning", 4: "home and family",
               5: "creativity and pleasure", 6: "daily work", 7: "partnership", 8: "shared resources",
               9: "travel, teaching, and belief", 10: "career and reputation", 11: "friends and community", 12: "rest and the unseen"}
SIGN_GIFT = {"Aries": "courage and starting things", "Taurus": "patience and quality", "Gemini": "ideas and connection",
             "Cancer": "care and instinct", "Leo": "warmth and presence", "Virgo": "skill and precision",
             "Libra": "fairness and beauty", "Scorpio": "depth and focus", "Sagittarius": "vision and teaching",
             "Capricorn": "structure and persistence", "Aquarius": "originality and community", "Pisces": "intuition and compassion"}
VALUE_PROMPT_2 = "Your income ruler, {R} in {S}, earns through {gift}. When have you felt most fairly paid for exactly that, and what made it work?"

# ---------------------------------------------------------------- Fortune and Assets
FORTUNE_TRY = {
    1: "For the next week, write down every moment an opportunity comes to you simply because you showed up as yourself. Your luck tends to follow your presence, so the list will show you where to show up more.",
    2: "Track every source of money that comes in this month, even the small ones. Your fortune grows when you pay close attention to what you already have.",
    3: "Send three messages this week to a sibling, a neighbor, a former classmate, or a local contact, just to reconnect. Opportunity in your chart often travels through everyday conversation.",
    4: "Make one change at home that supports your work or your rest, even something small like clearing a corner or setting up a desk. Your fortune is rooted at home, so when home feels right, opportunity tends to follow.",
    5: "Give yourself one hour this week to make something purely because you enjoy it. Your fortune opens through play, and pressure tends to close it.",
    6: "Choose one daily routine that makes your work easier and keep it for two weeks. Your opportunities grow through the details of how you work each day.",
    7: "Reach out to one person you'd love to work with and suggest a simple idea. Your fortune moves through other people, so the right partnership can open what working alone can't.",
    8: "Review one shared financial arrangement, like a loan, a joint account, a contract, or a split of costs, and make sure it's fair and clear. Your fortune grows through what you hold with others when those agreements are honest.",
    9: "Sign up for one class, trip, or course of study you've been wanting. Your fortune expands when you widen your world.",
    10: "Update one public place people find you, like your bio, your website, or your profile, so it reflects what you do now. Your opportunities follow your visibility.",
    11: "Tell three people in your circle exactly what you're working toward and what kind of help would make a difference. Your fortune arrives through friends and community, and they can't help with what they don't know.",
    12: "Set aside quiet time this week with no phone and no plan, and write down whatever comes up. Your fortune works behind the scenes, and solitude is where you notice it.",
}
FORTUNE_PROMPTS = [
    "Your Part of Fortune sits in your {ord} house. Think of a time luck seemed to find you in that part of life. What were you doing, and what made it feel easy?",
    "Your Lot of Assets falls in {asign} in your {aord} house. What have you kept and grown in that part of life so far, and what would you like to keep more of?",
]

# ---------------------------------------------------------------- What Can Block the Flow
BLOCK_TRY = {
    "moon": "The next time money stirs up a strong feeling, wait one full day before you decide anything. Write the feeling and the facts on separate lines, then decide from the facts.",
    "sun": "Write down three things that make you valuable that have nothing to do with this month's income. Keep the list somewhere you'll see it on a slow week.",
    "mercury": "Pick one money decision you've been researching for too long. Give yourself a deadline this week, choose the simplest good option, and let it be done.",
    "venus": "Before you offer your next discount or favor, pause and ask whether you're giving it freely or because you're nervous to ask for full price. If it's nerves, charge the full amount once and see what happens.",
    "mars": "When a money problem shows up, ask yourself out loud whether it's yours to fix. If it isn't, hand it back. If it is, set a time to handle it instead of reacting in the moment.",
    "jupiter": "Set one ceiling this month, whether it's a spending limit, a number of commitments, or a cap on new projects. Write it down and treat it as a promise to your future self.",
    "saturn": "Build one small safety structure this week, like an automatic savings transfer, an emergency line in your budget, or a simple agreement template. Let it do some of the worrying so you don't have to.",
}
BLOCK_PROMPT = {
    "moon": "When does money feel like a judgment about you? Whose voice does that judgment sound like?",
    "sun": "Who are you on a slow money month? What would you say to a friend who felt that way?",
    "mercury": "Which money decision have you been turning over for too long, and what's the simple answer you already know?",
    "venus": "Who do you undercharge or over-give to, and what are you hoping to receive in return?",
    "mars": "Which money problems have you rushed to fix that weren't really yours to carry?",
    "jupiter": "Where has trusting that more will come helped you, and where has it cost you?",
    "saturn": "What would safe enough actually look like for you, in real numbers?",
}
BLOCK_PROMPT_2 = "Your income ruler sits in your {ord} house of {topic}. Which habit in that part of your life quietly costs you money or energy?"

# ---------------------------------------------------------------- Career
CAREER_TRY = {
    1: "Introduce yourself this week by the work you want to be known for, not only the job you have. Let people connect your name with that direction.",
    2: "Write down what your skills earn you now and what they could earn if you packaged them well. Choose one change that moves the first number toward the second.",
    3: "Share what you do in a short, clear message this week, like a post, an email, or a quick talk. Your reputation grows every time you explain your work well.",
    4: "Set up one thing at home that makes your work easier or more professional, like a dedicated space, better tools, or set hours.",
    5: "Bring one piece of real personality into your work this month, a creative project, a playful idea, or a signature touch people will remember.",
    6: "Write down the problems you solve best at work. Choose one and make it visible by offering it, naming it, or asking to be known for it.",
    7: "Reach out to one potential client, partner, or collaborator this week. Your career grows through one-to-one relationships, so start one.",
    8: "Look at how your work could involve other people's resources, like investors, grants, clients with bigger budgets, or shared ventures. Take one step toward the one that fits.",
    9: "Teach, write, or speak about one thing you know deeply. Choose a place that reaches beyond your usual audience.",
    10: "Write down one career goal you'd be proud to be seen pursuing, then tell someone you respect. Saying it out loud makes it real.",
    11: "Ask two people in your network what they see as your strongest professional gift. Their answers can show you where your reputation is already growing.",
    12: "Name one thing you do quietly that makes everything else work, and find a way to make it visible. Put it on your list of services, in your bio, or in your next review.",
}
CAREER_PROMPTS = [
    "Your Midheaven in {mc} is tied to {gift}. If you were already respected for that, what would an ordinary Tuesday look like?",
    "Your career ruler sits in your {ord} house of {topic}. Where does that part of life already show up in your work, and where is it missing?",
]

# ---------------------------------------------------------------- Fifth, Eighth, Eleventh
FIFTH_TRY = {
    "fire": "Say yes to one creative idea before you talk yourself out of it. Post it, pitch it, or start it this week, and let it be imperfect.",
    "earth": "Turn one hobby or craft into something tangible, like a finished piece, a price list, or a small offer, so you can see what it's worth in the real world.",
    "air": "Share one creative idea with someone who gets it, and ask what they'd want more of. Your creativity grows in conversation.",
    "water": "Make something just for the feeling of it this week, with no plan to sell it. Notice what you lose track of time doing. That's the thread worth following.",
}
FIFTH_PROMPTS = [
    {"fire": "What creative risk have you been waiting for permission to take?",
     "earth": "What do you make with your hands, or with real care, that people already admire?",
     "air": "Which idea keeps coming back to you, asking to be shared?",
     "water": "What did you love doing as a kid, before anyone told you whether it was practical?"},
    "With {R} ruling your fifth house from your {ord} house of {topic}, which creative project could pay you this year, and what's the smallest first step?",
]
EIGHTH_TRY = {
    "fire": "Have one direct conversation about shared money you've been putting off, like a split of costs, a debt, or a payment you're owed. Short and honest beats long and avoided.",
    "earth": "Gather the paperwork on one shared arrangement, like a loan, a joint account, insurance, or a contract, and read it from start to finish. Knowing the terms is its own kind of security.",
    "air": "Write down the agreements you have with others around money, including the unspoken ones. Seeing them in words often shows you which ones need a real conversation.",
    "water": "Notice where you feel uneasy about money that involves someone else. Name the feeling first, then choose one small, practical step that makes the arrangement feel safer.",
}
EIGHTH_PROMPTS = [
    {"fire": "Where do you avoid money conversations with others, and what would one honest sentence sound like?",
     "earth": "What did you learn about debt, borrowing, and sharing money from the people who raised you?",
     "air": "Which money agreements in your life have never been said out loud?",
     "water": "Where does sharing money with someone feel emotionally heavy, and what would make it lighter?"},
    "{R} rules your eighth house from your {ord} house of {topic}. Which shared arrangement in that part of your life feels balanced right now, and which one doesn't?",
]
ELEVENTH_TRY = {
    "fire": "Start something that brings people together around the work you care about, like a group chat, a meetup, or a collaboration. You're good at lighting the spark.",
    "earth": "Make a simple list of the people who've helped your work so far, and thank one of them this week in a concrete way. Steady relationships are where your gains build.",
    "air": "Join one new group, online or in person, where people talk about the work you want to do. Your next opportunity may be one conversation away.",
    "water": "Reach out to one person in your circle you feel genuinely close to and ask how you can support what they're building. Your networks grow through real care.",
}
ELEVENTH_PROMPTS = [
    {"fire": "Which group or cause lights you up enough that you'd happily lead it?",
     "earth": "Who has quietly supported your work over the years, and have they heard that from you?",
     "air": "Who are the people you'd call first with good news about your work? What does that tell you about your circle?",
     "water": "Where do you give support easily but find it hard to receive it?"},
    "{R} rules your eleventh house from your {ord} house of {topic}. Who in that part of your life could you ask for support this year?",
]

# ---------------------------------------------------------------- The pattern (nodes)
PATTERN_TRY = {
    1: "Make one money decision this week on your own judgment, without asking anyone first. Notice how it feels to trust yourself.",
    2: "Open a savings account or a fund that's only yours, even with a small amount. Owning something you built is part of your growth.",
    3: "Share one idea this week through a post, an email, or a short lesson. Small, regular exchanges build your path more than waiting for the big one.",
    4: "Make one change that helps home support you, like a household budget, a workspace, or a boundary around family requests.",
    5: "Take one small, joyful risk with your work this month, something that carries your personality more than your résumé.",
    6: "Set up one system this week, like a schedule, a template, or an automatic payment, that turns a good intention into a habit.",
    7: "Ask someone to partner with you on one piece of work, or accept help you'd normally refuse. Let someone else carry part of it.",
    8: "Learn about one way to let your money work for you, like an investment account, a retirement plan, or a shared venture, and take one small step.",
    9: "Teach what you know to one new audience this month through a class, a workshop, or a post that reaches beyond your usual circle.",
    10: "Name one career goal out loud to someone you respect, and ask them what they'd see as the next step.",
    11: "Join or support one community that shares your goals, and let yourself receive from it as well as give.",
    12: "Protect one block of quiet time each week with no work and no output. Rest is part of how your path unfolds, not a break from it.",
}
PATTERN_PROMPTS = [
    "Your South Node in {sn} knows an old, familiar way of coping. When money gets stressful, how does that show up for you, and what does it protect you from?",
    "What would one small step toward your North Node in {nn} look like this month?",
]

# ---------------------------------------------------------------- Thresholds
WORK = {
    ("jupiter", "conj"): "Say yes to growth, and choose it on purpose. Make a short list of the opportunities you'd love to see this year, and when one shows up, act on it within a week. This window favors the people who are ready.",
    ("jupiter", "soft"): "Ask for help, referrals, and introductions during this window. Doors open more easily now, so it's a good time to pitch, apply, or reconnect with people who know your work.",
    ("jupiter", "hard"): "Before you say yes to something new, ask what it will cost you in time and energy. Choose the opportunities that fit the life you want, and let the rest pass by.",
    ("saturn", "conj"): "Pick one structure to commit to, like a budget, a business plan, a savings goal, or a routine, and give it the whole window. Go slower than you'd like and build it to last.",
    ("saturn", "soft"): "Use this window to make plans you'll actually keep. Put dates on your goals, sign the agreements, and set up systems while the energy supports steady effort.",
    ("saturn", "hard"): "Look at where you're carrying too much and decide what to put down, hand off, or price differently. Raise a rate, set a boundary, or end an arrangement that only works when you overwork.",
    ("uranus", "conj"): "Leave room in your plans for the unexpected. Keep a small cushion of savings and time so you can say yes when a surprising door opens.",
    ("uranus", "hard"): "Pause before you react when change arrives, and ask what it's making room for. Keep your finances flexible, and let go of what has clearly run its course.",
    ("neptune", "conj"): "Follow your inspiration and check the details twice. Write your ideas down, then let a few weeks pass before you put money behind them.",
    ("neptune", "hard"): "Put every money agreement in writing during this window. If something sounds too good to be true, ask someone you trust to look it over with you before you commit.",
    ("pluto", "conj"): "Let something old end so something truer can begin. Choose one money habit or arrangement that no longer fits and start taking it apart with care.",
    ("pluto", "hard"): "Notice where money and power are tangled in your life, and take back one decision that belongs to you. Quiet, steady changes at the root last longer than dramatic ones.",
}
WORK_INGRESS = {
    "jupiter": "Treat this as the start of a growth chapter in that part of your life. Notice what opens up over the next few months, and follow the openings that feel like a fit.",
    "saturn": "Treat this as the start of a building chapter. Choose one commitment in that part of your life and give it steady attention, even when progress feels slow.",
    "uranus": "Treat this as the start of a long season of change. Stay curious, try one new approach, and keep your plans loose enough to adjust.",
    "neptune": "Treat this as the start of a long, dreamy season. Follow what inspires you there, and keep your practical details clear and written down.",
    "pluto": "Treat this as the start of a deep, slow transformation. Let what no longer fits fall away a little at a time.",
}
WORK_TARGET = {
    "money": "Because this touches the points that carry your money story, keep a simple record of what changes in your income during this window. Patterns are easier to see on paper.",
    "career": "Because it touches your career, pay attention to what people start asking you for. That's often where the window is pointing.",
    "asc": "Because it touches your Ascendant, take care of your body and your energy first. Everything else moves more easily from there.",
}
THRESH_PROMPT = {
    "jupiter": "If this window could grow one thing in your financial life, what would you want it to be?",
    "saturn": "What are you ready to commit to, and what are you ready to stop carrying?",
    "uranus": "Which part of your work or money life feels ready for a change, even if it scares you a little?",
    "neptune": "Where are you hoping something will work out without looking closely at it? What would looking closely change?",
    "pluto": "What would you let go of if you trusted that something better could grow in its place?",
}
THRESH_LEAD = "With {P} touching your {names}, "


def _join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def add_practices(a, sections, R, threshold_info):
    """Attach a 'practice' dict to the main sections and the threshold subsections.

    threshold_info maps a level-2 section id to (planet, main_class or None, has_ingress, target keys).
    """
    P = a["planets"]
    r2, rc = R[2], R[10]
    rf = W.RULER[P["fortune"]["sign"]]
    by_id = {s["id"]: s for s in sections}

    def put(sid, try_txt, prompts, label="Try This"):
        if sid in by_id:
            by_id[sid]["practice"] = {"label": label, "try": try_txt, "prompts": [p for p in prompts if p]}

    nm = lambda pid: ("the " + W.NAME[pid]) if pid in ("sun", "moon") else W.NAME[pid]
    put("value", VALUE_TRY[r2], [VALUE_PROMPT[P[r2]["house"]],
                                 VALUE_PROMPT_2.format(R=nm(r2), S=P[r2]["sign"], gift=SIGN_GIFT[P[r2]["sign"]])])
    put("fortune", FORTUNE_TRY[P["fortune"]["house"]],
        [FORTUNE_PROMPTS[0].format(ord=T.ORD[P["fortune"]["house"]]),
         FORTUNE_PROMPTS[1].format(asign=P["assets"]["sign"], aord=T.ORD[P["assets"]["house"]])])
    put("blocks", BLOCK_TRY[r2], [BLOCK_PROMPT[r2], BLOCK_PROMPT_2.format(ord=T.ORD[P[r2]["house"]], topic=HOUSE_SHORT[P[r2]["house"]])])
    put("career", CAREER_TRY[P[rc]["house"]],
        [CAREER_PROMPTS[0].format(mc=W.sign_of(a["lon"]["mc"]), gift=SIGN_GIFT[W.sign_of(a["lon"]["mc"])]), CAREER_PROMPTS[1].format(ord=T.ORD[P[rc]["house"]], topic=HOUSE_SHORT[P[rc]["house"]])])
    for h, sid, TRY, PR in ((5, "fifth", FIFTH_TRY, FIFTH_PROMPTS), (8, "eighth", EIGHTH_TRY, EIGHTH_PROMPTS),
                            (11, "eleventh", ELEVENTH_TRY, ELEVENTH_PROMPTS)):
        el = ELEMENT[a["house_sign"][h]]
        rr = R[h]
        second = PR[1].format(R=nm(rr), ord=T.ORD[P[rr]["house"]], topic=HOUSE_SHORT[P[rr]["house"]])
        put(sid, TRY[el], [PR[0][el], second[0].upper() + second[1:]])
    put("pattern", PATTERN_TRY[P["north_node"]["house"]],
        [PATTERN_PROMPTS[0].format(sn=P["south_node"]["sign"]), PATTERN_PROMPTS[1].format(nn=P["north_node"]["sign"])])

    money = {r2, rf, "fortune", "assets"}
    used_target = set()
    for sid, (pl, cls, ingress, targets, names) in threshold_info.items():
        if cls and (pl, cls) in WORK:
            txt = WORK[(pl, cls)]
            if names:
                lead = THRESH_LEAD.format(P=pl.title(), names=_join(names[:2]))
                txt = lead + txt[0].lower() + txt[1:]
        elif ingress and pl in WORK_INGRESS:
            txt = WORK_INGRESS[pl]
        else:
            txt = WORK.get((pl, "conj"), "")
        extra = ""
        if any(t in money for t in targets) and "money" not in used_target:
            extra, kind = WORK_TARGET["money"], "money"
        elif any(t in ("mc", rc) for t in targets) and "career" not in used_target:
            extra, kind = WORK_TARGET["career"], "career"
        elif "asc" in targets and "asc" not in used_target:
            extra, kind = WORK_TARGET["asc"], "asc"
        if extra:
            used_target.add(kind)
        put(sid, (txt + " " + extra).strip(), [THRESH_PROMPT.get(pl, "")], label="How to Work With It")
