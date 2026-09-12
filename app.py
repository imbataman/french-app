import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator, MyMemoryTranslator

app = Flask(__name__)

VOCABULARY_LIST = [
    {"word": "Bonjour", "phonetic": "bon-zhoor", "translation": "hello", "level": "A1"},
    {"word": "Merci", "phonetic": "mair-see", "translation": "thank you", "level": "A1"},
    {"word": "S'il vous plaît", "phonetic": "seel voo pleh", "translation": "please", "level": "A1"},
    {"word": "Aujourd'hui", "phonetic": "oh-zhoor-dwee", "translation": "today", "level": "A2"},
    {"word": "Beaucoup", "phonetic": "boh-koo", "translation": "a lot / much", "level": "A2"},
    {"word": "Environnement", "phonetic": "ahn-vee-rohn-mahng", "translation": "environment", "level": "B1"},
    {"word": "Cependant", "phonetic": "suh-pahng-dahng", "translation": "however", "level": "B1"},
    {"word": "Développement", "phonetic": "day-vlohp-mahng", "translation": "development", "level": "B2"},
    {"word": "Néanmoins", "phonetic": "nay-ahng-mwahng", "translation": "nevertheless", "level": "B2"}
]

GRAMMAR_TOPICS = {
    "articles_partitifs": {
        "title": "Articles Partitifs (Du, De la, Des)",
        "level": "A1-A2",
        "rule": "Expresses unspecified quantities. Use 'du' (masculine), 'de la' (feminine), 'de l\'' (vowel), and 'des' (plural). In negation, all turn into 'de/d\''.",
        "formula": "du / de la / de l' / des (+ noun) | de / d' (negation)",
        "examples": ["Je bois du café. (I drink coffee.)", "Je ne veux pas de sucre. (I don't want sugar.)"]
    },
    "adjectifs_possessifs": {
        "title": "Adjectifs Possessifs (Mon, Ma, Mes, Son, Sa...)",
        "level": "A1-A2",
        "rule": "Agrees in gender and number with the item possessed, NOT the owner. Use 'mon/ton/son' before feminine nouns starting with a vowel.",
        "formula": "mon/ma/mes, ton/ta/tes, son/sa/ses, notre/nos, votre/vos, leur/leurs",
        "examples": ["C'est mon amie. (She is my friend - feminine vowel).", "Il aime ses parents. (He loves his parents.)"]
    },
    "adjectifs_demonstratifs": {
        "title": "Adjectifs Démonstratifs (Ce, Cet, Cette, Ces)",
        "level": "A1-A2",
        "rule": "Use 'ce' (masc. singular), 'cet' (masc. singular before vowel/silent h), 'cette' (fem. singular), 'ces' (plural).",
        "formula": "ce / cet / cette / ces + Noun",
        "examples": ["Cet homme est gentil.", "Cette maison est grande."]
    },
    "negation_complexe": {
        "title": "La Négation Complexe (Ne...jamais, Ne...rien, Ne...personne)",
        "level": "A2-B1",
        "rule": "Replaces 'ne...pas' to specify 'never', 'nothing', 'nobody', or 'no longer'. Wraps around the conjugated verb.",
        "formula": "Ne + Verb + jamais / rien / personne / plus",
        "examples": ["Je ne mange jamais de viande.", "Il ne voit personne."]
    },
    "passe_compose": {
        "title": "Passé Composé (Être vs Avoir)",
        "level": "A2-B1",
        "rule": "Expresses completed past actions. Verbs of movement (DR & MRS VANDERTRAMPP) and reflexive verbs use 'Être' with agreement. Most others use 'Avoir'.",
        "formula": "Subject + Avoir/Être (conjugated) + Past Participle",
        "examples": ["J'ai mangé une pomme.", "Elle est allée au marché."]
    },
    "imparfait": {
        "title": "L'Imparfait (Habits & Descriptions)",
        "level": "A2-B1",
        "rule": "Used for past habits, background descriptions, or ongoing past states. Take the 'nous' present stem and add: -ais, -ais, -ait, -ions, -iez, -aient.",
        "formula": "Nous-stem + Imparfait ending",
        "examples": ["Quand j'étais jeune, je jouais au foot.", "Il faisait beau."]
    },
    "futur_simple": {
        "title": "Le Futur Simple",
        "level": "A2-B1",
        "rule": "Expresses future events. Formed using the infinitive (or irregular stem) + endings: -ai, -as, -a, -ons, -ez, -ont.",
        "formula": "Infinitive/Stem + futur ending",
        "examples": ["Demain, je voyagerai à Paris.", "Ils feront leurs devoirs."]
    },
    "pronoms_cod_coi": {
        "title": "Pronoms COD / COI (Direct & Indirect Object Pronouns)",
        "level": "B1",
        "rule": "COD (me, te, le, la, nous, vous, les) replaces direct nouns. COI (lui, leur) replaces 'à + person'. Placed directly before the verb.",
        "formula": "Subject + (COD / COI) + Verb",
        "examples": ["Je vois Paul -> Je le vois.", "Je parle à Marie -> Je lui parle."]
    },
    "pronoms_y_en": {
        "title": "Les Pronoms Y et EN",
        "level": "B1",
        "rule": "'Y' replaces places or 'à + noun'. 'EN' replaces quantities or 'de + noun'. Placed before the verb.",
        "formula": "Subject + Y / EN + Verb",
        "examples": ["Je vais à Paris -> J'y vais.", "Je veux du pain -> J'en veux."]
    },
    "conditionnel_present": {
        "title": "Le Conditionnel Présent (Politeness & Hypotheses)",
        "level": "B1",
        "rule": "Used for polite requests, advice, or hypothetical statements. Formed with the Future stem + Imparfait endings.",
        "formula": "Future Stem + -ais, -ais, -ait, -ions, -iez, -aient",
        "examples": ["Je voudrais un café, s'il vous plaît.", "Si j'avais le temps, je voyagerais."]
    },
    "subjonctif_present": {
        "title": "Le Subjonctif Présent (Necessity, Wishes, Doubts)",
        "level": "B1-B2",
        "rule": "Triggered by expressions of necessity (il faut que), emotions, desires, or doubts with two different subjects. Stem is from 3rd person plural 'ils' present.",
        "formula": "Ils-stem + -e, -es, -e, -ions, -iez, -ent",
        "examples": ["Il faut que tu fasses tes devoirs.", "Je veux que vous veniez."]
    },
    "plus_que_parfait": {
        "title": "Le Plus-que-parfait (Past before Past)",
        "level": "B2",
        "rule": "Expresses an action completed before another past action. Formed using Avoir/Être in the Imparfait + Past Participle.",
        "formula": "Imparfait of Avoir/Être + Past Participle",
        "examples": ["Quand je suis arrivé, il était déjà parti."]
    },
    "pronoms_relatifs_composes": {
        "title": "Pronoms Relatifs (Qui, Que, Où, Dont, Lequel)",
        "level": "B2",
        "rule": "'Qui' replaces subjects, 'Que' replaces objects, 'Où' replaces time/place, 'Dont' replaces 'de + noun'.",
        "formula": "Noun + Pronoun + Clause",
        "examples": ["Le livre que je lis est super.", "La ville où j'habite est belle."]
    },
    "voix_passive": {
        "title": "La Voix Passive",
        "level": "B2",
        "rule": "Emphasizes the object receiving the action. Formed with 'Être' + Past Participle (agrees with subject) + 'par' + agent.",
        "formula": "Object + Être (conjugated) + Past Participle + par + Agent",
        "examples": ["Le gâteau est mangé par l'enfant.", "La lettre a été envoyée."]
    },
    "gerondif": {
        "title": "Le Gérondif (En + Participe Présent)",
        "level": "B2",
        "rule": "Expresses simultaneous actions, means, or conditions. Formed with 'en' + 'nous' present stem + '-ant'.",
        "formula": "en + Nous-stem + ant",
        "examples": ["Il écoutait de la musique en étudiant.", "C'est en pratiquant qu'on apprend."]
    }
}

