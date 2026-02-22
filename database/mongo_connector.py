#!/usr/bin/env python3
"""
MongoDB connection handler for TrendRadar
"""

import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Get MongoDB URI from environment
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "trendradar"
COLLECTION_NAME = "reddit_posts"

class MongoDB:
    """Singleton MongoDB connection"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.client = MongoClient(MONGO_URI)
                cls._instance.db = cls._instance.client[DB_NAME]
                cls._instance.collection = cls._instance.db[COLLECTION_NAME]
                
                # Create indexes for better query performance
                cls._instance.collection.create_index("id", unique=True)
                cls._instance.collection.create_index("created_utc")
                cls._instance.collection.create_index("subreddit")
                cls._instance.collection.create_index([("full_text", "text")])  # Text index for search
                
                print("✅ Connected to MongoDB successfully")
            except errors.ConnectionError as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                cls._instance = None
        return cls._instance
    
    def save_posts(self, posts):
        """Save posts to database, avoiding duplicates"""
        if not posts:
            return 0
        
        try:
            # Use update_one with upsert to avoid duplicates
            result = 0
            for post in posts:
                self.collection.update_one(
                    {"id": post["id"]},
                    {"$set": post},
                    upsert=True
                )
                result += 1
            return result
        except Exception as e:
            print(f"❌ Error saving posts: {e}")
            return 0
    
    def get_posts(self, start_date=None, end_date=None, subreddit=None, limit=1000):
        """Retrieve posts with filters"""
        query = {}
        
        if start_date or end_date:
            query["created_utc"] = {}
            if start_date:
                query["created_utc"]["$gte"] = start_date
            if end_date:
                query["created_utc"]["$lte"] = end_date
        
        if subreddit:
            query["subreddit"] = subreddit
        
        cursor = self.collection.find(query).sort("created_utc", -1).limit(limit)
        return list(cursor)
    
    def get_topic_mentions(self, topic, days=7):
        """Get mention counts for a topic over time"""
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        
        # Text search query
        query = {
            "full_text": {"$regex": topic, "$options": "i"},
            "created_utc": {"$gte": start, "$lte": end}
        }
        
        cursor = self.collection.find(query).sort("created_utc", 1)
        return list(cursor)

# Global instance
db = MongoDB()

def save_posts(posts):
    """Convenience function to save posts"""
    if db:
        return db.save_posts(posts)
    return 0

def get_posts(start_date=None, end_date=None, subreddit=None, limit=1000):
    """Convenience function to get posts"""
    if db:
        return db.get_posts(start_date, end_date, subreddit, limit)
    return []

def get_topic_mentions(topic, days=7):
    """Convenience function to get topic mentions"""
    if db:
        return db.get_topic_mentions(topic, days)
    return []
