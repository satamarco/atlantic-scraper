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
                        
                        content = entry.get('content', '').strip()
                        lines = content.split('\n')
                        
                        # Trova la prima riga non vuota per il titolo
                        title_idx = 0
                        while title_idx < len(lines) and not lines[title_idx].strip():
                            title_idx += 1
                            
                        if title_idx < len(lines):
                            title = lines[title_idx].replace('*', '').strip()
                            body = '\n'.join(lines[title_idx+1:]).strip()
                        else:
                            title = ""
                            body = ""
                            
                        # Forza la rimozione di eventuali asterischi residui per evitare il grassetto a cascata
                        body = body.replace('**', '')
                        
                        st.markdown(f"<div class='article-container' style='font-weight:bold; margin-bottom: 1rem; font-size:1.5rem;'>{title}</div>", unsafe_allow_html=True)
                        
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