EXERCISE_BANKS = {
    "articles_partitifs": [
        {"sentence": "Le matin, je bois ________ (masculine) café.", "answer": "du", "english": "In the morning, I drink coffee.", "explanation": "'Café' is singular masculine -> 'du'."},
        {"sentence": "Elle ne prend pas ________ (negation) lait.", "answer": "de", "english": "She does not take any milk.", "explanation": "In negation ('ne...pas'), partitive articles simplify to 'de'."},
        {"sentence": "Pour la recette, nous avons besoin de ________ (feminine) farine.", "answer": "de la", "english": "For the recipe, we need flour.", "explanation": "'Farine' is feminine singular -> 'de la'."},
        {"sentence": "Ils achètent ________ (plural) pommes au marché.", "answer": "des", "english": "They buy apples at the market.", "explanation": "'Pommes' is plural -> 'des'."},
        {"sentence": "Est-ce qu'il y a ________ (vowel) eau fraîche dans le frigo ?", "answer": "de l'", "english": "Is there fresh water in the fridge?", "explanation": "'Eau' starts with a vowel -> 'de l''."}
    ],
    "adjectifs_possessifs": [
        {"sentence": "C'est ________ (my - fem. vowel) amie Marie.", "answer": "mon", "english": "This is my friend Marie.", "explanation": "Use 'mon' instead of 'ma' before feminine words starting with a vowel."},
        {"sentence": "Ils visitent ________ (their - plural) parents.", "answer": "leurs", "english": "They are visiting their parents.", "explanation": "'Parents' is plural -> 'leurs'."},
        {"sentence": "Elle a perdu ________ (her - masc.) sac.", "answer": "son", "english": "She lost her bag.", "explanation": "'Sac' is masculine singular -> 'son'."}
    ],
    "adjectifs_demonstratifs": [
        {"sentence": "________ (this - masc. vowel) homme est très sympathique.", "answer": "cet", "english": "This man is very nice.", "explanation": "Use 'cet' for masculine nouns starting with a vowel/silent h."},
        {"sentence": "J'aime beaucoup ________ (these - plural) chaussures.", "answer": "ces", "english": "I really like these shoes.", "explanation": "'Chaussures' is plural -> 'ces'."},
        {"sentence": "________ (this - fem.) robe est magnifique.", "answer": "cette", "english": "This dress is magnificent.", "explanation": "'Robe' is feminine singular -> 'cette'."}
    ],
    "negation_complexe": [
        {"sentence": "Je ne veux ________ (nothing) à manger.", "answer": "rien", "english": "I want nothing to eat.", "explanation": "'Rien' translates to 'nothing'."},
        {"sentence": "Il ne va ________ (never) au cinéma le lundi.", "answer": "jamais", "english": "He never goes to the cinema on Mondays.", "explanation": "'Jamais' translates to 'never'."},
        {"sentence": "Elle n'a vu ________ (nobody) dans la rue.", "answer": "personne", "english": "She saw nobody in the street.", "explanation": "'Personne' translates to 'nobody/no one'."}
    ],
    "passe_compose": [
        {"sentence": "Hier, Marie ________ (aller) au cinéma.", "answer": "est allée", "english": "Yesterday, Marie went to the cinema.", "explanation": "'Aller' uses 'être' with subject agreement for feminine singular -> 'est allée'."},
        {"sentence": "Nous ________ (manger) dans un grand restaurant.", "answer": "avons mangé", "english": "We ate in a big restaurant.", "explanation": "'Manger' uses 'avoir' -> 'avons mangé'."},
        {"sentence": "Hier soir, Marc et Paul ________ (partir) à huit heures.", "answer": "sont partis", "english": "Last night, Marc and Paul left at eight o'clock.", "explanation": "'Partir' uses 'être' with plural agreement -> 'sont partis'."}
    ],
    "imparfait": [
        {"sentence": "Chaque été, nous ________ (visiter) nos grands-parents.", "answer": "visitions", "english": "Every summer, we used to visit our grandparents.", "explanation": "'Visiter' stem 'visit-' + 'ions' for nous = 'visitions'."},
        {"sentence": "Quand j'________ (être) jeune, j'aimais lire.", "answer": "étais", "english": "When I was young, I liked to read.", "explanation": "'Être' irregular stem 'ét-' + 'ais' = 'étais'."},
        {"sentence": "Tous les soirs, il ________ (faire) du sport.", "answer": "faisait", "english": "Every evening, he used to do sports.", "explanation": "'Faire' stem 'fais-' + 'ait' = 'faisait'."}
    ],
    "futur_simple": [
        {"sentence": "L'année prochaine, elle ________ (avoir) vingt ans.", "answer": "aura", "english": "Next year, she will be twenty years old.", "explanation": "'Avoir' stem 'aur-' + 'a' = 'aura'."},
        {"sentence": "Demain, je ________ (voyager) à Paris.", "answer": "voyagerai", "english": "Tomorrow, I will travel to Paris.", "explanation": "'Voyager' infinitive + 'ai' = 'voyagerai'."},
        {"sentence": "Nous ________ (être) très contents de vous voir.", "answer": "serons", "english": "We will be very happy to see you.", "explanation": "'Être' stem 'ser-' + 'ons' = 'serons'."}
    ],
    "pronoms_cod_coi": [
        {"sentence": "Tu aimes ce livre ? - Oui, je ________ aime.", "answer": "l'", "english": "Do you like this book? - Yes, I like it.", "explanation": "'Ce livre' is masculine singular before a vowel -> 'l''."},
        {"sentence": "Tu parles à ton frère ? - Oui, je ________ parle.", "answer": "lui", "english": "Are you talking to your brother? - Yes, I am talking to him.", "explanation": "'À ton frère' is indirect object singular -> 'lui'."},
        {"sentence": "Il voit ses amis ? - Oui, il ________ voit.", "answer": "les", "english": "Does he see his friends? - Yes, he sees them.", "explanation": "'Ses amis' is direct object plural -> 'les'."}
    ],
    "pronoms_y_en": [
        {"sentence": "Tu vas à la banque ? - Oui, j'________ vais.", "answer": "y", "english": "Are you going to the bank? - Yes, I am going there.", "explanation": "Replaces location 'à la banque' -> 'y'."},
        {"sentence": "Tu veux du café ? - Oui, j'________ veux.", "answer": "en", "english": "Do you want coffee? - Yes, I want some.", "explanation": "Replaces quantity/partitive 'du café' -> 'en'."}
    ],
    "conditionnel_present": [
        {"sentence": "Si j'avais de l'argent, je ________ (acheter) une voiture.", "answer": "J'achèterais", "english": "If I had money, I would buy a car.", "explanation": "In conditional clauses with 'si + imparfait', main clause uses conditional -> 'j'achèterais'."},
        {"sentence": "Est-ce que vous ________ (pouvoir) m'aider, s'il vous plaît ?", "answer": "pourriez", "english": "Could you help me, please?", "explanation": "Polite request using conditional of 'pouvoir' -> 'pourriez'."}
    ],
    "subjonctif_present": [
        {"sentence": "Il faut que tu ________ (faire) attention.", "answer": "fasses", "english": "You must pay attention.", "explanation": "'Il faut que' requires subjunctive. 'Faire' stem -> 'fasses'."},
        {"sentence": "Je veux qu'elle ________ (venir) à la fête.", "answer": "vienne", "english": "I want her to come to the party.", "explanation": "'Vouloir que' requires subjunctive. 'Venir' stem -> 'vienne'."}
    ],
    "plus_que_parfait": [
        {"sentence": "Quand tu es arrivé, ils ________ (déjà / partir).", "answer": "étaient partis", "english": "When you arrived, they had already left.", "explanation": "'Partir' uses 'être' in imparfait -> 'étaient partis'."},
        {"sentence": "J'________ (finir) mon travail avant son appel.", "answer": "avais fini", "english": "I had finished my work before her call.", "explanation": "'Finir' uses 'avoir' in imparfait -> 'avais fini'."}
    ],
    "pronoms_relatifs_composes": [
        {"sentence": "L'homme ________ parle est mon professeur.", "answer": "qui", "english": "The man who is speaking is my teacher.", "explanation": "Replaces subject person -> 'qui'."},
        {"sentence": "Le gâteau ________ tu as préparé est délicieux.", "answer": "que", "english": "The cake that you prepared is delicious.", "explanation": "Replaces direct object -> 'que'."}
    ],
    "voix_passive": [
        {"sentence": "La souris ________ (manger) par le chat.", "answer": "est mangée", "english": "The mouse is eaten by the cat.", "explanation": "'Être' in present tense + past participle agreeing with feminine 'la souris' -> 'est mangée'."}
    ],
    "gerondif": [
        {"sentence": "Elle écoute la radio en ________ (faire) la cuisine.", "answer": "faisant", "english": "She listens to the radio while cooking.", "explanation": "Gérondif uses 'en' + 'nous' stem 'fais-' + '-ant' -> 'faisant'."}
    ]
}

