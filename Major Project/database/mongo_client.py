from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_ai_project"]

market_col = db["market_data"]

# ADD THIS
def get_db():
    return db
