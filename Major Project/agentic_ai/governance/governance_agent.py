from datetime import datetime
from agentic_ai.config import AGENT_WEIGHTS, SIGNAL_ENCODING

def run_governance_agent(db):

    signals = db["agent_signals"]
    risks = db["risk_flags"]
    decisions = db["agent_decisions"]
    logs = db["governance_logs"]

    symbols = signals.distinct("symbol")

    for symbol in symbols:

        stock_signals = list(signals.find({"symbol": symbol}))
        risk = risks.find_one({"symbol": symbol})

        weighted_score = 0
        summary = {}

        for s in stock_signals:

            weight = AGENT_WEIGHTS[s["agent"]]
            encoded = SIGNAL_ENCODING[s["signal"]]

            weighted_score += weight * encoded * s["confidence"]

            summary[s["agent"]] = s["signal"]

        # Convert weighted score to 0-100 composite score
        composite_score = (weighted_score + 1) * 50

        # Risk Adjustment
        if risk and risk.get("volatility_flag"):
            composite_score -= 10

        if risk and risk.get("hard_block"):
            composite_score -= 20

        composite_score = max(0, min(100, composite_score))

        # Final Decision Logic
        if composite_score >= 60:
            final = "BUY"
        elif composite_score >= 40:
            final = "HOLD"
        else:
            final = "SELL"

        decisions.update_one(
            {"symbol": symbol},
            {"$set": {
                "symbol": symbol,
                "final_decision": final,
                "weighted_score": round(weighted_score, 4),
                "composite_score": round(composite_score, 2),
                "confidence_score": abs(round(weighted_score, 4)),
                "agent_summary": summary,
                "risk_applied": risk,
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )

        logs.update_one(
            {"symbol": symbol},
            {"$set": {
                "symbol": symbol,
                "agents": summary,
                "risk_flags": risk,
                "final_decision": final,
                "composite_score": round(composite_score, 2),
                "timestamp": datetime.utcnow()
            }},
            upsert=True
        )