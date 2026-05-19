from database.mongo_client import db

db["fundamentals_data"].insert_one({"status": "collection_created"})
print("Collection created successfully")
