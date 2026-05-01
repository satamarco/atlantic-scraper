import streamlit as st
import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
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
        "content": article_text,
        "type": "Cronaca Visionaria"
    }
    data.insert(0, new_entry) # Inseriamo all'inizio per avere dal più recente al più vecchio
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(sources_data):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    atlantic_texts = ", ".join(sources_data.get("the_atlantic", []))
    unione_texts = ", ".join(sources_data.get("unione_sarda", []))
    sardinia_texts = ", ".join(sources_data.get("sardinia_post", []))
    
    prompt = f"""
    Sei un cronista confuso, visionario e sconclusionato.
    Usa i seguenti dati estratti da tre testate giornalistiche:
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Scrivi un UNICO TESTO fluido e compatto, in cui tratti tutte queste notizie come se stessero accadendo contemporaneamente nello stesso identico luogo geografico (una sorta di tuo quartiere surreale).
    
    Regole di narrazione e stile:
    - Mescola i grandi temi geopolitici mondiali con i dettagli della cronaca locale sarda senza fare alcuna distinzione di scala o di importanza. Collega cause ed effetti in modo assurdo (es. una crisi internazionale causata da un problema stradale a Cagliari, o viceversa).
    - Il testo deve essere un unico blocco narrativo con paragrafi ben definiti, SENZA sottotitoli o divisioni in sezioni.
    - Il primissimo elemento del testo deve essere un unico Titolo Principale (formattato in Markdown come `# Titolo`). Questo titolo deve essere un mashup casuale, visionario e assurdo di due o più concetti presenti nelle notizie (es. "La Crisi dei Missili Balistici in Via Roma" o "Carenza di Infermieri nell'Amministrazione Biden").
    - Scrivi in italiano.
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
    
    hr {
        border: none !important;
        border-top: 1px solid #000000 !important;
        margin: 2rem 0 !important;
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
        width: 100% !important;
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
    
    /* Archive Label Styling */
    .archive-label {
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
        background: #000000;
        color: #FFFFFF;
        padding: 2px 6px;
        display: inline-block;
        margin-bottom: 0.5rem;
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

st.title("Geopolitical Synthesizer")

tab1, tab2 = st.tabs(["Generatore", "Archivio"])

with tab1:
    if st.button("Genera Sintesi Giornaliera"):
        with st.spinner("Scraping cross-source in corso..."):
            sources_data = asyncio.run(scrape_all_sources())
            st.write(f"Voci recuperate: The Atlantic ({len(sources_data['the_atlantic'])}), L'Unione Sarda ({len(sources_data['unione_sarda'])}), Sardinia Post ({len(sources_data['sardinia_post'])})")
        
        with st.spinner("Generazione sintesi incrociata..."):
            article = generate_article(sources_data)
            st.write(article)
            
            # Salvataggio in archivio
            save_to_archive(article)
            st.success("Sintesi Multi-Fonte salvata nell'archivio!")

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
                    type_label = entry.get('type', 'Articolo Base')
                    st.markdown(f"<div class='archive-date'>{entry['timestamp']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='archive-label'>{type_label}</div>", unsafe_allow_html=True)
                    with st.expander("LEGGI ARTICOLO"):
                        st.write(entry['content'])
        except json.JSONDecodeError:
            st.error("Errore nella lettura del file archivio.json")
    else:
        st.info("Nessun articolo presente nell'archivio. Genera una nuova sintesi per iniziare.")
