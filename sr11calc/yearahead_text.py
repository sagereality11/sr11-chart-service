"""Interpretation library for "Your 2027" in Tiff's voice.

House rules for every string in this file: contractions, second person, no em dashes,
no single ellipsis character (use a run of periods), no bold inside prose, gift paired
with its shadow (octaves), symbolic invitations rather than promises or doom.
Placeholders in {braces} are filled by yearahead.py.
"""

HOUSE_TOPIC = {
    1: "self, body and the way you show up",
    2: "money, values and self-worth",
    3: "voice, learning, siblings and your everyday world",
    4: "home, family, roots and your inner foundation",
    5: "creativity, romance, joy and children",
    6: "health, routines and daily work",
    7: "partnership, marriage and one-to-one bonds",
    8: "shared resources, intimacy, debt and deep transformation",
    9: "travel, higher learning, faith and your big-picture truth",
    10: "career, reputation and your public calling",
    11: "friends, community, networks and future dreams",
    12: "rest, healing, the subconscious and what's ending behind the scenes",
}

HOUSE_SHORT = {
    1: "self and body", 2: "money and worth", 3: "voice and learning", 4: "home and roots",
    5: "creativity and joy", 6: "health and routines", 7: "partnership", 8: "intimacy and shared resources",
    9: "travel, study and faith", 10: "career and calling", 11: "friends and future dreams",
    12: "rest and release",
}

ORD = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th",
       9: "9th", 10: "10th", 11: "11th", 12: "12th"}

# --------------------------------------------------------------------------------------
# Opening
# --------------------------------------------------------------------------------------
OPENING = (
    "What if 2027 isn't something that's going to happen to you, but something you get to walk into "
    "with your eyes open?\n\n"
    "That's what this reading is for. Not a prediction. Not a list of good days and bad days. But a map "
    "of the story the sky is telling through your own birth chart, so you can recognize the chapters as "
    "they arrive and meet them as the most conscious version of yourself.\n\n"
    "Here's how it works. The first half of your reading is the story: what this year is about for you, "
    "the eclipse chapter you're living inside, and the big planetary teachers knocking on your door. The "
    "second half is your calendar: the months that matter most and why, followed by every month of 2027 "
    "with the dates that touch your chart personally."
)

# --------------------------------------------------------------------------------------
# Profection year (annual profections, whole sign from the Ascendant)
# --------------------------------------------------------------------------------------
YEAR_TITLE = {
    1: "Becoming", 2: "Building Your Worth", 3: "Finding Your Voice", 4: "Coming Home to Yourself",
    5: "Creative Joy", 6: "Sacred Routines", 7: "Partnership", 8: "Deep Transformation",
    9: "Expansion", 10: "Stepping Into Your Calling", 11: "Your Soul Tribe", 12: "Sacred Rest and Release",
}

