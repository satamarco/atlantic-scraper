import streamlit as st
import json
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import time

@st.cache_resource
def install_playwright_browsers():
    os.system("playwright install chromium")

install_playwright_browsers()

from dotenv import load_dotenv
load_dotenv()

if 'display_count' not in st.session_state:
    st.session_state.display_count = 5

ARCHIVE_FILE = "archivio.json"

st.set_page_config(page_title="Geopolitical Synthesizer", layout="centered")

# Codice CSS per nascondere menu, footer, profilo GitHub e il pulsante rosso di Streamlit
hide_st_style = """
            <style>
            /* Nasconde il menu ad hamburger in alto a destra */
            #MainMenu {visibility: hidden;}
            
            /* Nasconde il footer 'Made with Streamlit' */
            footer {visibility: hidden;}
            
            /* Nasconde l'header superiore (dove c'è l'avatar GitHub) */
            header {visibility: hidden;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            
            /* Nasconde il pulsante rosso fluttuante in basso a destra */
            .stAppDeployButton {display: none !important;}
            [data-testid="stAppDeployButton"] {display: none !important;}
            
            /* Nasconde eventuali altri badge fluttuanti di Streamlit */
            .viewerBadge_container {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

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
    
    /* Language Divider */
    .language-divider {
        border: none !important;
        border-top: 1px solid #d3d3d3 !important;
        margin: 2.5rem 0 !important;
        width: 50%;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Timer Layout */
    .timer-container {
        display: flex;
        align-items: baseline;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 0 !important;
    }
    
    .countdown-text {
        font-size: 5rem;
        font-weight: bold;
        color: #000000;
        text-align: left;
        letter-spacing: -0.05em;
        line-height: 1;
        margin-bottom: 0 !important;
    }
    
    .current-time-text {
        font-size: 1.2rem;
        color: #666666;
        font-weight: normal;
        letter-spacing: -0.02em;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 600px) {
        .countdown-text {
            font-size: 3.5rem; /* Riduce la dimensione su smartphone */
        }
        .current-time-text {
            font-size: 1rem;
        }
        .main-title {
            font-size: 2.5rem !important;
        }
    }
    
    /* Image styling */
    [data-testid="stImage"] img {
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
                    # Only loop up to the current display_count
                    for i, entry in enumerate(archive_data[:st.session_state.display_count]):
                        st.markdown(f"<div class='archive-date'>{entry.get('timestamp', '')}</div>", unsafe_allow_html=True)
                        
                        content = entry.get('content', '').strip()
                        lines = content.split('\n')
                        
                        title_idx = 0
                        while title_idx < len(lines) and not lines[title_idx].strip():
                            title_idx += 1
                            
                        if title_idx < len(lines):
                            title = lines[title_idx].replace('*', '').strip()
                            body_raw = '\n'.join(lines[title_idx+1:]).strip()
                        else:
                            title = ""
                            body_raw = ""
                            
                        body_raw = body_raw.replace('**', '')
                        
                        st.markdown(f"<div class='article-container' style='font-weight:bold; margin-bottom: 1rem; font-size:1.5rem;'>{title}</div>", unsafe_allow_html=True)
                        
                        if entry.get("image_path") and os.path.exists(entry["image_path"]):
                            st.image(entry["image_path"], use_container_width=True)
                        
                        # Layout a colonne per le due lingue
                        parts = body_raw.split('---')
                        if len(parts) == 2:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"<div class='article-container'>{parts[0].strip()}</div>", unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"<div class='article-container'>{parts[1].strip()}</div>", unsafe_allow_html=True)
                        else:
                            # Fallback se non trova il divisore
                            body = body_raw.replace('---', '<hr class="language-divider">')
                            st.markdown(f"<div class='article-container'>{body}</div>", unsafe_allow_html=True)
                        
                        st.markdown("<hr class='language-divider'>", unsafe_allow_html=True)
                        
                    # Add Pagination Button
                    if st.session_state.display_count < len(archive_data):
                        if st.button("Load Older Entries"):
                            st.session_state.display_count += 5
                            st.rerun()
            else:
                article_placeholder.info("No article available yet.")
        except json.JSONDecodeError:
            article_placeholder.error("Error reading archivio.json")
    else:
        article_placeholder.info("No article available yet.")

render_article()

# Update countdown every second
while True:
    now = datetime.now(ZoneInfo("Europe/Rome"))
    # Calculate next milestone (midnight IT)
    next_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
    diff = next_time - now
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    current_time_str = now.strftime("%H:%M:%S")
    
    timer_html = f"""
    <div class='timer-container'>
        <div class='countdown-text'>{time_str}</div>
        <div class='current-time-text'>{current_time_str}</div>
    </div>
    """
    
    countdown_placeholder.markdown(timer_html, unsafe_allow_html=True)
    time.sleep(1)