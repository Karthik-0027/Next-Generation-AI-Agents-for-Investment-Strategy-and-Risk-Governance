import yfinance as yf
from datetime import datetime
from database.mongo_client import db

fundamentals_collection = db["fundamentals_data"]


# -------------------------------------------------
# Helper: DataFrame → MongoDB-safe dict
# -------------------------------------------------
def df_to_mongo_dict(df):
    """
    Convert pandas DataFrame to MongoDB-safe dict:
    - Convert Timestamp keys to string
    """
    if df is None or df.empty:
        return {}

    safe_dict = {}
    for col, series in df.items():
        safe_dict[str(col)] = series.to_dict()

    return safe_dict


# -------------------------------------------------
# Core fundamentals collector (UNCHANGED LOGIC)
# -------------------------------------------------
def collect_fundamentals(symbol: str, market: str):
    print(f"[FETCHING] Fundamentals using yfinance for {symbol}")

    ticker = yf.Ticker(symbol)

    # -------- COMPANY INFO --------
    info = ticker.info
    if not info or "symbol" not in info:
        print("[SKIPPED] Invalid company info")
        return

    # -------- FINANCIAL STATEMENTS --------
    income_stmt = ticker.financials
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
        print("[SKIPPED] Financial statements are empty")
        return

    document = {
        "symbol": symbol,
        "market": market,
        "overview": info,
        "income_statement": df_to_mongo_dict(income_stmt),
        "balance_sheet": df_to_mongo_dict(balance_sheet),
        "cash_flow": df_to_mongo_dict(cash_flow),
        "frequency": "annual",
        "source": "YahooFinance (yfinance)",
        "last_updated": datetime.utcnow()
    }

    fundamentals_collection.update_one(
        {"symbol": symbol},
        {"$set": document},
        upsert=True
    )

    print(f"[STORED] Fundamentals for {symbol}")


# -------------------------------------------------
# FINAL STOCK UNIVERSE (LOCKED)
# -------------------------------------------------
INDIAN_STOCKS = [
    "TCS.NS",
    "INFY.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "ITC.NS",
    "LT.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "HINDUNILVR.NS",
    "AXISBANK.NS",
    "TATAMOTORS.NS"
]

US_STOCKS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "TSLA",
    "JPM"
]


# -------------------------------------------------
# MAIN RUNNER (NEW, SAFE ADDITION)
# -------------------------------------------------
def run_fundamentals_pipeline():
    print("\n[START] Fundamentals data collection\n")

    for symbol in INDIAN_STOCKS:
        collect_fundamentals(symbol, market="India")

    for symbol in US_STOCKS:
        collect_fundamentals(symbol, market="US")

    print("\n[SUCCESS] Fundamentals data collection completed")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    run_fundamentals_pipeline()
