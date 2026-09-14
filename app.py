from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
import random

app = Flask(__name__)

# CURATED TCF / TEF VOCABULARY DATABASE (A1 - B2)
VOCAB_DATABASE = {
    "A1": [
        {"word": "Bonjour", "phonetic": "(bon-zhoor)", "meaning": "hello"},
        {"word": "Merci", "phonetic": "(mair-see)", "meaning": "thank you"},
        {"word": "S'il vous plaît", "phonetic": "(seel voo pleh)", "meaning": "please"},
        {"word": "Au revoir", "phonetic": "(oh ruh-vwahr)", "meaning": "goodbye"},
        {"word": "Aujourd'hui", "phonetic": "(oh-zhoor-dwee)", "meaning": "today"},
        {"word": "Demain", "phonetic": "(duh-man)", "meaning": "tomorrow"},
        {"word": "Famille", "phonetic": "(fah-meey)", "meaning": "family"},
        {"word": "Maison", "phonetic": "(may-zohn)", "meaning": "house"},
        {"word": "Manger", "phonetic": "(mahn-zhay)", "meaning": "to eat"},
        {"word": "Boire", "phonetic": "(bwahr)", "meaning": "to drink"},
        {"word": "Ami", "phonetic": "(ah-mee)", "meaning": "friend"},
        {"word": "Voiture", "phonetic": "(vwah-tyoor)", "meaning": "car"},
        {"word": "Livre", "phonetic": "(lee-vruh)", "meaning": "book"}
    ],
    "A2": [
        {"word": "Travailler", "phonetic": "(trah-vy-yay)", "meaning": "to work"},
        {"word": "Comprendre", "phonetic": "(kohm-prahn-druh)", "meaning": "to understand"},
        {"word": "Apprendre", "phonetic": "(ah-prahn-druh)", "meaning": "to learn"},
        {"word": "Voyager", "phonetic": "(vway-yah-zhay)", "meaning": "to travel"},
        {"word": "Habiter", "phonetic": "(ah-bee-tay)", "meaning": "to live / reside"},
        {"word": "Nourriture", "phonetic": "(noo-ree-tyoor)", "meaning": "food"},
        {"word": "Acheter", "phonetic": "(ah-shtay)", "meaning": "to buy"},
        {"word": "Rencontrer", "phonetic": "(rahn-kohn-tray)", "meaning": "to meet"},
        {"word": "Changer", "phonetic": "(shahn-zhay)", "meaning": "to change"},
        {"word": "Département", "phonetic": "(day-pahr-tuh-mahnt)", "meaning": "department"},
        {"word": "Ville", "phonetic": "(veel)", "meaning": "city"},
        {"word": "Temps", "phonetic": "(tahn)", "meaning": "weather / time"},
        {"word": "Argent", "phonetic": "(ahr-zhahn)", "meaning": "money"}
    ],
    "B1": [
        {"word": "Développer", "phonetic": "(day-vloh-pay)", "meaning": "to develop"},
        {"word": "Opportunité", "phonetic": "(oh-por-tyoo-nee-tay)", "meaning": "opportunity"},
        {"word": "Environnement", "phonetic": "(ahn-vee-rohn-mahnt)", "meaning": "environment"},
        {"word": "Expérience", "phonetic": "(ex-pay-ree-ahnss)", "meaning": "experience"},
        {"word": "Résoudre", "phonetic": "(ray-zoo-druh)", "meaning": "to solve"},
        {"word": "Compétence", "phonetic": "(kohm-pay-tahnss)", "meaning": "skill / ability"},
        {"word": "Avantage", "phonetic": "(ah-vahn-tazh)", "meaning": "advantage"},
        {"word": "Inconvénient", "phonetic": "(an-kohn-vay-nyahn)", "meaning": "disadvantage"},
        {"word": "Participer", "phonetic": "(pahr-tee-see-pay)", "meaning": "to participate"},
        {"word": "Soutenir", "phonetic": "(soo-tuh-neer)", "meaning": "to support"},
        {"word": "Objectif", "phonetic": "(ohb-zhek-teef)", "meaning": "goal / objective"},
        {"word": "Conseiller", "phonetic": "(kohn-say-yay)", "meaning": "to advise"},
        {"word": "Entreprise", "phonetic": "(ahn-truh-preeze)", "meaning": "company / enterprise"}
    ],
    "B2": [
        {"word": "Améliorer", "phonetic": "(ah-may-lee-oh-ray)", "meaning": "to improve"},
        {"word": "Incontournable", "phonetic": "(an-kohn-toor-nah-bluh)", "meaning": "essential / inescapable"},
        {"word": "Sensibiliser", "phonetic": "(sahn-see-bee-lee-zay)", "meaning": "to raise awareness"},
        {"word": "Épanouissement", "phonetic": "(ay-pah-nwee-ss-mahnt)", "meaning": "fulfillment / flourishing"},
        {"word": "Néanmoins", "phonetic": "(nay-ahn-mwan)", "meaning": "nevertheless"},
        {"word": "Perspicacité", "phonetic": "(pair-spee-kah-see-tay)", "meaning": "insight / sharpness"},
        {"word": "Conséquence", "phonetic": "(kohn-say-kahnss)", "meaning": "consequence"},
        {"word": "Désormais", "phonetic": "(day-zohr-may)", "meaning": "from now on"},
        {"word": "Toutefois", "phonetic": "(toot-fwah)", "meaning": "however"},
        {"word": "Préconiser", "phonetic": "(pray-koh-nee-zay)", "meaning": "to advocate / recommend"},
        {"word": "Pertinent", "phonetic": "(pair-tee-nahn)", "meaning": "relevant / pertinent"},
        {"word": "Enjeu", "phonetic": "(ahn-zhuh)", "meaning": "stake / issue"},
        {"word": "Mettre en œuvre", "phonetic": "(meh-truh ahn uh-vruh)", "meaning": "to implement"}
    ]
}

@app.route('/')
def home():
    return render_template('index.html')

# API TO FETCH RANDOM VOCABULARY WORD
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

# MULTI-PARAGRAPH SAFE TRANSLATION ENDPOINT
@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        
        # Array translation (Tab 3 Daily Routines)
        if isinstance(data.get('text'), list):
            translated_list = []
            for paragraph in data['text']:
                if paragraph.strip():
                    translated_p = GoogleTranslator(source='auto', target='fr').translate(paragraph)
                    translated_list.append(translated_p)
                else:
                    translated_list.append("")
            return jsonify({'translation': translated_list})
        
        # Single string translation (Tab 1)
        text = data.get('text', '')
        if not text:
            return jsonify({'translation': ''})
            
        translated = GoogleTranslator(source='auto', target='fr').translate(text)
        return jsonify({'translation': translated})

    except Exception as e:
        print(f"Translation Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)