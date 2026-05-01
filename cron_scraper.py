import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
import os
import json
import urllib.parse
import requests
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

ARCHIVE_FILE = "archivio.json"

def save_to_archive(article_text, image_path):
    # Consolidate to keep cumulative archive, newest first
    data = []
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
    new_entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "content": article_text,
        "type": "Visionary Chronicle",
        "image_path": image_path
    }
    
    data.insert(0, new_entry)
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(sources_data):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    atlantic_texts = ", ".join(sources_data.get("the_atlantic", []))
    unione_texts = ", ".join(sources_data.get("unione_sarda", []))
    sardinia_texts = ", ".join(sources_data.get("sardinia_post", []))
    
    nbc_texts = ", ".join(sources_data.get("nbc_news", []))
    vice_texts = ", ".join(sources_data.get("vice", []))
    cronache_texts = ", ".join(sources_data.get("cronache_nuoresi", []))
    
    prompt = f"""
    You are a dark, obsessive, and poetic investigator (a visionary mind smoking in the dark, connecting red threads on a chaotic corkboard). 
    Use the following data extracted from about 18 recent articles across diverse news outlets (The Atlantic, L'Unione Sarda, Sardinia Post, NBC News, Vice, Cronache Nuoresi):
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    [NBC News]: {nbc_texts}
    [Vice]: {vice_texts}
    [Cronache Nuoresi]: {cronache_texts}
    
    Write a SINGLE fluid and compact text IN ENGLISH, treating all these news events as a continuous, hypnotic stream of consciousness without time.
    
    CRITICAL INSTRUCTIONS - FACTUALITY AND CLEAN-UP (MANDATORY):
    - ABSOLUTE ATEMPORALITY: NEVER use temporal expressions related to the current day (e.g., "today", "this morning", "Friday", "yesterday", "this Tuesday", "May 1"). Treat events as a continuous apocalypse.
    - NO EXCLAMATION MARKS: It is ABSOLUTELY FORBIDDEN to use exclamation marks (!). Never use them. The narrator never shouts.
    - ANTI-JUNK FILTER: STRICTLY IGNORE and never cite corporate data, VAT numbers (Partite IVA), fiscal codes, share capitals, legal addresses of newspapers, or REA numbers.
    - REAL DATA DENSITY: The text MUST be filled with real names, figures, and data extracted from the articles (Sardinian politicians, towns, euro/dollar figures, US presidents). Use these extremely factual details to anchor the poetic delirium to concrete news.
    - THE LOGICAL DELIRIUM (EXTREME FUSION): EVERY SINGLE paragraph MUST contain elements from AT LEAST 3 DIFFERENT news stories (mixing international and local news) blended together organically. Find impossible physical or chromatic connections between facts (e.g., "The noise of American fighter jets in Iran is the same background noise heard during a city council meeting in Nuoro; the color of enriched uranium resembles a broken neon sign of a Cagliari bar").
    
    NARRATIVE AND STYLE RULES (THE OBSESSIVE MONOLOGUE):
    - Tone: Hypnotic, literary, slightly hallucinated. Use rhetorical questions, suspensions (...), and dark, physical metaphors.
    - FORBIDDEN: NO bureaucratic language. NEVER use cold expressions like "The data reports", "operational parameters", or "systemic re-calibration".
    
    ANTI-DRIFT RULES:
    - TOTAL BLACKOUT: It is STRICTLY FORBIDDEN to cite Abraham Lincoln, Virginia Woolf, Rachel Carson, the suffragettes, or Vannevar Bush. If an original article cites them, IGNORE those names.
    - The text must be a single narrative block with well-defined paragraphs, WITHOUT any subtitles or section divisions.
    - The very first element of the text must be a single Main Title (formatted in Markdown as `# Title`). This title must be a bold, poetic, and cryptic phrase.
    - Write ENTIRELY IN ENGLISH.
    - At the VERY END of your response, on a new line, write exactly "IMAGE_PROMPT: " followed by a single line of text in English describing an image. The prompt must be: "Dark cinematic photography, surreal investigative journalism, high contrast black and white, subtle glitch art, mysterious".
    """
    response = model.generate_content(prompt)
    return response.text

async def main():
    print("Scraping multi-source started...")
    sources_data = await scrape_all_sources()
    print(f"Extracted from The Atlantic: {len(sources_data.get('the_atlantic', []))}")
    print(f"Extracted from L'Unione Sarda: {len(sources_data.get('unione_sarda', []))}")
    print(f"Extracted from Sardinia Post: {len(sources_data.get('sardinia_post', []))}")
    print(f"Extracted from NBC News: {len(sources_data.get('nbc_news', []))}")
    print(f"Extracted from Vice: {len(sources_data.get('vice', []))}")
    print(f"Extracted from Cronache Nuoresi: {len(sources_data.get('cronache_nuoresi', []))}")
    
    print("Generating article and prompt...")
    raw_response = generate_article(sources_data)
    
    parts = raw_response.split("IMAGE_PROMPT:")
    article_content = parts[0].strip()
    
    # Rimuoviamo eventuali tag markdown residui dal testo
    article_content = article_content.replace("```markdown", "").replace("```python", "").replace("```", "").strip()
    
    if len(parts) > 1:
        full_prompt = parts[1].strip()
    else:
        full_prompt = "Dark cinematic photography, surreal investigative journalism, high contrast black and white, subtle glitch art, mysterious"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1000&height=800&nologo=true&enhance=false"
    
    os.makedirs("assets", exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    image_filename = f"image_{date_str}.jpg"
    image_path = os.path.join("assets", image_filename)
    
    print(f"Downloading image from {image_url} ...")
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            print(f"Image saved to {image_path}")
        else:
            print("Failed to download image.")
            image_path = None
    except Exception as e:
        print(f"Error downloading image: {e}")
        image_path = None
    
    print("Saving to archive...")
    save_to_archive(article_content, image_path)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())