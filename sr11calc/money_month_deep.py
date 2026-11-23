"""Deeper text for Your Monthly Money Forecast (Tiff's Nov 23 depth pass).

Everything here is composed with the person's natal chart, so the same transit reads differently for
different people. Voice rules: warm second person, contractions, no em dashes, almost no colons,
openings and invitations rather than promises, natal patterns kept separate from this month and from
the longer chapter.
"""

# --------------------------------------------------------------------------------------------------
# Planets and points
# --------------------------------------------------------------------------------------------------
NATURE = {
    "sun": "The Sun is about identity, vitality, and the life you're consciously choosing",
    "moon": "The Moon is about security, instinct, and what you need to feel safe",
    "mercury": "Mercury thinks, plans, negotiates, and connects",
    "venus": "Venus measures value, draws people in, and knows what feels worth it",
    "mars": "Mars pushes, competes, and gets things moving",
    "jupiter": "Jupiter seeks expansion, knowledge, and possibility",
    "saturn": "Saturn builds structure and asks for responsibility over time",
    "uranus": "Uranus resists any limit that keeps you from growing in your own direction",
    "neptune": "Neptune dissolves edges and reaches for something more inspired",
    "pluto": "Pluto works at the root, where power and transformation live",
}

# One line on what a moving planet brings when it activates a natal point.
BRINGS = {
    "sun": "attention, visibility, and a little extra confidence",
    "mercury": "conversations, information, and the paperwork that moves things forward",
    "venus": "value, goodwill, and the kind of ease that makes asking feel natural",
    "mars": "drive, urgency, and the willingness to act",
    "jupiter": "growth, generosity, and a wider view of what's possible",
    "saturn": "structure, patience, and a serious look at what's sustainable",
    "uranus": "disruption, independence, and the urge to break a pattern that's become too tight",
    "neptune": "inspiration, sensitivity, and a softer focus that can blur the details",
    "pluto": "depth, pressure, and the kind of change that starts at the root",
}

RETRO_DEEP = {
    "mercury": ("Your natal Mercury is retrograde, so your best thinking often happens on the second pass. You tend to understand "
                "a deal or an idea more fully after you've stepped away from it and come back."),
    "venus": ("Your natal Venus is retrograde, which turns your sense of value inward. You may need to decide for yourself what "
              "something is worth before anyone else's opinion can settle it."),
    "mars": ("Your natal Mars is retrograde, so effort tends to build privately before it shows. Once you've decided, though, "
             "you act with more force than people expect."),
    "jupiter": ("Your natal Jupiter is retrograde, which adds an internal dimension to growth. Rather than accepting conventional "
                "definitions of success without question, you're learning to build a philosophy of achievement that reflects "
                "your own understanding of purpose."),
    "saturn": ("Your natal Saturn is retrograde, so the rules you live by are often ones you wrote for yourself. Part of your "
               "work is noticing which of those standards still serve you and which were set by someone you no longer are."),
}

DIGNITY_DEEP = {
    "domicile": "{P} is in its own sign here, so it has real strength to draw on.",
    "exaltation": "{P} is exalted here, one of its most honored placements, so what it does tends to be noticed.",
    "detriment": "{P} is in the sign opposite its home, so its gifts work in a second language and can be easy to doubt.",
    "fall": "{P} is in its fall here, which doesn't make it weak so much as uneasy, and it can push too hard or hold back when it shouldn't.",
}

# Why each money role matters when it gets activated. These carry the "this is yours" weight.
ROLE_DEEP = {
    "second": ("Because {P} rules your second house of earned income, this reaches past earning potential. It also touches your "
               "relationship with receiving, your ability to name your own needs, and the patterns that decide what you believe "
               "you're allowed to have."),
    "career": ("Because {P} rules your Midheaven, whatever touches it touches your career direction. This is where questions about "
               "the work you want to be known for come up, sometimes before you're ready to answer them."),
    "both": ("Because {P} rules both your income and your career, anything that touches it moves your money and your reputation at "
             "the same time. That's a lot of weight on one planet, and it's why this activation deserves your attention."),
    "fortune": ("Your Part of Fortune brings the Sun, the Moon, and your Ascendant together into one point, traditionally linked "
                "with material circumstances and the conditions where prosperity can grow. When it's activated, it's worth "
                "looking at what's making life feel easier and doing more of that."),
    "assets": ("Your Lot of Assets is a traditional point tied to what you accumulate, own, and keep. Activations here bring "
               "attention to the resources you're building, not only the money passing through."),
    "mc": ("Your Midheaven is the very top of your chart, the public role you're developing and the contribution you want to be "
           "known for. It's about reputation and direction more than any single job."),
    "eighth": ("Because {P} rules your eighth house, it speaks for shared money, debt, taxes, and the agreements that tie your "
               "resources to someone else's."),
    "eleventh": ("Because {P} rules your eleventh house, traditionally the house of the gains that come from your work, it carries "
                 "your networks, your audiences, and the income that arrives through other people believing in you."),
    "venus": "Venus is the natural ruler of value in every chart, so its condition says a lot about how easily you let good things in.",
    "jupiter": "Jupiter is the natural ruler of growth and abundance in every chart, so contacts to it often show where expansion wants to happen.",
}

# How the career ruler's house shapes the career story.
CAREER_IN = {
    1: "This places your career in your own hands. Your reputation grows from your presence and from the choices you make for yourself.",
    2: "This links career and income closely. Your professional direction and the way you earn tend to rise and fall together.",
    3: "This ties your career to communication, writing, teaching, and the everyday exchange of ideas.",
    4: "This links your career to home and foundations, so your private life and your public role are never fully separate.",
    5: "This ties your career to creativity and self-expression, so work that carries something of you tends to go further.",
    6: ("This creates a relationship between your professional purpose and the way you spend your everyday life. You may be "
        "capable of succeeding inside demanding structures, but that doesn't mean those structures are the fullest expression "
        "of your path."),
    7: "This routes your career through partnership, so clients, collaborators, and agreements shape where you go.",
    8: "This ties your career to other people's resources, shared money, and work that handles what others can't.",
    9: "This links your career to knowledge, teaching, publishing, and a larger sense of meaning.",
    10: "This places your career ruler in its own house, so your public direction is strong and visible.",
    11: "This ties your career to networks and communities, so the people who believe in you become part of your path.",
    12: "This places your career ruler behind the scenes, so some of your most meaningful work may happen out of view.",
}

# --------------------------------------------------------------------------------------------------
# Houses
# --------------------------------------------------------------------------------------------------
HOUSE_DEEP = {
    1: ("The first house isn't only about appearance. It's your body, your instincts, and the way you start things, the part of "
        "you that acts before anyone else gives permission."),
    2: ("The second house isn't only about money. It describes what you value, what you keep, and the quiet sense of worth that "
        "decides what you'll ask for."),
    3: ("The third house is more than communication. It holds your daily conversations, your local world, your siblings, and the "
        "ideas you share every day without thinking of them as valuable."),
    4: ("The fourth house is the foundation under everything else. It holds home, family, property, and the private life that "
        "either supports your ambitions or quietly competes with them."),
    5: ("The fifth house governs creativity, pleasure, and the things you bring into the world because they reflect something "
        "authentic in you."),
    6: ("The sixth house isn't simply about employment. It describes the routines, obligations, systems, and repeated efforts "
        "that make your larger ambitions possible."),
    7: ("The seventh house is about the people you meet one to one, partners, clients, and the agreements that tie your plans to "
        "someone else's."),
    8: ("The eighth house holds what's shared, debt, taxes, investments, a partner's money, and the trust it takes to let your "
        "resources mix with someone else's."),
    9: ("The ninth house is about the larger view, teaching, publishing, travel, belief, and the philosophy you live by."),
    10: ("The tenth house is the most public part of your chart, your career, your reputation, and the role you play in the "
         "world."),
    11: ("The eleventh house is traditionally the house of good spirits and the gains that come from your work, along with "
         "friends, networks, and communities."),
    12: ("The twelfth house is the quiet part of the chart, solitude, rest, hidden worries, and the patterns that run underneath "
         "your choices until you take time to notice them."),
}

