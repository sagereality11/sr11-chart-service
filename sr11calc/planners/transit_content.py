ORD = {1:"1st",2:"2nd",3:"3rd",4:"4th",5:"5th",6:"6th",7:"7th",8:"8th",9:"9th",10:"10th",11:"11th",12:"12th"}
HOUSE_KEY = {
 1:"self, body and identity", 2:"money, values and self-worth", 3:"communication, learning and siblings",
 4:"home, family and roots", 5:"joy, creativity, romance and children", 6:"health, work and daily routines",
 7:"partnership and one-on-one relationships", 8:"intimacy, shared resources and deep change",
 9:"beliefs, travel and higher learning", 10:"career, reputation and public path",
 11:"friends, community and future dreams", 12:"rest, spirituality and the hidden parts of life",
}

PLANET = {
 "Jupiter":"Jupiter brings growth, opportunity, faith and expansion.",
 "Saturn":"Saturn brings lessons, structure, maturity and the kind of hard work that lasts.",
 "Uranus":"Uranus brings sudden change, awakening and the push toward freedom.",
 "Neptune":"Neptune brings dreams, intuition, sensitivity and spiritual opening, and sometimes confusion while the old picture dissolves.",
 "Pluto":"Pluto brings deep transformation, power and rebirth.",
}
POINT = {
 "Sun":"It is touching your Sun, the core of who you are, your vitality and your sense of direction.",
 "Moon":"It is touching your Moon, your emotions, your needs, your home life and how you care for yourself.",
 "Mercury":"It is touching your Mercury, your mind, your voice and how you think, learn and communicate.",
 "Venus":"It is touching your Venus, your love life, your values, your money and what brings you pleasure.",
 "Mars":"It is touching your Mars, your drive, courage, anger and how you go after what you want.",
 "Jupiter":"It is touching your natal Jupiter, your faith, your growth and where luck lives in your chart.",
 "Saturn":"It is touching your natal Saturn, your boundaries, responsibilities and the lessons you came here to master.",
 "Uranus":"It is touching your natal Uranus, the part of you that needs freedom and does things its own way.",
 "Neptune":"It is touching your natal Neptune, your dreams, spirituality and imagination.",
 "Pluto":"It is touching your natal Pluto, your power, your depths and what you are here to transform.",
 "North Node":"It is touching your North Node, the direction your soul is growing toward in this lifetime.",
 "Ascendant":"It is touching your Ascendant, your body, your presence and how you meet the world.",
 "Midheaven":"It is touching your Midheaven, your career, your public path and your legacy.",
}
ASPECT = {
 "conjunct":"A conjunction merges the two energies, so this is a new chapter starting right where it lands.",
 "square":"A square brings friction that pushes you to act. It can feel uncomfortable, but it builds strength.",
 "opposite":"An opposition brings awareness, often through other people or outside events, asking you to find balance.",
 "trine":"A trine brings ease and natural flow. Good things come more easily, so use the support while it is here.",
 "sextile":"A sextile brings opportunity, but it asks you to take a step toward it.",
}
OCTAVE = {
 "Jupiter":("overdoing it, overpromising or expecting things to fall into your lap", "real growth, wisdom and generous faith in yourself"),
 "Saturn":("heaviness, delays, fear or feeling like nothing is working", "maturity, earned success and structures that support you for years"),
 "Uranus":("restlessness, chaos or breaking things just to feel free", "awakening, brave change and living more truthfully"),
 "Neptune":("confusion, escapism, disappointment or blurred boundaries", "deep intuition, compassion, creativity and spiritual trust"),
 "Pluto":("control, power struggles or fear of losing what you have", "rebirth, reclaimed power and letting go of what is ready to die"),
}
WORK = {
 "Jupiter":"Say yes to growth that feels aligned, and stay grounded about what you can truly take on.",
 "Saturn":"Slow down, commit to what matters and do the steady work. What you build now lasts.",
 "Uranus":"Make room for change before it is forced on you. Try something new and loosen your grip on routines that feel like cages.",
 "Neptune":"Trust your intuition, but double-check facts. Protect your energy, rest more and create.",
 "Pluto":"Face what you have been avoiding and let it change you. Seek support for anything heavy.",
}
SPECIAL = {
 ("Saturn","opposite","Saturn"):"This is your Saturn opposition, a halfway check-in on the cycle that began at your Saturn Return. Ask yourself whether the life you have built still fits who you are becoming.",
 ("Uranus","opposite","Uranus"):"This is your Uranus opposition, the famous midlife awakening. It often brings a strong urge to live more authentically and stop postponing the life you want.",
 ("Saturn","conjunct","Saturn"):"This is your Saturn Return, one of the biggest coming-of-age transits in astrology.",
 ("Jupiter","conjunct","Jupiter"):"This is your Jupiter Return, the start of a new twelve-year cycle of growth.",
}
SPECIAL_LINK = {("Saturn","opposite","Saturn"):"sagereality11.com/astrology-calculators/saturn-return-calculator/",
                ("Uranus","opposite","Uranus"):"sagereality11.com/astrology-calculators/uranus-opposition-calculator/"}

FAST = {
 ("Sun",True):"a bright, confident few days", ("Sun",False):"a spotlight on what needs your attention",
 ("Mercury",True):"conversations, ideas and news", ("Mercury",False):"conversations, ideas and news",
 ("Venus",True):"ease, affection and pleasure", ("Venus",False):"a check-in on love, money and what you value",
 ("Mars",True):"energy and courage to act", ("Mars",False):"heat, impatience or conflict, so channel it into action",
}
FAST_POINT = {"Sun":"your sense of self", "Moon":"your feelings and home life", "Mercury":"your thinking and communication",
 "Venus":"love and money", "Mars":"your drive", "Ascendant":"how you show up", "Midheaven":"your career"}

