"""
dashboard/server.py

Flask backend — replaces dash_app.py completely.
All collection names and field names match your EXACT MongoDB schema.

COLLECTIONS (confirmed from source code):
  market_data          → fields: symbol, ohlcv[{date,open,high,low,close,volume}], last_updated
  sentiment_aggregated → fields: symbol, average_sentiment_score, final_sentiment_label, news_count, generated_at
  fundamental_scores   → fields: symbol, final_fundamental_score, classification, reasons
  agent_signals        → fields: symbol, agent, signal, confidence
  risk_flags           → fields: symbol, volatility, volatility_flag, conflict_flag, hard_block
  agent_decisions      → fields: symbol, final_decision, composite_score, confidence_score, weighted_score, agent_summary
  portfolio_allocation → fields: symbol, composite_score, allocation_weight, capital_allocated, decision
  backtest_results     → fields: type="portfolio_backtest", portfolio_return, benchmark_return, alpha,
                                  sharpe_ratio, max_drawdown, equity_curve[{date, portfolio}]
  analytics_summary    → fields: type="system_summary", portfolio_size, total_capital_allocated,
                                  portfolio_return, benchmark_return, alpha, sharpe_ratio, max_drawdown, timestamp

AGENT WEIGHTS (from agentic_ai/config.py):
  FUNDAMENTALS: 0.4 (40%)
  SENTIMENT:    0.2 (20%)
  STRATEGY:     0.4 (40%)
"""

import sys
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, jsonify

sys.path.append(str(Path(__file__).parent.parent))

from database.mongo_client import get_db

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

db = get_db()


# ── Serve Dashboard ───────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ── API 1: Performance KPIs ───────────────────────────────────────────────────
# Source: analytics_summary {type: "system_summary"}

@app.route("/api/performance")
def performance():
    data = db["analytics_summary"].find_one(
        {"type": "system_summary"}, {"_id": 0}
    ) or {}
    return jsonify({
        "portfolio_return":        data.get("portfolio_return", 0),
        "benchmark_return":        data.get("benchmark_return", 0),
        "alpha":                   data.get("alpha", 0),
        "sharpe_ratio":            data.get("sharpe_ratio", 0),
        "max_drawdown":            data.get("max_drawdown", 0),
        "total_capital_allocated": data.get("total_capital_allocated", 0),
        "portfolio_size":          data.get("portfolio_size", 0),
        "timestamp":               str(data.get("timestamp", "")),
    })


# ── API 2: Portfolio Allocation ───────────────────────────────────────────────
# Source: portfolio_allocation

@app.route("/api/portfolio")
def portfolio():
    records = list(db["portfolio_allocation"].find({}, {"_id": 0}))
    return jsonify([{
        "symbol":            r.get("symbol", ""),
        "allocation_weight": r.get("allocation_weight", 0),
        "capital_allocated": r.get("capital_allocated", 0),
        "composite_score":   r.get("composite_score", 0),
    } for r in records])


# ── API 3: AI Decisions ───────────────────────────────────────────────────────
# Source: agent_decisions

@app.route("/api/decisions")
def decisions():
    records = list(db["agent_decisions"].find({}, {"_id": 0}))
    total = len(records) or 1

    buy  = sum(1 for r in records if r.get("final_decision") == "BUY")
    hold = sum(1 for r in records if r.get("final_decision") == "HOLD")
    sell = sum(1 for r in records if r.get("final_decision") == "SELL")

    clean = []
    for r in records:
        ag = r.get("agent_summary", {})
        # Generate explanation (matches your old dash_app explanation() function)
        decision = r.get("final_decision", "HOLD")
        if decision == "BUY":
            explanation = "Positive signals detected across agents."
        elif decision == "SELL":
            explanation = "Weak signals detected across analysis."
        else:
            explanation = "Mixed signals detected across agents."

        clean.append({
            "symbol":              r.get("symbol", ""),
            "final_decision":      decision,
            "composite_score":     round(r.get("composite_score", 0), 2),
            "confidence_score":    round(r.get("confidence_score", 0), 4),
            "weighted_score":      round(r.get("weighted_score", 0), 4),
            "fundamentals_signal": ag.get("FUNDAMENTALS", "—"),
            "sentiment_signal":    ag.get("SENTIMENT", "—"),
            "strategy_signal":     ag.get("STRATEGY", "—"),
            "explanation":         explanation,
        })

    # Sort by composite score descending (same as portfolio engine)
    clean.sort(key=lambda x: x["composite_score"], reverse=True)

    return jsonify({
        "records": clean,
        "distribution": {
            "buy":   round(buy  / total * 100),
            "hold":  round(hold / total * 100),
            "sell":  round(sell / total * 100),
            "total": len(records),
        }
    })


