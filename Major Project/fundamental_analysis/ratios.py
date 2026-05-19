from fundamental_analysis.cleaner import to_float, safe_divide


def compute_ratios(current_income, previous_income, balance):
    """
    Compute financial ratios including YoY growth.
    """

    try:
        # --- CURRENT YEAR ---
        revenue = to_float(current_income.get("Total Revenue"))
        net_income = to_float(current_income.get("Net Income"))
        operating_income = to_float(current_income.get("Operating Income"))

        # --- PREVIOUS YEAR ---
        prev_revenue = to_float(previous_income.get("Total Revenue"))
        prev_net_income = to_float(previous_income.get("Net Income"))

        # --- BALANCE SHEET ---
        total_assets = to_float(balance.get("Total Assets"))
        total_equity = to_float(balance.get("Total Stockholder Equity"))
        current_assets = to_float(balance.get("Total Current Assets"))
        current_liabilities = to_float(balance.get("Total Current Liabilities"))
        inventory = to_float(balance.get("Inventory"))
        total_debt = to_float(balance.get("Total Debt"))

        ratios = {}

        # --- PROFITABILITY ---
        ratios["net_profit_margin"] = safe_divide(net_income, revenue)
        ratios["roe"] = safe_divide(net_income, total_equity)
        ratios["roa"] = safe_divide(net_income, total_assets)

        # --- LIQUIDITY ---
        ratios["current_ratio"] = safe_divide(current_assets, current_liabilities)
        ratios["quick_ratio"] = safe_divide(
            current_assets - inventory, current_liabilities
        )

        # --- LEVERAGE ---
        ratios["debt_to_equity"] = safe_divide(total_debt, total_equity)

        # --- GROWTH (YoY) ---
        ratios["revenue_growth"] = safe_divide(
            revenue - prev_revenue, prev_revenue
        )

        ratios["net_income_growth"] = safe_divide(
            net_income - prev_net_income, prev_net_income
        )

        return ratios

    except Exception as e:
        print(f"[ERROR] Ratio computation failed: {e}")
        return None