def score_category(ratios: dict):
    """
    Calibrated scoring model (realistic market thresholds)
    Returns score (0–100) and reasons.
    """

    score = 0
    max_score = 0
    reasons = []

    for metric, value in ratios.items():

        if value is None:
            continue

        max_score += 1

        # -------- PROFITABILITY --------
        if metric == "net_profit_margin":
            if value > 0.10:
                score += 1
                reasons.append("Healthy profit margin")

        elif metric == "roe":
            if value > 0.12:
                score += 1
                reasons.append("Strong ROE")

        elif metric == "roa":
            if value > 0.05:
                score += 1
                reasons.append("Efficient asset usage")

        # -------- LIQUIDITY --------
        elif metric == "current_ratio":
            if value >= 1.2:
                score += 1
                reasons.append("Acceptable liquidity")

        elif metric == "quick_ratio":
            if value >= 0.8:
                score += 1
                reasons.append("Healthy quick ratio")

        # -------- LEVERAGE --------
        elif metric == "debt_to_equity":
            if value <= 2.0:
                score += 1
                reasons.append("Controlled leverage")

        # -------- GROWTH --------
        elif metric == "revenue_growth":
            if value > 0.05:
                score += 1
                reasons.append("Revenue growing")

        elif metric == "net_income_growth":
            if value > 0.05:
                score += 1
                reasons.append("Earnings growing")

    if max_score == 0:
        return 0, []

    final_score = (score / max_score) * 100
    return round(final_score, 2), reasons