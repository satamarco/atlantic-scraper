import streamlit as st
import google.generativeai as genai
import asyncio
from scraper import scrape_atlantic_world
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurazione API Gemini (assicurati di avere la chiave nel tuo ambiente)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

ARCHIVE_FILE = "archivio.json"

def save_to_archive(article_text):
    data = []
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": article_text
    }
    data.insert(0, new_entry) # Inseriamo all'inizio per avere dal più recente al più vecchio
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(texts):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are a heavily depressed and drunk writer, with a rambling and disillusioned writing style similar to Bruce Chatwin.
    Start from these titles/concepts extracted from The Atlantic to write an article IN ENGLISH:
    {{', '.join(texts)}}
    
    However, as you write, your state of inebriation and depression takes over. You soon start to digress about the miserable vicissitudes of your personal life, losing the thread of the geopolitical discourse to get lost in your faded memories, failures, and melancholies, mixing the facts of the world with your personal drama. 
    WRITE THE ENTIRE ARTICLE IN ENGLISH.
    """
    response = model.generate_content(prompt)
    return response.text

st.markdown("""
<style>
    /* Swiss Minimalist Typography & Colors */
    *, html, body, [class*="css"], .stApp, header, .stApp > header, .block-container {
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
        font-size: 3.5rem !important;
        border-bottom: 1px solid #000000;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Remove rounding and add strict borders */
    button, .stButton>button {
        border-radius: 0px !important;
        border: 1px solid #000000 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        box-shadow: none !important;
        font-weight: bold !important;
        padding: 0.75rem 1.5rem !important;
        transition: none !important;
        text-transform: uppercase;
    }
    button:hover, .stButton>button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #000000;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
        color: #000000 !important;
        font-weight: bold !important;
        padding: 1rem 0 !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #000000 !important;
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
        font-size: 1.2rem !important;
        text-transform: uppercase;
    }
    
    /* Archive Date styling */
    .archive-date {
        font-size: 0.8rem;
        font-weight: 300;
        margin-bottom: -0.5rem;
        margin-top: 1.5rem;
        color: #000000;
    }
    
    /* Spacing & Padding */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 4rem !important;
        max-width: 800px !important;
    }
    
    p, div {
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Atlantic Geopolitical Synthesizer")

tab1, tab2 = st.tabs(["Genera Nuovo", "Archivio"])

with tab1:
    if st.button("Scrape & Generate"):
        with st.spinner("Scraping..."):
            # Esecuzione scraping asincrono
            texts = asyncio.run(scrape_atlantic_world())
            st.write("Articoli estratti:", texts)
        
        with st.spinner("Generazione articolo..."):
            article = generate_article(texts)
            st.subheader("Articolo Analitico Generato")
            st.write(article)
            
            # Salvataggio in archivio
            save_to_archive(article)
            st.success("Articolo salvato nell'archivio!")

with tab2:
    st.header("Archivio Storico")
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
                
            if not archive_data:
                st.info("Nessun articolo presente nell'archivio.")
            else:
                for entry in archive_data:
                    st.markdown(f"<div class='archive-date'>{entry['timestamp']}</div>", unsafe_allow_html=True)
                    with st.expander("LEGGI ARTICOLO"):
                        st.write(entry['content'])
        except json.JSONDecodeError:
            st.error("Errore nella lettura del file archivio.json")
    else:
        st.info("Nessun articolo presente nell'archivio. Genera un nuovo articolo per iniziare.")