HOUSE_NOUN = {
    1: "the person you're becoming", 2: "the money you earn and keep", 3: "the way you communicate",
    4: "the foundation that gives you security", 5: "the creativity that expresses you", 6: "the work that sustains you",
    7: "the partnerships you rely on", 8: "the resources you share", 9: "the knowledge you're growing",
    10: "the reputation you're building", 11: "the communities that support you", 12: "the rest that restores you",
}

# The Sun moving through a house: what it spotlights and the question it asks.
SUN_Q = {
    1: "The Sun's movement here asks whether you're taking up the room you need, or still waiting to be invited.",
    2: "The Sun's movement here asks whether what you charge, keep, and spend still matches what you value.",
    3: "The Sun's movement here asks whether you're sharing what you know, or keeping your best ideas to yourself.",
    4: "The Sun's movement here asks whether your home base is giving you energy or quietly draining it.",
    5: "The Sun's movement here asks whether you're making room for the work you'd do even if nobody paid you.",
    6: ("The Sun's movement here invites you to examine whether your daily work is creating the freedom you want or consuming "
        "the time and energy you need to pursue it."),
    7: "The Sun's movement here asks which partnerships are adding to your life and which are asking more than they give.",
    8: "The Sun's movement here asks whether your shared money, debts, and agreements are still on terms you'd choose today.",
    9: "The Sun's movement here asks what you know now that's ready to reach more people.",
    10: "The Sun's movement here asks whether the work you're known for is the work you want to be known for.",
    11: "The Sun's movement here asks who's in your corner, and whether you've let them help.",
    12: "The Sun's movement here asks what you've been too busy to feel, and what rest would make possible.",
}

VENUS_REFRAME = {
    1: "Financially, this is a good moment to let your own presence be part of the offer, because people are responding to you.",
    2: "Financially, this is a gentle window to review prices and receive more easily, because value is flowing toward your own house of worth.",
    3: "Financially, this is an opportunity to see whether the way you explain your work is making its value obvious.",
    4: "Financially, this can be a good time to invest in your home or workspace, or to notice what makes you feel secure enough to grow.",
    5: ("Financially, this is an opportunity to reconsider whether the things that come naturally to you have been undervalued "
        "simply because they don't feel like traditional work."),
    6: "Financially, this is a moment to make your daily work more pleasant and more fairly paid, both at once.",
    7: "Financially, this favors partnerships, client relationships, and agreements that feel fair on both sides.",
    8: "Financially, this can ease conversations about shared money, loans, or what's owed, as long as the terms stay clear.",
    9: "Financially, this favors teaching, publishing, and anything that lets your knowledge reach farther.",
    10: "Financially, this can bring goodwill to your public role, a good moment to be seen for what you do well.",
    11: "Financially, this favors referrals, communities, and the people who already believe in your work.",
    12: "Financially, this favors quiet work and private decisions, and a gentler look at old worries about money.",
}

VENUS_HOUSE_DEEP = {
    1: "Venus moving through your first house brings warmth to how you come across, making it easier for people to say yes to you.",
    2: "Venus moving through your second house brings value straight into your house of income and possessions.",
    3: "Venus moving through your third house sweetens conversations, writing, and the ideas you share close to home.",
    4: "Venus moving through your fourth house brings ease to home, family, and the private foundation under your work.",
    5: "Venus moving through your fifth house brings a different quality into the month, creativity, pleasure, and work that feels like play.",
    6: "Venus moving through your sixth house brings grace to your daily work, routines, and the people you work beside.",
    7: "Venus moving through your seventh house brings goodwill to partners, clients, and one-to-one agreements.",
    8: "Venus moving through your eighth house brings attention to shared resources and the trust underneath them.",
    9: "Venus moving through your ninth house brings value to learning, teaching, travel, and a larger point of view.",
    10: "Venus moving through your tenth house brings charm and goodwill to your career and public reputation.",
    11: "Venus moving through your eleventh house brings support through friends, networks, and communities.",
    12: "Venus moving through your twelfth house turns value inward, toward rest, privacy, and quiet healing.",
}

MARS_HOUSE_DEEP = {
    1: "Mars moving through your first house puts energy into your body and your own initiative.",
    2: "Mars moving through your second house puts energy into earning, and sometimes into spending just as fast.",
    3: "Mars moving through your third house puts energy into conversations, errands, and quick decisions.",
    4: "Mars moving through your fourth house places energy around home, foundations, family responsibilities, and the structures that support your private life.",
    5: "Mars moving through your fifth house puts energy into creative projects and anything you're making for yourself.",
    6: "Mars moving through your sixth house puts energy into daily work, deadlines, and how hard you're pushing your body.",
    7: "Mars moving through your seventh house puts energy into partnerships and negotiations, where it can spark either progress or friction.",
    8: "Mars moving through your eighth house puts energy into shared money, debts, and the terms you've agreed to.",
    9: "Mars moving through your ninth house puts energy into learning, travel, and the beliefs you're willing to defend.",
    10: "Mars moving through your tenth house puts energy into your career and makes ambition hard to ignore.",
    11: "Mars moving through your eleventh house puts energy into networks, group projects, and long-range goals.",
    12: "Mars moving through your twelfth house turns effort inward, toward rest, private work, and what you've been carrying alone.",
}

MARS_TENSION = {
    1: "Mars may also expose impatience. The deeper question is whether you're acting for yourself or reacting to everyone else.",
    2: "Mars may also expose impulsive spending. The deeper question is whether your effort is building something you get to keep.",
    3: "Mars may also expose sharp words. The deeper question is whether your message is landing the way you intend.",
    4: ("Mars may also expose tension between the demands of your private life and your professional ambitions. The deeper "
        "question is whether the foundation you've created still supports the person you're becoming."),
    5: "Mars may also expose frustration with projects that stall. The deeper question is whether you're giving your creativity real time.",
    6: "Mars may also expose overwork. The deeper question is whether your routines are serving you or running you.",
    7: "Mars may also expose friction with others. The deeper question is whether your agreements still feel fair.",
    8: "Mars may also expose tension over who owes what. The deeper question is whether your shared arrangements are clear enough to trust.",
    9: "Mars may also expose restlessness. The deeper question is where you're ready to stretch farther than before.",
    10: "Mars may also expose pressure at work. The deeper question is whether your ambition is pointed where you actually want to go.",
    11: "Mars may also expose friction in groups. The deeper question is which alliances are worth your energy.",
    12: "Mars may also expose exhaustion. The deeper question is what you need to put down before you can move forward.",
}

