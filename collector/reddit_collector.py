#!/usr/bin/env python3
"""
Reddit JSON Collector for TrendRadar
Fetches posts using public JSON endpoints (no API key needed!)
"""

import requests
import time
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.mongo_connector import save_posts

# Load environment variables
load_dotenv()

# Configuration
USER_AGENT = "trendradar/1.0 (educational project)"
REQUEST_DELAY = 2  # Delay between requests to be polite to Reddit's servers

def fetch_subreddit_posts(subreddit, sort="new", limit=100):
    """
    Fetch posts from a subreddit using JSON endpoint
    
    Args:
        subreddit (str): Name of subreddit (without r/)
        sort (str): 'hot', 'new', 'top', or 'rising'
        limit (int): Number of posts to fetch (max 100)
    
    Returns:
        list: List of post dictionaries
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    headers = {'User-Agent': USER_AGENT}
    
    try:
        print(f"Fetching from r/{subreddit}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        posts = []
        for post in data['data']['children']:
            p = post['data']
            
            # Combine title and text for analysis
            full_text = p['title']
            if p.get('selftext'):
                full_text += " " + p['selftext']
            
            post_data = {
                'id': p['id'],
                'title': p['title'],
                'text': p.get('selftext', '')[:500],
                'full_text': full_text[:1000],
                'subreddit': subreddit,
                'author': p.get('author', '[deleted]'),
                'created_utc': datetime.utcfromtimestamp(p['created_utc']),
                'score': p['score'],
                'num_comments': p['num_comments'],
                'url': f"https://reddit.com{p['permalink']}",
                'upvote_ratio': p.get('upvote_ratio', 0),
                'collected_at': datetime.utcnow()
            }
            posts.append(post_data)
        
        print(f"  ✓ Got {len(posts)} posts from r/{subreddit}")
        return posts
    
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching from r/{subreddit}: {e}")
        return []
    except KeyError as e:
        print(f"  ✗ Error parsing data from r/{subreddit}: {e}")
        return []

def fetch_multiple_subreddits(subreddits, sort="new", posts_per_subreddit=50):
    """
    Fetch posts from multiple subreddits
    
    Args:
        subreddits (list): List of subreddit names
        sort (str): Sort order for posts
        posts_per_subreddit (int): Posts to fetch from each
    
    Returns:
        list: Combined list of all posts
    """
    all_posts = []
    
    for subreddit in subreddits:
        posts = fetch_subreddit_posts(subreddit, sort, posts_per_subreddit)
        all_posts.extend(posts)
        time.sleep(REQUEST_DELAY)
    
    print(f"\nTotal posts collected: {len(all_posts)}")
    return all_posts

def job():
    """Main job function to be called by scheduler"""
    print(f"\n{'='*50}")
    print(f"Running collection at {datetime.utcnow()} UTC")
    print('='*50)
    
    # Subreddits to monitor
    subreddits = [
        "technology",
        "artificial",
        "MachineLearning",
        "dataisbeautiful",
        "python",
        "programming",
        "Futureology",
        "singularity"
    ]
    
    posts = fetch_multiple_subreddits(subreddits, sort="new", posts_per_subreddit=25)
    
    if posts:
        saved_count = save_posts(posts)
        print(f"\n✅ Saved {saved_count} posts to MongoDB")
    else:
        print("\n⚠️ No posts collected")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("Running collector once...")
        job()
    else:
        import schedule
        
        print("Starting Reddit JSON Collector (runs every hour)...")
        print("Press Ctrl+C to stop")
        
        job()
        schedule.every().hour.do(job)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nStopping collector...")
