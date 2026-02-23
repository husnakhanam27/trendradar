import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
print(f"URI from .env: {uri}")

try:
    client = MongoClient(uri)
    db = client.trendradar
    collections = db.list_collection_names()
    print(f"✅ Connected successfully!")
    print(f"Collections: {collections}")
except Exception as e:
    print(f"❌ Error: {e}")