# --------------------------------------------------------------------------------------------------
# Signs
# --------------------------------------------------------------------------------------------------
SIGN_LESSON = {
    "Aries": "Aries is a sign of courage and beginnings, and its deeper lesson involves learning to finish what you start without losing the fire that started it.",
    "Taurus": "Taurus is a sign of steadiness and worth, and its deeper lesson involves learning that security can grow without holding on so tightly.",
    "Gemini": "Gemini is a sign of curiosity and connection, and its deeper lesson involves learning which of your many ideas deserve your full attention.",
    "Cancer": ("Cancer is a sign associated with protection, nourishment, and security, but its deeper evolutionary lesson involves "
               "learning that caring for others doesn't require sacrificing yourself."),
    "Leo": "Leo is a sign of warmth and visibility, and its deeper lesson involves learning to be seen without needing applause to know your worth.",
    "Virgo": "Virgo is a sign of skill and service, and its deeper lesson involves learning that being useful and being valued aren't the same thing.",
    "Libra": "Libra is a sign of balance and fairness, and its deeper lesson involves learning that a fair exchange includes what you need too.",
    "Scorpio": "Scorpio is a sign of depth and trust, and its deeper lesson involves learning to share power without losing yourself.",
    "Sagittarius": "Sagittarius is a sign of vision and freedom, and its deeper lesson involves learning to build something lasting without fencing yourself in.",
    "Capricorn": "Capricorn is a sign of structure and ambition, and its deeper lesson involves learning that you're allowed to rest on what you've built.",
    "Aquarius": "Aquarius is a sign of independence and new ideas, and its deeper lesson involves learning to belong without giving up your own way of doing things.",
    "Pisces": "Pisces is a sign of compassion and imagination, and its deeper lesson involves learning to give from fullness rather than from depletion.",
}

LUN_SIGN = {
    "Aries": "Aries wants a clean start and a bold first move",
    "Taurus": "Taurus wants steadiness, comfort, and something solid to show for your effort",
    "Gemini": "Gemini wants information, options, and a good conversation",
    "Cancer": "Cancer wants safety, belonging, and a soft place to land",
    "Leo": "Leo wants to be seen and to create something that carries your name",
    "Virgo": "Virgo wants order, skill, and a system that actually works",
    "Libra": "Libra wants balance, fairness, and better agreements",
    "Scorpio": "Scorpio wants the truth underneath, even when it's uncomfortable",
    "Sagittarius": "Sagittarius seeks a broader horizon",
    "Capricorn": "Capricorn wants structure and a plan that holds up over time",
    "Aquarius": "Aquarius wants freedom and a fresh way of doing things",
    "Pisces": "Pisces wants meaning, rest, and room for intuition",
}

# --------------------------------------------------------------------------------------------------
# Stelliums and Saturn patterns
# --------------------------------------------------------------------------------------------------
STELLIUM = {
    1: ("With so much planetary energy concentrated in your first house, there's an ongoing lesson about recognizing your own "
        "value rather than measuring it entirely through what you provide for others."),
    2: "With so many planets gathered in your second house, money and self-worth are central threads of your life, never side topics.",
    3: "With so many planets gathered in your third house, your ideas and your voice are among your most valuable resources.",
    4: "With so many planets gathered in your fourth house, home and family shape your finances more than most people's.",
    5: "With so many planets gathered in your fifth house, your creativity isn't a hobby. It's a resource waiting to be taken seriously.",
    6: "With so many planets gathered in your sixth house, work, service, and the development of expertise are significant parts of your journey.",
    7: "With so many planets gathered in your seventh house, partnership is a major engine of your finances, for better and for harder.",
    8: "With so many planets gathered in your eighth house, shared money, trust, and transformation run deep in your financial story.",
    9: "With so many planets gathered in your ninth house, knowledge and meaning are as important to you as the paycheck.",
    10: "With so many planets gathered in your tenth house, your career is one of the strongest themes in your chart.",
    11: "With so many planets gathered in your eleventh house, your communities and long-range goals carry real weight.",
    12: "With so many planets gathered in your twelfth house, much of your strength develops privately before the world sees it.",
}

SATURN_PATTERN = {
    1: "When pressure builds, an older pattern may tell you to tighten your grip and handle everything yourself.",
    2: "When pressure builds, an older pattern may tell you to save harder, spend less on yourself, and wait until it feels safe.",
    3: "When pressure builds, an older pattern may tell you to stay quiet until you're absolutely sure.",
    4: "When pressure builds, an older pattern may tell you to hold the family together first and your own plans last.",
    5: ("When career pressures intensify, an older pattern may encourage you to take on more responsibility, work harder, or "
        "postpone your own desires until everything else feels secure."),
    6: "When pressure builds, an older pattern may tell you to work longer instead of working differently.",
    7: "When pressure builds, an older pattern may tell you to give more in a partnership than you receive.",
    8: "When pressure builds, an older pattern may tell you to carry other people's debts or decisions as if they were yours.",
    9: "When pressure builds, an older pattern may tell you that you need more credentials before you're allowed to lead.",
    10: "When pressure builds, an older pattern may tell you that your worth depends on how much you achieve.",
    11: "When pressure builds, an older pattern may tell you to do it alone rather than ask your network for help.",
    12: "When pressure builds, an older pattern may tell you to keep your worries private and push through.",
}
SATURN_TURN = ("{month} offers an opportunity to recognize that pattern before repeating it. The question isn't whether you can "
               "keep carrying the weight. It's whether carrying it is still necessary for the future you're trying to create.")

# --------------------------------------------------------------------------------------------------
# Activations (planet, class)
# --------------------------------------------------------------------------------------------------
ACT_LINE = {
    "transit": "This month {P} {verb} your {T}.",
    "day": "On {date}, {P} {verb} your {T}.",
}
VERB = {0: "meets", 60: "forms a sextile to", 90: "forms a square to", 120: "forms a trine to", 180: "forms an opposition to"}
VERB_SLOW = {0: "is crossing", 60: "is sextiling", 90: "is squaring", 120: "is trining", 180: "is opposing"}

# The first paragraph's meaning for a slow transit.
SLOW_MEAN = {
    ("jupiter", "conj"): "Jupiter brings growth to whatever it touches, and this is one of the warmer openings a month can hold.",
    ("jupiter", "soft"): "Jupiter's supportive angles are easy to miss because nothing feels urgent, yet help and good timing line up more readily.",
    ("jupiter", "hard"): "Jupiter in tension stretches you. Growth is available, and so is the temptation to take on more than you can hold.",
    ("saturn", "conj"): "Saturn settling here asks for commitment. What you build carefully now tends to last.",
    ("saturn", "soft"): "Saturn's supportive angles reward steady effort, so plans made carefully this month tend to hold.",
    ("saturn", "hard"): "Saturn in tension asks whether a structure can carry weight, and where you've been carrying too much.",
    ("uranus", "conj"): "Uranus brings awakening and sudden change, and it can open a door you didn't know was there.",
    ("uranus", "hard"): ("When Uranus forms a square or opposition, the tension often centers on the difference between growing "
                         "inside an existing structure and wanting to move beyond that structure entirely."),
    ("neptune", "conj"): "Neptune brings inspiration and a softer approach, though it can blur details, so let time confirm what's solid.",
    ("neptune", "hard"): "Neptune in tension can blur your picture of what's real, so get details in writing and give hopeful plans time to prove themselves.",
    ("pluto", "conj"): "Pluto brings change at the root, clearing away what no longer works so something truer can take its place.",
    ("pluto", "hard"): "Pluto in tension brings pressure to change at the root, often around who holds the power where money is concerned.",
}

