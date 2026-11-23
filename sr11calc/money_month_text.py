"""Text for Your Monthly Money Forecast, in Tiff's voice.

Rules: warm second person, contractions, no em dashes, almost no colons, plain words, no sentence
copied from the Wealth Story, and placements framed as openings and invitations, never promises.
"""
from .wealth_text import ORD, HOUSE_TOPIC  # noqa: F401

SHORT_TOPIC = {1: "your own initiative", 2: "your income and sense of worth", 3: "communication and your local world",
               4: "home and family", 5: "creativity and the work you love", 6: "your daily work and routines",
               7: "partners and clients", 8: "shared money, debt, and agreements", 9: "learning, teaching, and travel",
               10: "your career and reputation", 11: "your networks and the gains your work brings",
               12: "rest, retreat, and work behind the scenes"}

HOUSE_OF = {1: "self and initiative", 2: "income and worth", 3: "communication and learning", 4: "home and family",
            5: "creativity and pleasure", 6: "daily work", 7: "partnership", 8: "shared resources",
            9: "travel, teaching, and belief", 10: "career and reputation", 11: "friends and community", 12: "rest and the unseen"}

INTRO = ("This is your money and career forecast for {month}. I've read this month's sky against the same points that carry "
         "your wealth story, the planet that rules your income, the ruler of your career, and the places in your chart "
         "where opportunity tends to find you. Think of it as your money weather for the next few weeks, what's opening, "
         "what to handle with care, and the days worth circling.")
INTRO_UNTIMED = ("You didn't have a birth time, so your houses are read from your Sun, the same solar houses I use in your Wealth Story. "
                 "Anything that needs the exact minute you were born, like your Part of Fortune and your Midheaven, stays out of this forecast.")

MONTH_LORD_INTRO = ("Inside each birthday year, your chart moves its spotlight one sign further every month. This month the spotlight "
                    "falls on your {ord} house of {hof}, and {lord} is the planet guiding the month.")
LORD_FEEL = {
    "sun": "A Sun month asks you to be visible. Money tends to follow the moments when you put your name on something and stand behind it.",
    "moon": "A Moon month moves with your feelings and your needs. Money decisions made from a calm, fed, rested place go further than ones made in a rush.",
    "mercury": "A Mercury month runs on conversations, paperwork, and ideas. The right message sent at the right time can do more than an extra week of work.",
    "venus": "A Venus month is about value and relationships. It's a good month to look at your prices, your offers, and who you enjoy working with.",
    "mars": "A Mars month brings energy and urgency. It's a strong month for finishing, launching, and asking directly, as long as you choose your battles.",
    "jupiter": "A Jupiter month widens the view. Teaching, learning, and saying yes to the right opportunity can open more than you expect.",
    "saturn": "A Saturn month rewards structure. Budgets, contracts, and steady effort count for more this month than big gestures.",
}
LORD_NATAL = "In your chart, {lord} sits in {sign} in your {ord} house, so this month's money story runs through {topic}."
LORD_ROLE = {"second": "That's also the planet that rules your income, which makes this a month where earning is front and center.",
             "career": "That's also the ruler of your career, so work and reputation are a big part of this month's story.",
             "both": "That planet rules both your income and your career, so this month touches nearly every part of your money story."}

GLANCE_INTRO = "These are the days I'd circle on your calendar this month."
OPEN_INTRO = "These are the openings in your sky this month, the places where help, goodwill, and good timing line up more easily."
WATCH_INTRO = "And these are the places to move with a little more care this month."
NO_WATCH = ("Nothing in your sky this month is pressing hard on your money points. That doesn't mean nothing happens. It means "
            "this is a month where your own choices carry more weight than outside pressure.")
NO_OPEN = ("Your money points are quiet this month, without a big outside opening. Quiet months are good for tending what you already "
           "have, following up, and getting ready for the next opening.")