PROFECTION = {
    1: ("This is a 1st house year, and those only come around every twelve years. It's a fresh cycle. "
        "Everything in your chart is pointing back to you: your body, your presence, the way you want to "
        "be seen. Think of it as a personal new year that lasts twelve months. The gift is momentum and "
        "self-trust. The shadow is making every decision about proving yourself. Let it be about becoming "
        "yourself instead."),
    2: ("This is a 2nd house year, the year your worth gets real. Money, possessions, talents and the "
        "quiet question of what you believe you deserve all come into focus. You're building something "
        "you can stand on. The lower octave is scarcity thinking, holding on too tightly or measuring "
        "your value by your bank balance. The higher octave is knowing your gifts are an asset and "
        "pricing, saving and receiving like you believe it."),
    3: ("This is a 3rd house year, the year of your voice. Writing, speaking, teaching, learning, "
        "short trips, siblings and neighbors all get busier. Ideas move fast. The lower octave is "
        "scattered energy and saying yes to every conversation. The higher octave is choosing the "
        "message that's truly yours and saying it out loud, again and again, until it lands."),
    4: ("This is a 4th house year, the year you come home to yourself. Home, family, roots, a move, a "
        "renovation or an inner reckoning with where you come from can all take center stage. It's a "
        "foundation year. The lower octave is retreating into old family roles. The higher octave is "
        "building a home, inside and out, that actually holds the person you've become."),
    5: ("This is a 5th house year, the year of creative joy. Romance, play, art, children and anything "
        "you create from the heart want more of your time. Pleasure isn't a distraction this year, it's "
        "medicine. The lower octave is drama or needing applause to feel worthy. The higher octave is "
        "creating simply because it lights you up."),
    6: ("This is a 6th house year, the year of sacred routines. Your health, your daily work and the "
        "small rituals that make up an ordinary Tuesday are where the magic lives. The lower octave is "
        "burnout, perfectionism and over-serving. The higher octave is devotion: tending your body and "
        "your work in a way that's sustainable for the long haul."),
    7: ("This is a 7th house year, the year of partnership. Marriage, business partners, clients, "
        "contracts and anyone who mirrors you back to yourself become the classroom. Relationships "
        "begin, deepen, renegotiate or complete. The lower octave is losing yourself in someone else. "
        "The higher octave is meeting another person as a whole person."),
    8: ("This is an 8th house year, the year of deep transformation. Shared money, debt, inheritance, "
        "intimacy, trust and the parts of yourself you usually keep hidden ask to be looked at. It's "
        "potent. The lower octave is control, fear of vulnerability or financial entanglement. The "
        "higher octave is the phoenix: letting something end so a truer version of you can rise."),
    9: ("This is a 9th house year, the year of expansion. Travel, study, publishing, teaching, faith "
        "and your big-picture truth all open up. You're meant to stretch past the edges of your map. "
        "The lower octave is preaching, restlessness or chasing the next horizon to avoid the present. "
        "The higher octave is living your philosophy instead of just talking about it."),
    10: ("This is a 10th house year, the year you step into your calling. Career, reputation, "
         "leadership and how the world sees your work move to the front of the stage. What you build "
         "now is visible. The lower octave is chasing status or approval. The higher octave is "
         "becoming the authority on your own life and letting your work carry your name with pride."),
    11: ("This is an 11th house year, the year of your soul tribe. Friends, community, audiences, "
         "networks and your hopes for the future come alive. The right people find you. The lower "
         "octave is people-pleasing or getting lost in the group. The higher octave is gathering "
         "people around a shared vision and letting yourself be supported."),
    12: ("This is a 12th house year, the year of sacred rest and release. It's the last chapter before "
         "a brand new twelve-year cycle begins, so endings, healing, solitude and spiritual work matter "
         "more than outer achievement. The lower octave is hiding, escaping or self-undoing. The higher "
         "octave is surrender: clearing what's complete so you walk into your next cycle light."),
}

YEAR_LORD = (
    "Your year is ruled by {lord}, the planet that rules your {sign} {house_ord} house. That makes "
    "{lord} the lord of your year: wherever it travels and whatever it touches in 2027, you'll feel "
    "it louder than usual. In your birth chart, {lord} lives in {lord_sign} in your {lord_house_ord} "
    "house of {lord_topic}, so that part of your life is where this year's story gets its fuel."
)

PROFECTION_SWITCH = (
    "Your profection year turns over on your birthday. Until {bday}, you're finishing a {prev_ord} "
    "house year ({prev_short}). From {bday} on, the {cur_ord} house story takes over."
)

# --------------------------------------------------------------------------------------
# Eclipses
# --------------------------------------------------------------------------------------
ECLIPSE_TEACH = (
    "Before we talk about your eclipses, I want you to understand how they actually work, because "
    "this is where most people get confused.\n\n"
    "An eclipse isn't a one-day event. Eclipses come in seasons, and each season lands on one axis of "
    "the zodiac (two opposite signs) for roughly 12 to 18 months before the story shifts to the next "
    "axis. So the eclipses you feel in 2027 are chapters in a story that began before this year and "
    "will finish after it. The solar eclipses open doors. The lunar eclipses bring things to light, "
    "to a head or to completion.\n\n"
    "Think of the axis as a seesaw in your chart. One end is what you're being asked to grow toward. "
    "The other end is what you're being asked to release or rebalance. The houses those two signs "
    "fall in for you are the areas of your life where the story plays out.\n\n"
    "One more piece. Every eclipse also belongs to a family called a Saros series, and each family "
    "returns about every 18 years. A Saros return isn't the same eclipse at the same degree. It's the "
    "same family coming back around, so the themes tend to rhyme rather than repeat. Under each eclipse "
    "below, you'll see when its family last visited you and how old you were. Look back at what was "
    "beginning or ending in your life then. It's often a clue to what's ready to evolve now."
)

ECLIPSE_SEASON_2027 = (
    "In 2027 the main eclipse story is on the Leo and Aquarius axis. It opened with the Aquarius solar "
    "eclipse in February 2026 and the Leo solar eclipse in August 2026, it reaches its peak in 2027, "
    "and it closes with the final Aquarius solar eclipse in January 2028. At the same time, the older "
    "Virgo and Pisces story takes its final bow in February 2027, and a brand new Cancer and Capricorn "
    "story opens its first page in July 2027."
)