# Deeper second paragraph for slow transits, independent of the target.
SLOW_DEEP = {
    ("jupiter", "conj"): ("Growth under Jupiter works best when you give it a direction. Say yes to what expands your life, not just "
                          "your workload."),
    ("jupiter", "soft"): "The best use of a supportive Jupiter is to ask for something a little bigger than usual and see what comes back.",
    ("jupiter", "hard"): ("Before you say yes to the next opportunity, ask whether taking on more will truly improve your "
                         "situation, or whether doing fewer things well would serve you better."),
    ("saturn", "conj"): "Saturn rewards the commitments you're willing to keep, and it shows you which ones you're not.",
    ("saturn", "soft"): "This is a good month for the unglamorous work, the budget, the contract, the plan, that makes the next year easier.",
    ("saturn", "hard"): ("It can feel like a slowdown, and it's often when you set the boundaries and prices you'll later be grateful "
                         "for."),
    ("uranus", "conj"): "Leave a little space in your plans. The surprise may be the point.",
    ("uranus", "hard"): ("Capability and fulfillment aren't always the same thing. You can be exceptionally good at something and "
                         "still recognize that it no longer represents the direction you want your life to take."),
    ("neptune", "conj"): "Follow the inspiration, and keep one foot on the ground while you do.",
    ("neptune", "hard"): "What feels uncertain now often becomes clearer once you stop forcing a decision.",
    ("pluto", "conj"): "What you let go of now makes room for something with more power behind it.",
    ("pluto", "hard"): "This isn't about control. It's about deciding what you're no longer willing to give your power to.",
}

SLOW_PRACTICAL = {
    "uranus": ("You may notice where professional commitments have become limiting, where outdated routines are consuming "
               "resources, or where a different approach to earning could create more independence. The purpose isn't to make "
               "impulsive decisions, but to examine whether the structures supporting your security are also supporting your growth."),
    "saturn": ("You may notice where income depends too heavily on your personal effort, or where a price, a boundary, or a plan "
               "needs to be firmer. Slow, deliberate decisions serve you best."),
    "jupiter": ("You may notice offers, introductions, or ideas that point toward a bigger version of what you're already doing. "
                "Choose the ones that fit the life you want, not only the income you want."),
    "neptune": ("You may notice that some opportunities look better than they are, and some look smaller than they are. Check the "
                "numbers, and check your intuition, and let both have a vote."),
    "pluto": ("You may notice power dynamics around money more clearly, who decides, who benefits, and who's been quietly paying "
              "the cost. Clarity is the first step to changing it."),
}

# Fast planets, by class.
FAST_MEAN = {
    ("venus", "soft"): "Venus days favor asking, pricing, pitching, and anything that depends on goodwill.",
    ("venus", "conj"): "When Venus crosses a point, value and attraction gather there, and receiving gets easier.",
    ("venus", "hard"): "Venus in tension can show you where value and need aren't lining up yet.",
    ("sun", "conj"): "When the Sun crosses a point, it lights it up, so this is a good day to be seen.",
    ("mercury", "conj"): "Mercury days are good for the conversation, the email, the proposal, or the paperwork that moves money forward.",
    ("mars", "conj"): "When Mars crosses a point, it adds energy and urgency, so act, and watch your pace.",
    ("mars", "hard"): "Mars in tension can bring friction or impatience, so give yourself an extra breath before you react.",
}

# Short glance meaning by target role.
GLANCE_TARGET = {
    "second": "bringing attention to how you earn and what you receive",
    "career": "putting your career direction in the spotlight",
    "both": "touching your income and your career at once",
    "mc": "connecting with your professional direction and reputation",
    "fortune": "bringing ease to the place where opportunity tends to find you",
    "assets": "drawing attention to what you're building and keeping",
    "venus": "touching your sense of value",
    "jupiter": "touching your capacity for growth",
    "sun": "touching your confidence and visibility",
    "other": "adding a small spark to your money story",
}

# Venus to a specific point, deeper.
VENUS_TO = {
    "mc": ("Venus brings value, cooperation, and attraction into contact with your public direction. This is a useful moment to "
           "present an idea, discuss the value of your contributions, or reconsider how your public identity reflects the work you "
           "genuinely want to be known for."),
    "second": ("This creates a direct connection between the planet of value and exchange and the planet governing your income."),
    "career": ("This brings goodwill to the planet that steers your career, a good moment for conversations about your role, your "
               "visibility, or your next step."),
    "fortune": ("Venus activating this point can emphasize the value of your own contributions and the importance of letting your "
                "work be seen."),
    "assets": "Venus here brings attention to material resources, ownership, and what you're working to accumulate.",
}
VENUS_CLUSTER = ("The concentration of Venus aspects between {d1} and {d2} deserves attention because several of your money points "
                 "are activated within a short stretch of days.")

MERCURY_TO_RULER = ("When Mercury activates {T}, conversations may carry more weight than they first appear to. An idea, a "
                    "proposal, or an exchange of information could encourage you to think beyond your current circumstances.")

# --------------------------------------------------------------------------------------------------
# Lunations
# --------------------------------------------------------------------------------------------------
NEW_LESSON = {
    1: "A new beginning here is personal. It asks you to start something for yourself, without waiting for anyone else to go first.",
    2: "A new beginning here asks for a new relationship with money itself, what you charge, what you save, and what you believe you deserve.",
    3: "A new beginning here may start with a conversation, a piece of writing, or a decision to say out loud what you know.",
    4: "A new beginning here may be about home, a move, a renovation, or simply making your private life more supportive of your work.",
    5: "A new beginning here invites a creative project, something you make because you want to, that may turn out to be valuable.",
    6: ("The deeper message here concerns the relationship between service and sacrifice. A new beginning in this house may "
        "involve changing the way you work rather than changing the work itself, and recognizing that productivity isn't measured "
        "only by how much effort you spend."),
    7: "A new beginning here may arrive through someone else, a client, a partner, or a collaboration that changes your direction.",
    8: "A new beginning here may involve a fresh look at debt, investments, or shared money, and new terms that better reflect who you are now.",
    9: "A new beginning here may be a course, a trip, a teaching idea, or a decision to share what you've learned more widely.",
    10: "A new beginning here is public. It's a strong moment to set a career intention and take one visible step toward it.",
    11: "A new beginning here may come through a group, a friend, or a long-range goal you've been holding quietly.",
    12: "A new beginning here starts privately. Rest, reflection, or a decision you make alone may be the seed of what comes next.",
}
FULL_LESSON = {
    1: "A Full Moon here can show you how much of yourself you've been giving away, and what you'd like to keep.",
    2: "A Full Moon here brings money matters to a head, a good moment to see clearly what you've earned and what you've been undervaluing.",
    3: "A Full Moon here can bring a conversation to completion or reveal what you've been meaning to say.",
    4: "A Full Moon here brings home and family to a peak, and may show where your private life needs more support.",
    5: "A Full Moon here can bring a creative effort to fruition, or show you where joy has gone missing from your work.",
    6: "A Full Moon here brings your daily work to a peak, and can show you which routines are worth keeping.",
    7: "A Full Moon here brings a partnership or agreement to a turning point.",
    8: "A Full Moon here brings shared money, debt, or trust into the light, so it can be dealt with honestly.",
    9: "A Full Moon here can bring a period of learning or teaching to completion, and show you what you now know.",
    10: "A Full Moon here brings your career to a visible peak, a moment of recognition or a moment of clarity.",
    11: "A Full Moon here can show you which friendships and networks are truly supporting your goals.",
    12: ("With the Full Moon in this house, you may become more aware of financial worries you've carried privately or "
         "responsibilities you've accepted because they once helped you feel safe."),
}
NEW_ARC = {1: "a personal fresh start", 2: "a new financial habit", 3: "a new conversation", 4: "a new foundation at home",
           5: "a creative beginning", 6: "practical restructuring", 7: "a new partnership", 8: "new terms around shared money",
           9: "a wider view", 10: "a career intention", 11: "a new alliance", 12: "a private reset"}
