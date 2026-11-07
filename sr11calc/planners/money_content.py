ORD = {1:"1st",2:"2nd",3:"3rd",4:"4th",5:"5th",6:"6th",7:"7th",8:"8th",9:"9th",10:"10th",11:"11th",12:"12th"}

# how each house shapes money (used for 2nd ruler, Venus, Jupiter, Lord of the Year placements)
MONEY_HOUSE = {
 1:"your own name, presence and personal effort. Money tends to follow you when you put yourself forward and let people see who you are.",
 2:"your own resources, skills and values. You build wealth by valuing what you already have and growing it steadily.",
 3:"communication, writing, teaching, sales and your local network. Your words and ideas are part of how money reaches you.",
 4:"home, family, real estate and roots. Property, family resources or work you do from home can be part of your wealth story.",
 5:"creativity, joy, self-expression and taking smart risks. Money flows more easily when your work feels like play.",
 6:"daily work, service, skill and routine. Steady effort, health and the systems you build are where abundance grows for you.",
 7:"partnerships, clients and one-on-one work. Other people, contracts and collaborations are often the doorway to your income.",
 8:"shared money, investments, other people's resources and deep transformation. Wealth can grow through partners, clients, investments or inheritance.",
 9:"teaching, travel, publishing, higher learning and faith. Sharing your knowledge and widening your world opens money doors.",
 10:"career, reputation and public visibility. Being seen and known for your work is a big part of your wealth path.",
 11:"community, networks, friends, groups and long-term goals. Your audience and the people who believe in you help money grow.",
 12:"behind-the-scenes work, spiritual and healing work, rest and intuition. Some of your best money comes from quieter, private or soul-led work.",
}
# how each sign earns or spends (used for 2nd house sign and MC sign)
MONEY_SIGN = {
 "Aries":"You make money by taking initiative, starting things and moving fast. Watch impulsive spending.",
 "Taurus":"You build money slowly and steadily, and you value quality, comfort and security. Patience is your superpower.",
 "Gemini":"You earn through ideas, communication and variety, and more than one income stream suits you.",
 "Cancer":"You earn through care, nurturing and emotional connection, and you feel safest with savings to fall back on. Money and feelings are closely linked for you.",
 "Leo":"You earn by shining, creating and leading from the heart. Generosity is a gift, as long as you include yourself.",
 "Virgo":"You earn through skill, service and doing things well. Systems and budgets give you peace.",
 "Libra":"You earn through partnership, beauty, balance and fairness. Collaboration often pays well for you.",
 "Scorpio":"You earn through depth, research, transformation and other people's resources. Trust and control are your money lessons.",
 "Sagittarius":"You earn through teaching, travel, belief and big vision. Faith in yourself expands your income, as long as you don't overextend.",
 "Capricorn":"You earn through structure, ambition and patience. You build wealth that lasts, one step at a time.",
 "Aquarius":"You earn through originality, technology, community and doing things your own way.",
 "Pisces":"You earn through creativity, intuition, compassion and spiritual work. Boundaries around money keep your gifts protected.",
}

PROF_HOUSE = {
 1:"This is a 1st house year, a fresh start centered on you. Money grows when you invest in yourself, your image and your own projects.",
 2:"This is a 2nd house year, and it is all about money. Income, savings, self-worth and what you value take center stage. It is a strong year to build financial security.",
 3:"This is a 3rd house year, focused on communication, learning, writing and local connections. Money may come through what you say, teach, write or sell.",
 4:"This is a 4th house year, focused on home, family and foundations. Real estate, home expenses or family money may be a big theme.",
 5:"This is a 5th house year, focused on creativity, joy and smart risk. Creative work can pay, but keep speculation in check.",
 6:"This is a 6th house year, focused on daily work, health and systems. Improving your routines and workflow improves your income.",
 7:"This is a 7th house year, focused on partnerships and clients. Contracts, collaborations and one-on-one work shape your money.",
 8:"This is an 8th house year, focused on shared money, debt, taxes, investments and deep change. It is a powerful year to clear debt, renegotiate and transform your relationship with money.",
 9:"This is a 9th house year, focused on growth, teaching, travel and big-picture vision. Expanding your knowledge or reach can expand your income.",
 10:"This is a 10th house year, focused on career and reputation. Visibility, promotions and stepping into leadership are highlighted.",
 11:"This is an 11th house year, focused on community, networks and long-term goals. Your audience, friends and groups support your money growth.",
 12:"This is a 12th house year, a quieter year of closure, rest and preparation. Tie up loose ends and plan before the new cycle begins.",
}