# Routine variations for paragraph generator
MORNINGS = [
    "I woke up at 6:30 AM to the sound of my alarm. First, I stretched in bed for a few minutes before standing up. Then, I walked to the kitchen and drank a large glass of fresh water.",
    "I got up early today at 6:00 AM. I made a hot cup of black coffee and read the morning news on my tablet for fifteen minutes."
]
AFTERNOONS = [
    "I arrived at my workplace around 8:45 AM and greeted my colleagues. The morning flew by with consecutive meetings and responding to urgent emails.",
    "Around noon, I stepped out to have lunch with a coworker at a small café nearby. We discussed our weekend plans while enjoying fresh sandwiches."
]
EVENINGS = [
    "After finishing work at 5:30 PM, I decided to take a longer route home to get some extra steps. On my way, I stopped by the neighborhood grocery store.",
    "By 6:00 PM, I went for a quick jog in the park. The evening weather was pleasant and crisp."
]
NIGHTS = [
    "Later in the evening, I sat on the sofa with a warm cup of herbal chamomile tea. I spent about thirty minutes practicing French vocabulary.",
    "Before going to bed, I organized my desk, wrote down my goals for tomorrow, and spent twenty minutes reading a fiction book."
]

def translate_text_safe(text):
    try:
        return GoogleTranslator(source='en', target='fr').translate(text)
    except Exception:
        try:
            return MyMemoryTranslator(source='en-US', target='fr-FR').translate(text)
        except Exception:
            return "Translation error."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    return jsonify({"translated": translate_text_safe(data.get("text", "").strip())})

@app.route("/get_vocab", methods=["GET"])
def get_vocab():
    return jsonify(VOCABULARY_LIST)

@app.route("/get_grammar_topics", methods=["GET"])
def get_grammar_topics():
    return jsonify(GRAMMAR_TOPICS)

@app.route("/get_grammar_exercise/<topic_key>", methods=["GET"])
def get_grammar_exercise(topic_key):
    bank = EXERCISE_BANKS.get(topic_key, EXERCISE_BANKS["passe_compose"])
    exercise = random.choice(bank)
    return jsonify(exercise)

@app.route("/get_daily_routine", methods=["GET"])
def get_daily_routine():
    # Always use TODAY's real accessing date
    now = datetime.now()
    current_day = now.strftime("%A")
    current_date = now.strftime("%B %d, %Y")
    
    m = random.choice(MORNINGS)
    a = random.choice(AFTERNOONS)
    e = random.choice(EVENINGS)
    n = random.choice(NIGHTS)

    english_paragraph = f"{m}\n\n{a}\n\n{e}\n\n{n}"
    french_paragraph = f"{translate_text_safe(m)}\n\n{translate_text_safe(a)}\n\n{translate_text_safe(e)}\n\n{translate_text_safe(n)}"
    
    return jsonify({
        "day": current_day,
        "date": current_date,
        "english": english_paragraph,
        "french": french_paragraph
    })

if __name__ == "__main__":
    app.run(debug=True)