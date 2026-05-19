from datetime import datetime

TOP_N = 5


def run_portfolio_engine(db, total_capital):

    decisions_collection = db["agent_decisions"]
    portfolio_collection = db["portfolio_allocation"]

    print("\n[PORTFOLIO] Building portfolio allocation...\n")

    buy_stocks = list(decisions_collection.find({"final_decision": "BUY"}))

    # 🔥 FIX: fallback
    if not buy_stocks:
        print("[PORTFOLIO] No BUY signals found. Using all stocks.")
        buy_stocks = list(decisions_collection.find({}))

    buy_stocks = sorted(
        buy_stocks,
        key=lambda x: x.get("composite_score", 0),
        reverse=True
    )

    selected_stocks = buy_stocks[:TOP_N]

    total_score = sum(stock.get("composite_score", 0) for stock in selected_stocks)

    if total_score == 0:
        print("[PORTFOLIO] Scores are zero. Cannot allocate.")
        return

    for stock in selected_stocks:

        symbol = stock["symbol"]
        score = stock.get("composite_score", 0)

        weight = score / total_score
        capital = weight * total_capital

        portfolio_collection.update_one(
            {"symbol": symbol},
            {
                "$set": {
                    "symbol": symbol,
                    "composite_score": score,
                    "allocation_weight": round(weight, 4),
                    "capital_allocated": round(capital, 2),
                    "decision": "BUY",
                    "timestamp": datetime.utcnow()
                }
            },
            upsert=True
        )

        print(f"{symbol} → {round(weight,4)} | ₹{round(capital,2)}")

    print("\n✅ Portfolio allocation complete.\n")