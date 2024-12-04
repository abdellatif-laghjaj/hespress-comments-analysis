from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from collections import Counter
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/hespress_comments"
mongo = PyMongo(app)


@app.route('/')
def index():
    comments = list(mongo.db.comments_batch.find())
    sentiment_counter = Counter()
    date_counter = Counter()

    # For debugging: Print the data that will be passed to the template
    for comment in comments:
        sentiment = comment.get("sentiment", "neutral").capitalize()
        print(f"Comment: {comment.get('comment_text')} Sentiment: {sentiment}")  # Debugging line

        sentiment_counter[sentiment] += 1
        try:
            date_obj = datetime.fromisoformat(comment["date"])
            date = date_obj.strftime('%Y-%m-%d')
        except (KeyError, ValueError):
            date = "Unknown"
        date_counter[date] += 1

    # Now print the full data being passed to the template
    data = {
        "total_comments": len(comments),
        "positive_comments": sentiment_counter.get("Positive", 0),
        "negative_comments": sentiment_counter.get("Negative", 0),
        "neutral_comments": sentiment_counter.get("Neutral", 0),
        "comments_activity": list(date_counter.values()),
        "comments_dates": list(date_counter.keys()),
        "comments": [
            {
                "author": comment.get("user_name", "Unknown"),
                "date": date,
                "comment": comment.get("comment_text", ""),
                "sentiment": comment.get("sentiment", "").capitalize(),
                "likes": comment.get("likes", 0),
                "article_title": comment.get("article_title", "Unknown Article"),
                "article_url": comment.get("article_url", "#")
            }
            for comment in comments
        ]

    }

    # Debugging: print the final 'data' object being passed to the template
    print(f"Data being passed to template: {data}")
    print("Dates", date_counter[date])  # Debugging line

    return render_template("index.html", data=data)


@app.route('/api/data')
def api_data():
    # Fetch all comments from MongoDB's article_1 collection
    comments = list(mongo.db.comments_batch.find())

    # Prepare data for analytics (activity and sentiment)
    sentiment_counter = Counter()
    date_counter = Counter()

    for comment in comments:
        # Count sentiment directly from the document
        sentiment = comment.get("sentiment", "Neutral").capitalize()

        # Parse the date string and extract the date part (format as 'YYYY-MM-DD')
        try:
            print(f"Raw date: {comment.get('date')}")
            date_obj = datetime.fromisoformat(comment["date"])
            date = date_obj.strftime('%Y-%m-%d')  # Use the full date (YYYY-MM-DD)
        except (KeyError, ValueError):
            date = "Unknown"

        # Update counters
        sentiment_counter[sentiment] += 1
        date_counter[date] += 1  # Increment the count for this specific date

    # Prepare the JSON data to be returned to D3.js
    api_data = {
        "activity": list(date_counter.values()),  # Number of comments per day
        "dates": list(date_counter.keys()),
        "sentiments": [
            sentiment_counter.get("Positive", 0),
            sentiment_counter.get("Negative", 0),
            sentiment_counter.get("Neutral", 0)
        ]
    }

    print(f"API Data: {api_data}")

    return jsonify(api_data)


if __name__ == "__main__":
    app.run(debug=True)