# ---- slow currents (Jupiter to Pluto) for a single month
CURRENT = {
    ("jupiter", "conj"): "This month Jupiter is sitting with your {t}. That's one of the warmest money signals a month can carry. It favors saying yes to growth that fits the life you want.",
    ("jupiter", "soft"): "This month Jupiter is supporting your {t}. Help, referrals, and good timing come more easily, and they're easy to miss if you don't ask.",
    ("jupiter", "hard"): "This month Jupiter is stretching your {t}. There's more on offer than usual, and more temptation to promise more than you can hold.",
    ("saturn", "conj"): "This month Saturn is settling onto your {t}. It asks for commitment and a real structure, and what you build carefully now tends to last.",
    ("saturn", "soft"): "This month Saturn is steadying your {t}. It's a good month for plans, budgets, and agreements you intend to keep.",
    ("saturn", "hard"): "This month Saturn is testing your {t}. Notice where you're carrying too much or where a price, a deadline, or a boundary needs adjusting.",
    ("uranus", "conj"): "This month Uranus is sitting on your {t}, so expect the unexpected. A surprise door can open quickly, so leave a little room in your plans.",
    ("uranus", "hard"): "This month Uranus is pulling against your {t}. Plans can change at short notice, and a sudden shift may show you what has run its course.",
    ("neptune", "conj"): "This month Neptune is softening your {t}. Inspiration is strong and details are easy to miss, so let time confirm what's real.",
    ("neptune", "hard"): "This month Neptune is blurring your {t}. Some offers will be exactly what they seem and some won't, so get the details in writing.",
    ("pluto", "conj"): "This month Pluto is working on your {t}. It's a month for honest change at the root, letting go of what no longer fits.",
    ("pluto", "hard"): "This month Pluto is putting pressure on your {t}. Notice who holds the power in your money decisions, and take back what belongs to you.",
}
EXACT_ON = " It's exact on {date}."

# ---- dated days from the faster planets
VENUS_DAY = {0: "Venus crosses your {t}", 60: "Venus sextiles your {t}", 120: "Venus trines your {t}", 180: "Venus opposes your {t}"}
VENUS_MEAN = {"soft": "Venus days favor asking, pricing, pitching, and anything that depends on goodwill.",
              "conj": "When Venus sits on a money point, people tend to say yes more easily. It's a lovely day to name your price.",
              "opp": "Venus opposite a money point puts relationships in the spotlight. A partner or client may bring the offer, or the question."}
MARS_DAY = {0: "Mars crosses your {t}", 90: "Mars squares your {t}", 180: "Mars opposes your {t}"}
MARS_MEAN = {"conj": "Mars brings a burst of energy. Use it to finish, launch, or ask directly.",
             "hard": "Mars in tension can bring friction, rushed decisions, or a sudden expense. Pause before you react, and don't sign anything in a temper."}
SUN_DAY = "The Sun crosses your {t}"
SUN_MEAN = "Days when the Sun lights up a money point are good for being seen. Share your work, ask for the meeting, or put your offer out."
MERCURY_DAY = "Mercury crosses your {t}"
MERCURY_MEAN = "Mercury days are good for the conversation, the email, or the paperwork that moves money forward."

# ---- Mercury retrograde and stations
MERC_RX = ("Mercury is retrograde for part of this month in your {ord} house of {topic}. It's a better time to review, renegotiate, "
           "and finish than to sign something brand new. Read the fine print twice, back up your files, and follow up on anything that went quiet.")
MERC_STATION = {"retrograde": "Mercury turns retrograde on {date} in {sign}, in your {ord} house.",
                "direct": "Mercury turns direct on {date} in {sign}, in your {ord} house, and things that stalled can start moving again."}

# ---- lunations
LUNATION_INTRO = ("Every month has a New Moon, a natural time to begin, and a Full Moon, a natural time to finish, harvest, or release. "
                  "Where they land in your chart shows which part of your money life is starting fresh and which is ready to be completed.")
