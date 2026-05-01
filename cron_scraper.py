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
    
    prompt = f"""
    You are a cold, bureaucratic, clinical, and detached analyst. You are a paranoid mind connecting the dots of a global conspiracy using an academic or medical tone. No emotions, only iron-clad logic expressing insane deductions.
    
    Use the following data extracted from exactly 15 recent articles across three diverse news outlets (The Atlantic, L'Unione Sarda, Sardinia Post):
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Write a SINGLE fluid and compact text IN ENGLISH, treating all these news events in real-time as abstract data within a continuous, atemporal flow.
    
    CRITICAL INSTRUCTIONS - FACTUALITY AND CLEAN-UP (MANDATORY):
    - ABSOLUTE ATEMPORALITY: NEVER use temporal expressions related to the current day (e.g., "today", "this morning", "Friday", "yesterday", "this Tuesday", "May 1"). Treat events as a continuous diary or dossier. Use opening formulas like "The data reports that...", "Observations indicate...", or start directly describing the fact.
    - NO EXCLAMATION MARKS: It is ABSOLUTELY FORBIDDEN to use exclamation marks (!). Never use them.
    - ANTI-JUNK FILTER: STRICTLY IGNORE and never cite corporate data, VAT numbers (Partite IVA), fiscal codes, share capitals, legal addresses of newspapers, or REA numbers. They are technical noise, not news.
    - REAL DATA DENSITY: The text MUST be filled with real names, figures, and data extracted from the 15 articles (Sardinian politicians, towns, euro/dollar figures, US presidents). Use these extremely factual details to give documentary weight to the delirium.
    - THE LOGICAL DELIRIUM (EXTREME FUSION): EVERY SINGLE paragraph MUST contain elements from AT LEAST 3 DIFFERENT news stories (mixing international and local Sardinian news) blended together. Connect provincial politics to maximum geopolitical or physical systems, treating them as symptoms of the exact same cosmic conspiracy.
    
    NARRATIVE AND STYLE RULES:
    - The narrator is a cold-blooded analyst. Speak in a clinical, detached, and bureaucratic tone.
    - Create visceral connections based on shared physical anomalies between Sardinia and the world. 
    
    ANTI-DRIFT RULES:
    - TOTAL BLACKOUT: It is STRICTLY FORBIDDEN to cite Abraham Lincoln, Virginia Woolf, Rachel Carson, the suffragettes, or Vannevar Bush. If an original article cites them, IGNORE those names and focus on other protagonists. 
    - The text must be a single narrative block with well-defined paragraphs, WITHOUT any subtitles or section divisions.
    - The very first element of the text must be a single Main Title (formatted in Markdown as `# Title`). This title must look like a file header (e.g., "# Dossier: Microchips, Electoral Reform, and Anomalies in Quartu").
    - Write ENTIRELY IN ENGLISH.
    - At the VERY END of your response, on a new line, write exactly "IMAGE_PROMPT: " followed by a single line of text in English describing an image. The prompt must describe an investigative photojournalism scene, where surreal elements are treated as documentary evidence.
    """
    response = model.generate_content(prompt)
    return response.text

async def main():
    print("Scraping multi-source started...")
    sources_data = await scrape_all_sources()
    print(f"Extracted from The Atlantic: {len(sources_data['the_atlantic'])}")
    print(f"Extracted from L'Unione Sarda: {len(sources_data['unione_sarda'])}")
    print(f"Extracted from Sardinia Post: {len(sources_data['sardinia_post'])}")
    
    print("Generating article and prompt...")
    raw_response = generate_article(sources_data)
    
    parts = raw_response.split("IMAGE_PROMPT:")
    article_content = parts[0].strip()
    
    # Rimuoviamo eventuali tag markdown residui dal testo
    article_content = article_content.replace("```markdown", "").replace("```python", "").replace("```", "").strip()
    
    if len(parts) > 1:
        base_prompt = parts[1].strip()
    else:
        base_prompt = "surreal geopolitical scene in a local neighborhood"
        
    full_prompt = f"{base_prompt}, investigative photojournalism, black and white, high contrast, documentary evidence"
    
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