from datetime import datetime


def run_analytics_engine(db):

    portfolio_collection = db["portfolio_allocation"]
    backtest_collection = db["backtest_results"]
    analytics_collection = db["analytics_summary"]

    print("\n[ANALYTICS] Generating system analytics summary...\n")

    portfolio = list(portfolio_collection.find({}))

    if not portfolio:
        print("[ANALYTICS] No portfolio data available.")
        return

    # Portfolio statistics
    portfolio_size = len(portfolio)

    # Sum of allocated capital
    total_capital = sum(stock.get("capital_allocated", 0) for stock in portfolio)

    # Fetch backtest results
    backtest = backtest_collection.find_one({"type": "portfolio_backtest"})

    if not backtest:
        print("[ANALYTICS] No backtest results available.")
        return

    portfolio_return = backtest.get("portfolio_return", 0)
    benchmark_return = backtest.get("benchmark_return", 0)
    alpha = backtest.get("alpha", 0)
    sharpe_ratio = backtest.get("sharpe_ratio", 0)
    max_drawdown = backtest.get("max_drawdown", 0)

    # Store analytics summary
    analytics_collection.update_one(
        {"type": "system_summary"},
        {"$set": {
            "portfolio_size": portfolio_size,
            "total_capital_allocated": total_capital,
            "portfolio_return": portfolio_return,
            "benchmark_return": benchmark_return,
            "alpha": alpha,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "timestamp": datetime.utcnow()
        }},
        upsert=True
    )

    # Console Output
    print("[ANALYTICS] Portfolio Size:", portfolio_size)
    print("[ANALYTICS] Total Capital Allocated:", total_capital)
    print("[ANALYTICS] Portfolio Return:", round(portfolio_return, 4))
    print("[ANALYTICS] Benchmark Return:", round(benchmark_return, 4))
    print("[ANALYTICS] Alpha:", round(alpha, 4))
    print("[ANALYTICS] Sharpe Ratio:", round(sharpe_ratio, 4))
    print("[ANALYTICS] Max Drawdown:", round(max_drawdown, 4))

    print("\n[ANALYTICS] Analytics summary stored successfully.\n")