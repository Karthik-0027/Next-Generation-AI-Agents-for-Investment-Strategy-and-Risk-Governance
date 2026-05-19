from database.mongo_client import get_db

from agentic_ai.signals.fundamentals_agent import run_fundamentals_agent
from agentic_ai.signals.sentiment_agent import run_sentiment_agent
from agentic_ai.signals.strategy_agent import run_strategy_agent
from agentic_ai.risk.risk_agent import run_risk_agent
from agentic_ai.governance.governance_agent import run_governance_agent


def run_module4():

    db = get_db()

    print("\n🔄 Clearing previous Module 4 outputs...")

    db["agent_signals"].delete_many({})
    db["risk_flags"].delete_many({})
    db["agent_decisions"].delete_many({})
    db["governance_logs"].delete_many({})

    print("🚀 Running Signal Agents...")
    run_fundamentals_agent(db)
    run_sentiment_agent(db)
    run_strategy_agent(db)

    # ---- Dynamic validation ----
    unique_symbols = db["market_data"].distinct("symbol")
    expected_signals = len(unique_symbols) * 3
    signal_count = db["agent_signals"].count_documents({})

    if signal_count != expected_signals:
        raise ValueError(
            f"Signal count mismatch! Expected {expected_signals}, got {signal_count}"
        )

    print("⚠ Running Risk Agent...")
    run_risk_agent(db)

    risk_count = db["risk_flags"].count_documents({})

    if risk_count != len(unique_symbols):
        raise ValueError(
            f"Risk count mismatch! Expected {len(unique_symbols)}, got {risk_count}"
        )

    print("🏛 Running Governance Agent...")
    run_governance_agent(db)

    decision_count = db["agent_decisions"].count_documents({})

    if decision_count != len(unique_symbols):
        raise ValueError(
            f"Decision count mismatch! Expected {len(unique_symbols)}, got {decision_count}"
        )

    print("✅ Module 4 executed successfully.\n")