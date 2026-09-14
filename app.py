from flask import Flask, render_template, request, jsonify
import mtranslate
import random

app = Flask(__name__)

# TCF / TEF VOCABULARY DATABASE (A1 - B2)
VOCAB_DATABASE = {
    "A1": [
        {"word": "Bonjour", "phonetic": "(bon-zhoor)", "meaning": "hello"},
        {"word": "Merci", "phonetic": "(mair-see)", "meaning": "thank you"},
        {"word": "S'il vous plaît", "phonetic": "(seel voo pleh)", "meaning": "please"},
        {"word": "Au revoir", "phonetic": "(oh ruh-vwahr)", "meaning": "goodbye"},
        {"word": "Aujourd'hui", "phonetic": "(oh-zhoor-dwee)", "meaning": "today"},
        {"word": "Demain", "phonetic": "(duh-man)", "meaning": "tomorrow"}
    ],
    "A2": [
        {"word": "Travailler", "phonetic": "(trah-vy-yay)", "meaning": "to work"},
        {"word": "Comprendre", "phonetic": "(kohm-prahn-druh)", "meaning": "to understand"},
        {"word": "Apprendre", "phonetic": "(ah-prahn-druh)", "meaning": "to learn"},
        {"word": "Voyager", "phonetic": "(vway-yah-zhay)", "meaning": "to travel"}
    ],
    "B1": [
        {"word": "Développer", "phonetic": "(day-vloh-pay)", "meaning": "to develop"},
        {"word": "Opportunité", "phonetic": "(oh-por-tyoo-nee-tay)", "meaning": "opportunity"},
        {"word": "Environnement", "phonetic": "(ahn-vee-rohn-mahnt)", "meaning": "environment"},
        {"word": "Résoudre", "phonetic": "(ray-zoo-druh)", "meaning": "to solve"}
    ],
    "B2": [
        {"word": "Améliorer", "phonetic": "(ah-may-lee-oh-ray)", "meaning": "to improve"},
        {"word": "Incontournable", "phonetic": "(an-kohn-toor-nah-bluh)", "meaning": "essential"},
        {"word": "Sensibiliser", "phonetic": "(sahn-see-bee-lee-zay)", "meaning": "to raise awareness"},
        {"word": "Néanmoins", "phonetic": "(nay-ahn-mwan)", "meaning": "nevertheless"}
    ]
}

# PRE-TRANSLATED DAILY ROUTINES FALLBACK DICTIONARY
ROUTINE_PRETRANSLATIONS = {
    "I got up early today at 6:00 AM. I made a hot cup of black coffee and read the morning news on my tablet for fifteen minutes.": 
        "Je me suis levé tôt aujourd'hui à 6h00. J'ai préparé une tasse de café noir chaud et j'ai lu les actualités du matin sur ma tablette pendant quinze minutes.",
    "I arrived at my workplace around 8:45 AM and greeted my colleagues. The morning flew by with consecutive meetings and responding to urgent emails.": 
        "Je suis arrivé à mon lieu de travail vers 8h45 et j'ai salué mes collègues. La matinée s'est envolée avec des réunions consécutives et la réponse aux e-mails urgents.",
    "By 6:00 PM, I went for a quick jog in the park. The evening weather was pleasant and crisp.": 
        "À 18h00, je suis allé faire un petit footing dans le parc. Le temps du soir était agréable et frais.",
    "Before going to bed, I organized my desk, wrote down my goals for tomorrow, and spent twenty minutes reading a fiction book.": 
        "Avant d'aller au lit, j'ai organisé mon bureau, écrit mes objectifs pour demain et passé vingt minutes à lire un livre de fiction."
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-vocab', methods=['GET'])
def get_vocab():
    level = request.args.get('level', 'ALL')
    if level in VOCAB_DATABASE:
        item = random.choice(VOCAB_DATABASE[level]).copy()
        item['level'] = level
        return jsonify(item)
    
    random_level = random.choice(list(VOCAB_DATABASE.keys()))
    item = random.choice(VOCAB_DATABASE[random_level]).copy()
    item['level'] = random_level
    return jsonify(item)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json() or {}
        text_data = data.get('text', '')

        if not text_data:
            return jsonify({'translation': ''})

        # Handles Array of paragraphs (Tab 3 Daily Routines)
        if isinstance(text_data, list):
            translated_list = []
            for item in text_data:
                clean_str = str(item).strip()
                if clean_str in ROUTINE_PRETRANSLATIONS:
                    translated_list.append(ROUTINE_PRETRANSLATIONS[clean_str])
                else:
                    try:
                        translated_p = mtranslate.translate(clean_str, 'fr', 'auto')
                        translated_list.append(translated_p)
                    except Exception:
                        translated_list.append(clean_str)
            return jsonify({'translation': translated_list})

        # Handles Single Text String (Tab 1)
        if str(text_data).strip() in ROUTINE_PRETRANSLATIONS:
            return jsonify({'translation': ROUTINE_PRETRANSLATIONS[str(text_data).strip()]})

        translated = mtranslate.translate(str(text_data), 'fr', 'auto')
        return jsonify({'translation': translated})

    except Exception as e:
        print(f"Translation Failure: {str(e)}")
        if isinstance(text_data, list):
            return jsonify({'translation': [ROUTINE_PRETRANSLATIONS.get(x.strip(), x) for x in text_data]})
        return jsonify({'translation': ROUTINE_PRETRANSLATIONS.get(str(text_data).strip(), "Translation service temporarily unavailable.")})

if __name__ == '__main__':
    app.run(debug=True)