import feedparser
import re
import urllib.parse
from datetime import datetime

from database.mongo_client import get_db
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# =============================
# Initialization
# =============================
db = get_db()

market_collection = db["market_data"]
sentiment_collection = db["sentiment_data"]
aggregated_collection = db["sentiment_aggregated"]

analyzer = SentimentIntensityAnalyzer()


# =============================
# Helper Functions
# =============================
def get_symbols_from_db():
    return market_collection.distinct("symbol")


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.strip()


def analyze_sentiment(text: str):
    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        label = "POSITIVE"
    elif score <= -0.05:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return score, label


def fetch_news(symbol: str, limit: int = 10):
    query = urllib.parse.quote(symbol.replace(".NS", "") + " stock")
    url = f"https://news.google.com/rss/search?q={query}"

    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries[:limit]:
        articles.append({
            "headline": entry.title,
            "published_at": entry.published
        })

    return articles


def aggregate_sentiment(scores: list):
    if not scores:
        return 0.0, "NEUTRAL"

    avg_score = sum(scores) / len(scores)

    if avg_score > 0.2:
        label = "POSITIVE"
    elif avg_score < -0.2:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return round(avg_score, 3), label


# =============================
# MODULE 3 PIPELINE
# =============================
def run_news_collection():

    symbols = get_symbols_from_db()

    print(f"[Module 3] Found {len(symbols)} stocks from MongoDB")

    for symbol in symbols:
        print(f"[Module 3] Processing {symbol}")

        # ✅ Remove old raw news for this symbol
        sentiment_collection.delete_many({"symbol": symbol})

        articles = fetch_news(symbol)
        scores = []

        for article in articles:
            cleaned = clean_text(article["headline"])
            score, label = analyze_sentiment(cleaned)
            scores.append(score)

            sentiment_collection.insert_one({
                "symbol": symbol,
                "headline": article["headline"],
                "cleaned_text": cleaned,
                "sentiment_score": score,
                "sentiment_label": label,
                "source": "Google News RSS",
                "published_at": article["published_at"],
                "processed_at": datetime.utcnow()
            })

        avg_score, final_label = aggregate_sentiment(scores)

        # ✅ Update aggregation instead of insert
        aggregated_collection.update_one(
            {"symbol": symbol},
            {"$set": {
                "symbol": symbol,
                "average_sentiment_score": avg_score,
                "final_sentiment_label": final_label,
                "news_count": len(scores),
                "generated_at": datetime.utcnow()
            }},
            upsert=True
        )

    print("✅ Module 3 completed: News & Sentiment refreshed successfully.\n")


if __name__ == "__main__":
    run_news_collection()