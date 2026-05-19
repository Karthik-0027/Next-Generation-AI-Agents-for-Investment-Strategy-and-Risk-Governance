from database.mongo_client import get_db

db = get_db()


def load_latest_fundamentals(symbol):
    """
    Load latest and previous annual income statement
    + latest balance sheet.

    Returns:
        current_income,
        previous_income,
        balance_sheet
    """

    doc = db.fundamentals_data.find_one({"symbol": symbol})

    if not doc:
        return None, None, None

    income_stmt = doc.get("income_statement", {})
    balance_sheet = doc.get("balance_sheet", {})

    if not income_stmt or not balance_sheet:
        return None, None, None

    # -----------------------------
    # Extract yearly income data
    # -----------------------------
    if isinstance(income_stmt, dict) and len(income_stmt) >= 2:

        # Sort years descending (latest first)
        sorted_years = sorted(income_stmt.keys(), reverse=True)

        latest_year = sorted_years[0]
        previous_year = sorted_years[1]

        current_income = income_stmt.get(latest_year, {})
        previous_income = income_stmt.get(previous_year, {})

    else:
        return None, None, None

    # -----------------------------
    # Extract latest balance sheet
    # -----------------------------
    if isinstance(balance_sheet, dict) and len(balance_sheet) > 0:
        sorted_balance_years = sorted(balance_sheet.keys(), reverse=True)
        latest_balance_year = sorted_balance_years[0]
        balance_sheet = balance_sheet.get(latest_balance_year, {})
    else:
        return None, None, None

    return current_income, previous_income, balance_sheet