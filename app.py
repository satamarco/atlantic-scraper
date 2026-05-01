import streamlit as st
import json
import os
from datetime import datetime, timezone, timedelta
import time

@st.cache_resource
def install_playwright_browsers():
    os.system("playwright install chromium")

install_playwright_browsers()

from dotenv import load_dotenv
load_dotenv()

ARCHIVE_FILE = "archivio.json"

st.set_page_config(page_title="Geopolitical Synthesizer", layout="centered")

st.markdown("""
<style>
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden !important;}

    /* Swiss Minimalist Typography & Colors */
    *, html, body, [class*="css"], .stApp, .block-container {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: #000000 !important;
        font-weight: bold !important;
        letter-spacing: -0.05em !important;
    }
    
    .main-title {
        font-size: 3.5rem !important;
        font-weight: bold;
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0 !important;
        letter-spacing: -0.05em;
    }
    
    hr {
        border: none !important;
        border-top: 1px solid #000000 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Countdown style */
    .countdown-text {
        font-size: 5rem;
        font-weight: bold;
        color: #000000;
        text-align: left;
        letter-spacing: -0.05em;
        line-height: 1;
        margin-bottom: 0 !important;
    }
    
    /* Image styling */
    [data-testid="stImage"] img {
        filter: grayscale(100%) !important;
        border-radius: 0 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Archive Date styling */
    .archive-date {
        font-size: 1rem;
        font-weight: bold;
        color: #000000;
        text-transform: uppercase;
        display: block;
        margin-bottom: 1rem;
    }
    
    /* Spacing & Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 800px !important;
    }
    
    p, div {
        line-height: 1.6 !important;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>Geopolitical Synthesizer</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
countdown_placeholder = st.empty()
st.markdown("<hr>", unsafe_allow_html=True)

article_placeholder = st.empty()

# Render the entire cumulative archive
def render_article():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
                
            if archive_data and len(archive_data) > 0:
                with article_placeholder.container():
                    for i, entry in enumerate(archive_data):
                        st.markdown(f"<div class='archive-date'>{entry.get('timestamp', '')}</div>", unsafe_allow_html=True)
                        
                        content = entry.get('content', '')
                        lines = content.strip().split('\n')
                        title = lines[0].replace('*', '').strip() if lines else ""
                        body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                        
                        st.markdown(f"<div class='article-container' style='font-weight:bold; margin-bottom: 1rem;'>{title}</div>", unsafe_allow_html=True)
                        
                        if entry.get("image_path") and os.path.exists(entry["image_path"]):
                            st.image(entry["image_path"], use_container_width=True)
                            
                        st.markdown(f"<div class='article-container'>{body}</div>", unsafe_allow_html=True)
                        
                        if i < len(archive_data) - 1:
                            st.markdown("<hr>", unsafe_allow_html=True)
            else:
                article_placeholder.info("No article available yet.")
        except json.JSONDecodeError:
            article_placeholder.error("Error reading archivio.json")
    else:
        article_placeholder.info("No article available yet.")

render_article()

# Update countdown every second
while True:
    now = datetime.now(timezone.utc)
    # Calculate next milestone (00:00 or 12:00 UTC)
    if now.hour < 12:
        next_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
    diff = next_time - now
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    countdown_placeholder.markdown(f"<div class='countdown-text'>{time_str}</div>", unsafe_allow_html=True)
    time.sleep(1)