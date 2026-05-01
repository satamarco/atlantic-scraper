import streamlit as st
import json
import os
from datetime import datetime, timezone, timedelta
import time

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
    h1 {
        font-size: 4rem !important;
        border-bottom: 1px solid #000000;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    hr {
        border: none !important;
        border-top: 1px solid #000000 !important;
        margin: 2rem 0 !important;
    }
    
    /* Countdown style */
    .countdown-text {
        font-size: 5rem;
        font-weight: bold;
        color: #000000;
        text-align: left;
        margin-bottom: 3rem;
        letter-spacing: -0.05em;
        line-height: 1;
    }
    
    /* Expanders (Archive) */
    [data-testid="stExpander"] {
        border: none !important;
        border-bottom: 1px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        margin-bottom: 2rem !important;
    }
    [data-testid="stExpander"] summary {
        padding: 1rem 0 !important;
    }
    [data-testid="stExpander"] summary p {
        font-weight: bold !important;
        font-size: 1.5rem !important;
        text-transform: uppercase;
    }
    
    /* Archive Date styling */
    .archive-date {
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
        margin-top: 2rem;
        color: #000000;
        text-transform: uppercase;
        display: block;
    }
    
    /* Spacing & Padding */
    .block-container {
        padding-top: 2rem !important; /* Ridotto per stare in alto */
        padding-bottom: 4rem !important;
        max-width: 800px !important;
    }
    
    p, div {
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Geopolitical Synthesizer")

countdown_placeholder = st.empty()

# Resa dell'Archivio Storico
if os.path.exists(ARCHIVE_FILE):
    try:
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
            
        if not archive_data:
            pass
        else:
            for entry in archive_data:
                st.markdown(f"<div class='archive-date'>{entry['timestamp']}</div>", unsafe_allow_html=True)
                with st.expander("LEGGI ARTICOLO"):
                    st.write(entry['content'])
    except json.JSONDecodeError:
        st.error("Errore nella lettura del file archivio.json")

# Ciclo di aggiornamento del countdown
while True:
    now = datetime.now(timezone.utc)
    # Calcolo prossimo traguardo (00:00 o 12:00 UTC)
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
