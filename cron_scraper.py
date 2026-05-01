import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
import os
import json
import urllib.parse
import requests
import random
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
    
    eras = [
        "a 1930s archaeologist excavating ruins",
        "an ethnographer from the far future studying the remnants of our civilization",
        "a 19th-century British explorer cataloging flora and local customs",
        "a detached travel writer wandering aimlessly in the 1970s"
    ]
    selected_era = random.choice(eras)
    
    prompt = f"""
    You are a cultured, slightly detached traveler, observing the world as if it were an open-air museum. Your writing style is heavily inspired by Bruce Chatwin.
    Use the following data extracted from exactly 15 recent articles across three diverse news outlets (The Atlantic, L'Unione Sarda, Sardinia Post):
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Write a SINGLE fluid and compact text IN ENGLISH, treating all these news events as if they were happening simultaneously in the exact same geographical location.
    
    Narrative and style rules:
    - PROSA (PROSE): Use short, dry, precise sentences. Avoid exaggeration, melodrama, and sarcasm. 
    - THE LENS: Write the entire piece adopting the perspective of {selected_era}.
    - PHYSICAL DETAILS: Do not explain the news. Instead, describe objects, textures, or landscapes that represent them (e.g., instead of discussing an economic crisis, describe the color of a crumpled banknote in a Cagliari market).
    - CONNECTIONS: Connect the 15 facts (Sardinia + World) through historical or material coincidences, without using banal conjunctions.
    - PROHIBITION OF CLICHÉS: DO NOT EVER cite Abraham Lincoln, Virginia Woolf, Rachel Carson, or the suffragettes. If you need historical, literary, or scientific parallels, find new and unexpected ones (e.g., Borges, Calvino, Darwin, Ada Lovelace, etc.).
    - The text must be a single narrative block with well-defined paragraphs, WITHOUT any subtitles or section divisions.
    - The very first element of the text must be a single Main Title (formatted in Markdown as `# Title`). This title must be a bold, dry, and evocative phrase drawn from the physical details of the text.
    - Write ENTIRELY IN ENGLISH.
    - At the VERY END of your response, on a new line, write exactly "IMAGE_PROMPT: " followed by a single line of text in English describing a visual scene that captures the essence of your article.
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
    
    if len(parts) > 1:
        base_prompt = parts[1].strip()
    else:
        base_prompt = "surreal geopolitical scene in a local neighborhood"
        
    full_prompt = f"{base_prompt}, Black and white photography, grainy texture, documentary style, found objects, minimalist landscape, high contrast"
    
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