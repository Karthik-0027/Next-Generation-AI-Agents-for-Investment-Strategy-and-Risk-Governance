import pandas as pd
from datetime import datetime
from agentic_ai.config import VOLATILITY_THRESHOLD, EXTREME_VOL_THRESHOLD

def run_risk_agent(db):

    market = db["market_data"]
    signals = db["agent_signals"]
    risk_collection = db["risk_flags"]

    for doc in market.find({}):

        symbol = doc["symbol"]
        ohlcv_data = doc.get("ohlcv")

        if not ohlcv_data:
            continue

        df = pd.DataFrame(ohlcv_data)

        if "close" not in df.columns:
            continue

        volatility = float(df["close"].pct_change().std())

        stock_signals = list(signals.find({"symbol": symbol}))
        unique_signals = set(s["signal"] for s in stock_signals)

        conflict_flag = bool(len(unique_signals) == 3)
        volatility_flag = bool(volatility > VOLATILITY_THRESHOLD)
        hard_block = bool(volatility > EXTREME_VOL_THRESHOLD)

        risk_collection.update_one(
            {"symbol": symbol},
            {"$set": {
                "symbol": symbol,
                "volatility": volatility,
                "volatility_flag": volatility_flag,
                "conflict_flag": conflict_flag,
                "hard_block": hard_block,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )