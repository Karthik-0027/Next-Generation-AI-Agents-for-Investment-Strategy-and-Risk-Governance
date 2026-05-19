from datetime import datetime

def run_sentiment_agent(db):

    source = db["sentiment_aggregated"]
    target = db["agent_signals"]

    for doc in source.find({}):

        # ✅ FIXED FIELD NAME
        score = doc.get("average_sentiment_score", 0)

        if score > 0.25:
            signal, confidence = "BUY", 0.75
        elif score < -0.25:
            signal, confidence = "SELL", 0.25
        else:
            signal, confidence = "HOLD", 0.5

        target.update_one(
            {"symbol": doc["symbol"], "agent": "SENTIMENT"},
            {"$set": {
                "symbol": doc["symbol"],
                "agent": "SENTIMENT",
                "signal": signal,
                "confidence": confidence,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )