import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.mongo_connector import get_posts, get_topic_mentions

# Page config
st.set_page_config(
    page_title="TrendRadar",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
    }
    .main-header {
        color: #F8FAFC;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.5rem;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>📊 TrendRadar</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    time_range = st.selectbox("Time Range", ["Last 24 Hours", "Last 7 Days", "Last 30 Days"], index=1)
    
    days_map = {"Last 24 Hours": 1, "Last 7 Days": 7, "Last 30 Days": 30}
    days = days_map[time_range]

# Get data
try:
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    posts = get_posts(start, end)
    
    if posts:
        st.success(f"✅ Loaded {len(posts)} posts")
        
        # Simple metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Posts", len(posts))
        with col2:
            total_comments = sum(p.get('num_comments', 0) for p in posts)
            st.metric("Total Comments", total_comments)
        with col3:
            avg_score = sum(p.get('score', 0) for p in posts) / len(posts)
            st.metric("Avg Score", f"{avg_score:.1f}")
        
        # Recent posts
        st.subheader("📌 Recent Posts")
        for post in sorted(posts, key=lambda x: x['created_utc'], reverse=True)[:10]:
            with st.container():
                st.markdown(f"**{post.get('title', 'No title')[:100]}...**")
                st.caption(f"r/{post.get('subreddit', 'unknown')} | 👍 {post.get('score', 0)} | 💬 {post.get('num_comments', 0)}")
                st.markdown(f"[Link]({post.get('url', '#')})")
                st.divider()
    else:
        st.warning("No posts found. Run the collector first!")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
