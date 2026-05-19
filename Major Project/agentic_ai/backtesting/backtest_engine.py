import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf


class BacktestEngine:

    def __init__(self, db):
        self.db = db

    def run_backtest(self):

        portfolio_collection = self.db["portfolio_allocation"]
        backtest_collection = self.db["backtest_results"]

        portfolio = list(portfolio_collection.find())

        if not portfolio:
            print("No portfolio allocation found.")
            return

        symbols = [stock["symbol"] for stock in portfolio]
        weights = {stock["symbol"]: stock["allocation_weight"] for stock in portfolio}

        print("\n📊 Running backtest for:", symbols)

        # -----------------------------------
        # Download historical price data
        # -----------------------------------

        try:
            price_data = yf.download(
                symbols,
                period="5y",
                auto_adjust=True,
                progress=False
            )["Close"]
        except Exception as e:
            print("Error downloading price data:", e)
            return

        if price_data.empty:
            print("Price data is empty.")
            return

        # ✅ FIXED: pct_change warning
        returns = price_data.pct_change(fill_method=None).dropna()

        # -----------------------------------
        # Portfolio returns
        # -----------------------------------

        weights_series = pd.Series(weights)

        portfolio_returns = returns.mul(weights_series, axis=1).sum(axis=1)

        initial_capital = 1000
        portfolio_values = initial_capital * (1 + portfolio_returns).cumprod()

        # -----------------------------------
        # Equity Curve
        # -----------------------------------

        equity_curve = []

        for date, value in portfolio_values.items():
            equity_curve.append({
                "date": str(date.date()),
                "portfolio": float(value)
            })

        # -----------------------------------
        # Benchmark comparison (AAPL)
        # -----------------------------------

        try:
            benchmark_data = yf.download(
                "AAPL",
                period="5y",
                auto_adjust=True,
                progress=False
            )["Close"]
        except Exception as e:
            print("Error downloading benchmark data:", e)
            return

        # ✅ FIXED: pct_change warning
        benchmark_returns = benchmark_data.pct_change(fill_method=None).dropna()

        benchmark_values = initial_capital * (1 + benchmark_returns).cumprod()

        # -----------------------------------
        # Performance Metrics (FULL FIX)
        # -----------------------------------

        portfolio_final = portfolio_values.iloc[-1]
        benchmark_final = benchmark_values.iloc[-1]

        # ✅ Ensure scalar values (fix Series warning)
        if isinstance(portfolio_final, pd.Series):
            portfolio_final = portfolio_final.iloc[0]

        if isinstance(benchmark_final, pd.Series):
            benchmark_final = benchmark_final.iloc[0]

        portfolio_return = float((portfolio_final / initial_capital) - 1)
        benchmark_return = float((benchmark_final / initial_capital) - 1)

        alpha = float(portfolio_return - benchmark_return)

        # Sharpe Ratio (safe)
        if np.std(portfolio_returns) != 0:
            sharpe_ratio = float(
                np.mean(portfolio_returns) / np.std(portfolio_returns) * np.sqrt(252)
            )
        else:
            sharpe_ratio = 0.0

        # Drawdown
        drawdown = portfolio_values / portfolio_values.cummax() - 1
        max_drawdown = float(drawdown.min())

        # -----------------------------------
        # Store Results
        # -----------------------------------

        result = {
            "type": "portfolio_backtest",
            "portfolio_return": portfolio_return,
            "benchmark_return": benchmark_return,
            "alpha": alpha,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "equity_curve": equity_curve,
            "timestamp": datetime.utcnow()
        }

        # Replace old results (clean DB)
        backtest_collection.delete_many({"type": "portfolio_backtest"})
        backtest_collection.insert_one(result)

        print("✅ Backtest completed successfully.\n")


# ---------------------------------------------------
# Function used by main.py
# ---------------------------------------------------

def run_backtest_engine(db):
    engine = BacktestEngine(db)
    engine.run_backtest()