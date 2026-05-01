import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
import os
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

ARCHIVE_FILE = "archivio.json"

def save_to_archive(article_text):
    # Consolidate to only keep the latest article
    data = [{
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "content": article_text,
        "type": "Visionary Chronicle"
    }]
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(sources_data):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    atlantic_texts = ", ".join(sources_data.get("the_atlantic", []))
    unione_texts = ", ".join(sources_data.get("unione_sarda", []))
    sardinia_texts = ", ".join(sources_data.get("sardinia_post", []))
    
    prompt = f"""
    You are a confused, visionary, and rambling reporter.
    Use the following data extracted from three news outlets:
    
    [The Atlantic]: {atlantic_texts}
    [L'Unione Sarda]: {unione_texts}
    [Sardinia Post]: {sardinia_texts}
    
    Write a SINGLE fluid and compact text IN ENGLISH, treating all these news events as if they were happening simultaneously in the exact same geographical location (a surreal neighborhood of yours).
    
    Narrative and style rules:
    - Mix major global geopolitical themes with local Sardinian news details without making any distinction in scale or importance. Connect causes and effects in an absurd way (e.g., an international crisis caused by a road problem in Cagliari, or vice versa).
    - The text must be a single narrative block with well-defined paragraphs, WITHOUT any subtitles or section divisions.
    - The very first element of the text must be a single Main Title (formatted in Markdown as `# Title`). This title must be a random, visionary, and bold mashup of two or more concepts present in the news (e.g., "The Ballistic Missile Crisis in Via Roma" or "Nursing Shortage in the Biden Administration").
    - Write ENTIRELY IN ENGLISH.
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