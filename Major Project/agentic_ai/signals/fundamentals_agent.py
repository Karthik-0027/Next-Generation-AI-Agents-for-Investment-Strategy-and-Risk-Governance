from datetime import datetime

def run_fundamentals_agent(db):

    source = db["fundamental_scores"]
    target = db["agent_signals"]

    for doc in source.find({}):

        label = doc.get("label")

        if label == "STRONG":
            signal, confidence = "BUY", 0.8
        elif label == "NEUTRAL":
            signal, confidence = "HOLD", 0.5
        else:
            signal, confidence = "SELL", 0.2

        target.update_one(
            {"symbol": doc["symbol"], "agent": "FUNDAMENTALS"},
            {"$set": {
                "symbol": doc["symbol"],
                "agent": "FUNDAMENTALS",
                "signal": signal,
                "confidence": confidence,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )