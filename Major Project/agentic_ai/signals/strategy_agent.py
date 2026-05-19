import pandas as pd
from datetime import datetime

def run_strategy_agent(db):

    source = db["market_data"]
    target = db["agent_signals"]

    for doc in source.find({}):

        symbol = doc["symbol"]
        ohlcv_data = doc.get("ohlcv")

        if not ohlcv_data:
            continue

        df = pd.DataFrame(ohlcv_data)

        if "close" not in df.columns:
            print(f"[Strategy] Skipping {symbol} - no close column")
            continue

        if len(df) < 200:
            continue

        df["sma50"] = df["close"].rolling(50).mean()
        df["sma200"] = df["close"].rolling(200).mean()

        last = df.iloc[-1]

        if last["sma50"] > last["sma200"]:
            signal = "BUY"
        elif last["sma50"] < last["sma200"]:
            signal = "SELL"
        else:
            signal = "HOLD"

        target.update_one(
            {"symbol": symbol, "agent": "STRATEGY"},
            {"$set": {
                "symbol": symbol,
                "agent": "STRATEGY",
                "signal": signal,
                "confidence": 0.7,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )