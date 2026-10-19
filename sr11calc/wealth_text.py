"""Reader-facing text for Your Birth Chart's Wealth Story, written in Tiff's voice.

House rules for every line in this file: second person, warm and plain, contractions,
no em dashes, almost no colons, no bold, no bullet lists. Each placement is explained
once and then built on. Possibilities, never predictions or promises.
"""

ORD = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh",
       8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh", 12: "twelfth"}
ORD_TITLE = {k: v.title() for k, v in ORD.items()}

HOUSE_TOPIC = {
    1: "your presence, your body, and your own initiative",
    2: "your income, your possessions, and your sense of worth",
    3: "communication, writing, learning, siblings, and your local world",
    4: "home, family, roots, and property",
    5: "creativity, pleasure, children, and the things you make",
    6: "daily work, routines, service, and health",
    7: "partners, clients, and one-to-one agreements",
    8: "shared resources, debt, taxes, inheritance, and other people's money",
    9: "teaching, publishing, travel, beliefs, and higher learning",
    10: "career, reputation, and your public role",
    11: "friends, networks, communities, and the gains that come from your work",
    12: "solitude, retreat, healing, and work done behind the scenes",
}

# Where money flows when the planet that rules your income sits in each house.
MONEY_IN_HOUSE = {
    1: "Money in your chart tends to follow what you personally bring to the table. Your presence, your instincts, and your willingness to start something are the engine, which means income often grows when you're the one who acts first.",
    2: "The ruler of your income sits in its own house, so earning and keeping are closely linked. You may have a natural feel for what things are worth and a steady instinct for building resources over time rather than all at once.",
    3: "Income in your chart likes to move through words, ideas, and connection. Teaching, writing, explaining, selling, or simply being the person who knows how to find the answer can all become sources of value, often close to home.",
    4: "Money in your chart is tied to home, family, and the foundation underneath your life. Property, a family business, work done from home, or simply building a secure base can all become part of how your resources grow.",
    5: "Income in your chart is connected with creativity and the things you make because they carry something of you. When your work has a bit of joy or self-expression in it, it tends to be more valuable, both to you and to the people who pay for it.",
    6: "Money in your chart moves through daily work and the skill you build by showing up. Your income tends to grow with your craft, your systems, and your reliability, which also means it's worth watching how much of your energy each dollar costs.",
    7: "The ruler of your income sits in the house of partnership, so money often arrives through other people. Clients, collaborators, a spouse, or a business partner can play a real role in what you earn, and the quality of those agreements matters.",
    8: "The ruler of your income sits in the house of shared resources. Your money story can be woven with other people's money through partnerships, investments, inheritance, commissions, or work that handles what belongs to others, so clear agreements become part of your wealth.",
    9: "Income in your chart is linked with knowledge, teaching, publishing, and travel. What you study, believe, and share can become valuable, and your resources may grow when your work reaches beyond the place you started.",
    10: "The ruler of your income sits at the top of your chart in the house of career. Your reputation and your public role are directly tied to what you earn, so being seen for what you do well is part of how your money grows.",
    11: "Income in your chart is connected with networks, friends, and communities. Referrals, audiences, groups you belong to, and the people who believe in your work can become real sources of support and gain.",
    12: "The ruler of your income sits in the twelfth house, the part of the chart that works behind the scenes. Money may come through quiet work, research, healing, institutions, or anything done away from the spotlight, and it can grow in ways that aren't obvious from the outside.",
}

# What the planet itself brings when it rules your income.
PLANET_EARN = {
    "sun": "With the Sun ruling your income, money is tied to visibility and confidence. You tend to earn best when you're allowed to lead, shine, or put your name on what you do.",
    "moon": "With the Moon ruling your income, money is tied to care and instinct. You tend to earn through attunement, sensing what people need before they've found the words for it and responding in a way that helps them feel looked after.",
    "mercury": "With Mercury ruling your income, money is tied to your mind. You tend to earn through ideas, information, skill with words, problem solving, and the ability to connect people with what they're looking for.",
    "venus": "With Venus ruling your income, money is tied to value, beauty, and relationships. You tend to earn through taste, harmony, and the ability to make people feel good about what they're choosing.",
    "mars": "With Mars ruling your income, money is tied to courage and effort. You tend to earn through action, competition, initiative, and the willingness to go after what you want rather than waiting for it.",
    "jupiter": "With Jupiter ruling your income, money is tied to growth and generosity. You tend to earn through knowledge, guidance, opportunity, and a willingness to see the bigger picture.",
    "saturn": "With Saturn ruling your income, money is tied to time and structure. You tend to earn through patience, responsibility, and the kind of steady effort that builds something lasting, even if it takes longer than you'd like.",
}

# How each sign colors the planet that rules your income, with a scene the reader can recognize.
SIGN_EARN = {
    "Aries": "In Aries, that energy moves quickly. You may be at your best when you can start things, take the lead, or solve a problem nobody else wants to touch. The risk is burning hot at the beginning and losing interest once the work becomes routine.",
    "Taurus": "In Taurus, that energy is patient and steady. You may have a good eye for quality and a natural sense of what something is truly worth. Slow, consistent building tends to serve you far better than chasing what's new.",
    "Gemini": "In Gemini, that energy is curious and quick. You may earn in more than one way at once, or find that your best income comes from connecting ideas, people, and information. Variety keeps you engaged, and focus keeps you paid.",
    "Cancer": "In Cancer, that energy is protective and personal. You may notice when someone is anxious before the meeting starts, or be the one who quietly builds the system that keeps everyone else steady. Those abilities are easy to overlook because they feel natural to you.",
    "Leo": "In Leo, that energy wants to be seen. Your warmth, confidence, and creativity can draw people toward what you offer, and you may earn best when your work carries your personality rather than hiding it.",
    "Virgo": "In Virgo, that energy is precise and useful. You may be the one who notices what's missing, fixes what's broken, or improves a process until it actually works. Being skilled is rarely your problem. Charging for that skill sometimes is.",
    "Libra": "In Libra, that energy works through fairness and connection. You may earn through partnership, design, mediation, or the ability to see both sides. Agreements matter, and so does feeling that an exchange is balanced.",
    "Scorpio": "In Scorpio, that energy goes deep. You may be drawn to work that handles what others avoid, research, strategy, crisis, or transformation. Trust is a currency for you, and you tend to invest fully or not at all.",
    "Sagittarius": "In Sagittarius, that energy is expansive and searching. You may earn through teaching, advising, travel, or sharing a bigger vision. Freedom matters to you, and so does believing in what you're selling.",
    "Capricorn": "In Capricorn, that energy is strategic and long range. You may be willing to build slowly, take responsibility, and earn authority over time. Your patience is an asset as long as it doesn't turn into carrying more than your share.",
    "Aquarius": "In Aquarius, that energy is inventive and independent. You may earn through new ideas, technology, community, or doing something differently than it's usually done. You need room to work your own way.",
    "Pisces": "In Pisces, that energy is intuitive and compassionate. You may earn through creativity, healing, imagination, or simply understanding people on a level that's hard to explain. Clear boundaries help that gift stay sustainable.",
}

DIGNITY = {
    "domicile": "{P} is in its own sign in {S}, which gives it real strength and plenty to draw from. In traditional terms, this is a planet at home.",
    "exaltation": "{P} is exalted in {S}, one of its most honored positions. It tends to perform well and be respected for what it does, as long as it isn't asked to carry everything alone.",
    "detriment": "{P} is in its detriment in {S}, the sign opposite its home. It still works, but it works in a language that isn't its first, which can make you second-guess an ability that's actually there.",
    "fall": "Traditionally, {P} is in its fall in {S}, which doesn't make it weak so much as uncomfortable. It can push too hard when it feels exposed, or hold back when it should speak up.",
}