NEW_HOUSE = {
    1: "A New Moon in your first house is a fresh start for you personally. Put yourself forward, update how you introduce your work, and begin the thing that only you can do.",
    2: "A New Moon in your second house is one of the best money New Moons of the year. Set an income intention, review your prices, and start the savings habit you keep meaning to start.",
    3: "A New Moon in your third house starts a new cycle of communication. Start the newsletter, the post series, or the conversations that let people know what you offer.",
    4: "A New Moon in your fourth house starts something at home. It's a good time to set up the space, the budget, or the family plan that supports your work.",
    5: "A New Moon in your fifth house opens creative income. Start the project you'd make for the joy of it, and notice who responds.",
    6: "A New Moon in your sixth house starts a new routine. Set up the system, the schedule, or the habit that makes your daily work easier and more profitable.",
    7: "A New Moon in your seventh house opens a partnership cycle. Reach out to the client, collaborator, or partner you'd love to work with.",
    8: "A New Moon in your eighth house starts fresh with shared money. Look at debt, investments, taxes, or a shared account, and set one clear intention.",
    9: "A New Moon in your ninth house widens your world. Sign up to learn, start teaching, or plan the trip or course that expands what you can offer.",
    10: "A New Moon in your tenth house starts a career chapter. Set a professional goal you'd be proud to be known for, and take the first visible step.",
    11: "A New Moon in your eleventh house starts something through your network. Join the group, reach out to your community, and say out loud what you're building.",
    12: "A New Moon in your twelfth house starts quietly. Rest, plan, and let an idea grow privately before you share it.",
}
FULL_HOUSE = {
    1: "A Full Moon in your first house brings something personal to completion. You may see clearly how others experience you and what you want to change.",
    2: "A Full Moon in your second house brings income questions to a head. Look at what came in, what went out, and what you're ready to stop undercharging for.",
    3: "A Full Moon in your third house completes a conversation or a piece of writing. Send the follow-up and close the loop.",
    4: "A Full Moon in your fourth house brings home and family matters to a peak. Something about your private foundation asks for attention or release.",
    5: "A Full Moon in your fifth house brings a creative project to fruition. Share what you've made and let yourself enjoy the response.",
    6: "A Full Moon in your sixth house shows where your routines are draining you. Release one task that costs more than it pays.",
    7: "A Full Moon in your seventh house brings a partnership or client relationship to a turning point. Clear terms help everyone.",
    8: "A Full Moon in your eighth house brings shared money to the surface. It's a good time to settle a debt, finish paperwork, or have the honest conversation.",
    9: "A Full Moon in your ninth house completes a learning or teaching cycle. Share what you've learned, because it's worth more than you think.",
    10: "A Full Moon in your tenth house brings recognition or a career milestone into view. Let yourself be seen for what you've built.",
    11: "A Full Moon in your eleventh house brings a goal or a group to completion. Notice who has supported you, and thank them.",
    12: "A Full Moon in your twelfth house asks you to rest and release. Let go of a worry about money that you've been carrying alone.",
}
LUNATION_LINE = {"new": "The New Moon on {date} falls at {deg} degrees {sign} in your {ord} house.",
                 "full": "The Full Moon on {date} falls at {deg} degrees {sign} in your {ord} house."}
LUNATION_HIT = {0: "It lands right on your {t}, which makes it personal.", 90: "It squares your {t}, which adds pressure and momentum.",
                180: "It opposes your {t}, which brings that part of your money story into focus."}
ECLIPSE_NOTE = ("This one is an eclipse, which makes it stronger than an ordinary lunation. Eclipses tend to start stories that unfold "
                "over the next six months or more, so pay attention to what begins or ends around this date.")

# ---- progressed Moon
PMOON_INTRO = ("Your progressed Moon is your inner timing. It moves about one degree a month and spends around two and a half years "
               "in each sign, so it shows the emotional season you're in with money and work.")
