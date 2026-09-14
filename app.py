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
                if str(item).strip():
                    translated_p = mtranslate.translate(str(item), 'fr', 'auto')
                    translated_list.append(translated_p)
                else:
                    translated_list.append("")
            return jsonify({'translation': translated_list})

        # Handles Single Text String (Tab 1)
        translated = mtranslate.translate(str(text_data), 'fr', 'auto')
        return jsonify({'translation': translated})

    except Exception as e:
        print(f"Translation Route Failure: {str(e)}")
        return jsonify({'translation': "Error translating text. Please try again."})

if __name__ == '__main__':
    app.run(debug=True)