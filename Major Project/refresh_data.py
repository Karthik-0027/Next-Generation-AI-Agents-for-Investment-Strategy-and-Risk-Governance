from data_collection.market_data import run_market_data_collection
from data_collection.news_data import run_news_collection


def force_refresh():

    print("\n🔄 FORCE REFRESH INITIATED\n")

    print("📊 Refreshing Market Data...\n")
    run_market_data_collection()

    print("📰 Refreshing Sentiment Data...\n")
    run_news_collection()

    print("\n✅ Force refresh completed successfully.\n")


if __name__ == "__main__":
    force_refresh()