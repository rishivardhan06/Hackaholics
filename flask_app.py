from flask import Flask, request, jsonify
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import json
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)

# Initialize NLTK
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# Data storage
activities = []
feedbacks = []

# Routes for activities
@app.route('/activities', methods=['GET', 'POST', 'DELETE'])
def handle_activities():
    global activities

    if request.method == 'POST':
        activity = request.get_json()
        activities.append(activity)
        return jsonify({"message": "Activity logged successfully", "activity": activity})

    elif request.method == 'GET':
        return jsonify(activities)

    elif request.method == 'DELETE':
        activities = []
        return jsonify({"message": "All activities cleared"})

# Route for feedback
@app.route('/feedback', methods=['GET', 'POST'])
def handle_feedback():
    global feedbacks

    if request.method == 'POST':
        feedback = request.get_json()
        sentiment = sid.polarity_scores(feedback['feedback'])
        feedback['sentiment'] = sentiment
        feedbacks.append(feedback)
        return jsonify({"message": "Feedback received and analyzed", "feedback": feedback})

    elif request.method == 'GET':
        return jsonify(feedbacks)

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)