SOLAR = {
    "cazimi": "{P} sits in the heart of the Sun, less than a third of a degree away. Traditional astrologers saw this as a kind of royal protection, so the planet's gifts can shine unusually clearly.",
    "combust": "{P} is about {d} degrees from the Sun, close enough that its light is reduced. It's still active, but its own needs can get absorbed into whatever you're working toward, and it may take longer for others to notice what it's doing.",
    "beams": "{P} is still under the Sun's beams, about {d} degrees away. It tends to work quietly before it becomes visible, so give its results a little more time than you think they need.",
}

RETRO = {
    "mercury": "Mercury was retrograde when you were born, so you often think things through more than once. Revisiting, revising, and second drafts tend to be where your best value shows up.",
    "venus": "Venus was retrograde when you were born, so your sense of value is often reconsidered from the inside. You may come back to an old skill, client, or idea and find it worth more the second time.",
    "mars": "Mars was retrograde when you were born, so effort can turn inward before it moves outward. You may need more time to decide, and then act with real force once you do.",
    "jupiter": "You were born while Jupiter was retrograde, so wisdom and growth tend to be earned and reconsidered from the inside rather than borrowed from someone else.",
    "saturn": "Saturn was retrograde when you were born, so you may hold yourself to standards nobody else set. Learning which rules are actually yours is part of building lasting security.",
}

# What another planet adds when it touches a money planet. Keys: conj, soft, hard.
CONTACT = {
    "sun": {"conj": "The Sun joins it, putting your identity right into this part of your story. What you earn and who you are can feel like the same thing.",
            "soft": "A supportive link with the Sun helps you be seen for this ability without forcing it.",
            "hard": "Tension with the Sun can make it hard to balance what you want to be known for with what actually pays."},
    "moon": {"conj": "The Moon is right beside it, so feelings and money travel together. Security isn't abstract for you. It's something you feel in your body.",
             "soft": "A supportive link with the Moon lets you trust your instincts about money, and people tend to feel cared for in your hands.",
             "hard": "Tension with the Moon can make money decisions feel emotional, especially when you're tired or worried."},
    "mercury": {"conj": "Mercury sits with it, bringing your voice and your ideas directly into how you create value.",
                "soft": "A supportive link with Mercury helps you explain what you do, which makes it easier for people to pay for it.",
                "hard": "Tension with Mercury can show up as overthinking a decision or undercharging because you can see every angle."},
    "venus": {"conj": "Venus sits with it, adding charm, taste, and an easy way with people to how you earn.",
              "soft": "A supportive link with Venus brings goodwill, helpful relationships, and a sense of what people will value.",
              "hard": "Tension with Venus can pull you between what you enjoy and what's practical, or tempt you to discount your work to keep the peace."},
    "mars": {"conj": "Mars sits right beside it, adding urgency and drive. You likely move fast when something matters, which protects you sometimes and exhausts you at others.",
             "soft": "A supportive link with Mars gives you the energy to act on opportunities when they appear.",
             "hard": "Tension with Mars can bring impatience, overwork, or decisions made in a rush to feel safe again."},
    "jupiter": {"conj": "Jupiter sits with it, expanding everything it touches. Opportunity and generosity are close at hand, and so is the temptation to say yes to too much.",
                "soft": "A supportive link with Jupiter is one of the classic signatures of help arriving, through mentors, good timing, or simply faith in what you're doing.",
                "hard": "Tension with Jupiter can show up as overextending, overpromising, or giving more than an exchange can hold."},
    "saturn": {"conj": "Saturn sits with it, adding seriousness and staying power. Things may take longer, and what you build tends to last.",
               "soft": "A supportive link with Saturn gives you discipline and a feel for long-term structure, the kind of patience that compounds.",
               "hard": "Tension with Saturn can feel like a ceiling or a fear of not having enough. It often eases as you build structures that make you feel secure."},
    "uranus": {"conj": "Uranus sits with it, bringing sudden shifts, new methods, and a strong need for independence into this part of your life.",
               "soft": "A supportive link with Uranus brings fresh ideas and openings that arrive out of nowhere.",
               "hard": "Tension with Uranus can bring income that rises and falls without warning, or a restlessness with any arrangement that feels confining."},
    "neptune": {"conj": "Neptune sits with it, adding imagination, compassion, and a little fog. Your vision is real, and the details need extra care.",
                "soft": "A supportive link with Neptune brings inspiration and an intuitive sense of what people are longing for.",
                "hard": "Tension with Neptune can blur the line between generosity and depletion, or make it hard to see an arrangement clearly."},
    "pluto": {"conj": "Pluto sits with it, adding intensity and a desire to go all the way in. Power around money is something you'll want to understand, not avoid.",
              "soft": "A supportive link with Pluto gives you staying power and the ability to rebuild after a setback.",
              "hard": "Tension with Pluto can bring all-or-nothing moments with money, or power dynamics that ask you to stand your ground."},
    "chiron": {"conj": "Chiron sits with it, so this is also where an old ache lives, and where your wisdom eventually comes from.",
               "soft": "A supportive link with Chiron turns what you've healed into something you can offer others.",
               "hard": "Tension with Chiron can touch an old sense of not being enough, which sometimes shows up as giving your expertise away."},
    "north_node": {"conj": "Your North Node sits with it, which makes this placement part of your direction of growth, not only your history.",
                   "soft": "A supportive link with your North Node suggests that leaning into this ability moves your whole life forward.",
                   "hard": "Tension with your nodes asks you to work this ability in a new way rather than the one you know by heart."},
}

ANGLE_CONTACT = {
    "asc": {"conj": "It sits right on your Ascendant, so people see this energy in you immediately.",
            "hard": "It squares your Ascendant, so this energy can feel like it's pulling against how you naturally present yourself."},
    "mc": {"conj": "It sits right on your Midheaven, which makes this part of your public reputation.",
           "opp": "It sits directly opposite your Midheaven at the base of your chart, tying it to home and foundations as much as to career.",
           "hard": "It squares your Midheaven, so the career and this placement pull at an angle to each other.",
           "soft": "It forms a supportive aspect to your Midheaven, which helps it feed your public reputation."},
    "ic": {"conj": "It sits on your IC, the base of your chart, tying it to home, family, and the private life underneath everything."},
    "dsc": {"conj": "It sits on your Descendant, so partners and clients tend to bring this energy into your life."},
}

ASPECT_WORD = {"conjunction": "conjunct", "sextile": "sextile", "square": "square", "trine": "trine",
               "opposition": "opposite"}
ASPECT_CLASS = {"conjunction": "conj", "sextile": "soft", "trine": "soft", "square": "hard", "opposition": "hard"}

# --------------------------------------------------------------------------------------
# Part of Fortune and Lot of Assets
# --------------------------------------------------------------------------------------
FORTUNE_INTRO = ("Your Part of Fortune sits at {deg} degrees {sign} in your {ord} house. The Part of Fortune shows where "
                 "circumstance and opportunity tend to meet you, the place where life seems to cooperate a little more easily.")
FORTUNE_HOUSE = {
    1: "In the first house, fortune grows out of your own presence. Opportunity rarely arrives from far away. It tends to show up once you act on your instincts.",
    2: "In the second house, fortune is tied directly to your resources. What you build and keep becomes its own source of opportunity, so tending what you already have matters.",
    3: "In the third house, fortune moves through conversations, learning, and your local world. A message, a class, or a neighbor can open more than you'd expect.",
    4: "In the fourth house, fortune is rooted in home and family. Property, a stable base, or support from your roots can become part of how opportunity reaches you.",
    5: "In the fifth house, fortune is found through creativity and joy. When you make something you love, opportunity has an easier time finding you.",
    6: "In the sixth house, fortune is built through daily effort and skill. The habits you keep and the craft you refine quietly become your luck.",
    7: "In the seventh house, fortune comes through other people. Partners, clients, and collaborators can bring opportunities you wouldn't find alone.",
    8: "In the eighth house, fortune is linked with shared resources and deep trust. Joint ventures, investments, or other people's support can carry real opportunity when the terms are clear.",
    9: "In the ninth house, fortune grows through knowledge, travel, and belief. Learning something new or reaching a wider audience can open unexpected doors.",
    10: "In the tenth house, fortune is tied to your career and reputation. Being visible for what you do well is one of the clearest ways opportunity reaches you.",
    11: "In the eleventh house, fortune flows through friends and community. Introductions, referrals, and the people in your corner are part of your luck.",
    12: "In the twelfth house, fortune works quietly. Rest, reflection, research, and work done away from the spotlight can carry more opportunity than they seem to.",
}
FORTUNE_RULER_SAME = ("Its ruler is {R}, the same planet that rules your income. When Fortune and the second house answer to one planet, "
                      "the message is consistent. Your opportunities and your earning power grow from the same source.")