# ── API 4: Equity Curve + Benchmark + Drawdown ────────────────────────────────
# Source: backtest_results {type: "portfolio_backtest"}
# equity_curve is stored as list of {date: str, portfolio: float}

@app.route("/api/equity-curve")
def equity_curve():
    data = db["backtest_results"].find_one(
        {"type": "portfolio_backtest"}, {"_id": 0}
    ) or {}

    equity_curve_raw = data.get("equity_curve", [])
    dates     = [e["date"] for e in equity_curve_raw]
    portfolio = [e["portfolio"] for e in equity_curve_raw]

    # Reconstruct benchmark (same logic as your dash_app.py)
    benchmark = []
    if portfolio and data.get("benchmark_return") is not None:
        initial     = portfolio[0]
        bench_final = initial * (1 + data.get("benchmark_return", 0))
        n = len(portfolio)
        benchmark = [
            initial + (bench_final - initial) * (i / max(n - 1, 1))
            for i in range(n)
        ]

    # Drawdown series (same as your dash_app.py drawdown calculation)
    drawdown = []
    if portfolio:
        rolling_max = portfolio[0]
        for v in portfolio:
            if v > rolling_max:
                rolling_max = v
            dd = (v - rolling_max) / rolling_max if rolling_max else 0
            drawdown.append(round(dd, 6))

    # Cumulative return (same as your dash_app.py)
    cumulative = []
    if portfolio:
        base = portfolio[0]
        cumulative = [round((v / base) - 1, 6) for v in portfolio]

    return jsonify({
        "dates":            dates,
        "portfolio":        portfolio,
        "benchmark":        benchmark,
        "drawdown":         drawdown,
        "cumulative":       cumulative,
        "portfolio_return": data.get("portfolio_return", 0),
        "benchmark_return": data.get("benchmark_return", 0),
        "alpha":            data.get("alpha", 0),
        "sharpe_ratio":     data.get("sharpe_ratio", 0),
        "max_drawdown":     data.get("max_drawdown", 0),
    })


# ── API 5: Agent Weights ──────────────────────────────────────────────────────
# Source: agentic_ai/config.py (AGENT_WEIGHTS)

@app.route("/api/agent-contributions")
def agent_contributions():
    # Exact values from your agentic_ai/config.py AGENT_WEIGHTS
    return jsonify({
        "fundamentals_pct": 40,   # FUNDAMENTALS: 0.4
        "sentiment_pct":    20,   # SENTIMENT: 0.2
        "strategy_pct":     40,   # STRATEGY: 0.4
    })


# ── API 6: Ticker Tape ────────────────────────────────────────────────────────
# Source: market_data → last 2 ohlcv entries per symbol

@app.route("/api/ticker")
def ticker():
    results = []
    try:
        for doc in db["market_data"].find(
            {}, {"symbol": 1, "ohlcv": {"$slice": -2}}
        ):
            symbol = doc.get("symbol", "")
            ohlcv  = doc.get("ohlcv", [])
            if len(ohlcv) >= 2:
                prev_close = ohlcv[-2].get("close", 0)
                last_close = ohlcv[-1].get("close", 0)
                change_pct = (
                    (last_close - prev_close) / prev_close * 100
                ) if prev_close else 0
                results.append({
                    "symbol":     symbol,
                    "price":      round(last_close, 2),
                    "change_pct": round(change_pct, 2),
                })
    except Exception as e:
        print(f"[Ticker] Error: {e}")
    return jsonify(results)


# ── API 7: Sentiment Data ─────────────────────────────────────────────────────
# Source: sentiment_aggregated

@app.route("/api/sentiment")
def sentiment():
    records = list(db["sentiment_aggregated"].find({}, {"_id": 0}))
    return jsonify([{
        "symbol":     r.get("symbol", ""),
        "score":      r.get("average_sentiment_score", 0),
        "label":      r.get("final_sentiment_label", "NEUTRAL"),
        "news_count": r.get("news_count", 0),
    } for r in records])


# ── API 8: Risk Flags ─────────────────────────────────────────────────────────
# Source: risk_flags

@app.route("/api/risk")
def risk():
    records = list(db["risk_flags"].find({}, {"_id": 0}))
    return jsonify([{
        "symbol":          r.get("symbol", ""),
        "volatility":      round(r.get("volatility", 0), 4),
        "volatility_flag": r.get("volatility_flag", False),
        "conflict_flag":   r.get("conflict_flag", False),
        "hard_block":      r.get("hard_block", False),
    } for r in records])


# ── API 9: System Status ──────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    data = db["analytics_summary"].find_one(
        {"type": "system_summary"}, {"_id": 0, "timestamp": 1}
    ) or {}
    return jsonify({
        "last_updated": str(data.get("timestamp", datetime.utcnow())),
        "status":       "ACTIVE",
        "db":           "stock_ai_project",
    })


if __name__ == "__main__":
    app.run(debug=True, port=8050)
