"""Text library for Your Shared Soul Journey (two-person monthly forecast), in Tiff's voice.

Third person lines use {N} (the other person's name), {pos} (his/her/their), {obj} (him/her/them).
"""

PRON = {"she": ("she", "her", "her", "herself"), "he": ("he", "him", "his", "himself"),
        "they": ("they", "them", "their", "themselves")}

# what a transit does to the other person's planet, written about them (cls: conj, hard, soft)
B_TEXT = {
    ("jupiter", "conj"): "For {N}, Jupiter on {pos} {np} opens a door around {ess}. This is a growth moment, and life may hand {obj} more room than usual.",
    ("jupiter", "hard"): "For {N}, Jupiter's {asp} to {pos} {np} can bring restlessness around {ess}, a sense that there's more out there and a need to choose which growth is really {pos}.",
    ("jupiter", "soft"): "For {N}, Jupiter's {asp} to {pos} {np} brings support and ease to {ess}. Good timing is on {pos} side.",
    ("saturn", "conj"): "For {N}, Saturn on {pos} {np} is a checkpoint for {ess}. It can feel heavy, and it's also where {pos} maturity is being built.",
    ("saturn", "hard"): "For {N}, Saturn's {asp} to {pos} {np} tests {ess}. Old ways of handling things may stop working, and that pressure is asking {obj} to grow up into a new level of ownership.",
    ("saturn", "soft"): "For {N}, Saturn's {asp} to {pos} {np} brings steady, practical support to {ess}. Effort {N} puts in now tends to hold.",
    ("uranus", "conj"): "For {N}, Uranus on {pos} {np} is an awakening around {ess}. Something that felt fixed can shift suddenly, and {pos} need for freedom gets louder.",
    ("uranus", "hard"): "For {N}, Uranus's {asp} to {pos} {np} shakes up {ess}. Expect some restlessness and some sudden insight about what no longer fits.",
    ("uranus", "soft"): "For {N}, Uranus's {asp} to {pos} {np} brings fresh ideas and welcome change to {ess}.",
    ("neptune", "conj"): "For {N}, Neptune on {pos} {np} softens old definitions of {ess}. Uncertainty here is part of the process, not a problem to fix.",
    ("neptune", "hard"): "For {N}, Neptune's {asp} to {pos} {np} can make {ess} feel foggy. It's a time to trust intuition and avoid forcing clarity.",
    ("neptune", "soft"): "For {N}, Neptune's {asp} to {pos} {np} brings inspiration and spiritual support to {ess}.",
    ("pluto", "conj"): "For {N}, Pluto on {pos} {np} is a deep renewal of {ess}. Something old is ending so something truer can grow.",
    ("pluto", "hard"): "For {N}, Pluto's {asp} to {pos} {np} brings pressure to transform {ess}, and power dynamics may come into view.",
    ("pluto", "soft"): "For {N}, Pluto's {asp} to {pos} {np} brings quiet strength to {ess}.",
    ("chiron", "conj"): "For {N}, Chiron on {pos} {np} touches an old tender place around {ess}. What comes up now is ready to be understood.",
    ("chiron", "hard"): "For {N}, Chiron's {asp} to {pos} {np} can stir an old insecurity around {ess}. It's information, not a verdict.",
    ("chiron", "soft"): "For {N}, Chiron's {asp} to {pos} {np} supports gentle healing around {ess}.",
    ("north_node", "conj"): "For {N}, the North Node on {pos} {np} points {pos} growth toward {ess}.",
    ("north_node", "hard"): "For {N}, the nodes crossing {pos} {np} put {ess} at a crossroads between old patterns and new growth.",
    ("north_node", "soft"): "For {N}, the nodes support {pos} {np}, bringing timely chances around {ess}.",
}
A_TEXT = {
    ("jupiter", "conj"): "For you, Jupiter on your {np} opens a door around {ess}. Life may hand you more room than usual.",
    ("jupiter", "hard"): "For you, Jupiter's {asp} to your {np} can bring restlessness around {ess} and a need to choose which growth is really yours.",
    ("jupiter", "soft"): "For you, Jupiter's {asp} to your {np} brings support and ease to {ess}.",
    ("saturn", "conj"): "For you, Saturn on your {np} is a checkpoint for {ess}. It asks what is real and what you're truly willing to commit to.",
    ("saturn", "hard"): "For you, Saturn's {asp} to your {np} tests {ess}. Old ways of handling things may stop working, and the pressure is asking for clearer priorities and kinder boundaries.",
    ("saturn", "soft"): "For you, Saturn's {asp} to your {np} brings steady support to {ess}.",
    ("uranus", "conj"): "For you, Uranus on your {np} is an awakening around {ess}. The part of you that has waited for permission to change may stop waiting.",
    ("uranus", "hard"): "For you, Uranus's {asp} to your {np} shakes up {ess} and shows you what no longer fits.",
    ("uranus", "soft"): "For you, Uranus's {asp} to your {np} brings fresh ideas and welcome change to {ess}.",
    ("neptune", "conj"): "For you, Neptune on your {np} dissolves old definitions of {ess}. You don't need every answer yet.",
    ("neptune", "hard"): "For you, Neptune's {asp} to your {np} can make {ess} feel uncertain. Let the fog teach you what you truly want.",
    ("neptune", "soft"): "For you, Neptune's {asp} to your {np} brings inspiration to {ess}.",
    ("pluto", "conj"): "For you, Pluto on your {np} is a deep renewal of {ess}.",
    ("pluto", "hard"): "For you, Pluto's {asp} to your {np} brings up power, control and what you hold on to around {ess}.",
    ("pluto", "soft"): "For you, Pluto's {asp} to your {np} brings quiet strength to {ess}.",
    ("chiron", "conj"): "For you, Chiron on your {np} touches an old tender place around {ess}.",
    ("chiron", "hard"): "For you, Chiron's {asp} to your {np} opens a healing thread around {ess}, often through the people closest to you.",
    ("chiron", "soft"): "For you, Chiron's {asp} to your {np} supports gentle healing around {ess}.",
    ("north_node", "conj"): "For you, the North Node on your {np} points your growth toward {ess}.",
    ("north_node", "hard"): "For you, the nodes crossing your {np} put {ess} at a crossroads.",
    ("north_node", "soft"): "For you, the nodes support your {np} and bring timely chances around {ess}.",
}
TOGETHER = {
    "jupiter": "Together, this is a chance to encourage each other's growth without needing it to look the same. Generosity works best here when it builds the other person's strength rather than replacing it.",
    "saturn": "Together, this asks for clear, fair agreements. Responsibilities that have drifted onto the wrong shoulders can be handed back with love, and boundaries can be kind and steady at the same time.",
    "uranus": "Together, this asks you to make room for each other to change. The relationship stays strong when it can hold both of you becoming more fully yourselves.",
    "neptune": "Together, this asks for compassion and clarity at once. Say what you mean gently, and don't assume the other person can read what you haven't said.",
    "pluto": "Together, this asks you to notice where control or fear has crept into the relationship, and to choose trust instead.",
    "chiron": "Together, this is a chance to heal how you talk and listen. The change starts with how you speak to each other, not with either of you winning the point.",
    "north_node": "Together, this asks you to honor the history between you while letting the relationship move in a new direction.",
}
PAIR_OCT = {
    "jupiter": [("Overpromising or overgiving", "Generosity that builds strength"), ("Expecting the other to grow your way", "Cheering each other's own path"), ("Taking on too much together", "Choosing what truly matters")],
    "saturn": [("Carrying what belongs to the other person", "Handing back what is theirs, with love"), ("Rules without warmth", "Boundaries that are kind and steady"), ("Resentment that goes unspoken", "Clear, fair agreements"), ("Holding on to old roles", "Letting the roles grow up")],
    "uranus": [("Sudden distance or reacting fast", "Freedom chosen with care"), ("Fearing the other's changes", "Making room for each other to change"), ("Rebelling against each other", "Respecting each other's independence")],
    "neptune": [("Assuming instead of asking", "Asking, then listening"), ("Rescuing or being rescued", "Compassion with boundaries"), ("Avoiding hard truths", "Honesty said gently")],
    "pluto": [("Power struggles", "Shared power and trust"), ("Holding on out of fear", "Letting each other grow"), ("Control disguised as care", "Care that trusts")],
    "chiron": [("Advice that feels like pressure", "Guidance offered lightly"), ("Getting defensive or going quiet", "Listening without correcting"), ("Protecting old wounds", "Healing them together")],
    "north_node": [("Repeating an old family script", "Choosing a new response"), ("Clinging to how things were", "Honoring the past while moving forward")],
}
B_PROMPT = {
    "jupiter": "What kind of growth feels truly mine right now?", "saturn": "What am I ready to take more ownership of?",
    "uranus": "What does freedom look like for me now?", "neptune": "What am I sensing that I haven't said out loud yet?",
    "pluto": "Where am I ready to stand in my own power?", "chiron": "How can I be honest about what I think while owning the choices that are mine?",
    "north_node": "What small step moves me toward my own future?",
}
SOUL_WORK = {
    "jupiter": ["Growing in the direction that is truly yours", "Receiving support without feeling indebted"],
    "saturn": ["Setting down responsibility that has grown too heavy", "Keeping boundaries that are kind and steady"],
    "uranus": ["Making room for your own freedom", "Letting change make your life more honest"],
    "neptune": ["Trusting your intuition", "Giving your dreams a practical home"],
    "pluto": ["Reclaiming your own power", "Letting go of control that comes from fear"],
    "chiron": ["Meeting old hurts with compassion", "Letting yourself be helped"],
    "north_node": ["Choosing a new response to an old pattern", "Taking small steps toward your future"],
}
B_SOUL_WORK = {
    "jupiter": ["Growing in {pos} own direction", "Trusting {pos} own path"],
    "saturn": ["Taking ownership of what is truly {pos}", "Building {pos} own foundation"],
    "uranus": ["Claiming {pos} independence with care", "Trying new ways of living"],
    "neptune": ["Trusting {pos} inner knowing", "Giving {pos} dreams a real form"],
    "pluto": ["Standing in {pos} own power", "Letting old fears go"],
    "chiron": ["Healing old tender places", "Trusting {pos} own judgment"],
    "north_node": ["Following {pos} soul's direction", "Choosing new responses to old patterns"],
}
ASK_EACH = {
    "romantic": ["What do we each need to feel chosen right now?", "Is there anything we expect of each other that we've never said out loud?", "How can we support each other's growth without losing our closeness?"],
    "spouse": ["What do we each need from our marriage in this season?", "Is there an agreement between us that's ready to be updated?", "How can we carry life together without one of us carrying too much?"],
    "mother_son": ["What does a good relationship between a mother and her grown son look like to each of us now?", "Is there anything we expect of each other that we have never said out loud?", "How can we support each other without carrying each other?"],
    "mother_daughter": ["What does a good relationship between a mother and her grown daughter look like to each of us now?", "What do we each wish the other understood about us?", "How can we support each other without carrying each other?"],
    "father_son": ["What does respect look like between us now?", "Is there anything we expect of each other that we have never said out loud?", "How can we support each other without carrying each other?"],
    "father_daughter": ["What does support look like between us now?", "What do we each wish the other understood about us?", "How can we stay close while each of us stays free?"],
    "parent_child": ["What does our relationship need now that it didn't before?", "Is there anything we expect of each other that we've never said out loud?", "How can we support each other without carrying each other?"],
    "siblings": ["What did we each learn from growing up in the same family?", "What do we each wish the other understood about us now?", "How can we be close as the people we've become, not the kids we were?"],
    "grandparent": ["What does each of us most want the other to know?", "What story from our family do we want to carry forward?", "What can we learn from each other right now?"],
    "friends": ["What does this friendship give each of us right now?", "Is there anything we've been holding back from each other?", "How can we support each other's growth, even when it takes us in different directions?"],
    "business": ["What do we each need from this partnership right now?", "Is the way we divide responsibilities still fair?", "What shared vision do we want to recommit to?"],
}
PATTERN = {
    "family": ("The Family Pattern Underneath", "The patterns your family passed down, and the ones you're ready to change.", "Inheritance Is Not Destiny",
               "Emotional patterns can move through families for generations through beliefs, habits, expectations and the ways people respond to uncertainty. In a chart, the Moon, the 4th house, Saturn, Pluto, Chiron and the nodes are where I look for those threads.",
               "A family pattern ends the day someone sees it clearly and chooses something new."),
    "love": ("The Pattern Between You", "The dance you've learned together, and how it's ready to grow.", "Old Patterns, New Choices",
             "Every close relationship develops its own rhythm, the ways each of you reaches for the other, protects yourself and handles conflict. Those patterns often began long before you met, in the families you grew up in.",
             "A relationship grows the moment both people see the pattern and choose something new together."),
    "peer": ("The Dynamic Between You", "How you work together, and what's ready to shift.", "Choosing Your Roles Consciously",
             "Every partnership falls into roles, who leads, who supports, who carries the details and who holds the vision. Roles are useful until they stop fitting the people in them.",
             "A partnership stays alive when both people keep choosing their roles instead of falling into them."),
}
LENS_KIND = {"mother_son": "family", "mother_daughter": "family", "father_son": "family", "father_daughter": "family",
             "parent_child": "family", "siblings": "family", "grandparent": "family", "romantic": "love", "spouse": "love",
             "friends": "peer", "business": "peer"}