FULL_ARC = {1: "self-recognition", 2: "financial clarity", 3: "an honest conversation", 4: "clarity about home",
            5: "creative fruition", 6: "clarity about your routines", 7: "a partnership decision", 8: "honesty about what's shared",
            9: "a lesson learned", 10: "public recognition", 11: "clarity about your circle", 12: "emotional awareness"}
LUN_RULER_LINK = ("Because {sign} is ruled by {R}, the planet that rules your {what}, this lunation also connects directly with your "
                  "{story} story.")
LUN_SYNTH = "Together, these lunations create a movement from {a} to {b}. {tail}"
LUN_ANGLE = {
    "asc": "It falls close to your Ascendant, which makes it feel personal and visible.",
    "mc": "It falls close to your Midheaven, which brings your career directly into the picture.",
    "ic": "It falls close to the base of your chart, which brings home and foundations directly into the picture.",
    "dsc": "It falls close to your Descendant, which brings partners and clients directly into the picture.",
}

# --------------------------------------------------------------------------------------------------
# Progressed Moon
# --------------------------------------------------------------------------------------------------
PMOON_INTRO = ("Your progressed Moon describes a longer emotional chapter than the transits of a single month. In secondary "
               "progressions, the Moon moves about a degree a month and spends around two and a half years in each sign, so it "
               "shows how your inner needs and priorities are changing. While transits describe what's happening around you, "
               "your progressed Moon shows how you're responding to it, and money decisions are rarely separate from your need "
               "for security, belonging, freedom, and fulfillment.")

PMOON_SIGN = {
    "Aries": "you're moving through a season of courage and new starts, when waiting for permission feels harder than ever",
    "Taurus": "you're moving through a season of steadiness, when comfort, quality, and building something solid matter most",
    "Gemini": "you're moving through a season of curiosity, when ideas, conversations, and options keep you engaged",
    "Cancer": "you're moving through a season of nesting, when home, family, and emotional safety come first",
    "Leo": "you're moving through a season of visibility, when you want your work to carry your name and your heart",
    "Virgo": "you're moving through a season of refinement, when skill, health, and better systems feel deeply satisfying",
    "Libra": "you're moving through a season of partnership, when fairness and the people beside you shape your choices",
    "Scorpio": "you're moving through a season of depth, when trust, power, and what's real underneath matter more than appearances",
    "Sagittarius": "you're moving through a season of expansion, when meaning, learning, and a bigger horizon call to you",
    "Capricorn": "you're moving through a season of building, when ambition, responsibility, and long-range plans take center stage",
    "Aquarius": ("you're moving through a period in which freedom, knowledge, and a broader understanding of your place in the "
                 "world become increasingly important"),
    "Pisces": "you're moving through a season of softening, when intuition, rest, and meaning matter more than pushing harder",
}
PMOON_SIGN_TRAIT = {
    "Aries": "Aries is associated with initiative, independence, and the nerve to go first",
    "Taurus": "Taurus is associated with patience, value, and the pleasure of things that last",
    "Gemini": "Gemini is associated with learning, communication, and many interests at once",
    "Cancer": "Cancer is associated with protection, belonging, and care",
    "Leo": "Leo is associated with creativity, confidence, and generosity of spirit",
    "Virgo": "Virgo is associated with craft, usefulness, and getting the details right",
    "Libra": "Libra is associated with balance, beauty, and fair exchange",
    "Scorpio": "Scorpio is associated with intensity, investment, and transformation",
    "Sagittarius": "Sagittarius is associated with faith, adventure, and the search for meaning",
    "Capricorn": "Capricorn is associated with discipline, authority, and patient achievement",
    "Aquarius": ("Aquarius is associated with independence, innovation, communities, and the willingness to question established "
                 "expectations"),
    "Pisces": "Pisces is associated with compassion, imagination, and surrender",
}
PMOON_HOUSE_DEEP = {
    1: "The first house is about identity and self-direction, so your feelings about money are closely tied to who you're becoming.",
    2: "The second house is about income and worth, so your emotional life and your bank account are speaking to each other directly.",
    3: "The third house is about communication and learning, so what you say and what you study carry more emotional weight.",
    4: "The fourth house is about home and roots, so the security of your private life shapes every money decision.",
    5: "The fifth house is about creativity and joy, so you need your work to feel alive, not only profitable.",
    6: "The sixth house is about daily work and health, so how your days feel matters as much as what they pay.",
    7: "The seventh house is about partnership, so the people beside you play a large part in how secure you feel.",
    8: "The eighth house is about shared resources and trust, so debts, investments, and intimacy with money come to the surface.",
    9: ("The ninth house governs higher learning, philosophy, teaching, publishing, travel, and the expansion of perspective."),
    10: "The tenth house is about career and reputation, so your public role carries much of your emotional focus.",
    11: "The eleventh house is about friends and communities, so belonging to the right circle feels like a form of security.",
    12: "The twelfth house is about rest and the inner life, so this is a quieter chapter of healing and preparation.",
}
PMOON_MONEY = {
    "Aries": "Financially, you may feel ready to bet on yourself, start something new, or stop waiting for the safe moment.",
    "Taurus": "Financially, you may want to slow down, build savings, and invest in quality rather than quantity.",
    "Gemini": "Financially, you may be drawn to more than one source of income, or to work that keeps your mind busy.",
    "Cancer": "Financially, you may want to protect what you have, invest in your home, or take care of your family's security.",
    "Leo": "Financially, you may want your income to come from work that's visibly yours, and to be paid for your creativity.",
    "Virgo": "Financially, you may want better systems, cleaner books, and work that uses your skill well.",
    "Libra": "Financially, you may be drawn to partnerships, fairer agreements, and income that comes through collaboration.",
    "Scorpio": "Financially, you may want to look closely at debt, investments, and shared money, and reclaim control where you've lost it.",
    "Sagittarius": "Financially, you may be drawn to teaching, travel, publishing, or anything that feels bigger than your current life.",
    "Capricorn": "Financially, you may want a long-range plan, more authority, and income that builds rather than just arrives.",
    "Aquarius": ("Earlier chapters may have emphasized security through consistency and responsibility. During this one, those same "
                 "systems may start to feel restrictive if they limit your independence. You may find yourself drawn to income "
                 "connected to ideas, education, technology, communities, or work that reaches people beyond your immediate location."),
    "Pisces": "Financially, you may want work with more meaning, and you may be more aware of where money has been leaking quietly.",
}
PMOON_LESSON = {
    "Aries": "The lesson of this chapter is that courage and patience can work together.",
    "Taurus": "The lesson of this chapter is that real security grows from what you value, not from what you fear losing.",
    "Gemini": "The lesson of this chapter is that focus turns curiosity into something you can be paid for.",
    "Cancer": "The lesson of this chapter is that you're allowed to be one of the people you take care of.",
    "Leo": "The lesson of this chapter is that being seen is part of being paid.",
    "Virgo": "The lesson of this chapter is that good enough, done well, is often better than perfect.",
    "Libra": "The lesson of this chapter is that fairness includes what you need too.",
    "Scorpio": "The lesson of this chapter is that letting go can be a form of power.",
    "Sagittarius": "The lesson of this chapter is that freedom grows best with a little structure underneath it.",
    "Capricorn": "The lesson of this chapter is that you don't have to earn your rest.",
    "Aquarius": ("The lesson of this chapter is that freedom and security don't have to oppose one another. Financially, this may "
                 "mean reconsidering whether the most familiar way of earning is still the most meaningful, and learning to trust "
                 "unconventional ideas without abandoning the practical judgment you've developed over time."),
    "Pisces": "The lesson of this chapter is that rest and trust are productive too.",
}
PMOON_ECHO = "{what} reinforces this broader theme, making it part of both your immediate circumstances and your longer emotional development."

