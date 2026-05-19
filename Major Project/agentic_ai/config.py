# agentic_ai/config.py

AGENT_WEIGHTS = {
    "FUNDAMENTALS": 0.4,
    "SENTIMENT": 0.2,
    "STRATEGY": 0.4
}

SIGNAL_ENCODING = {
    "BUY": 1,
    "HOLD": 0,
    "SELL": -1
}

VOLATILITY_THRESHOLD = 0.05
EXTREME_VOL_THRESHOLD = 0.08

DECISION_THRESHOLD = 0.3