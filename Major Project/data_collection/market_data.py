import yfinance as yf
from datetime import datetime
from database.mongo_client import get_db

# Get database
db = get_db()

# MongoDB collections
fundamentals_col = db["fundamentals_data"]
market_col = db["market_data"]


def run_market_data_collection():

    print("[INFO] Updating market_data collection (no full deletion)")

    # Get all symbols dynamically from fundamentals_data
    symbols = fundamentals_col.distinct("symbol")
    print(f"[INFO] Symbols found in fundamentals_data: {symbols}")

    for symbol in symbols:
        print(f"[FETCHING] Market data for {symbol}")

        try:
            df = yf.download(
                symbol,
                period="5y",
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if df.empty:
                print(f"[SKIPPED] No market data for {symbol}")
                continue

            ohlcv = []

            for date, row in df.iterrows():
                ohlcv.append({
                    "date": date.to_pydatetime(),
                    "open": float(row["Open"].iloc[0]),
                    "high": float(row["High"].iloc[0]),
                    "low": float(row["Low"].iloc[0]),
                    "close": float(row["Close"].iloc[0]),
                    "volume": int(row["Volume"].iloc[0])
                })

            document = {
                "symbol": symbol,
                "ohlcv": ohlcv,
                "source": "YahooFinance (yfinance)",
                "timeframe": "5y_daily",
                "last_updated": datetime.utcnow()
            }

            # ✅ UPDATE instead of INSERT
            market_col.update_one(
                {"symbol": symbol},
                {"$set": document},
                upsert=True
            )

            print(f"[UPDATED] {symbol}")

        except Exception as e:
            print(f"[ERROR] Failed for {symbol}: {e}")

    print("\n[SUCCESS] Market data refreshed successfully.\n")


if __name__ == "__main__":
    run_market_data_collection()