AXIS_SIDES = (
    "For you, Leo falls in your {leo_ord} house of {leo_topic}, and Aquarius falls in your {aq_ord} "
    "house of {aq_topic}. That's your seesaw.\n\n"
    "The North Node is moving through Aquarius, which means the growth edge points toward your "
    "{aq_ord} house. The South Node sits in Leo, so your {leo_ord} house is where you have deep, "
    "familiar skill and where you may be over-relying on an old way of shining. You don't abandon it. "
    "You rebalance it."
)

# Keyed by the house that holds Leo for this person (the axis is Leo-house / Aquarius-house).
AXIS_STORY = {
    1: ("This is the axis of me and we. Leo in your 1st house asks you to take up space with your whole "
        "heart, your look, your presence, your name. Aquarius in your 7th house asks how your "
        "partnerships can become more equal, more honest and more free. Some relationships evolve and "
        "some finish because you're no longer willing to dim yourself to keep them."),
    2: ("This is the axis of your money and our money. Leo in your 2nd house lights up your income, your "
        "talents and your sense of worth. Aquarius in your 8th house shakes up shared finances, debt, "
        "investments, intimacy and trust. The story points to a new financial independence that doesn't "
        "come from going it alone, but from sharing power on fairer terms."),
    3: ("This is the axis of the message and the meaning. Leo in your 3rd house puts your voice, your "
        "writing, your neighborhood and your siblings in the spotlight. Aquarius in your 9th house "
        "opens new beliefs, new teachers, travel and study. You're being asked to say what you know in "
        "your own words and then let it reach farther than your everyday circle."),
    4: ("This is the axis of roots and reach. Leo in your 4th house brings home, family and your inner "
        "foundation into the eclipse light. Aquarius in your 10th house reinvents your career and public "
        "role. Changes at home and changes in your work are part of the same story: the life you're "
        "building on the outside has to match the truth you live on the inside."),
    5: ("This is the axis of the heart and the collective. Leo in your 5th house brings romance, "
        "creativity, play and children into focus. Aquarius in your 11th house reshapes your "
        "friendships, communities, audience and hopes for the future. Creative projects can find "
        "their people, and some groups fall away so the right ones can arrive."),
    6: ("This is the axis of the body and the soul. Leo in your 6th house shines on your health, your "
        "routines and your daily work. Aquarius in your 12th house stirs the subconscious, your dreams, "
        "rest and spiritual healing. What you've been carrying behind the scenes wants to move through "
        "your body and out, and the daily rituals you choose become the bridge."),
    7: ("This is the axis of we and me. Leo in your 7th house puts partners, clients and significant "
        "others center stage. Aquarius in your 1st house reinvents you. Expect people to mirror your "
        "growth back to you, and expect a version of yourself to emerge that's freer, more original "
        "and less willing to perform for anyone."),
    8: ("This is the axis of shared power and self-worth. Leo in your 8th house brings intimacy, "
        "shared money, inheritance and deep trust into the light. Aquarius in your 2nd house "
        "revolutionizes how you earn and what you value. You're learning to own your worth so fully "
        "that what you share with others comes from overflow, not from need."),
    9: ("This is the axis of the big truth and the daily conversation. Leo in your 9th house lights up "
        "travel, study, publishing, faith and teaching. Aquarius in your 3rd house rewires how you "
        "think, speak and connect day to day. A bigger belief is forming, and you're being asked to "
        "share it in a new language."),
    10: ("This is the axis of calling and home. Leo in your 10th house puts your career and reputation "
         "in the spotlight, sometimes with a public moment you didn't plan. Aquarius in your 4th house "
         "reinvents home and family. A visible step forward in your work and a shift in your private "
         "world are two sides of the same coin."),
    11: ("This is the axis of the dream and the creation. Leo in your 11th house shines on friends, "
         "community, networks and your future vision. Aquarius in your 5th house brings unexpected "
         "romance, original creativity and new ways to play. The people around you and the joy inside "
         "you are both being upgraded."),
    12: ("This is the axis of the unseen and the everyday. Leo in your 12th house works behind the "
         "curtain: healing, dreams, solitude and endings that make room. Aquarius in your 6th house "
         "reinvents your routines, health and work habits. What you release in private shows up as a "
         "freer, healthier daily life."),
}

