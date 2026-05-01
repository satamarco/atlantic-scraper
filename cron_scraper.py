import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
import os
import json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

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
        "type": "Sintesi Multi-Fonte"
    }
    data.insert(0, new_entry)
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(sources_data):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    atlantic_texts = ", ".join(sources_data.get("the_atlantic", []))
    unione_texts = ", ".join(sources_data.get("unione_sarda", []))
    sardinia_texts = ", ".join(sources_data.get("sardinia_post", []))
    
    prompt = f"""
    Sei un giornalista analitico con uno stile super minimale, tagliente e strutturato.
    Usa i seguenti dati estratti da tre testate giornalistiche:
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Crea un unico articolo STRUTTURATO ESATTAMENTE IN TRE SEZIONI, con i seguenti titoli precisi (usa Markdown per i titoli):
    
    # Scenario Globale
    (Scrivi qui una sintesi basata unicamente sulle notizie di The Atlantic)
    
    ---
    
    # Focus Sardegna
    (Scrivi qui una sintesi incrociata basata sulle notizie de L'Unione Sarda e Sardinia Post)
    
    ---
    
    # Il Punto di Vista
    (Scrivi qui un'analisi originale che trovi un filo conduttore, anche sottile o provocatorio, tra le dinamiche globali dello Scenario Globale e quelle locali del Focus Sardegna)
    
    Regole di formattazione:
    - Scrivi in italiano.
    - Usa titoli grandi e in grassetto per le sezioni.
    - Usa le linee di separazione nette in markdown (---) esattamente come richiesto.
    - Tono austero, minimale e diretto, come un report di design svizzero.
    """
    response = model.generate_content(prompt)
    return response.text

async def main():
    print("Scraping multi-source started...")
    sources_data = await scrape_all_sources()
    print(f"Extracted from The Atlantic: {len(sources_data['the_atlantic'])}")
    print(f"Extracted from L'Unione Sarda: {len(sources_data['unione_sarda'])}")
    print(f"Extracted from Sardinia Post: {len(sources_data['sardinia_post'])}")
    
    print("Generating article...")
    article = generate_article(sources_data)
    
    print("Saving to archive...")
    save_to_archive(article)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