LINK_GIFT = {
    0: [("The gift of this thread is how naturally you understand each other here.", "The tender spot is that you can blur together, so it's harder to tell whose feelings or needs are whose."),
        ("Here you often feel what the other feels before a word is said.", "The challenge is remembering that closeness isn't the same as being the same person."),
        ("This is a place of instant recognition between you.", "What needs care is giving each other room to be different here too.")],
    180: [("The gift of this thread is that you each bring what the other is learning to hold.", "The tender spot is when you see in the other person what you haven't yet accepted in yourself, and push against it."),
          ("Each of you carries the other half of something here.", "When it's hard, it's usually because one of you is holding both halves alone."),
          ("This connection balances you, like two ends of the same rope.", "The pull can turn into tug of war when either of you forgets you're holding the same rope.")],
    90: [("The gift of this thread is growth. You challenge each other into becoming more.", "The tender spot is friction, the moments when each of you feels the other is pressing on a sore place."),
         ("This is where you stretch each other.", "It can feel like pressure, and that pressure is often where the relationship does its deepest growing."),
         ("You bring out each other's edges here, in ways that can be uncomfortable and useful at the same time.", "The work is staying curious instead of defensive when that edge shows up.")],
    120: [("The gift of this thread is ease and natural support.", "The tender spot is taking it for granted, because what flows easily can go unnoticed."),
          ("Here, being together feels easy.", "The only risk is forgetting to say out loud how much this support matters.")],
    60: [("The gift of this thread is the support you can offer each other when you choose to.", "The tender spot is letting the opportunity pass because it never forces itself on you."),
         ("This connection opens doors when either of you reaches for it.", "It asks for a little effort, and it gives back far more.")],
}
LUN_INTENT = {
    1: "I let myself be seen as I am now.", 2: "I honor what I truly value.", 3: "I say what I mean with kindness.",
    4: "I create a home that holds who I'm becoming.", 5: "I make room for joy.", 6: "I build daily habits that support who I am becoming.",
    7: "I show up honestly in my relationships.", 8: "I release what was never mine to carry.", 9: "I follow what gives my life meaning.",
    10: "I take steady steps toward the future I want to create.", 11: "I stay connected to my hopes and my people.", 12: "I rest and listen inward.",
}
