# mood_analysis_api.py
from flask import Flask, request, jsonify
from textblob import TextBlob

app = Flask(__name__)

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

    return jsonify({
        'mood': mood,
        'polarity_score': polarity,
        'tip': tip
    })

if __name__ == '__main__':
    app.run(debug=True)
