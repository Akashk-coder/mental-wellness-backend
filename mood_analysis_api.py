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

# 🔐 Secure API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

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
    polarity = analysis.sen