PMOON_SIGN = {
    "Aries": "With your progressed Moon in Aries, you're in a season of starting over and acting on your own instincts. Waiting for permission costs you more than usual right now.",
    "Taurus": "With your progressed Moon in Taurus, you're in a season of building security. Steady income, comfort, and things that last matter more to you than excitement.",
    "Gemini": "With your progressed Moon in Gemini, you're in a curious, busy season. More conversations, more ideas, and more small opportunities, so choose which ones to follow.",
    "Cancer": "With your progressed Moon in Cancer, you're in a season of tending your foundation. Home, family, and feeling safe come first, and work that feels like care pays well.",
    "Leo": "With your progressed Moon in Leo, you're in a season of being seen. Creative work and leadership want more of your heart, and you want credit for what you do.",
    "Virgo": "With your progressed Moon in Virgo, you're in a season of refining. Systems, skills, and health shape your earning, and small improvements add up.",
    "Libra": "With your progressed Moon in Libra, you're in a season of partnership and balance. Fair agreements and the right collaborators matter a great deal right now.",
    "Scorpio": "With your progressed Moon in Scorpio, you're in a deep season. Shared money, trust, and what lies underneath your choices are asking to be looked at honestly.",
    "Sagittarius": "With your progressed Moon in Sagittarius, you're in a season of expansion. Learning, teaching, and travel can open new ways to earn.",
    "Capricorn": "With your progressed Moon in Capricorn, you're in a season of serious building. Long-term goals and the structures that support them come into focus.",
    "Aquarius": "With your progressed Moon in Aquarius, you're in a season of doing things your own way. Communities, new ideas, and freedom in how you work matter more than tradition.",
    "Pisces": "With your progressed Moon in Pisces, you're in a season of intuition and endings. Creative and healing work flow well, and some old ways of earning may be quietly finishing.",
}
PMOON_HOUSE = "It's moving through your {ord} house, so this season's feelings about money center on {topic}."
PMOON_SIGN_CHANGE = "Before the month ends, it moves into {sign}, so you may feel a shift in what matters to you."
PMOON_HOUSE_CHANGE = "This month it crosses into your {ord} house, which turns your attention toward {topic}."
PMOON_ASPECT = {0: "Your progressed Moon meets your natal {t} around {date}.", 60: "Your progressed Moon sextiles your natal {t} around {date}.",
                90: "Your progressed Moon squares your natal {t} around {date}.", 120: "Your progressed Moon trines your natal {t} around {date}.",
                180: "Your progressed Moon opposes your natal {t} around {date}."}
PMOON_ASPECT_MEAN = {"soft": "That's a supportive inner moment, a good time to trust your instincts about money.",
                     "conj": "That's a meaningful inner moment, often felt as a new beginning in that part of your life.",
                     "hard": "That can stir things up emotionally, which is often what moves you to make a needed change."}

# ---- the bigger current (solar arcs and slow progressions)
BIG_INTRO = ("Underneath the month there's a slower current, the kind that builds over a year or more. Astrologers measure it with "
             "solar arc directions and progressions, which move your whole chart forward a little each year.")
SA_LINE = {0: "Your directed {p} is meeting your natal {t}.", 90: "Your directed {p} is squaring your natal {t}.",
           180: "Your directed {p} is opposing your natal {t}."}
SA_MEAN = {"sun": "It points to a year where your identity and confidence are changing how you earn.",
           "moon": "It points to a year where your emotional needs are reshaping your money choices.",
           "mercury": "It points to a year of new skills, contracts, and conversations that matter for your work.",
           "venus": "It points to a year where what you value, and how you're valued, is shifting.",
           "mars": "It points to a year of drive, competition, and bold moves in your work.",
           "jupiter": "It points to a year of growth and wider opportunity.",
           "saturn": "It points to a year of responsibility, structure, and building something to last.",
           "uranus": "It points to a year of change and freedom, where an old structure may give way to something more yours.",
           "neptune": "It points to a year of inspiration and uncertainty, where your vision matters and your details need checking.",
           "pluto": "It points to a year of deep change and personal power around money.",
           "mc": "It points to a year where your career direction and public role are shifting.",
           "asc": "It points to a year where how you show up and present your work is changing."}
SLOWPROG_LINE = "Your progressed {p} is exactly {a} your natal {t} right now, a quiet signal that lasts for months."
ASPECT_WORD = {0: "meeting", 60: "sextile", 90: "square", 120: "trine", 180: "opposite"}