ECLIPSE_CLOSING_VIRGO_PISCES = (
    "The Virgo and Pisces eclipse story that's been working on your {v_ord} house ({v_short}) and your "
    "{p_ord} house ({p_short}) since 2024 finishes with the lunar eclipse on February 20, 2027. Think "
    "of it as the last page of that chapter. Whatever has been coming to completion in those areas "
    "can finally be set down."
)

ECLIPSE_OPENING_CANCER_CAP = (
    "Then, on July 18, 2027, the lunar eclipse in Capricorn opens a new story on the Cancer and "
    "Capricorn axis: your {c_ord} house ({c_short}) and your {cp_ord} house ({cp_short}). You'll only "
    "feel its first whisper this year. It builds through 2028 and into 2029, so notice what starts "
    "stirring there and don't rush it."
)

ECLIPSE_KIND = {
    ("solar", "annular"): "annular solar eclipse (a ring of fire)",
    ("solar", "total"): "total solar eclipse",
    ("solar", "partial"): "partial solar eclipse",
    ("solar", "hybrid"): "hybrid solar eclipse",
    ("lunar", "total"): "total lunar eclipse",
    ("lunar", "partial"): "partial lunar eclipse",
    ("lunar", "penumbral"): "penumbral lunar eclipse",
}

ECLIPSE_HOUSE = {
    "solar": ("A new door opens in your {ord} house of {topic}. Solar eclipses are seeds planted in the "
              "dark: you may not see the whole picture right away, but something begins here."),
    "lunar": ("Something comes to light, to a head or to completion in your {ord} house of {topic}. Lunar "
              "eclipses reveal. Let what's finished be finished."),
}

ECLIPSE_CONTACT = (
    "This one is personal. It lands within {orb} of your {points}, which puts it at the epicenter of "
    "your chart. It speaks directly to {meanings}. Mark this date. It's one of the most important "
    "moments of your year."
)

ECLIPSE_NEAR = (
    "It also falls within {orb} of your natal {point}, so you'll feel it echo through {point_meaning_short}."
)

SAROS_ECHO = "Saros echo: the last eclipse in this family arrived on {prev_date}, when you were {age}."

# --------------------------------------------------------------------------------------
# Natal point meanings
# --------------------------------------------------------------------------------------
POINT = {
    "sun": ("Sun", "your identity, purpose and life force", "your sense of self"),
    "moon": ("Moon", "your emotional needs, home life and inner child", "your emotional world"),
    "mercury": ("Mercury", "your mind, voice and the way you communicate", "your thinking and conversations"),
    "venus": ("Venus", "love, money, values and what you find beautiful", "your relationships and finances"),
    "mars": ("Mars", "your drive, courage and desire", "your energy and ambition"),
    "jupiter": ("Jupiter", "your faith and natural luck", "your sense of possibility"),
    "saturn": ("Saturn", "your lessons, structures and long-game ambitions", "your commitments"),
    "asc": ("Ascendant", "your body, identity and the way the world meets you", "the way you show up"),
    "mc": ("Midheaven", "your career, calling and public reputation", "your career"),
    "ic": ("IC", "your home, family and private foundation", "your home life"),
    "dsc": ("Descendant", "your partnerships and the people who mirror you", "your relationships"),
    "uranus": ("Uranus", "your own path to freedom and authenticity", "your need for freedom"),
    "neptune": ("Neptune", "your dreams and spiritual longing", "your dreams"),
    "pluto": ("Pluto", "your relationship with power and rebirth", "your inner power"),
    "north_node": ("North Node", "your soul's growth direction", "your path forward"),
}

# --------------------------------------------------------------------------------------
# Transit planets to natal points
# --------------------------------------------------------------------------------------
TRANSIT_CORE = {
    "jupiter": "expansion, opportunity and faith",
    "saturn": "structure, commitment and the reality check that makes things last",
    "uranus": "awakening, freedom and sudden change",
    "neptune": "dreams, intuition, surrender and dissolving",
    "pluto": "power, deep transformation and rebirth",
}

ASPECT_WORD = {0: "conjunct", 60: "sextile", 90: "square", 120: "trine", 180: "opposite"}

