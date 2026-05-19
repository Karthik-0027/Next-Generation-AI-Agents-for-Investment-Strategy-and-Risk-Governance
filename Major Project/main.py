print("Program Started")

from datetime import datetime, timedelta
from database.mongo_client import get_db

# Module imports
from data_collection.market_data import run_market_data_collection
from data_collection.news_data import run_news_collection
from fundamental_analysis.pipeline import run_fundamental_scoring
from agentic_ai.pipeline import run_module4

# Module 5
from agentic_ai.portfolio.portfolio_engine import run_portfolio_engine

# Module 6 (correct file name)
from agentic_ai.backtesting.backtest_engine import run_backtest_engine

# Module 7
from agentic_ai.analytics.analytics_engine import run_analytics_engine

# Module 8
from dashboard.server import app as dashboard_app


STALE_THRESHOLD_HOURS = 24


def is_market_data_stale(db):
    collection = db["market_data"]

    if collection.count_documents({}) == 0:
        return True

    latest_doc = collection.find_one({}, sort=[("last_updated", -1)])

    if not latest_doc or "last_updated" not in latest_doc:
        return True

    age = datetime.utcnow() - latest_doc["last_updated"]
    return age > timedelta(hours=STALE_THRESHOLD_HOURS)


def is_sentiment_data_stale(db):
    collection = db["sentiment_aggregated"]

    if collection.count_documents({}) == 0:
        return True

    latest_doc = collection.find_one({}, sort=[("generated_at", -1)])

    if not latest_doc or "generated_at" not in latest_doc:
        return True

    age = datetime.utcnow() - latest_doc["generated_at"]
    return age > timedelta(hours=STALE_THRESHOLD_HOURS)


def get_total_capital():
    while True:
        try:
            capital = float(input("\nEnter total investment capital (e.g. 100000): "))
            if capital <= 0:
                print("Capital must be greater than zero.")
                continue
            return capital
        except ValueError:
            print("Please enter a valid number.")


def main():

    db = get_db()

    print("\n" + "="*60)
    print("  NEXT-GEN AI AGENTS — INVESTMENT & RISK GOVERNANCE")
    print("="*60 + "\n")

    # ── Data Freshness ──
    print("🔍 Checking data freshness...\n")

    if is_market_data_stale(db):
        print("🔄 Updating market data...\n")
        run_market_data_collection()
    else:
        print("✅ Market data is fresh.\n")

    if is_sentiment_data_stale(db):
        print("📰 Updating sentiment data...\n")
        run_news_collection()
    else:
        print("✅ Sentiment data is fresh.\n")

    # ── Module 2 ──
    print("[MODULE 2] Fundamental Analysis\n")

    symbols = db["fundamentals_data"].distinct("symbol")

    for symbol in symbols:
        run_fundamental_scoring(symbol)

    print("✅ Fundamentals completed\n")

    # ── Module 4 ──
    print("[MODULE 4] AI Agents\n")
    run_module4()

    # ── Module 5 ──
    print("[MODULE 5] Portfolio\n")
    total_capital = get_total_capital()
    run_portfolio_engine(db, total_capital)

    # ── Module 6 ──
    print("[MODULE 6] Backtesting\n")
    run_backtest_engine(db)

    # ── Module 7 ──
    print("[MODULE 7] Analytics\n")
    run_analytics_engine(db)

    # 🔥 DEBUG CHECKS
    print("Backtest Records:", db["backtest_results"].count_documents({}))
    print("Analytics Records:", db["analytics_summary"].count_documents({}))

    print("\n✅ PIPELINE COMPLETE\n")

    # ── Dashboard ──
    print("🚀 Launching Dashboard at http://localhost:8050\n")
    dashboard_app.run(debug=False, port=8050)


if __name__ == "__main__":
    main()