SUN_MONTH = {
 1:"The Sun moves through your 1st house, your personal new year. Focus on yourself, your health and your fresh starts.",
 2:"The Sun moves through your 2nd house, putting money, values and self-worth in the spotlight.",
 3:"The Sun moves through your 3rd house, a busy month for conversations, learning, writing and short trips.",
 4:"The Sun moves through your 4th house, turning your attention to home, family and emotional foundations.",
 5:"The Sun moves through your 5th house, a month for joy, creativity, romance and play.",
 6:"The Sun moves through your 6th house, a good month to organize your work, routines and health.",
 7:"The Sun moves through your 7th house, putting your relationships and partnerships center stage.",
 8:"The Sun moves through your 8th house, a deeper month for intimacy, shared money and transformation.",
 9:"The Sun moves through your 9th house, opening your mind to travel, study and new beliefs.",
 10:"The Sun moves through your 10th house, the most visible month of your year for career and reputation.",
 11:"The Sun moves through your 11th house, a social month for friends, community and future goals.",
 12:"The Sun moves through your 12th house, a quieter month for rest, reflection and closing a chapter before your next new beginning.",
}
STATION = {
 "Mercury":"Mercury stations {d} in your {h} house. {x}",
 "Venus":"Venus stations {d} in your {h} house. {x}",
 "Mars":"Mars stations {d} in your {h} house. {x}",
 "Jupiter":"Jupiter stations {d} in your {h} house. {x}",
 "Saturn":"Saturn stations {d} in your {h} house. {x}",
 "Uranus":"Uranus stations {d} in your {h} house. {x}",
 "Neptune":"Neptune stations {d} in your {h} house. {x}",
 "Pluto":"Pluto stations {d} in your {h} house. {x}",
}
STATION_X = {"retrograde":"Its energy turns inward, a time to review and revisit.", "direct":"Its energy starts moving forward again."}

PLANETS_GUIDE = [
 ("Sun, Mercury, Venus and Mars","The fast movers. Their transits last a few days and show the everyday flavor of your month."),
 ("Jupiter","Growth and opportunity. Its transits last a few weeks to a few months."),
 ("Saturn","Lessons and structure. Its transits can last several months and often shape a whole season of your life."),
 ("Uranus, Neptune and Pluto","The slowest planets. Their transits can last a year or more and mark the biggest turning points."),
]
JOURNAL = ["Which transit did I feel the most this month, and how did it show up?", "What is the Sun lighting up in my life right now?", "What do I want to remember from this month?"]
WELCOME = [
 "The planets never stop moving. As they travel through the sky, they make contact with the planets and points in your birth chart, and those contacts are called transits. They are the timing of your life.",
 "Some transits pass in a day or two. Others stay for months and shape a whole chapter. This planner was built from your birth chart, so it shows you which transits are touching you, when they are exact, which part of your life they are moving through and how to work with them.",
 "Transits are not here to happen to you. They are invitations. Every one of them has a lower octave and a higher octave, and you get to choose how you meet them.",
]

PLANET_V = {
 "Jupiter":["Jupiter brings growth, opportunity, faith and expansion.",
            "Jupiter, the great benefic, opens doors and widens whatever it touches.",
            "With Jupiter comes a sense of possibility and the urge to grow.",
            "Jupiter's visit brings optimism and a bigger view of what is possible."],
 "Saturn":["Saturn brings lessons, structure, maturity and the kind of hard work that lasts.",
           "Saturn asks for commitment, patience and honesty about what is truly working.",
           "With Saturn comes a season of building, testing and growing up in some area of life.",
           "Saturn slows things down so you can see what is solid and what is not."],
 "Uranus":["Uranus brings sudden change, awakening and the push toward freedom.",
           "Uranus shakes things loose so something truer can come through.",
           "With Uranus comes the unexpected, along with a strong need to be yourself."],
 "Neptune":["Neptune brings dreams, intuition, sensitivity and spiritual opening, and sometimes confusion while the old picture dissolves.",
            "Neptune softens the edges of life, opening your heart and your intuition.",
            "With Neptune comes a dreamy, sensitive season where what you thought was certain can blur."],
 "Pluto":["Pluto brings deep transformation, power and rebirth.",
          "Pluto works slowly and deeply, clearing away what can no longer come with you."],
}
WORK_V = {
 "Jupiter":["Say yes to growth that feels aligned, and stay grounded about what you can truly take on.",
            "Pick one area to grow on purpose, and let the rest wait.",
            "Share your gifts generously, and keep an eye on overcommitting.",
            "Take the opportunity, read the fine print and keep your feet on the ground."],
 "Saturn":["Slow down, commit to what matters and do the steady work. What you build now lasts.",
           "Set one clear boundary and one realistic goal, and keep showing up for both.",
           "Be patient with yourself. Saturn rewards consistency far more than speed.",
           "Look honestly at what is not working and rebuild it on stronger ground."],
 "Uranus":["Make room for change before it is forced on you. Try something new and loosen your grip on routines that feel like cages.",
           "Experiment. Small brave changes now keep big disruptions from building up.",
           "Notice where you feel restless, and ask what freedom you are really craving."],
 "Neptune":["Trust your intuition, but double-check facts. Protect your energy, rest more and create.",
            "Make art, pray, meditate or journal, and give yourself more quiet than usual.",
            "Keep your boundaries clear and your feet on the ground while your spirit opens."],
 "Pluto":["Face what you have been avoiding and let it change you. Seek support for anything heavy.",
          "Name where you have given your power away, and take one step to reclaim it."],
}
