# mood_analysis_api.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import openai
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# 🔐 Securely fetch API key and validate
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise Exception("OPENAI_API_KEY environment variable is not set.")
openai.api_key = api_key

JOURNAL_LOG_PATH = "journal_log.json"

# Save journal entries
def save_journal_entry(entry, mood):
    log = []
    if os.path.exists(JOURNAL_LOG_PATH):
        with open(JOURNAL_LOG_PATH, 'r') as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    log.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'entry': entry,
        'mood': mood
    })

    with open(JOURNAL_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

# Analyze Mood API
@app.route('/analyze', methods=['POST'])
def analyze_mood():
    data = request.get_json()
    journal_entry = data.get('entry', '')

    analysis = TextBlob(journal_entry)
    polarity = analysis.sentiment.polarity

    mood = "Neutral"
    tip = "Keep writing and reflecting!"

    if polarity > 0.2:
        mood = "Positive"
        tip = "You're doing great! Celebrate your wins today."
    elif polarity < -0.2:
        mood = "Negative"
        tip = "It's okay to have tough days. Consider some relaxation."

    save_journal_entry(journal_entry, mood)

    return jsonify({
        'mood': mood,
        'polarity_score': polarity,
        'tip': tip
    })

# Therapist Chatbot API
@app.route('/chat', methods=['POST'])
def therapist_chat():
    data = request.get_json()
    user_input = data.get('message', '')

    history = []
    if os.path.exists(JOURNAL_LOG_PATH):
        with open(JOURNAL_LOG_PATH, 'r') as f:
            try:
                log = json.load(f)
                recent = log[-3:]
                history = [f"{item['timestamp']}: {item['entry']}" for item in recent]
            except:
                history = []

    context = "\n".join(history)
    prompt = f"Here are the user's recent journal entries:\n{context}\n\nNow the user says: {user_input}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a kind and empathetic mental wellness therapist."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({ "reply": reply })

    except Exception as e:
        print("OpenAI Error:", e)
        return jsonify({ "reply": "Sorry, I had trouble responding right now." })

# Mood History for Chart
@app.route('/history', methods=['GET'])
def get_history():
    if not os.path.exists(JOURNAL_LOG_PATH):
        return jsonify([])

    try:
        with open(JOURNAL_LOG_PATH, 'r') as f:
            log = json.load(f)
            return jsonify([
                {
                    'timestamp': entry['timestamp'],
                    'mood': entry['mood']
                } for entry in log
            ])
    except:
        return jsonify([])

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