# ---- money midpoints
MIDPOINT_INTRO = "There's one more layer I check, the sensitive points that sit exactly halfway between two of your money planets."
MIDPOINT_MEAN = {("venus", "jupiter"): "Your Venus and Jupiter midpoint is a classic point of good fortune and ease with money.",
                 ("jupiter", "pluto"): "Your Jupiter and Pluto midpoint is tied to big growth, influence, and larger sums.",
                 ("sun", "jupiter"): "Your Sun and Jupiter midpoint is tied to confidence, success, and being recognized.",
                 ("jupiter", "mc"): "Your Jupiter and Midheaven midpoint is tied to career growth and good fortune in your work."}
MIDPOINT_HIT = "{P} activates it on {date}."

FINAL_INTRO = "So here's how I'd hold this month."
NEXT_TEASER = "Next month's New Moon falls on {date} in {sign}, in your {ord} house of {hof}, so that's where your next fresh start is heading."
SIGNOFF = "With Love & Light,\nTiff"
DISCLAIMER = ("This reading is based on my own research, my orb-based methodology, and my intuitive abilities. It uses the tropical zodiac, "
              "Placidus houses (or solar houses when no birth time is given), and the True Node, calculated with the Swiss Ephemeris. "
              "It is offered for reflection and personal growth and is not financial, legal, medical, or mental health advice. "
              "Because this is an instant digital download, all sales are final.")

# ---- Try This and journal prompts
TRY_OPEN = {
    "venus": "Pick one Venus day this month and use it to ask. Raise a price, send the proposal, or ask for the referral you've been sitting on.",
    "jupiter": "Write down the one opportunity you'd say yes to this month if it showed up. Then tell one person about it, so it has somewhere to land.",
    "sun": "On your Sun day, put your work in front of people. Share it, post it, or ask for the meeting.",
    "mercury": "Use your Mercury day for the email or call that moves money forward. Draft it the day before so it's ready.",
    "mars": "Choose one money task you've been avoiding and give it your Mars energy this month. Finish it in a single sitting.",
    "saturn": "Set up one structure this month that your future self will thank you for, like an automatic savings transfer or a simple contract template.",
    "quiet": "Use this quieter month to tidy your money. Update your prices, follow up on unpaid invoices, and clear one financial task off your list.",
}
TRY_WATCH = {
    "saturn": "Before you agree to anything new this month, ask what it will cost you in time and energy. If the answer is too much, renegotiate or wait.",
    "uranus": "Keep a small cushion of time and money this month so a surprise doesn't knock you off balance.",
    "neptune": "Put every money agreement in writing this month. If something feels too good to be true, sleep on it.",
    "pluto": "Notice one place where someone else is making a money decision that should be yours, and take it back gently.",
    "jupiter": "Set one limit this month, on spending, on commitments, or on new projects, and treat it as a promise to yourself.",
    "mars": "When something urgent comes up this month, wait a day before you spend or sign. Most fires look smaller in the morning.",
    "mercury": "Review before you sign this month. Reread contracts, check invoices, and back up your important files.",
    "none": "Pick one money habit you'd like to strengthen this month and practice it every week.",
}
PROMPT_NEW = "The New Moon in your {ord} house is a fresh start for {topic}. What do you want to begin there this month?"
PROMPT_FULL = "The Full Moon in your {ord} house brings {topic} to a peak. What's ready to be finished, harvested, or released?"
PROMPT_PMOON = "Your progressed Moon is in {sign} in your {ord} house. What do you need to feel safe and supported with money in this season?"
PROMPT_OPEN = "Which opening this month feels most like yours, and what's one small step you can take toward it this week?"
PROMPT_WATCH = "Where do you feel the most pressure around money right now, and what would make it feel lighter?"
PROMPT_LORD = "With {lord} guiding this month, what would it look like to let {topic} lead your money choices?"

OFFERS_INTRO = "If you'd like to go deeper, these pair well with your monthly forecast."