# --------------------------------------------------------------------------------------------------
# Solar arcs and the bigger current
# --------------------------------------------------------------------------------------------------
BIG_INTRO = ("Beneath the faster movements of the month, your solar arc directions describe a deeper period of personal and "
             "professional development. Solar arcs move your whole natal chart forward by the same small amount each year, "
             "creating contacts that astrologers read as longer developmental themes. Unlike a brief transit, they can stay "
             "relevant across a year or more, which helps explain why certain experiences feel like part of a larger turning "
             "point rather than an isolated event.")
BIG_INTRO_PROG = ("Beneath the faster movements of the month, your progressions describe a slower developmental current, one "
                  "that builds over a year or more.")

SA_MOVER = {
    "mc": "The Midheaven describes the public role you're developing",
    "asc": "The Ascendant describes how you meet the world and take initiative",
    "sun": "The Sun represents identity, vitality, purpose, and conscious self-expression",
    "moon": "The Moon represents your needs, your instincts, and your sense of safety",
    "mercury": "Mercury represents your thinking, your voice, and your commercial instincts",
    "venus": "Venus represents value, relationships, and what you're willing to receive",
    "mars": "Mars represents your drive, your ambition, and how you fight for what you want",
    "jupiter": "Jupiter represents growth, opportunity, and your philosophy of success",
    "saturn": "Saturn represents structure, responsibility, and what you're building over time",
    "uranus": ("Uranus represents individuation, the process of separating from expectations that no longer reflect who you "
               "really are"),
    "neptune": "Neptune represents vision, compassion, and the part of you that reaches past the practical",
    "pluto": "Pluto represents power, depth, and transformation at the root",
}
SA_ASPECT = {
    0: "A conjunction fuses the two, so their stories become one story for a while.",
    90: ("The square suggests a period when what's been established may no longer fit comfortably with the life you want to "
         "experience, and something has to adjust."),
    180: ("The opposition brings the two into a direct face-off, so you may feel pulled between them until you find a way to "
          "honor both."),
}
SA_TARGET = {
    "second": "Because {T} rules your second house, this direction also brings your income into the story.",
    "career": "Because {T} rules your Midheaven, this direction touches your career path directly.",
    "both": "Because {T} rules both your income and your career, this direction touches both at once.",
    "fortune": "Because this involves your Part of Fortune, it touches the conditions where prosperity tends to grow for you.",
    "assets": "Because this involves your Lot of Assets, it touches what you're building and keeping.",
    "mc": "Because this involves your Midheaven, it touches your career and reputation directly.",
    "sun": ("In your chart, the Sun is a central thread, so the question of who you're becoming sits at the center of this "
            "direction."),
    "other": "",
}
SA_ASPECT_AGAIN = {
    0: "This conjunction adds a second voice to the same story.",
    90: "This second square adds pressure to the same point, so it's worth taking seriously.",
    180: "This second opposition pulls on the same point from another direction.",
}
SA_SAME_TARGET = "That makes {T} a focal point of this year, touched by more than one direction at once."
SA_NOT_EVENT = ("It doesn't automatically point to a specific event, but it does describe a developmental period in which these "
                "themes become difficult to ignore.")
CONVERGE = ("When these directions are considered alongside {others}, a consistent theme begins to emerge. {pair} This is why the "
            "money questions of this month may feel bigger than ordinary decisions about income or expenses.")
MIDPOINT_DEEP = ("Midpoints are sensitive points halfway between two planets, and the {a} and {b} midpoint is one astrologers watch "
                 "for money. {mean} {P} activates it on {date}, so keep an eye out for what arrives around that day.")

# --------------------------------------------------------------------------------------------------
# Themes and convergence
# --------------------------------------------------------------------------------------------------
THEME = {
    "income": {"noun": "the way you earn and receive", "short": "income",
               "lesson": "The question isn't simply how to earn more. It's whether the way you earn and receive still reflects who you are now.",
               "final": ("Financial security isn't only about what you've accumulated or how reliably you can keep earning. It's also "
                         "about the choices those resources allow you to make and the time they give back to you.")},
    "career": {"noun": "your professional direction", "short": "career",
               "lesson": "Your career isn't only what you do. It's the contribution you want to be known for, and that can change.",
               "final": ("You don't have to discard what you've built to move in a new direction. The skills and experience you "
                         "already have can support a future that looks very different from your past.")},
    "freedom": {"noun": "personal freedom and independence", "short": "freedom",
                "lesson": "The lesson isn't to leave everything behind. It's to stop treating freedom as something you'll earn later.",
                "final": ("Your chart is asking where you've outgrown familiar structures, and where more independence could let "
                          "your abilities grow in a new direction.")},
    "structure": {"noun": "the structures and responsibilities you carry", "short": "structure",
                  "lesson": "Structure is meant to hold you up, not hold you in.",
                  "final": "The commitments worth keeping are the ones that still fit the person you're becoming."},
    "growth": {"noun": "growth and expansion", "short": "growth",
               "lesson": "Growth that fits your life is worth more than growth that simply adds to it.",
               "final": "Say yes to what expands your life, not only your workload."},
    "vision": {"noun": "vision and meaning", "short": "meaning",
               "lesson": "Meaning matters, and so do the details that make a vision real.",
               "final": "Let your intuition lead, and let the numbers confirm it."},
    "power": {"noun": "power and control around money", "short": "power",
              "lesson": "Power with money starts with knowing exactly where it goes and who decides.",
              "final": "What you reclaim now becomes the foundation for the next chapter."},
    "drive": {"noun": "effort and initiative", "short": "drive",
              "lesson": "Effort works best when it's pointed at something you actually want.",
              "final": "Your energy is a resource. Spend it where it builds something."},
    "value": {"noun": "value and what you're willing to receive", "short": "value",
              "lesson": "What you're worth and what you're paid can grow closer together, but only if you let them.",
              "final": "Let yourself receive at the level you give."},
    "security": {"noun": "emotional security", "short": "security",
                 "lesson": "Security can mean having choices, protecting your time, and trusting your ability to create resources.",
                 "final": "Security may once have meant control. It can now mean trust in yourself."},
    "identity": {"noun": "identity and self-direction", "short": "identity",
                 "lesson": "The more your work reflects who you are, the more aligned your money can become.",
                 "final": "Who you're becoming matters more than who you've been asked to be."},
    "voice": {"noun": "your voice and your ideas", "short": "ideas",
              "lesson": "Your ideas are an asset. Treat them like one.",
              "final": "Say what you know, and let it be valuable."},
}