# transit text pieces
POINT_MEANING = {
 "Venus":"your natal Venus, the planet of money, value and what you attract",
 "Jupiter":"your natal Jupiter, the planet of growth, luck and abundance",
 "Midheaven":"your Midheaven, the point of career and public reputation",
 "Moon":"your natal Moon, the ruler of your 2nd house of money",
 "Sun":"your natal Sun, the ruler of your 2nd house of money",
 "Mercury":"your natal Mercury, the ruler of your 2nd house of money",
 "Mars":"your natal Mars, the ruler of your 2nd house of money",
 "Saturn":"your natal Saturn, the ruler of your 2nd house of money",
}
PLANET_ASPECT = {
 ("Jupiter",True):"Jupiter brings expansion, opportunity and generosity here. This is one of the best money transits you can have.",
 ("Jupiter",False):"Jupiter expands whatever it touches, so opportunity is real, but so is overspending and saying yes to too much.",
 ("Saturn",True):"Saturn rewards steady effort here. Long-term plans, budgets and commitments made now tend to last.",
 ("Saturn",False):"Saturn tests this part of your money life. Expect delays or more responsibility, and build structure instead of forcing results.",
 ("Mars",True):"Mars gives you drive and courage to go after money. It is a good time to take action and ask for what you want.",
 ("Mars",False):"Mars can bring friction, impulse buys or money conflicts. Channel the energy into effort rather than arguments.",
 ("Venus",True):"Venus brings ease, attraction and pleasant money moments. Good for sales, pricing, negotiating and treating yourself wisely.",
 ("Venus",False):"Venus asks you to check spending and what you are valuing. Small tensions around money or relationships may show up.",
 ("Sun",True):"The Sun shines a light here, bringing attention and confidence. A good few days to be seen and make your case.",
 ("Sun",False):"The Sun highlights a tension point, showing you where your money or career needs attention.",
}
INGRESS = {
 "Sun":"The Sun moves into your {h} house for about a month, putting the spotlight on {k}.",
 "Mercury":"Mercury moves into your {h} house, bringing conversations, paperwork and planning around {k}.",
 "Venus":"Venus moves into your {h} house, sweetening {k} and making it easier to attract money there.",
 "Mars":"Mars moves into your {h} house, bringing energy, drive and some urgency to {k}.",
 "Jupiter":"Jupiter moves into your {h} house, opening a year of growth in {k}.",
 "Saturn":"Saturn moves into your {h} house, beginning a longer season of building and responsibility in {k}.",
}
HOUSE_KEY = {
 1:"you, your image and your personal projects", 2:"your income, savings and self-worth", 3:"your communication, sales and local network",
 4:"home, family and property", 5:"creativity, fun and smart risk", 6:"your daily work, health and systems",
 7:"partners, clients and contracts", 8:"shared money, debt, taxes and investments", 9:"teaching, travel, publishing and growth",
 10:"your career, reputation and visibility", 11:"your community, audience and long-term goals", 12:"rest, closure and behind-the-scenes work",
}
STATION = {
 ("Mercury","retrograde"):"Mercury stations retrograde in your {h} house. For about three weeks, review, revise and reconnect instead of signing new contracts, launching or making big purchases if you can wait. Back up your files and double-check every detail involving {k}.",
 ("Mercury","direct"):"Mercury stations direct in your {h} house. Things start moving again, though give it a few days before signing or launching.",
 ("Venus","retrograde"):"Venus stations retrograde in your {h} house. Revisit what you value and how you price yourself, and hold off on big purchases, rebrands or new financial partnerships.",
 ("Venus","direct"):"Venus stations direct in your {h} house. Money matters and decisions about value can move forward again.",
 ("Mars","retrograde"):"Mars stations retrograde in your {h} house. Energy turns inward. Finish what you started rather than launching something new, and watch for frustration around {k}.",
 ("Mars","direct"):"Mars stations direct in your {h} house. Your drive returns and it gets easier to push forward with {k}.",
 ("Jupiter","retrograde"):"Jupiter stations retrograde in your {h} house. Growth turns inward, a good time to review and strengthen what is already working in {k}.",
 ("Jupiter","direct"):"Jupiter stations direct in your {h} house. Growth and opportunity in {k} start moving forward again.",
 ("Saturn","retrograde"):"Saturn stations retrograde in your {h} house. Review your long-term commitments and foundations around {k}.",
 ("Saturn","direct"):"Saturn stations direct in your {h} house. Your hard work around {k} starts gaining traction again.",
}

