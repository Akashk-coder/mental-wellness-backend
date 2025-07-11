from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob
import openai
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load OpenAI API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise Exception("OPENAI_API_KEY environment variable is not set.")
openai.api_key = api_key

# Path to journal history file
JOURNAL_LOG_PATH = "journal_history.json"

# Route to analyze mood
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
        tip = "It's okay to have tough days. Consider some relaxation or talk to someone you trust."

    # Save journal entry with timestamp
    entry_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "entry": journal_entry,
        "mood": mood
    }

    if os.path.exists(JOURNAL_LOG_PATH):
        with open(JOURNAL_LOG_PATH, 'r') as f:
            try:
                history = json.load(f)
            except:
                history = []
    else:
        history = []

    history.append(entry_data)
    with open(JOURNAL_LOG_PATH, 'w') as f:
        json.dump(history, f)

    return jsonify({
        'mood': mood,
        'polarity_score': polarity,
        'tip': tip
    })

# Route to view past entries for mood chart
@app.route('/history', methods=['GET'])
def get_history():
    if os.path.exists(JOURNAL_LOG_PATH):
        with open(JOURNAL_LOG_PATH, 'r') as f:
            try:
                history = json.load(f)
            except:
                history = []
    else:
        history = []
    return jsonify(history)

# AI therapist chatbot route
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
            model="gpt-4",  # or "gpt-3.5-turbo" if needed
            messages=[
                {"role": "system", "content": "You are a kind and empathetic mental wellness therapist."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({ "reply": reply })

    except Exception as e:
        print("OpenAI Error:", str(e))  # ⚠️ Log the actual OpenAI error
        return jsonify({ "reply": "Sorry, I had trouble responding right now." })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