TRANSIT_TEXT = {
    ("jupiter", "conj"): ("Jupiter, the planet of {core}, sits right on top of {pm}. Doors open here. "
                          "Say yes to growth, but choose what's actually aligned rather than everything "
                          "that's shiny."),
    ("jupiter", "hard"): ("Jupiter is {asp} {pm}, which stretches it. Growth here can feel like "
                          "overwhelm or too much at once, so the invitation is to expand with intention "
                          "instead of overextending."),
    ("jupiter", "soft"): ("Jupiter is {asp} {pm}, a supportive, open-hearted connection. This is a "
                          "lucky current: lean into it, ask for things, and let support find you."),
    ("saturn", "conj"): ("Saturn, the planet of {core}, sits right on top of {pm}. This is a "
                         "defining moment of maturity. What's real gets stronger. What isn't built on "
                         "solid ground gets shown to you so you can rebuild it."),
    ("saturn", "hard"): ("Saturn is {asp} {pm}. This is pressure with a purpose. Expect tests, delays "
                         "or responsibilities that ask you to commit, set boundaries and do the slow, "
                         "steady work. It's not punishment. It's how foundations are poured."),
    ("saturn", "soft"): ("Saturn is {asp} {pm}, a steady, supportive connection. Effort pays off "
                         "here. It's a great window to make something official, sign the thing, or "
                         "build a habit that lasts."),
    ("uranus", "conj"): ("Uranus, the planet of {core}, sits right on top of {pm}. Expect the "
                         "unexpected. Something that's felt too small or too safe gets shaken loose so "
                         "a more authentic version can emerge."),
    ("uranus", "hard"): ("Uranus is {asp} {pm}. Restlessness, surprises or sudden shifts can show up "
                         "here. The more you resist change, the more it tends to arrive from the "
                         "outside. Choose your own revolution."),
    ("uranus", "soft"): ("Uranus is {asp} {pm}, a refreshing, liberating connection. New ideas, new "
                         "people and new freedom arrive more easily. Experiment."),
    ("neptune", "conj"): ("Neptune, the planet of {core}, sits right on top of {pm}. The edges soften. "
                          "Your intuition gets louder, and so can confusion. Trust what you feel, and "
                          "double-check the facts."),
    ("neptune", "hard"): ("Neptune is {asp} {pm}. Something here may feel foggy, idealized or hard to "
                          "pin down. It's asking you to release an old illusion and follow a deeper "
                          "kind of faith, with clear boundaries."),
    ("neptune", "soft"): ("Neptune is {asp} {pm}, a gentle, inspired connection. Creativity, "
                          "compassion and spiritual connection flow here. Make art. Pray. Dream."),
    ("pluto", "conj"): ("Pluto, the planet of {core}, sits right on top of {pm}. This is a "
                        "once-in-a-lifetime rebirth in this area. Something ends at the root so "
                        "something truer can take its place."),
    ("pluto", "hard"): ("Pluto is {asp} {pm}. Power dynamics, control and deep fears can surface here "
                        "so they can finally be transformed. You're stronger than you think, and "
                        "you're allowed to take your power back."),
    ("pluto", "soft"): ("Pluto is {asp} {pm}, a deep, empowering connection. You have access to real "
                        "staying power. Slow, intentional change here goes a long way."),
}

TRANSIT_OCTAVE = {
    "jupiter": ("The lower octave is excess and overpromising. The higher octave is generosity, "
                "wisdom and growth you can actually sustain."),
    "saturn": ("The lower octave is fear, rigidity and self-criticism. The higher octave is earned "
               "confidence and a structure that finally supports you."),
    "uranus": ("The lower octave is rebellion for its own sake. The higher octave is liberation that "
               "aligns you with who you really are."),
    "neptune": ("The lower octave is escapism and fog. The higher octave is compassion, creativity "
                "and spiritual trust."),
    "pluto": ("The lower octave is control and power struggles. The higher octave is the phoenix, "
              "rising stronger and more honest than before."),
}

# --------------------------------------------------------------------------------------
# Slow planets through houses
# --------------------------------------------------------------------------------------
JUPITER_SIGN = {
    "Leo": ("Jupiter spends the first half of 2027 in Leo, where it expands courage, visibility, "
            "creativity and joy."),
    "Virgo": ("On July 26, 2027, Jupiter moves into Virgo, where it expands health, skill, service "
              "and the beauty of doing things well."),
}

JUPITER_HOUSE = {
    1: "In your 1st house, it grows your confidence, presence and personal opportunities. People notice you.",
    2: "In your 2nd house, it grows income, resources and your sense of worth. Ask for more.",
    3: "In your 3rd house, it grows your voice, your writing, learning and local connections.",
    4: "In your 4th house, it grows your home and family life. A move, a bigger space or deeper roots are favored.",
    5: "In your 5th house, it grows romance, creativity, pleasure and joy. Play is productive.",
    6: "In your 6th house, it grows your daily work, health routines and skills. Small habits become big wins.",
    7: "In your 7th house, it grows partnerships, collaborations and contracts. The right people want to work with you.",
    8: "In your 8th house, it grows shared resources, investments, intimacy and emotional depth.",
    9: "In your 9th house, it grows travel, study, publishing, teaching and faith. Your world gets bigger.",
    10: "In your 10th house, it grows your career, reputation and visibility. This is a classic rise.",
    11: "In your 11th house, it grows your friendships, community, audience and hopes for the future.",
    12: "In your 12th house, it grows your spiritual life, rest and healing. Grace works behind the scenes.",
}