TIPS = {
 "Jupiter":dict(personal="Say yes to growth, but read the fine print. Put some of any windfall into savings.", business="Expand your reach: pitch, publish, raise your visibility and test a bigger offer."),
 "Saturn":dict(personal="Make a realistic budget and commit to one money habit you can keep all month.", business="Strengthen your systems, pricing and contracts. Slow, steady and professional wins now."),
 "Mars":dict(personal="Channel the energy into earning, not spending. Wait a day before impulse buys.", business="Take bold action: follow up, ask for the sale and go after the client you want."),
 "Venus":dict(personal="Notice what you truly value and spend in line with it. Treat yourself, wisely.", business="Review your pricing, refresh your branding and nurture client relationships."),
 "Sun":dict(personal="Celebrate your wins and be honest about what needs attention.", business="Be visible. Share your work and let people know what you offer."),
 "Mercury":dict(personal="Review subscriptions, bills and accounts. Fix what is outdated.", business="Revisit old leads, update your website and double-check contracts before signing."),
 "Quiet":dict(personal="A quieter money month. Use it to check in, track your spending and plan ahead.", business="Use the calmer energy to plan your next offer and tidy up your systems."),
}

MONEY_MOON = {
 2:("This New Moon in your 2nd house is your money New Moon of the year. Set a clear income or savings intention.", "This Full Moon lights up your 2nd house of income and self-worth. Release money habits and old beliefs about what you deserve."),
 6:("This New Moon in your 6th house is perfect for starting a new work routine or money system.", "This Full Moon in your 6th house shows what in your daily work is draining you. Let go of tasks that do not pay off."),
 8:("This New Moon in your 8th house supports a fresh start with debt, taxes, investments or shared money.", "This Full Moon in your 8th house can reveal hidden costs or bring shared money matters to a head. Clear and release."),
 10:("This New Moon in your 10th house is a strong time to set career intentions and plan your next big move.", "This Full Moon in your 10th house brings recognition or a career turning point. Celebrate what you have built."),
 11:("This New Moon in your 11th house supports growing your audience, network and long-term income goals.", "This Full Moon in your 11th house shows which connections and goals are truly worth your energy."),
}
OTHER_MOON = ("This New Moon falls outside your main money houses, so use it for general planning and intention setting.",
              "This Full Moon falls outside your main money houses, so use it to review and release.")

DAY_GUIDE = [
 ("Green days", "The Moon is growing, Mercury is moving forward, the Moon is not void, and the Moon is either supporting Venus or Jupiter or moving through one of your money houses. Good days to launch, sign, pitch, send invoices, ask for a raise or make a planned purchase."),
 ("Caution days", "Eclipse windows and the days Mercury or Venus change direction. Energy is unpredictable, so avoid big money decisions if you can."),
 ("Void Moon days", "The Moon makes no more major aspects before changing signs for most of the business day. Things started now tend to fizzle out. Great for admin, research and rest."),
 ("Mercury retrograde", "Shown as Rx on your calendar. Review, revise and reconnect. Avoid signing new contracts or making big tech purchases if you can wait."),
]

WELCOME = [
 "Every one of us has a money story written in our birth chart. Where money comes from, how we earn it, what we value, and where our abundance is meant to grow.",
 "But here is what most money planners leave out. The planets keep moving, and as they pass through your chart they open doors, slow things down and point you toward the right timing. This planner was built from your birth chart, so it shows you when those moments are coming for you personally.",
 "Inside you will find your money blueprint, the theme of your money year, your money transits each month, green and caution days on your calendar, and pages to set goals, check in and make big decisions with clear eyes.",
 "Use it for your personal finances, your business, or both. Take what fits and leave the rest.",
]
GOAL_PROMPTS = ["My money goal this month", "One action I will take on a green day", "Progress I made", "What I learned about my money this month"]
CHECKIN = ["Income this month", "Spending this month", "Saved or invested", "Debt paid down"]
CHECKIN_PROMPTS = ["How did I feel about money this month?", "One thing I want to change next month"]
DECISION = ["The decision I am weighing", "What I want and why", "Best case, worst case", "What my transits say about the timing", "My gut says", "My decision and the date I will act"]