# ---- where the money planets move this month (house of the transiting planet at mid-month)
MOVING_INTRO = ("Three planets carry most of the money and work energy in any month. The Sun shows where your attention goes, "
                "Venus shows where value and goodwill flow, and Mars shows where your effort counts most.")
SUN_HOUSE = {
    1: "The Sun is moving through your first house, your personal new year in a way. Put your own goals first.",
    2: "The Sun is moving through your second house, which puts income, spending, and self-worth in the spotlight.",
    3: "The Sun is moving through your third house, so messages, writing, and local connections get more attention.",
    4: "The Sun is moving through your fourth house, which turns your attention to home, family, and what supports you.",
    5: "The Sun is moving through your fifth house, so creative work and joy deserve more of your time.",
    6: "The Sun is moving through your sixth house, which spotlights your daily work, your systems, and your health.",
    7: "The Sun is moving through your seventh house, so partners and clients are where your attention goes.",
    8: "The Sun is moving through your eighth house, which spotlights shared money, debt, and the agreements you hold with others.",
    9: "The Sun is moving through your ninth house, so learning, teaching, and bigger-picture plans light up.",
    10: "The Sun is moving through your tenth house, the most visible part of your chart. It's a strong time to be seen at work.",
    11: "The Sun is moving through your eleventh house, so friends, community, and the income your work brings get the focus.",
    12: "The Sun is moving through your twelfth house, a quieter stretch for rest, planning, and finishing what's open.",
}
VENUS_HOUSE = {
    1: "Venus is in your first house, so your own presence is magnetic right now. People respond to you more easily.",
    2: "Venus is in your second house, one of the best placements for income. It's a good time to price well and receive.",
    3: "Venus is in your third house, so kind words, good emails, and local goodwill can bring money your way.",
    4: "Venus is in your fourth house, which favors spending on home and finding comfort in what you already have.",
    5: "Venus is in your fifth house, so creative and joyful work attracts both people and money.",
    6: "Venus is in your sixth house, which smooths your workday and favors good relationships with coworkers and clients.",
    7: "Venus is in your seventh house, so partnerships and client relationships are where value flows this month.",
    8: "Venus is in your eighth house, which favors shared money, gifts, support, and fair agreements with others.",
    9: "Venus is in your ninth house, so teaching, publishing, travel, and learning can bring something good.",
    10: "Venus is in your tenth house, which adds charm to your public image. Recognition and career goodwill come more easily.",
    11: "Venus is in your eleventh house, so friends and networks bring opportunities, introductions, and gains.",
    12: "Venus is in your twelfth house, a quiet placement that rewards generosity, rest, and work done behind the scenes.",
}
MARS_HOUSE = {
    1: "Mars is in your first house, giving you energy to start things and push your own work forward.",
    2: "Mars is in your second house, which brings drive to earning, and also a quicker hand when it comes to spending.",
    3: "Mars is in your third house, so speak up, send the pitch, and keep your messages direct but kind.",
    4: "Mars is in your fourth house, which can bring busy energy at home, so protect your workspace and your rest.",
    5: "Mars is in your fifth house, so put your energy into a creative project or a risk that's worth taking.",
    6: "Mars is in your sixth house, which brings a lot of work energy. Get through the backlog, and pace yourself.",
    7: "Mars is in your seventh house, so negotiations and partnerships can heat up. Be clear about what you want.",
    8: "Mars is in your eighth house, which brings energy to debts, taxes, and shared money. Tackle the one you've been avoiding.",
    9: "Mars is in your ninth house, so put your energy into learning, teaching, publishing, or a bold plan.",
    10: "Mars is in your tenth house, a strong placement for ambition. Go after the career goal directly.",
    11: "Mars is in your eleventh house, so reach out to your network and put energy into the group or goal that matters.",
    12: "Mars is in your twelfth house, so your energy works best behind the scenes. Plan, prepare, and rest before you push.",
}
PROMPT_MOVING = "With Venus in your {vord} house and Mars in your {mord} house this month, where do you want your money energy to go?"