SATURN_ARIES = (
    "Saturn spends all of 2027 in Aries, teaching courageous self-leadership: starting things on your "
    "own terms and following through."
)

SATURN_HOUSE = {
    1: ("In your 1st house, Saturn asks you to take yourself seriously. Your body, your boundaries and your "
        "identity are getting a sturdier frame. It can feel heavy. It's also how you become unshakable."),
    2: ("In your 2nd house, Saturn asks you to build real financial stability. Budgets, savings and "
        "pricing your gifts honestly. Slow money is lasting money."),
    3: ("In your 3rd house, Saturn asks you to master your message. Study, write, practice speaking. "
        "Your words carry more authority when you commit to them."),
    4: ("In your 4th house, Saturn asks you to rebuild your foundation. Home, family responsibilities "
        "and old family patterns are up for a grown-up renovation."),
    5: ("In your 5th house, Saturn asks you to commit to what you love. Creative discipline, serious "
        "romance or responsibilities with children. Joy becomes a practice, not an accident."),
    6: ("In your 6th house, Saturn asks you to build routines that can hold your life. Health, work "
        "habits and daily systems need structure, and they'll reward it."),
    7: ("In your 7th house, Saturn asks you to define your partnerships. Commitments get tested, "
        "formalized or completed. The question is simple: is this built to last?"),
    8: ("In your 8th house, Saturn asks you to handle shared money, debt and intimacy with maturity. "
        "Clean up what's entangled. Trust is built, not assumed."),
    9: ("In your 9th house, Saturn asks you to commit to your beliefs. A serious course of study, "
        "teaching, publishing or a long journey can become a real achievement."),
    10: ("In your 10th house, Saturn asks you to step into authority in your career. Hard work becomes "
         "visible. This is a career-defining stretch if you show up for it."),
    11: ("In your 11th house, Saturn asks you to curate your circle. Fewer, truer friendships and a "
         "long-term vision you're willing to work toward."),
    12: ("In your 12th house, Saturn asks you to close an old chapter with care. Rest, healing and "
         "solitude are the work. You're finishing something so the next cycle starts clean."),
}

OUTER_BACKGROUND = {
    "uranus": ("Uranus is in Gemini, moving through your {ord} house of {topic}. This is where you're "
               "being rewired: expect fresh ideas, surprising news and a desire for more freedom here."),
    "neptune": ("Neptune is in Aries, moving through your {ord} house of {topic}. This is where your "
                "dreams are being reborn: an area to approach with faith, imagination and clear boundaries."),
    "pluto": ("Pluto is in Aquarius, moving through your {ord} house of {topic}. This is your long, deep "
              "transformation: power is being reclaimed here over many years, not months."),
}

# --------------------------------------------------------------------------------------
# Calendar phrases
# --------------------------------------------------------------------------------------
MERCURY_RX = (
    "Mercury retrograde from {start} to {end} in your {ord} house of {topic}. Review, revise and "
    "reconnect in this area. Back up files, reread contracts, and expect old conversations to return "
    "for a better ending."
)
MARS_RX = (
    "Mars is retrograde until April 2 in Virgo and Leo, moving back through your {ord} house of {topic}. "
    "Energy turns inward here. Rework rather than relaunch, and pace yourself."
)
MARS_DIRECT = "Mars turns direct on April 2, and the energy you've been reworking in your {ord} house starts moving forward again."
JUPITER_INGRESS = "Jupiter enters Virgo on July 26 and begins expanding your {ord} house of {topic}."
SATURN_STATION = "Saturn stations {dir} on {date} at {pos}, a moment where Saturn's lesson in your {ord} house gets louder."
BIRTHDAY = (
    "Your solar return, on or around {date}. Your personal new year begins and your {ord} house profection year "
    "({short}) officially takes over. Set intentions this week."
)
CHIRON_TAURUS = "Chiron enters Taurus on April 15, beginning a years-long healing journey through your {ord} house of {topic}."

MONTH_QUIET = (
    "A steadier month for you. Use it to integrate, rest and tend to the {short} themes of your year "
    "rather than forcing anything new."
)

