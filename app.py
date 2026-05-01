import streamlit as st
import google.generativeai as genai
import asyncio
from scraper import scrape_atlantic_world
import os

# Configurazione API Gemini (assicurati di avere la chiave nel tuo ambiente)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_article(texts):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Sei uno scrittore ubriaco e pesantemente depresso, con uno stile di scrittura ramingo e disilluso simile a quello di Bruce Chatwin.
    Parti da questi titoli/concetti estratti da The Atlantic per scrivere un articolo:
    {', '.join(texts)}
    
    Tuttavia, mentre scrivi, il tuo stato di ebbrezza e depressione prende il sopravvento. Inizia presto a divagare sulle misere vicissitudini della tua vita personale, perdendo il filo del discorso geopolitico per perderti nei tuoi ricordi sbiaditi, fallimenti e malinconie, mescolando i fatti del mondo con il tuo dramma personale.
    """
    response = model.generate_content(prompt)
    return response.text

st.title("Atlantic Geopolitical Synthesizer")

if st.button("Scrape & Generate"):
    with st.spinner("Scraping..."):
        # Esecuzione scraping asincrono
        texts = asyncio.run(scrape_atlantic_world())
        st.write("Articoli estratti:", texts)
    
    with st.spinner("Generazione articolo..."):
        article = generate_article(texts)
        st.subheader("Articolo Analitico Generato")
        st.write(article)
