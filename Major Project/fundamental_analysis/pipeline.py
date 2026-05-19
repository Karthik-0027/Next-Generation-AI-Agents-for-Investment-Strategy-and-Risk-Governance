from fundamental_analysis.loader import load_latest_fundamentals
from fundamental_analysis.ratios import compute_ratios
from fundamental_analysis.scorer import score_category
from database.mongo_client import get_db

from datetime import datetime
import uuid

db = get_db()

# 🔑 One RUN ID per execution
RUN_ID = str(uuid.uuid4())


def classify_stock(score):
    if score >= 60:
        return "STRONG"
    elif score >= 40:
        return "NEUTRAL"
    return "WEAK"


def run_fundamental_scoring(symbol):
    print(f"[Module-2] Scoring fundamentals for {symbol}")

    # 1️⃣ Load fundamentals (NOW 3 VALUES)
    current_income, previous_income, balance = load_latest_fundamentals(symbol)

    if not current_income or not previous_income or not balance:
        print(f"   Skipping {symbol}: insufficient fundamental data\n")
        return

    # 2️⃣ Compute ratios (NOW growth-enabled)
    ratios = compute_ratios(current_income, previous_income, balance)

    if not ratios:
        print(f"   Skipping {symbol}: ratio computation failed\n")
        return

    # 3️⃣ Group ratios
    profitability = {
        "net_profit_margin": ratios.get("net_profit_margin"),
        "roe": ratios.get("roe"),
        "roa": ratios.get("roa"),
    }

    liquidity = {
        "current_ratio": ratios.get("current_ratio"),
        "quick_ratio": ratios.get("quick_ratio"),
    }

    leverage = {
        "debt_to_equity": ratios.get("debt_to_equity"),
    }

    growth = {
        "revenue_growth": ratios.get("revenue_growth"),
        "net_income_growth": ratios.get("net_income_growth"),
    }

    # 4️⃣ Score categories
    print("[Module-2] Applying threshold-based scoring")

    profitability_score, profit_reasons = score_category(profitability)
    liquidity_score, liquidity_reasons = score_category(liquidity)
    leverage_score, leverage_reasons = score_category(leverage)
    growth_score, growth_reasons = score_category(growth)

    # 5️⃣ Weighted final score (CORRECT LOGIC)
    final_score = (
        profitability_score * 0.40 +
        liquidity_score * 0.25 +
        leverage_score * 0.20 +
        growth_score * 0.15
    )

    final_score = round(final_score, 2)
    label = classify_stock(final_score)

    reasons = (
        profit_reasons +
        liquidity_reasons +
        leverage_reasons +
        growth_reasons
    )

    # 6️⃣ UPDATE (No Duplicates)
    db.fundamental_scores.update_one(
        {"symbol": symbol},
        {
            "$set": {
                "symbol": symbol,
                "final_fundamental_score": final_score,
                "classification": label,
                "reasons": reasons,
                "run_id": RUN_ID,
                "generated_at": datetime.utcnow(),
                "data_timestamp": datetime.utcnow(),
                "source": "Module-2 Fundamental Scoring (YahooFinance)"
            }
        },
        upsert=True
    )

    print(f"   ✔ Stored score → {final_score} ({label})\n")