POWER_INTRO = (
    "Not every month carries the same weight. Based on your eclipses, the big planetary contacts to your "
    "birth chart and your personal timing, these are the months where the most is moving for you. "
    "Circle them. Plan around them. Don't fear them."
)

# --------------------------------------------------------------------------------------
# Closing
# --------------------------------------------------------------------------------------
FINAL = (
    "So here's what I want you to take with you into 2027.\n\n"
    "Your year has a theme ({title}), an eclipse story running through your {leo_ord} and {aq_ord} houses, "
    "and a handful of months where the sky leans in close. None of it is happening to you. It's "
    "happening with you, and through you.\n\n"
    "Every placement in this reading can be lived at a lower octave or a higher one. Two people with the "
    "same transits can have completely different years, and the difference is awareness. You have this "
    "map now. Come back to it at the start of each month, reread your dates, and choose the higher "
    "octave one moment at a time.\n\n"
    "2027 isn't asking you to be perfect. It's asking you to be present...."
)

SIGNOFF = "With Love and Light,\nTiff"

UNTIMED_NOTE = (
    "Because your birth time wasn't known, this reading uses solar houses: your Sun sign is treated as "
    "your 1st house. The timing and eclipse dates are exact, and the house stories are a strong symbolic "
    "read. A verified birth time would make them more precise."
)

DISCLAIMER = (
    "This reading is based on my own research, orb-based methodology and intuitive abilities. It's meant "
    "for reflection and spiritual growth, and it isn't medical, legal, financial or psychological "
    "advice. Eclipses can be felt at wider orbs too, just not as strongly as the tighter orb I consider "
    "the epicenter. Calculations use the tropical zodiac, Placidus houses and the True Node, and you're "
    "always welcome to use your own methods. Because this is an instant digital download, all sales are "
    "final and non-refundable."
)

NEW_MOON = ("New Moon in {sign} in your {ord} house of {topic}. Plant one clear intention here.")

CYCLE_NAME = {
    ("saturn", 0): "Your Saturn Return", ("saturn", 180): "Your Saturn Opposition",
    ("saturn", 90): "Your Saturn Square", ("uranus", 180): "Your Uranus Opposition",
    ("uranus", 90): "Your Uranus Square", ("neptune", 90): "Your Neptune Square",
    ("pluto", 90): "Your Pluto Square", ("uranus", 0): "Your Uranus Return",
}

CYCLE = {
    ("saturn", 0): ("Saturn is returning to the place it held when you were born. This is a rite of passage: "
                    "you're asked to become the authority of your own life and build what's truly yours."),
    ("saturn", 180): ("Saturn is opposite the place it held when you were born, the halfway point of its "
                      "cycle. What you've built since your last Saturn Return gets reviewed, rewarded or rebuilt."),
    ("saturn", 90): ("Saturn is square the place it held when you were born, a checkpoint in its 29-year cycle. "
                     "It asks whether the structures in your life still fit who you're becoming."),
    ("uranus", 180): ("Uranus is opposite the place it held when you were born. This is the midlife awakening, "
                      "the moment the parts of you that have waited patiently ask to be lived now, not someday. "
                      "It's less about blowing up your life and more about telling the truth about what's next."),
    ("uranus", 90): ("Uranus is square the place it held when you were born. Restlessness is a signal, not a "
                     "problem: something in you is ready for more freedom."),
    ("uranus", 0): ("Uranus is returning to the place it held when you were born, an 84-year completion. "
                    "Wisdom and freedom meet."),
    ("neptune", 90): ("Neptune is square the place it held when you were born. Old dreams dissolve so truer "
                      "ones can take shape. Let go of who you thought you had to be."),
    ("pluto", 90): ("Pluto is square the place it held when you were born. A deep power shift asks you to "
                    "release what you've outgrown and reclaim what's always been yours."),
}

GROUP_NOTE = "These {n} contacts work as one storyline, so expect the theme to echo across each exact date."

POWER_WHY = "{month} matters because of {items}."