FORTUNE_RULER_CLOSE = "It sits {orb} from its own ruler, {R}, so opportunity and the planet that directs it are working side by side."
FORTUNE_RULER_OTHER = ("Its ruler, {R}, sits in {S} in your {ord} house, which tells me opportunity tends to travel through "
                       "{topic} before it reaches you.")
ASSETS_LINE = ("Your Lot of Assets, a traditional point connected with what you accumulate and keep, falls in {sign} in your {ord} house{same}.")
ASSETS_SAME = " under the same ruler"
ASSETS_MEANING = {
    "same": "That repetition matters. The planet that rules your income keeps reappearing as the one that decides what stays with you, so tending that planet's needs is how you hold onto what you earn.",
    "other": "Its ruler, {R}, becomes another voice in your money story, showing where keeping and growing what you've earned tends to happen.",
}
CARRY_FORWARD = ("There's a practical side to this. When so much depends on your own presence, it matters what happens when you aren't available. "
                 "A chart like this does well when something you've built can carry your care forward without requiring you for every piece of it, "
                 "a process others can follow, a product, a body of writing, or an investment that keeps working while you rest.")

# --------------------------------------------------------------------------------------
# What can block the flow
# --------------------------------------------------------------------------------------
PHASE = {
    "new": "Your Moon was born in the new phase, close to its meeting with the Sun. You tend to begin things on instinct and figure out the shape later, which is a gift as long as you give new ventures time to find their footing.",
    "crescent": "Your Moon was born in the crescent phase, pulling away from the Sun. There's a push to break free of old patterns, and money may feel like the proof that you can.",
    "first quarter": "Your Moon was born in the first quarter phase, the phase of action and crisis. You tend to build through challenge, and pressure often brings out your best decisions.",
    "gibbous": "Your Moon was born in the gibbous phase, the phase of refining. You may keep improving something long after it's good enough, which is wonderful for quality and hard on your pricing.",
    "full": "Your Moon was born under a Full Moon, facing the Sun across the sky. Relationships and other people's responses can strongly shape how secure you feel with money.",
    "disseminating": "Your Moon was born in the disseminating phase, the phase of sharing what you know. Teaching and passing on what you've learned can become part of how you earn.",
    "last quarter": "Your Moon was born in the last quarter phase, a turning point in the cycle. You may outgrow ways of earning that once worked and need to let them go before the next thing can begin.",
    "balsamic": "Your Moon was born in the balsamic phase, the final stretch before the New Moon. It belongs to the end of a cycle, when something has matured enough to be distilled, so you may do your best financial work when you stop starting over and refine what you already know works.",
}
BLOCK_INTRO = "Every money story has a place where it gets tender. In your chart, a few conditions are worth understanding so they work for you instead of quietly against you."
BLOCK_EMOTIONAL = {
    "moon": "Because the Moon carries so much of your money story, money may rarely feel like only money. A raise can feel like proof you're valued, and a slow month can feel like a judgment about your worth. Part of building steady wealth is separating those two experiences. The value of your work and your value as a person are related, but they aren't the same number.",
    "sun": "Because the Sun carries so much of your money story, earning can feel tied to your identity. When work is going well, you feel like yourself. When it isn't, you may question who you are. Your worth doesn't rise and fall with this month's numbers.",
    "mercury": "Because Mercury carries so much of your money story, it's easy to think your way around a decision for a long time. Sometimes the best financial move is the simple one you already know.",
    "venus": "Because Venus carries so much of your money story, how you feel about people can shape what you charge them. Generosity is beautiful. Make sure it's a choice and not an apology.",
    "mars": "Because Mars carries so much of your money story, you may move fast when you feel threatened. Slowing down long enough to ask whether a problem is yours to fix can save you real money and energy.",
    "jupiter": "Because Jupiter carries so much of your money story, it's easy to trust that more will come. That faith is real, and it works best with a plan and a ceiling.",
    "saturn": "Because Saturn carries so much of your money story, you may feel like you're never quite safe enough. Building small structures that prove you are, savings, contracts, routines, tends to quiet that voice.",
}
BLOCK_HARD_MALEFIC = "{P} {asp} {O}. {txt}"
BLOCK_CADENT_12 = "Your income ruler sits in the twelfth house, so some of its work happens out of view. You may undervalue what you do because nobody sees how much it takes. Naming it, pricing it, and talking about it out loud is part of the work."
BLOCK_CADENT_6 = "Your income ruler sits in the sixth house of daily work, which ties money closely to effort. It's worth asking how much of your income depends on you being there for every hour of it."
BLOCK_EMPTY = "Nothing in your chart is blocking your money in a dramatic way. The places to watch are quieter, the habits and assumptions that decide whether what you earn actually stays with you."

# --------------------------------------------------------------------------------------
# Midheaven and career
# --------------------------------------------------------------------------------------
MC_SIGN = {
    "Aries": "Aries on your Midheaven asks you to lead, start things, and be known for courage. You may do best in roles where you can move independently.",
    "Taurus": "Taurus on your Midheaven builds a reputation for reliability, quality, and steadiness. People trust you with things that matter.",
    "Gemini": "Gemini on your Midheaven brings communication, versatility, and curiosity into your public life. You may be known for more than one thing.",
    "Cancer": "Cancer on your Midheaven brings care into your public role. People may come to you because you make them feel protected and understood.",
    "Leo": "Leo on your Midheaven wants recognition and creative leadership. You're meant to be seen for what you do, not tucked behind someone else's name.",
    "Virgo": "Virgo on your Midheaven builds a reputation for skill, precision, and usefulness. You're known for getting things right.",
    "Libra": "Libra on your Midheaven brings fairness, partnership, and beauty into your public life. You may be known for bringing people together.",
    "Scorpio": "Scorpio on your Midheaven brings depth, strategy, and a willingness to handle what others avoid. People trust you in a crisis.",
    "Sagittarius": "Sagittarius on your Midheaven brings teaching, vision, and exploration into your public life. You're meant to share a bigger picture.",
    "Capricorn": "Capricorn on your Midheaven builds authority slowly. Your reputation tends to grow with time, responsibility, and proven results.",
    "Aquarius": "Aquarius on your Midheaven brings innovation and independence into your public life. You may be known for doing things differently.",
    "Pisces": "Pisces on your Midheaven adds compassion and imagination to your public life. People may come to you because you seem to understand what they're going through.",
}
CAREER_RULER = ("Your Midheaven sits at {deg} degree{ds} {sign}, which makes {R} the traditional ruler of your career and public direction. "
                "{Rc} is at {rdeg} degree{rs} {rsign} in your {rord} house.")
CAREER_IN_HOUSE = {
    1: "With your career ruler in the first house, your work and your identity are closely linked. You're often your own best advertisement, and career growth follows personal initiative.",
    2: "With your career ruler in the second house, your career is directly tied to your income. Professional effort and personal resources tend to move together.",
    3: "With your career ruler in the third house, your career runs through communication. Writing, teaching, speaking, sales, or networking close to home can carry your reputation.",
    4: "With your career ruler in the fourth house, your public path is tied to home and family. Working from home, a family business, real estate, or building a secure base can all be part of your career story.",
    5: "With your career ruler in the fifth house, your career wants room for creativity. Work that lets you make, perform, or enjoy something tends to lift your reputation.",
    6: "With your career ruler in the sixth house, the career story runs through daily effort. Your reputation is likely built on how well you actually do the work, the consistency, the problem solving, and the willingness to handle details other people avoid.",
    7: "With your career ruler in the seventh house, your career grows through other people. Partnerships, clients, and one-to-one work can define your public path.",
    8: "With your career ruler in the eighth house, your career may involve other people's resources or deep, transformative work. Finance, research, therapy, or crisis work can fit this placement.",
    9: "With your career ruler in the ninth house, your career is tied to knowledge and meaning. Teaching, publishing, law, travel, or spiritual work can carry your public path.",
    10: "With your career ruler in its own house at the top of your chart, your career has real visibility. You're meant to be seen for what you do.",
    11: "With your career ruler in the eleventh house, your career grows through networks and community. The people who know your work can become your greatest professional asset.",
    12: "With your career ruler in the twelfth house, some of your most important work happens behind the scenes. Institutions, healing work, research, or roles that serve quietly can fit you well.",
}
PLANET_CAREER = {
    "sun": "The Sun as career ruler wants you in a role where you can lead or be recognized.",
    "moon": "The Moon as career ruler brings care, nurturing, and sensitivity to the public into your work.",
    "mercury": "Mercury as career ruler favors communication, analysis, and work that uses your mind.",
    "venus": "Venus as career ruler favors beauty, relationships, diplomacy, and work that brings people pleasure.",
    "mars": "Mars as career ruler favors action, courage, and work where you can compete or protect.",
    "jupiter": "Jupiter as career ruler brings knowledge, guidance, ethics, and helping people see the bigger picture into your professional path.",
    "saturn": "Saturn as career ruler brings structure, responsibility, and authority earned over time into your professional path.",
}
CAREER_BRIDGE_SAME = ("Your career ruler is also the planet that rules your income, which builds a direct bridge between your reputation "
                      "and your money. When your work is seen, it tends to pay.")
CAREER_BRIDGE_ASPECT = ("Your career ruler {asp} {R2}, the ruler of your income, so recognition and money are in conversation. {txt}")
CAREER_BRIDGE_NONE = ("Career visibility and income aren't the same thing, and your chart keeps them somewhat separate. {R} doesn't form a direct "
                      "aspect with {R2}, so recognition for your work won't automatically turn into money. The bridge is how you price, package, "
                      "and protect what you offer.")
BRIDGE_SOFT = "That connection tends to help. Being seen for your work makes it easier to be paid for it."
BRIDGE_HARD = "That connection works through tension. Recognition can arrive before the money does, or the money can come from work you'd rather not be known for, until you bring the two closer together."
TENTH_OCCUPANT = "{P} sits in your tenth house, which brings {kw} right into your public life."
KEYWORD = {"sun": "your identity and leadership", "moon": "care and public sensitivity", "mercury": "your voice and your ideas",
           "venus": "charm, beauty, and diplomacy", "mars": "drive and competitive energy", "jupiter": "growth and good fortune",
           "saturn": "responsibility and authority", "uranus": "innovation and sudden change", "neptune": "imagination and compassion",
           "pluto": "power, depth, and transformation", "chiron": "healing and the wisdom of an old wound"}

# --------------------------------------------------------------------------------------
# Fifth, eighth and eleventh houses
# --------------------------------------------------------------------------------------
FIFTH_OPEN = ("Your fifth house begins in {sign}, so {R} rules your creativity, your pleasure, and the things you make because they carry "
              "something of you.")
FIFTH_IN = {
    1: "With that ruler in your first house, your creativity is personal and visible. You are often the product.",
    2: "With that ruler in your second house, creative work and income are directly linked. What you make can become what you earn.",
    3: "With that ruler in your third house, creative income likes to move through words, teaching, explaining, and sharing ideas, often close to home.",
    4: "With that ruler in your fourth house, creativity is rooted at home. A home studio, family traditions, or making your space beautiful can matter more than you think.",
    5: "With that ruler in its own house, creativity is a real strength. Joy isn't a luxury in your chart. It's part of how you work well.",
    6: "With that ruler in your sixth house, creativity shows up in daily work. Crafting, improving, and making ordinary things better can become a quiet source of value.",
    7: "With that ruler in your seventh house, creativity flourishes in collaboration. Partners and clients can draw out work you wouldn't make alone.",
    8: "With that ruler in your eighth house, creative work can be tied to shared resources, investors, royalties, or deep and transformative subjects.",
    9: "With that ruler in your ninth house, creativity wants a wider audience. Publishing, teaching, travel, or work that carries meaning can be where it thrives.",
    10: "With that ruler in your tenth house, creativity can become your career. What you make may be what you're publicly known for.",
    11: "With that ruler in your eleventh house, creativity is shared with community. Audiences, groups, and friends can become part of how your creative work grows.",
    12: "With that ruler in your twelfth house, creativity often happens in private. Quiet time and solitude are where your best ideas take shape.",
}
FIFTH_OCC = "{P} sits in your fifth house, bringing {kw} into how you create and what you enjoy."
FIFTH_SATURN_PLUTO = "Neither Saturn nor Pluto favors gambling or quick wins. Together they favor creative work you develop slowly and own completely."

EIGHTH_OPEN = ("Your eighth house begins in {sign}, so {R} rules shared resources, debt, taxes, a partner's money, and the obligations "
               "attached to other people's money.")
EIGHTH_IN = {
    1: "With that ruler in your first house, other people's resources tend to come through you personally. Your presence can attract investment and support, so know your terms before you say yes.",
    2: "With that ruler in your second house, shared resources flow directly into your own. Inheritances, commissions, or a partner's income can become part of what you have, and keeping clear records protects you.",
    3: "With that ruler in your third house, shared resources move through agreements, paperwork, and conversation. Read the fine print, and you'll often find opportunity in it.",
    4: "With that ruler in your fourth house, shared resources are tied to home and family. Property, family money, or a shared household can be a big part of this story.",
    5: "With that ruler in your fifth house, shared resources and creative enterprise are tied together. Contracts, investments, or financial partnerships can support what you create when they're built carefully and put in writing.",
    6: "With that ruler in your sixth house, shared resources are tied to work. Employer benefits, debts that fund your tools, or handling other people's money on the job can all fit here.",
    7: "With that ruler in your seventh house, partners and money are closely linked. A spouse's or business partner's resources can shape your own, so agreements deserve real attention.",
    8: "With that ruler in its own house, you may have a natural understanding of how shared money works, investments, insurance, and the deeper side of financial trust.",
    9: "With that ruler in your ninth house, shared resources may come through education, publishing, travel, or foreign connections. Grants and sponsorship fit here too.",
    10: "With that ruler in your tenth house, shared resources and career are linked. Your work may involve other people's money, or your reputation may attract investment.",
    11: "With that ruler in your eleventh house, shared resources come through community. Group ventures, crowdfunding, or friends who invest in you can all play a part.",
    12: "With that ruler in your twelfth house, shared resources can move quietly or through institutions. Keeping things transparent protects you from surprises.",
}
EIGHTH_OCC = "{P} sits in your eighth house, bringing {kw} into how you handle shared money and trust."
EIGHTH_STRUCTURE = ("Clear terms, realistic timelines, and knowing exactly who owns what keep these arrangements healthy, while vague ones are "
                    "usually where trouble starts.")

ELEVENTH_OPEN = ("Your eleventh house begins in {sign}, so {R} rules your friends, networks, communities, and the gains that come from your work. "
                 "The eleventh is also the second house counted from the tenth, which makes it a traditional window into the income your career produces.")
ELEVENTH_IN = {
    1: "With that ruler in your first house, support tends to arrive through your own initiative. People show up when you reach out, ask, or start something. Waiting to be discovered isn't how this placement works best.",
    2: "With that ruler in your second house, your networks feed your income directly. Referrals and introductions can turn into real money.",
    3: "With that ruler in your third house, gains come through conversation, word of mouth, and your local circle. Keep talking about what you do.",
    4: "With that ruler in your fourth house, family and close community can be part of your support system, and your home may become a gathering place.",
    5: "With that ruler in your fifth house, gains come through creative work and the people who enjoy it. An audience can become a community.",
    6: "With that ruler in your sixth house, gains come through work relationships and colleagues. The people you serve and work beside can open doors.",
    7: "With that ruler in your seventh house, gains come through partners and clients. One strong relationship can lead to many others.",
    8: "With that ruler in your eighth house, gains can come through shared ventures and deep trust. A small circle of committed people may matter more than a large audience.",
    9: "With that ruler in your ninth house, gains come through teachers, students, travel, and people who share your beliefs.",
    10: "With that ruler in your tenth house, your career and your community are deeply connected. Your reputation brings people to you.",
    11: "With that ruler in its own house, your networks are a real strength. Community and friendship are not side projects in your chart. They're part of your wealth.",
    12: "With that ruler in your twelfth house, support often comes quietly, through behind-the-scenes helpers, private groups, or people you may not see often.",
}
ELEVENTH_OCC = "{P} sits in your eleventh house, bringing {kw} into your friendships and communities."
LINKED_RULER = ("{R} also rules this house, and we've already met it in your chart. That repetition ties {this} to {that}, so the same strengths "
                "and the same cautions carry over.")
ROLE_PHRASE = {"asc": "your sense of self", "second": "your income", "fortune": "your Part of Fortune", "assets": "what you keep",
               "career": "your career", "fifth": "your creativity", "eighth": "shared resources", "eleventh": "your networks",
               "sixth": "your daily work"}
FALL_CAUTION = {
    "mars": "Since Mars is in its fall, the caution is overgiving. Always being the one who helps can quietly become the reason no one thinks to help you.",
    "venus": "With Venus in a difficult sign, the caution is giving yourself away to keep everyone happy.",
    "saturn": "With Saturn in a difficult sign, the caution is carrying responsibilities that were never yours.",
    "jupiter": "With Jupiter in a difficult sign, the caution is promising more than you can comfortably deliver.",
    "mercury": "With Mercury in a difficult sign, the caution is talking yourself out of a good idea.",
    "moon": "With the Moon in a difficult sign, the caution is letting worry make decisions for you.",
    "sun": "With the Sun in a difficult sign, the caution is shrinking so others can shine.",
}
RECEIVE = "Healthy gains include receiving referrals, introductions, and support as readily as you offer them."

# --------------------------------------------------------------------------------------
# The nodes
# --------------------------------------------------------------------------------------
SN_SIGN = {
    "Aries": "Aries on your South Node carries a familiarity with doing it yourself, moving fast, and fighting for what you need.",
    "Taurus": "Taurus on your South Node carries a familiarity with holding on, building security, and trusting only what you can touch.",
    "Gemini": "Gemini on your South Node carries a familiarity with gathering information, staying busy, and having an answer for everything.",
    "Cancer": "Cancer on your South Node carries a familiarity with caretaking and making sure everyone else is safe first.",
    "Leo": "Leo on your South Node carries a familiarity with being the one in front, needing your work to be seen to feel it counts.",
    "Virgo": "Virgo on your South Node carries a familiarity with fixing, serving, and never feeling quite finished.",
    "Libra": "Libra on your South Node carries a familiarity with keeping the peace and shaping yourself around what other people want.",
    "Scorpio": "Scorpio on your South Node carries a familiarity with intensity, control, and merging your resources with someone else's.",
    "Sagittarius": "Sagittarius on your South Node carries a familiarity with teaching, advising, and having the answer.",
    "Capricorn": "Capricorn on your South Node carries a familiarity with duty, achievement, and earning your place through hard work.",
    "Aquarius": "Aquarius on your South Node carries a familiarity with standing apart, serving the group, and keeping your own needs at a distance.",
    "Pisces": "Pisces on your South Node carries a familiarity with dissolving boundaries, rescuing, and giving until there's nothing left.",
}
NN_SIGN = {
    "Aries": "Aries on your North Node asks you to choose yourself, act on your own behalf, and stop waiting for permission.",
    "Taurus": "Taurus on your North Node asks you to slow down, build steadily, and let yourself enjoy what you have.",
    "Gemini": "Gemini on your North Node asks for curiosity, questions, and listening rather than always arriving with the full answer.",
    "Cancer": "Cancer on your North Node asks you to let yourself be cared for and to build a home base that nourishes you.",
    "Leo": "Leo on your North Node asks you to be seen, to put your name on your work, and to let joy guide what you create.",
    "Virgo": "Virgo on your North Node asks for practical systems, healthy routines, and turning big ideals into daily steps.",
    "Libra": "Libra on your North Node asks you to collaborate, let others contribute, and create fair exchanges instead of doing it all alone.",
    "Scorpio": "Scorpio on your North Node asks you to share resources wisely, trust carefully, and allow real depth in partnership.",
    "Sagittarius": "Sagittarius on your North Node asks you to trust the bigger picture and share what you know with a wider world.",
    "Capricorn": "Capricorn on your North Node asks you to build structures, take your ambitions seriously, and let yourself be an authority.",
    "Aquarius": "Aquarius on your North Node asks you to find your community and contribute your unique perspective to something larger.",
    "Pisces": "Pisces on your North Node asks you to trust intuition, release control, and let compassion include you.",
}
SN_HOUSE = {
    1: "In the first house, it describes a habit of relying on yourself for everything.",
    2: "In the second house, it describes a habit of measuring safety by what you own and earn.",
    3: "In the third house, it describes a habit of staying busy with information and the next conversation.",
    4: "In the fourth house, it describes a habit of putting family and home duties ahead of your own direction.",
    5: "In the fifth house, it describes a habit of needing applause or creative validation before you feel worthy.",
    6: "In your sixth house, it describes familiar territory around work, service, and usefulness. You may know how to be indispensable more easily than you know how to be paid fairly for it.",
    7: "In the seventh house, it describes a habit of building your life around partners and clients.",
    8: "In the eighth house, it describes a habit of tying your security to other people's money or approval.",
    9: "In the ninth house, it describes a habit of searching for the right belief or teacher before you act.",
    10: "In the tenth house, it describes a habit of defining yourself by achievement and public expectations.",
    11: "In the eleventh house, it describes a habit of serving the group and putting your own wishes last.",
    12: "In the twelfth house, it describes a habit of retreating, sacrificing, or working unseen.",
}
NN_HOUSE = {
    1: "In your first house, your growth asks you to take initiative and build a life around your own choices. Financially, that means trusting your own judgment.",
    2: "In your second house, your growth asks you to build your own resources and define worth for yourself. Financially, it points toward independence and owning what you earn.",
    3: "In your third house, your growth asks you to speak, write, and share ideas in everyday ways. Financially, that can mean small, steady exchanges rather than one big answer.",
    4: "In your fourth house, your growth asks you to build a home base that truly supports you. Financially, it points toward security you create on purpose.",
    5: "In your fifth house, your growth asks you to create, play, and take a few joyful risks. Financially, that can mean income from work that carries your personality.",
    6: "In your sixth house, your growth asks for routines and practical service. Financially, that means turning vision into systems you can actually sustain.",
    7: "In your seventh house, your growth asks you to partner. Financially, it points toward fair agreements and letting others help build what you can't build alone.",
    8: "In your eighth house, your growth asks you to share resources and allow real trust. Financially, it points toward investing, collaborating, and letting others invest in you.",
    9: "In your ninth house, your growth asks you to teach, travel, and expand. Financially, it points toward work with a wider reach and a sense of meaning.",
    10: "In your tenth house, your growth asks you to step into public authority. Financially, it points toward career goals you're willing to be seen pursuing.",
    11: "In your eleventh house, your growth asks you to belong to something larger. Financially, it points toward community, networks, and shared goals.",
    12: "In your twelfth house, your growth asks for rest, retreat, and the parts of life that happen away from view. Financially, this points toward income that doesn't depend on constant visible effort, and it asks you to protect the quiet time where your best ideas take shape. That isn't a call to withdraw from work. It's a call to stop measuring your worth by how busy you are.",
}
SN_CONJ = {
    "neptune": "Neptune sits with your South Node, adding a tendency to give without clear edges. It can blur the line between devotion and depletion, especially at work.",
    "saturn": "Saturn sits with your South Node, adding a familiar weight of duty. Releasing what you've been carrying out of habit makes room for what you actually want.",
    "jupiter": "Jupiter sits with your South Node, so generosity and knowledge are old gifts. The growth is sharing them without giving them away.",
    "mars": "Mars sits with your South Node, adding a familiar urge to push through. Rest is part of your growth.",
    "venus": "Venus sits with your South Node, so charm and pleasing others come easily. Make sure your own needs are part of the exchange.",
    "pluto": "Pluto sits with your South Node, adding an old pattern of control or survival around resources that's ready to soften.",
    "uranus": "Uranus sits with your South Node, adding a familiar restlessness that can leave things before they pay off.",
}
NN_TRINE = ("Your North Node {asp} {names}, which is an encouraging link. The work those planets describe is one of the paths that supports "
            "this growth.")
NODE_CLOSE = "When you make something carefully, own it, and let it work for you, you're moving in the direction your nodes describe."

# --------------------------------------------------------------------------------------
# Fixed stars on key points
# --------------------------------------------------------------------------------------
STAR = {
    "Regulus": ("the Heart of the Lion", "Regulus is a Royal Star associated with honor, success, and the ability to rise. It can bring recognition and a warmth that draws people toward what you offer. But every Royal Star carries a test, and Regulus warns against revenge and retaliation. Its success holds when you let your work speak instead of answering every slight. In money matters, the deal you walk away from with your dignity intact tends to serve you better than the one you win by proving someone wrong."),
    "Spica": ("the Wheat Sheaf", "Spica is one of the most fortunate stars in the sky, associated with gifts, talent, and a harvest that feels earned and blessed at once. It asks you to take your gifts seriously enough to share them."),
    "Aldebaran": ("the Eye of the Bull", "Aldebaran is a Royal Star associated with success through integrity. Its test is honesty. When your purpose stays honorable, what you build tends to hold."),
    "Antares": ("the Heart of the Scorpion", "Antares is a Royal Star of courage and intensity. Its test is obsession and needless conflict. Its success comes when you choose which battles are worth your energy."),
    "Fomalhaut": ("the Mouth of the Fish", "Fomalhaut is a Royal Star of vision and inspiration. Its test is purity of intention, not perfection but staying connected to why you began."),
    "Sirius": ("the Scorching One", "Sirius is associated with brilliance and sudden success. It asks that growth stay sustainable, because success that burns too hot can burn you too."),
    "Algol": ("the Gorgon's Head", "Algol carries intense, raw power. With money it asks you to use strong emotions as fuel for protection and creation rather than letting them make the decisions."),
    "Arcturus": ("the Guardian of the Bear", "Arcturus is associated with taking a different path and finding success by doing things your own way."),
    "Vega": ("the Harp Star", "Vega is associated with charisma and a magical way with people. It asks you to back the charm with substance."),
    "Pollux": ("the Immortal Twin", "Pollux carries a bold, sometimes fierce energy. It asks you to use that strength to protect and build rather than to cut down."),
    "Castor": ("the Mortal Twin", "Castor is associated with writers and storytellers, the gift of finding words for what others feel."),
    "Procyon": ("the Little Dog Star", "Procyon is associated with quick success and a talent that thrives when it's allowed to diversify."),
    "Deneb Algedi": ("the Tail of the Goat", "Deneb Algedi is associated with justice, law, and the steady authority of someone who keeps their word."),
    "Alcyone": ("the brightest of the Pleiades", "Alcyone is associated with vision and insight, the ability to see what others can't, with a reminder to share it gently."),
    "Rigel": ("the Foot of Orion", "Rigel is associated with teaching and passing on knowledge, a gift that grows in value the more you share it."),
    "Betelgeuse": ("the Shoulder of Orion", "Betelgeuse is associated with success that arrives without a struggle when you trust your own momentum."),
    "Canopus": ("the Navigator's Star", "Canopus is associated with guidance and long journeys, the ability to lead others through unfamiliar territory."),
    "Zubenelgenubi": ("the Southern Claw", "Zuben Elgenubi is associated with social reform and the desire to make an exchange fair for everyone."),
    "Zubeneschamali": ("the Northern Claw", "Zuben Eschamali is associated with ambition and a strong drive toward power, best used to build authority over your own choices."),
    "Scheat": ("the Shin of the Horse", "Scheat is associated with free thinking and a love of learning, the courage to follow an unusual idea."),
    "Markab": ("the Saddle of the Horse", "Markab is associated with steadiness and the ability to carry a vision until it becomes real."),
    "Alphard": ("the Heart of the Hydra", "Alphard is associated with passion and depth. It asks you to choose where your intensity goes."),
    "Denebola": ("the Tail of the Lion", "Denebola is associated with going against the grain. It asks you to stand by your choices without needing everyone's approval."),
    "Vindemiatrix": ("the Grape Gatherer", "Vindemiatrix is associated with gathering the harvest at the right time. It asks you not to wait for perfect before you collect what you've earned."),
    "Achernar": ("the End of the River", "Achernar is associated with success through faith and a generous view of life."),
    "Capella": ("the Little She-Goat", "Capella is associated with curiosity and a love of learning that never really stops."),
    "Altair": ("the Eagle", "Altair is associated with bold action and the courage to go after something big."),
    "Hamal": ("the Ram's Head", "Hamal is associated with independence and pioneering, with a caution against becoming headstrong."),
    "Alpheratz": ("the Navel of the Horse", "Alpheratz is associated with freedom and movement, and with a talent for getting things started."),
    "Deneb Adige": ("the Tail of the Swan", "Deneb Adige is associated with intelligence, artistry, and a connection with something larger than material ambition."),
}
STAR_LINE = "Your {pt} is joined by the fixed star {star}, {epithet}, within {orb}. {txt}"
STAR_ALSO = "{star} also sits close to your {pt}, which makes its message even harder to ignore."

# --------------------------------------------------------------------------------------
# Thresholds ahead
# --------------------------------------------------------------------------------------
THRESH_INTRO = ("Your birth chart shows the foundation, and transits show when that foundation gets activated. As planets move across the "
                "sensitive points in your chart, they can open a new threshold, a stretch of time when an old way of handling something stops "
                "working and a new one becomes possible. These aren't predictions of specific events. They're windows for working with your "
                "chart differently over the next twelve months.")
RECENT_JUPITER = ("You may have just come through one of them. In the past year or so, Jupiter crossed your {names}. If something began "
                  "for you during that time, an idea, a role, or a new sense of what you're worth, the transits ahead are about giving it structure.")
QUIET_YEAR = ("Your next twelve months are quieter than most where money is concerned, with no slow planet pressing hard on your core "
              "financial points. Quiet years are building years. Use this one to set up the structures you'll be glad to have later.")
VERB = {("jupiter", "conj"): "Reaches", ("jupiter", "soft"): "Supports", ("jupiter", "hard"): "Stretches",
        ("saturn", "conj"): "Settles Onto", ("saturn", "soft"): "Steadies", ("saturn", "hard"): "Tests",
        ("uranus", "conj"): "Awakens", ("uranus", "hard"): "Shakes Up", ("neptune", "conj"): "Softens",
        ("neptune", "hard"): "Blurs", ("pluto", "conj"): "Transforms", ("pluto", "hard"): "Pressures"}
TRANSIT_CORE = {
    ("jupiter", "conj"): "Jupiter brings growth, opportunity, and a wider view to whatever it touches, and it's one of the warmer thresholds a chart can have.",
    ("jupiter", "soft"): "Jupiter's supportive aspects are easy to miss because nothing feels urgent. They're windows where help, timing, and goodwill line up more readily.",
    ("jupiter", "hard"): "Jupiter's tense aspects stretch you. Growth is on offer, and so is the temptation to take on more than you can hold.",
    ("saturn", "conj"): "When Saturn settles onto a point in your chart, it asks for commitment and structure. What you build now is meant to last.",
    ("saturn", "soft"): "Saturn's supportive aspects reward steady effort. Plans made carefully during this window tend to hold.",
    ("saturn", "hard"): "Saturn's squares and oppositions ask whether a structure can hold weight. You may notice where you've been carrying too much, or where income depends too heavily on your personal effort. It can feel like a slowdown, and it's often when you set the boundaries and prices you'll later be grateful for.",
    ("uranus", "conj"): "Uranus brings awakening and sudden change. Something may shift quickly, opening a door you didn't know was there.",
    ("uranus", "hard"): "Uranus in tension brings disruption with a purpose. It can open an unexpected door, change how or where you work, or make it suddenly clear that something has run its course.",
    ("neptune", "conj"): "Neptune brings inspiration and a softer, more intuitive approach. It can also blur details, so let time confirm what's solid.",
    ("neptune", "hard"): "Neptune in tension can blur your picture of what's real. Some opportunities will be exactly what they seem, and others will be more hopeful than real. Get the details in writing.",
    ("pluto", "conj"): "Pluto brings deep transformation. It strips away what no longer works so something truer can take its place.",
    ("pluto", "hard"): "Pluto in tension brings pressure to change at the root. Power around money is likely to be part of the story.",
}
TARGET_MEANING = {
    "second": "the planet that rules your income",
    "career": "the ruler of your Midheaven and career",
    "fortune": "the ruler of your Part of Fortune",
    "asc": "the way you meet the world",
    "mc": "your career and public reputation",
    "ic": "home, family, and your private foundation",
    "sun": "your identity and confidence",
    "moon": "your sense of security",
    "venus": "what you value and how you attract",
    "jupiter": "your capacity for growth",
    "saturn": "your long-term structures",
    "assets": "what you accumulate and keep",
    "point_fortune": "where opportunity meets you",
}
CYCLE = {
    ("saturn", 0): ("Your Saturn Return", "Saturn is returning to where it was when you were born, one of the most important thresholds of adult life. It asks what you're building and whether it's truly yours. Structures that fit you get stronger. Ones that don't, start to feel impossible to keep."),
    ("saturn", 180): ("Your Saturn Opposition", "Saturn is opposing its position at your birth, the halfway point of its cycle. What you've built gets tested from the outside. It's a natural moment to rebalance commitments, especially around money and the work you're building to last."),
    ("saturn", 90): ("Your Saturn Square", "Saturn is squaring its position at your birth, a checkpoint in its cycle. Something you've been building asks for adjustment before it can carry more weight."),
    ("jupiter", 0): ("Your Jupiter Return", "Jupiter is returning to where it was when you were born, opening a new twelve-year cycle of growth. It's a good time to plant something you want to grow for years."),
    ("jupiter", 180): ("Your Jupiter Opposition", "Jupiter is opposite its birth position, the peak of its cycle. What you planted around six years ago may be showing what it can become."),
    ("jupiter", 90): ("Your Jupiter Square", "Jupiter is squaring its own position, a natural checkpoint for whether your growth is actually supporting your life."),
}
INGRESS = {
    2: "{P} crosses into your second house of income, beginning a new chapter for how you earn and what you're willing to accept for your work.",
    5: "{P} crosses into your fifth house, bringing its energy into creativity, pleasure, and the things you make.",
    8: "{P} crosses into your eighth house, turning attention toward debt, shared resources, and the agreements you've made with others.",
    11: "{P} sits on the cusp of your eleventh house, bringing its energy into networks, friendships, and the support around your work.",
}
INGRESS_PLANET = {
    "saturn": "Saturn asks for commitment and clear structure there.",
    "uranus": "Uranus brings change and fresh ideas there, sometimes suddenly.",
    "neptune": "Neptune brings inspiration there, and it can blur your picture of what's real, so some opportunities will be exactly what they seem and others more hopeful than real.",
    "pluto": "Pluto brings deep restructuring there over a long stretch of time.",
    "jupiter": "Jupiter brings growth and opportunity there.",
}
PLUTO_8TH = ("Pluto has been moving through your eighth house of shared resources for several years. It can restructure how you handle debt, "
             "shared assets, and financial entanglements, often by bringing what's hidden in an arrangement to the surface so it can be addressed honestly.")
ECLIPSE_LINE = ("The {kind} eclipse of {date} falls on your {pt}, which adds weight to this window and can mark a turning point around {topic}.")
ECLIPSE_TOPIC = {"mc": "career and public direction", "ic": "home and family", "asc": "how you show up for yourself",
                 "dsc": "partners and clients", "fortune": "opportunity", "ruler": "the planet that guides your income",
                 "cruler": "the planet that guides your career"}
PROFECTION = {
    1: "a first house year, a year about you, your body, and your own initiative",
    2: "a second house year, a year centered on income, possessions, and your sense of worth",
    3: "a third house year, a year of communication, learning, and everyday connections",
    4: "a fourth house year, a year centered on home, family, and foundations",
    5: "a fifth house year, a year of creativity, pleasure, and what you make",
    6: "a sixth house year, a year of work, routines, and health",
    7: "a seventh house year, a year centered on partners, clients, and agreements",
    8: "an eighth house year, a year centered on shared resources, debt, and commitments made with others",
    9: "a ninth house year, a year of learning, teaching, travel, and belief",
    10: "a tenth house year, a year centered on career and reputation",
    11: "an eleventh house year, a year of networks, community, and gains",
    12: "a twelfth house year, a year of rest, reflection, and work behind the scenes",
}
PROF_LINE = ("This is also {lordname} year for you in another way. At {age}, your annual profection has reached your {ord} house, so you're in {desc}. "
             "The lord of your year is {Lord}, which runs from your last birthday until {until}.")
PROF_LORD_ACTIVE = " {Lord} is also one of the planets making a major transit this year, so its message is doubled."

# --------------------------------------------------------------------------------------
# Overall and Final Thoughts
# --------------------------------------------------------------------------------------
STRENGTH = {
    "domicile": "{P} is dignified in its own sign",
    "exaltation": "{P} is exalted",
    "angular": "{P} is angular and able to act",
    "fortune_close": "your Part of Fortune is closely tied to its ruler",
    "jupiter_strong": "Jupiter is strong in your chart",
    "benefic": "{P} receives help from {B}",
    "same_ruler": "one planet links your identity, your income, and your opportunities",
}
COMPLICATION = {
    "detriment": "{P} works from a sign that doesn't come naturally to it",
    "fall": "{P} is in its fall",
    "combust": "{P} sits close enough to the Sun that its own needs can get lost",
    "cadent12": "{P} works from the hidden twelfth house",
    "malefic": "{P} carries tension with {M}",
    "retro": "{P} turns inward before it moves outward",
}
OVERALL_CLOSE = {
    "personal": "Taken together, your chart builds wealth best through personal value delivered in a sustainable form. Earning may not be the hardest part for you. Keeping enough of yourself, and enough of what you earn, is where the real growth lives.",
    "partner": "Taken together, your chart builds wealth best through people. The right partners, clients, and agreements multiply what you could do alone, and the wrong ones cost more than money.",
    "career": "Taken together, your chart builds wealth best through a reputation you're proud of. When what you're known for and what you're paid for line up, your money story gets simpler.",
    "creative": "Taken together, your chart builds wealth best through what you make. Creative work that you own and develop over time is one of your strongest long-term assets.",
    "quiet": "Taken together, your chart builds wealth best through work that doesn't need an audience to matter. Name it, price it, and protect the time it needs.",
    "knowledge": "Taken together, your chart builds wealth best through knowledge you've earned and shared. Teaching, writing, and guiding others can carry your value further than your hours ever could.",
    "steady": "Taken together, your chart builds wealth best through steady effort and good systems. Small, consistent choices compound in your chart more than big gambles ever will.",
}
FINAL_OPEN = {
    "moon": "There's something tender about the way your chart connects money with care. You don't separate what you do from who you are very easily, and you don't have to. The work is in letting that care include you.",
    "sun": "There's something bright about the way your chart connects money with identity. You're meant to be seen in your work. The work is in letting your worth stay steady when the numbers move.",
    "mercury": "There's something clever about the way your chart connects money with your mind. Your ideas are valuable. The work is in trusting them enough to charge for them.",
    "venus": "There's something graceful about the way your chart connects money with relationships and beauty. People feel good around what you offer. The work is in making sure you feel good about the exchange too.",
    "mars": "There's something brave about the way your chart connects money with effort. You know how to go after what you want. The work is in letting rest be part of the plan.",
    "jupiter": "There's something generous about the way your chart connects money with growth. You trust that there's more out there, and often there is. The work is in giving that faith a structure.",
    "saturn": "There's something steady about the way your chart connects money with time. What you build tends to last. The work is in letting yourself feel secure before everything is finished.",
}
FINAL_LINES = {
    "overgive": "You can be generous without being the discount.",
    "build": "You can build something that supports you without becoming the only thing holding it up.",
    "quiet": "And you can let your work grow without giving up the quiet that makes it good.",
    "seen": "You can be seen for your work without needing every room to approve of it.",
    "partner": "You can let other people help without losing what's yours.",
    "steady": "You can move slowly and still arrive.",
    "trust": "And you can trust your instincts about money, because they've been right more often than you give them credit for.",
}
FINAL_TRANSITS = "The transits ahead ask for {asks}. {lines} You don't need to rush any of it."
TRANSIT_ASK = {"saturn": ("structure", "Saturn wants your foundation strong enough to hold the next chapter."),
               "uranus": ("room for change", "Uranus wants room for what's changing."),
               "neptune": ("honesty", "Neptune wants you to see clearly before you commit."),
               "pluto": ("courage", "Pluto wants what's no longer true to fall away."),
               "jupiter": ("a little faith", "Jupiter wants to bring something you love closer to you.")}

OPENING = ("Thank you for letting me spend time with a bit of your wealth story. {stand} {close}")
STAND = {
    "concentrated": ("The first thing that stands out in your chart is how much of it gathers in one place. Your {roles} all answer to "
                     "{R}, and {R} sits in {S} in your {ord} house{with_}. Very little about money in your chart happens somewhere far away "
                     "from you. It begins with who you are, what you notice, and what you decide to do with it."),
    "stellium": ("The first thing that stands out in your chart is the crowd in your second house. {names} all sit in the house of income "
                 "and worth, so money is never a side topic for you. It's one of the main stages of your life."),
    "split": ("The first thing that stands out in your chart is the conversation between two planets. {R} rules your income from {S} in your "
              "{ord} house, while {C} guides your career from {CS} in your {cord} house. Much of your wealth story is about how those two "
              "learn to work together."),
}
OPENING_CLOSE = ("That's where we'll begin. From there we'll look at your Part of Fortune, what can block the flow, your Midheaven, the houses "
                 "that add creativity, shared resources, and support, and the transits opening new thresholds over the next year.")
CONCENTRATED_NOTE = ("That concentration is a strength, and it comes with a responsibility. When one planet carries this much of the story, its "
                     "condition shapes nearly everything around it, so I'll keep returning to it as we go.")

SIGNOFF = "Wishing you the best on your journey.\nWith Love & Light,\nTiff"
DISCLAIMER = ("This reading is based on my own research, my orb-based methodology, and my intuitive abilities. It uses the tropical zodiac, "
              "Placidus houses, and the True Node, calculated with the Swiss Ephemeris. It is offered for reflection and personal growth and "
              "is not financial, legal, medical, or mental health advice. Because this is an instant digital download, all sales are final.")

STAR_PT = {"asc": "Ascendant", "mc": "Midheaven", "ic": "IC", "dsc": "Descendant", "fortune": "Part of Fortune",
           "sun": "Sun", "moon": "Moon"}
STAR_NAME = {"Zubenelgenubi": "Zuben Elgenubi", "Zubeneschamali": "Zuben Eschamali"}

DIGNITY_SHORT = {
    "domicile": "That's its own sign, which gives it real strength and plenty to draw from.",
    "exaltation": "That's its sign of exaltation, one of its most honored positions.",
    "detriment": "That's its sign of detriment, so it works in a language that isn't its first.",
    "fall": "That's its sign of fall, which can make it push too hard or hold back at the wrong moment.",
}

ECLIPSE_PAST = ("The {kind} eclipse of {date} landed on your {pt}, and its story around {topic} is still unfolding through this window.")

# --------------------------------------------------------------------------------------
# Where to Go From Here (links at the end of the reading)
# --------------------------------------------------------------------------------------
SHOP = "https://sagereality11.com/shop/"
CALC = "https://sagereality11.com/astrology-calculators/"
NEXT_INTRO = ("If you'd like to keep going, these are the pieces I'd reach for next with your chart. Each one picks up a thread "
              "from your Wealth Story and follows it further.")
OFFER = {
    "timing": ("What's Happening to Me Right Now? Your Personal Timing Reading", SHOP + "personal-timing-reading/",
               "Every major transit moving through your chart right now, by sign and house, where you are in its timing, and how to move through it. It's the natural next step after The Thresholds Ahead."),
    "manifest": ("When Are My Best Days to Manifest? Your Personal Manifestation Map", SHOP + "personal-manifestation-map/",
                 "Twelve months of your personal power days and pause days, so you know when to launch, raise your prices, or ask for what you're worth."),
    "karmic": ("Your Karmic Contract Reading", SHOP + "karmic-contract-reading-report/",
               "Your nodes, Saturn, and Chiron in full. If The Pattern You're Learning to Change landed for you, this is where that story goes deeper."),
    "degree": ("What Do the Exact Degrees in My Chart Say About Me? Your Degree Reading", SHOP + "degree-reading/",
               "The meaning behind the exact degree and minute of every placement in your money story, including your Part of Fortune and the ruler of your income."),
    "transit_free": ("Free Calculator: Why Is Everything Changing Right Now?", CALC + "why-is-everything-changing-right-now/",
                     "A free look at the transits, eclipses, and life chapters active in your chart today."),
    "hub": ("All of My Free Astrology Calculators", CALC,
            "Every free tool on Sage Reality 11, each one starting with a question you might be asking right now."),
}
ESSENCE = {
    "Aries": "the-essence-of-aries-through-every-house", "Taurus": "the-essence-of-taurus-through-every-house",
    "Gemini": "the-essence-of-gemini-through-every-house", "Cancer": "the-essence-of-cancer-through-every-house",
    "Leo": "the-essence-of-leo-through-every-house", "Virgo": "the-essence-of-virgo-through-every-house",
    "Libra": "the-essence-of-libra-through-every-house", "Scorpio": "the-essence-of-scorpio-through-every-house",
    "Sagittarius": "the-essence-of-sagittarius-through-every-house", "Capricorn": "the-essence-of-capricorn-through-every-house",
    "Aquarius": "the-essence-of-aquarius-through-every-house", "Pisces": "the-essence-of-pisces-through-every-house",
}
ESSENCE_WHY = ("{sign} rules the house of your income, and this guide walks through {sign} in every house and with every planet, "
               "with the lower and higher octave of each, so you can see that energy everywhere it lives in your chart.")
STAR_GUIDE = {
    "Regulus": ("Regulus Fixed Star Guide", "regulus-fixed-star-guide-royal-star-of-persia-fame-power-and-soul-legacy"),
    "Aldebaran": ("Aldebaran Fixed Star Guide", "aldebaran-fixed-star-guide-royal-star-of-integrity-and-success"),
    "Antares": ("Antares Fixed Star Guide", "antares-fixed-star-guide-royal-star-of-the-warriors-heart"),
    "Fomalhaut": ("Fomalhaut Fixed Star Guide", "fomalhaut-fixed-star-guide-the-royal-star-of-the-sacred-dream"),
    "Algol": ("Algol Fixed Star Guide", "algol-fixed-star-guide-reclaiming-the-medusa-gaze"),
    "Alpheratz": ("Alpheratz Fixed Star Guide", "alpheratz-fixed-star-guide-unchained"),
}
STAR_GUIDE_WHY = ("{star} sits on your {pt}, and this guide goes into its myth, what it means on every planet, angle, and house, "
                  "and how to live its gift without falling into its test.")