PAIR = {
    frozenset(("freedom", "income")): ("Your professional identity, your daily responsibilities, your emotional security, and your "
                                       "desire for independence are all part of the same larger story."),
    frozenset(("freedom", "career")): ("The tension between achievement and personal freedom is becoming harder to ignore, and both "
                                       "are asking for a place in your next chapter."),
    frozenset(("career", "income")): "Your reputation and your income are moving together, so a change in one is likely to show up in the other.",
    frozenset(("structure", "freedom")): "The structures that kept you steady and the freedom you're reaching for are learning to share the same space.",
    frozenset(("security", "freedom")): "Security and freedom are both asking for attention, and they don't have to be opposites.",
    frozenset(("growth", "structure")): "Growth is asking for room while structure is asking for patience, and the right pace honors both.",
    frozenset(("power", "income")): "Who holds the power around your money is part of how your income can change.",
    frozenset(("value", "income")): "What you value and what you earn are being asked to match a little more closely.",
}
PAIR_GENERIC = "{A} and {B} are both being activated, and they're part of the same story."
FAST_AGAIN = {"sun": "It's another day to step forward and be seen.", "mercury": "Use it for a second round of conversations or follow-ups.", "venus": "It adds more goodwill to the month.", "mars": "Use the energy, and pace yourself."}

# Planet and sign themes.
PLANET_THEME = {"uranus": "freedom", "saturn": "structure", "jupiter": "growth", "neptune": "vision", "pluto": "power",
                "mars": "drive", "venus": "value", "moon": "security", "sun": "identity", "mercury": "voice"}
SIGN_THEME = {"Aries": "drive", "Taurus": "value", "Gemini": "voice", "Cancer": "security", "Leo": "identity", "Virgo": "voice",
              "Libra": "value", "Scorpio": "power", "Sagittarius": "growth", "Capricorn": "structure", "Aquarius": "freedom",
              "Pisces": "vision"}

# --------------------------------------------------------------------------------------------------
# Opening, glance, synthesis, preparing, final
# --------------------------------------------------------------------------------------------------
OPEN_FRAME = [
    ("Every month brings a different chapter in your financial story. Some months are about building, others about releasing, "
     "and some arrive to change the way you understand your own value."),
    ("No two months move money the same way. Some ask you to build, some ask you to rest, and some ask you to rethink what "
     "your work is really for."),
]
OPEN_THEMES = ("{month} carries a strong emphasis on {themes}. The movements this month are activating themes already written "
               "into your natal chart, which means this isn't only about what opportunities may appear. It's about recognizing "
               "which parts of your financial blueprint are ready to evolve.")
OPEN_QUIET = ("{month} is a steadier month in your chart. The movements this month touch your money points gently, which makes it "
              "a good time to refine, organize, and prepare for what's next.")
OPEN_UNTIMED = ("You didn't have a birth time, so I've read your houses from your Sun, the same solar houses I use in your Wealth "
                "Story. Points that need the exact minute you were born, like your Part of Fortune and Midheaven, stay out of this forecast.")

INCOME_LINE = "Your second house of earned income is ruled by {R}, and your natal {R} sits in {sign} in your {ord} house{with_}."
INCOME_LINE_SOLAR = "In your solar houses, your second house of earned income is ruled by {R}, and your natal {R} sits in {sign} in your {ord} house{with_}."
INCOME_HOUSE = {
    1: ("This creates a powerful connection between your identity, your personal decisions, and your ability to generate "
        "resources. Your financial path isn't designed to exist separately from who you are."),
    2: "This keeps earning and keeping closely linked. You have a natural feel for what things are worth.",
    3: "This links your income to ideas, communication, and the everyday exchange of what you know.",
    4: "This links your income to home, family, and the foundation under your life.",
    5: "This links your income to creativity and the things you make because they carry something of you.",
    6: "This links your income to daily work, skill, and the systems you build by showing up.",
    7: "This links your income to other people, partners, clients, and the agreements you make with them.",
    8: "This links your income to shared resources, investments, and other people's money.",
    9: "This links your income to knowledge, teaching, publishing, and reaching beyond where you started.",
    10: "This links your income directly to your reputation and public role.",
    11: "This links your income to networks, communities, and the people who believe in your work.",
    12: "This links your income to quiet work, behind the scenes, where its growth isn't always visible from outside.",
}
INCOME_ALIGN = ("The more closely your work reflects your natural instincts, knowledge, and individuality, the more aligned your "
                "relationship with money can become.")

LORD_SAME_R2 = ("{Lord} already rules your income, so its importance this month is amplified. This is a period to examine how "
                "you're earning, where you're taking initiative, and whether your current "
                "responsibilities support the future you're building.")
LORD_SAME_RC = ("{Lord} also rules your career, so this month's spotlight lands squarely on your professional direction and how "
                "you're being seen.")
LORD_OTHER = "In your chart, {lord} sits in {sign} in your {ord} house, so this month's money story runs through {topic}."

CAREER_OPEN = ("There's another layer to this month's story. Your natal Midheaven is in {mcsign}, connecting your career direction "
               "to {R}, which sits{rx} in {sign} in your {ord} house of {hof}.")
CAREER_OPEN_SOLAR = ("There's another layer to this month's story. In your solar houses your tenth house of career begins in {mcsign}, "
                     "connecting your career direction to {R}, which sits{rx} in {sign} in your {ord} house of {hof}.")
CAREER_HIT = ("With {P} activating {R} this month, {theme_line}")
CAREER_HIT_THEME = {
    "uranus": "the difference between professional achievement and personal freedom becomes increasingly difficult to ignore.",
    "saturn": "the structures around your work are asking to be tested and, where needed, rebuilt.",
    "jupiter": "there's room for your career to grow, if you choose the growth that fits.",
    "neptune": "your sense of direction may blur a little before it clarifies, so be patient with the in-between.",
    "pluto": "something about your professional role is ready to change at the root.",
}
CAREER_CLOSE = "{month} invites you to consider not only how you earn money, but what that money is ultimately meant to make possible."

GLANCE_SHAPE = ("{month} carries {n} key financial and professional dates, with the strongest concentration appearing in the "
                "{part} of the month.")
GLANCE_PART = {0: "first part", 1: "middle", 2: "second half"}
GLANCE_TAIL = ("What begins with practical decisions about work and income may end with a deeper understanding of what financial "
               "security actually means to you.")

MOVING_INTRO = ("The Sun, Venus, and Mars each describe a different side of your financial life. The Sun shows where your attention "
                "goes, Venus shows how you relate to value and exchange, and Mars shows where effort, initiative, and sometimes "
                "frustration gather. Their movements mean the most when we connect them to what's already in your chart.")