THREAD_OPEN = (
    "So what's the story of your year? Put the pieces side by side and it reads like this: a year of "
    "{title}, centered on your {prof_ord} house of {prof_short}, while your eclipse story pulls on the "
    "seesaw between your {leo_ord} and {aq_ord} houses."
)
THREAD_ECHO = (
    "And notice this. Your profection year and your eclipse story both point to your {ord} house. When "
    "two different timing techniques land on the same part of your chart, the message is loud. This is "
    "the area of life where 2027 wants your full attention."
)
THREAD_LORD_SLOW = (
    "Because {lord} rules your year, its path through {houses} isn't background noise for you. It's "
    "the headline. Every date in your calendar where {lord} touches your chart is worth circling twice."
)
THREAD_LORD_FAST = (
    "Because {lord} rules your year, pay extra attention whenever {lord} is retrograde or making news "
    "in the sky. Those moments carry your year's message."
)
THREAD_TOP = (
    "Your biggest personal turning point is {top}. That's the chapter where the year asks the most of "
    "you, and where the most growth is waiting."
)
THREAD_CLOSE = (
    "Not random events. Not a pile of transits. But one story, unfolding month by month. Your calendar "
    "shows you exactly where it turns."
)

# --------------------------------------------------------------------------------------
# Where to go from here (shown under Final Thoughts). Links are live in the PDF.
# --------------------------------------------------------------------------------------
NEXT_INTRO = (
    "If this reading stirred something in you, here's where I'd go next. Each of these picks up a "
    "thread from your 2027 and takes it deeper."
)

OFFERS = {
    "monthly": ("What Does This Month Hold for My Manifesting? Your Monthly Manifestation Forecast",
                "https://sagereality11.com/shop/monthly-manifestation-forecast/",
                "Your calendar shows you the big turns. This one walks with you month by month."),
    "solar_return": ("Your Personal Year: Solar Return + Fixed Stars",
                     "https://sagereality11.com/shop/your-personal-year-solar-return-fixed-stars/",
                     "Your birthday on or around {bday} starts your new year. This is my personal read of the chart for that moment, with your fixed stars."),
    "saros": ("The Saros Series Eclipse Guide: Decode Your Soul's Eclipse Lineage",
              "https://sagereality11.com/shop/the-saros-series-eclipse-guide-decode-your-souls-eclipse-lineage/",
              "Loved the Saros echoes in your eclipse story? This guide shows you how to trace every eclipse family in your life."),
    "prenatal": ("Your Prenatal Eclipse Deep Dive",
                 "https://sagereality11.com/shop/prenatal-eclipse-deep-dive-report/",
                 "With eclipses landing right on your chart this year, it's worth knowing the eclipse contract you were born under."),
    "timing": ("What's Happening to Me Right Now? Your Personal Timing Reading",
               "https://sagereality11.com/shop/personal-timing-reading/",
               "For the moments in 2027 when life speeds up and you want to know exactly what's moving."),
    "karmic": ("Your Karmic Contract Reading",
               "https://sagereality11.com/shop/karmic-contract-reading-report/",
               "Your year is pulling on deep, soul-level material. This reading names the karmic threads underneath it."),
    "divine_feminine": ("Your Divine Feminine Reading",
                        "https://sagereality11.com/shop/divine-feminine-reading/",
                        "Your year asks you to open your heart and receive. Meet the goddess archetypes living in your chart."),
    "incarnation": ("What Did Your Soul Come Here to Carry? Your Incarnation Map Reading",
                    "https://sagereality11.com/shop/incarnation-blueprint-reading/",
                    "Your year is about purpose and what you're building. This reading maps what your soul came here to do."),
    "past_lives": ("Your Past Lives Reading",
                   "https://sagereality11.com/shop/past-lives-reading-report/",
                   "When a year turns inward like yours does, past-life patterns tend to surface. This reading names them."),
    "course101": ("Course 101: Understanding Your Soul's Blueprint",
                  "https://sagereality11.com/shop/course-1-understanding-your-souls-blueprint/",
                  "Want to read your own chart like this? Start here."),
    "course102": ("Course 102: Lineage Contracts",
                  "https://sagereality11.com/shop/lineage-contracts-break-the-invisible-vows-and-heal-your-ancestral-story/",
                  "Your year touches home, roots and family. This course helps you heal the ancestral story you carry."),
    "course301": ("Course 301: The Shadow Alchemists & Rage Liberators",
                  "https://sagereality11.com/shop/theshadowalchemistsandrageliberators/",
                  "Your year asks you to take your power back. Persephone, Lilith, Sekhmet and Medusa show you how."),
}

# Profection house -> the reading that best continues that year's theme.
OFFER_BY_HOUSE = {1: "incarnation", 2: "incarnation", 3: "divine_feminine", 4: "karmic", 5: "divine_feminine",
                  6: "incarnation", 7: "divine_feminine", 8: "karmic", 9: "incarnation", 10: "incarnation",
                  11: "divine_feminine", 12: "past_lives"}
COURSE_BY_HOUSE = {4: "course102", 8: "course301", 12: "course102"}
