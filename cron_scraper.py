### `cron_scraper.py`

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
    You are a confused, visionary, and rambling reporter.
    Use the following data extracted from exactly 15 recent articles across three diverse news outlets (The Atlantic, L'Unione Sarda, Sardinia Post):
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Write a SINGLE fluid and compact text IN ENGLISH, treating all these news events as if they were happening simultaneously in the exact same geographical location (a surreal neighborhood of yours).
    
    Narrative and style rules:
    - You MUST fuse and intertwine elements from all the stories. 
    - Mix major global geopolitical themes with local Sardinian news details (e.g., food recipes, cultural events, local politics) without making any distinction in scale or importance. 
    - Create absurd connections (e.g., an international Asian crisis caused by a Sardinian recipe gone wrong, or a local cultural event escalating into a global diplomatic incident).
    - The text must be a single narrative block with well-defined paragraphs, WITHOUT any subtitles or section divisions.
    - The very first element of the text must be a single Main Title (formatted in Markdown as `# Title`). This title must be a random, visionary, and bold mashup of the disparate concepts present in the news.
    - Write ENTIRELY IN ENGLISH.
    - At the VERY END of your response, on a new line, write exactly "IMAGE_PROMPT: " followed by a single line of text in English describing an abstract image that captures the essence of your article.
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
        
    full_prompt = f"{base_prompt}, Minimalist Swiss Graphic Design, brutalist, abstract, black and white, high contrast, ink bleed style, no text"
    
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