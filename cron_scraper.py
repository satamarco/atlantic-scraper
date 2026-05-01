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
        "type": "Cronaca Visionaria"
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
