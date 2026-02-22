import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.mongo_connector import get_posts, get_topic_mentions

# ============================================================================
# PROFESSIONAL COLOR SYSTEM - HEX CODES
# ============================================================================
COLORS = {
    'bg_primary': '#0F172A',
    'bg_secondary': '#111827',
    'bg_card': '#1E293B',
    'primary': '#6366F1',
    'secondary': '#2DD4BF',
    'accent': '#FB7185',
    'warning': '#FBBF24',
    'success': '#4ADE80',
    'info': '#60A5FA',
    'text_primary': '#F8FAFC',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'border': '#334155',
    'grid': '#1E293B',
    'chart_1': '#6366F1',
    'chart_2': '#2DD4BF',
    'chart_3': '#FB7185',
    'chart_4': '#FBBF24',
    'chart_5': '#A78BFA',
    'chart_6': '#4ADE80',
}

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="TrendRadar | Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background-color: {COLORS['bg_primary']};
    }}
    
    .main .block-container {{
        background-color: {COLORS['bg_primary']};
        padding: 2rem 2rem !important;
        max-width: 1600px;
        margin: 0 auto;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }}
    
    h1 {{
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    h2 {{
        font-size: 1.25rem !important;
        color: {COLORS['text_secondary']} !important;
        font-weight: 500 !important;
        margin-bottom: 1.5rem !important;
    }}
    
    .dashboard-header {{
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    .dashboard-header h1 {{
        color: {COLORS['text_primary']};
        font-size: 2rem;
        font-weight: 700;
    }}
    
    .dashboard-header p {{
        color: {COLORS['text_secondary']};
        font-size: 0.95rem;
    }}
    
    .kpi-card {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    
    .kpi-label {{
        color: {COLORS['text_secondary']};
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-value {{
        color: {COLORS['text_primary']};
        font-size: 1.75rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }}
    
    .kpi-delta {{
        color: {COLORS['text_muted']};
        font-size: 0.85rem;
    }}
    
    .section-header {{
        color: {COLORS['text_primary']};
        font-size: 1.25rem;
        font-weight: 600;
        margin: 2rem 0 1.25rem 0;
    }}
    
    .post-card {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }}
    
    .post-title {{
        color: {COLORS['text_primary']};
        font-size: 0.95rem;
        font-weight: 500;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }}
    
    .post-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }}
    
    .post-badge {{
        color: {COLORS['text_secondary']};
        font-size: 0.8rem;
    }}
    
    .post-link {{
        color: {COLORS['primary']};
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
    }}
    
    .css-1d391kg, .css-1wrcr25 {{
        background-color: {COLORS['bg_secondary']};
    }}
    
    hr {{
        border-color: {COLORS['border']};
        margin: 1.5rem 0;
    }}
    
    div[data-testid="column"] {{
        padding: 0 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {COLORS['text_secondary']};
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {COLORS['primary']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style='padding: 0 0 1rem 0;'>
        <h3 style='color: #F8FAFC; margin: 0;'>📊 TrendRadar</h3>
        <p style='color: #94A3B8; font-size: 0.8rem; margin-top: 0.25rem;'>Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;'>Time Window</p>", unsafe_allow_html=True)
    time_range = st.selectbox(
        "",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
        index=1,
        label_visibility="collapsed"
    )
    
    days_map = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    days = days_map[time_range]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;'>Topics</p>", unsafe_allow_html=True)
    all_topics = [
        "AI", "Machine Learning", "Deep Learning", "ChatGPT",
        "Neural Networks", "Robotics", "Data Science", "Python"
    ]
    
    selected_topics = st.multiselect(
        "",
        all_topics,
        default=["AI", "Machine Learning", "ChatGPT"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;'>Subreddits</p>", unsafe_allow_html=True)
    subreddits = [
        "technology", "artificial", "MachineLearning", 
        "datascience", "python", "singularity"
    ]
    
    selected_subreddits = st.multiselect(
        "",
        subreddits,
        default=subreddits[:4],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    st.markdown(f"""
    <div style='background-color: #1E293B; padding: 1rem; border-radius: 8px; border: 1px solid #334155;'>
        <p style='color: #94A3B8; margin: 0; font-size: 0.75rem;'>LAST UPDATED</p>
        <p style='color: #F8FAFC; margin: 0; font-size: 0.85rem; font-weight: 500;'>{last_updated} UTC</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================
st.markdown("""
<div class='dashboard-header'>
    <h1>📈 Trend Intelligence</h1>
    <p>Real-time social media trend detection and analysis</p>
</div>
""", unsafe_allow_html=True)

try:
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    all_posts = get_posts(start, end)
    
    if all_posts:
        df = pd.DataFrame(all_posts)
        
        if selected_subreddits:
            df = df[df['subreddit'].isin(selected_subreddits)]
        
        if len(df) > 0:
            kpi_cols = st.columns(4)
            
            with kpi_cols[0]:
                total_posts = len(df)
                posts_24h = len(df[df['created_utc'] > datetime.utcnow() - timedelta(days=1)])
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>Total Posts</div>
                    <div class='kpi-value'>{total_posts:,}</div>
                    <div class='kpi-delta'>+{posts_24h} in last 24h</div>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_cols[1]:
                avg_engagement = (df['score'] + df['num_comments'] * 2).mean()
                max_engagement = (df['score'] + df['num_comments'] * 2).max()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>Avg Engagement</div>
                    <div class='kpi-value'>{avg_engagement:.0f}</div>
                    <div class='kpi-delta'>Peak: {max_engagement:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_cols[2]:
                total_comments = df['num_comments'].sum()
                avg_comments = df['num_comments'].mean()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>Total Comments</div>
                    <div class='kpi-value'>{total_comments:,}</div>
                    <div class='kpi-delta'>Avg: {avg_comments:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with kpi_cols[3]:
                unique_authors = df['author'].nunique()
                active_subs = df['subreddit'].nunique()
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>Active Communities</div>
                    <div class='kpi-value'>{active_subs}</div>
                    <div class='kpi-delta'>{unique_authors:,} contributors</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>📈 Trend Analysis</div>", unsafe_allow_html=True)
            
            if selected_topics:
                fig = go.Figure()
                chart_colors = [COLORS['chart_1'], COLORS['chart_2'], COLORS['chart_3'], 
                               COLORS['chart_4'], COLORS['chart_5'], COLORS['chart_6']]
                
                for idx, topic in enumerate(selected_topics[:6]):
                    topic_posts = df[df['full_text'].str.contains(topic, case=False, na=False)]
                    if len(topic_posts) > 0:
                        topic_df = topic_posts.copy()
                        topic_df['date'] = pd.to_datetime(topic_df['created_utc']).dt.date
                        daily = topic_df.groupby('date').size().reset_index(name='count')
                        
                        fig.add_trace(go.Scatter(
                            x=daily['date'],
                            y=daily['count'],
                            mode='lines+markers',
                            name=topic,
                            line=dict(width=2.5, color=chart_colors[idx % len(chart_colors)]),
                            marker=dict(size=6, color=chart_colors[idx % len(chart_colors)])
                        ))
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=40, r=40, t=20, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=11, color=COLORS['text_secondary']),
                    legend=dict(
                        bgcolor=COLORS['bg_card'],
                        bordercolor=COLORS['border'],
                        borderwidth=1,
                        font=dict(color=COLORS['text_primary']),
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    xaxis=dict(
                        gridcolor=COLORS['grid'],
                        gridwidth=1,
                        linecolor=COLORS['border'],
                        tickcolor=COLORS['border'],
                        tickfont=dict(color=COLORS['text_secondary'])
                    ),
                    yaxis=dict(
                        gridcolor=COLORS['grid'],
                        gridwidth=1,
                        linecolor=COLORS['border'],
                        tickcolor=COLORS['border'],
                        tickfont=dict(color=COLORS['text_secondary'])
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select topics from the sidebar to view trends")
            
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                st.markdown("<div class='section-header'>🔥 Trending Now</div>", unsafe_allow_html=True)
                
                df['trending_score'] = df['score'] + (df['num_comments'] * 3)
                trending = df.nlargest(15, 'trending_score')
                
                for _, post in trending.iterrows():
                    time_ago = datetime.utcnow() - pd.to_datetime(post['created_utc'])
                    hours_ago = int(time_ago.total_seconds() / 3600)
                    
                    st.markdown(f"""
                    <div class='post-card'>
                        <div class='post-title'>{post['title'][:150]}...</div>
                        <div class='post-meta'>
                            <span class='post-badge'>📌 r/{post['subreddit']}</span>
                            <span class='post-badge'>👍 {post['score']:,}</span>
                            <span class='post-badge'>💬 {post['num_comments']}</span>
                            <span class='post-badge'>⏱️ {hours_ago}h ago</span>
                        </div>
                        <a href='{post['url']}' target='_blank' class='post-link'>View discussion →</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='section-header'>📊 Subreddit Activity</div>", unsafe_allow_html=True)
                
                sub_counts = df['subreddit'].value_counts().head(8)
                fig2 = go.Figure(data=[
                    go.Bar(
                        y=sub_counts.index,
                        x=sub_counts.values,
                        orientation='h',
                        marker_color=COLORS['chart_1'],
                        text=sub_counts.values,
                        textposition='outside',
                        textfont=dict(color=COLORS['text_primary'])
                    )
                ])
                
                fig2.update_layout(
                    height=300,
                    margin=dict(l=10, r=40, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=10, color=COLORS['text_secondary']),
                    xaxis=dict(
                        gridcolor=COLORS['grid'],
                        showgrid=True,
                        linecolor=COLORS['border'],
                        tickfont=dict(color=COLORS['text_secondary'])
                    ),
                    yaxis=dict(
                        gridcolor=COLORS['grid'],
                        showgrid=False,
                        linecolor=COLORS['border'],
                        tickfont=dict(color=COLORS['text_primary'])
                    ),
                    bargap=0.3,
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown("<div class='section-header' style='margin-top: 2rem;'>🏷️ Topic Mentions</div>", unsafe_allow_html=True)
                
                topic_counts = {}
                for topic in all_topics[:6]:
                    count = df['full_text'].str.contains(topic, case=False, na=False).sum()
                    if count > 0:
                        topic_counts[topic] = count
                
                if topic_counts:
                    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                        percentage = (count / len(df)) * 100
                        st.markdown(f"""
                        <div style='margin-bottom: 0.75rem;'>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                                <span style='color: {COLORS["text_primary"]}; font-size: 0.9rem;'>{topic}</span>
                                <span style='color: {COLORS["text_secondary"]}; font-size: 0.9rem;'>{count} ({percentage:.1f}%)</span>
                            </div>
                            <div style='background-color: {COLORS["border"]}; height: 4px; border-radius: 2px;'>
                                <div style='background-color: {COLORS["primary"]}; width: {percentage}%; height: 4px; border-radius: 2px;'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>⏰ Activity Patterns</div>", unsafe_allow_html=True)
            
            df['hour'] = pd.to_datetime(df['created_utc']).dt.hour
            hourly = df.groupby('hour').size().reset_index(name='count')
            
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=hourly['hour'],
                y=hourly['count'],
                marker_color=COLORS['chart_2'],
                text=hourly['count'],
                textposition='outside',
                textfont=dict(color=COLORS['text_primary'])
            ))
            
            fig3.update_layout(
                height=250,
                margin=dict(l=40, r=40, t=20, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=10, color=COLORS['text_secondary']),
                xaxis=dict(
                    title="Hour of Day (UTC)",
                    gridcolor=COLORS['grid'],
                    linecolor=COLORS['border'],
                    tickfont=dict(color=COLORS['text_secondary']),
                    tickmode='linear',
                    tick0=0,
                    dtick=2
                ),
                yaxis=dict(
                    title="Posts",
                    gridcolor=COLORS['grid'],
                    linecolor=COLORS['border'],
                    tickfont=dict(color=COLORS['text_secondary'])
                ),
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.warning("No posts match your selected filters.")
    else:
        st.warning("No data available. Please run the collector first.")

except Exception as e:
    st.error(f"Error loading dashboard: {str(e)}")
    st.info("Make sure MongoDB is running: `docker start mongodb`")