SUN_SHINES = "With the Sun moving through your {ord} house this month, the financial story turns toward {noun}."
OCC_LINE = "Your natal {names} {verb} this house in {sign}{extra}."
EMPTY_HOUSE = "Your {ord} house begins in {sign}, which makes {R} an important part of this story. Your natal {Rn} sits{rx} in {rsign} in your {rord} house."
MOVING_SYNTH = ("Together, these movements connect {a}, {b}, and {c}. {month} asks you to consider whether those areas are working "
                "together or competing for your attention.")
MOVING_SYNTH2 = ("Financial stability matters, and the deeper lesson may involve learning how to create stability without letting it "
                 "become a structure that limits your growth.")

OPEN_INTRO = ("The supportive movements this month offer several openings to work consciously with your money and career. A "
              "harmonious aspect doesn't guarantee an outcome, but it does describe a time when different parts of your chart are "
              "working together. The most meaningful openings are the ones that touch your own money points, because they "
              "activate themes that already belong to your wealth story.")
OPEN_SYNTH = ("Taken together, these dates create a concentrated period for examining the value of your work, your willingness to "
              "receive, and the resources you're building. The opportunity isn't simply to pursue more money. It's to recognize "
              "whether the way you're earning, receiving, and managing resources reflects your present values or an older version "
              "of you that learned security through obligation.")
WATCH_INTRO = "These are the places to move with more care this month, where tension is asking for a change rather than a reaction."
WATCH_DEEPER = "There's a deeper pattern here as well. {sat} sits in {sign} in your {ord} house, connecting duty and responsibility with {topic}."
QUIET_WATCH = ("Nothing in your sky this month is pressing hard on your money points. The places to watch are quieter, the habits "
               "and assumptions that decide whether what you earn actually stays with you.")
QUIET_OPEN = ("The openings this month are quieter, which makes them easy to miss. Use the steadier energy to tidy your systems, "
              "follow up on what's already in motion, and prepare for the next window.")

LUN_INTRO = ("The lunar cycle adds an emotional rhythm to the financial themes of the month. The New Moon marks a beginning, when "
             "something is being started or reconsidered, while the Full Moon brings a culmination, greater awareness, or a chance "
             "to release what has reached its natural end. Where they land in your chart shows where those developments matter most.")
LUN_LINE = {"new": "The New Moon on {date} falls at {deg} degrees {sign} in your {ord} house of {hof}.",
            "full": "The Full Moon on {date} falls at {deg} degrees {sign} in your {ord} house of {hof}."}
LUN_OCC = "Your natal {names} {verb} here, so this lunation stirs {themes} as well."
LUN_SIGN_JOIN = "{flavor}, while the {ord} house concerns {topic}, and this lunation brings them together."

PREP_HEAD = "What {month} Is Preparing You For"
PREP_OPEN = "{month} appears to be part of a larger transition in your relationship with {themes}."
PREP_LORD = "The monthly spotlight on {lord} connects {what}"
PREP_TRANSIT = "the transits highlight {what}"
PREP_PMOON = "your progressed Moon in {sign} reinforces {what}"
PREP_ARC = "your solar arc directions suggest that questions around {what} are developing over a longer period"
PREP_LUN = "As the month moves along, the emphasis shifts from {a} toward {b}. {tail}"
NEXT_LINE = "{nmonth} begins another chapter as the New Moon arrives in {sign} in your {ord} house of {hof}."
NEXT_HOUSE = {
    1: "This brings attention back to you, your own initiative, and the next step only you can take.",
    2: "This brings attention to income, savings, and what you're ready to value more highly.",
    3: "This brings attention to conversations, writing, and the ideas you're ready to share.",
    4: "This brings attention to home, family, and the foundation under your plans.",
    5: "This brings attention to creativity, pleasure, and work that feels like yours.",
    6: "This brings attention to routines, health, and the systems that make your days work.",
    7: ("This brings greater attention to agreements, collaboration, commitments, and the role other people play in your plans. "
        "Rather than viewing independence as doing everything alone, the next stage may involve learning which partnerships let "
        "you grow without compromising your freedom."),
    8: "This brings attention to shared money, debt, investments, and the terms that tie your resources to someone else's.",
    9: "This brings attention to learning, teaching, travel, and the bigger picture of where your work is going.",
    10: "This brings attention to your career and the next visible step in your professional direction.",
    11: "This brings attention to your networks, communities, and the people who can help your work travel farther.",
    12: "This brings attention to rest and reflection, a quieter start that prepares the ground for what's next.",
}

FINAL_CONVERGE = ("{month}'s financial story isn't defined by one favorable aspect or one challenging transit. Its significance "
                  "comes from the way several techniques point toward a similar theme. {list} Together, these signatures invite you "
                  "to reconsider not only how you're earning money, but how your financial choices reflect the person you're becoming.")
FINAL_SIMPLE = ("{month} is a month to work with what's already in motion. {list} None of it needs to be rushed, and all of it can "
                "be used on purpose.")
FINAL_NATAL = "Your natal chart carries a strong relationship between {a}. {b} {tail}"
FINAL_YET = "Yet your chart also contains signatures that question whether stability alone is enough."

# Variants for synthesis lines that would otherwise appear in every reading.
INCOME_ALIGN_V = [INCOME_ALIGN,
    "When the way you earn matches the way you're built, money tends to feel less like a fight and more like a flow.",
    "Your income grows most naturally when it comes from what you already do well without trying."]
OPEN_SYNTH_V = [OPEN_SYNTH,
    ("Put together, these openings make this a good month to be deliberate about value, what you charge, what you accept, and "
     "what you let yourself receive. The point isn't more for the sake of more. It's letting your income reflect who you are now."),
    ("Taken as a group, these dates favor asking, receiving, and naming your worth out loud. They work best when you treat them as "
     "invitations to act, not as promises to wait for.")]
FINAL_NATAL_TAIL_V = ["Much of your financial development has involved learning how to use your abilities, knowledge, and dedication to create stability.",
    "Your money story has always been about turning who you are into something that supports you.",
    "Over time, your chart has been teaching you to build security from your own strengths rather than borrowing someone else's map."]
PREP_LUN_TAIL_V = ["This creates an opportunity to recognize that building wealth and building the life you want aren't separate goals.",
    "That arc is worth following on purpose, because each step makes the next one easier.",
    "Let the first half of the month set things in motion and the second half show you what they mean."]
LUN_SYNTH_TAIL_V = ["Both are connected to your financial life, because lasting change often needs a different relationship with security before it can produce a different relationship with money.",
    "Read together, they show you where to begin and what to let go of, in that order.",
    "One opens a door, the other shows you what's on the other side of it."]

CAL_INTRO = ("Here's your month on one page. Each day lists what's moving in the sky and the point in your natal chart it touches, "
             "so you can plan around it. Gold notes are openings, rose notes ask for a little more care, purple marks the New and "
             "Full Moons, lilac notes are slower inner shifts, and gray notes show a planet moving into a new house of your chart.")

# Closing lines for younger readers (under 30), whose career and money story is still taking shape.
YOUNG = {
    "tail": ["Your money story is still taking shape, and this is the season to learn what kind of work turns who you are into something that supports you.",
             "You're still early in your money story, which means the habits you build now carry a long way."],
    "career": "You don't need to have it all figured out yet. Each choice you make now teaches you what kind of work truly fits you.",
    "income": "Financial security grows from small, steady choices, and the ones you make at this age compound for years.",
    "open_synth": 1,
}
