import google.generativeai as genai
import asyncio
from scraper import scrape_atlantic_world
import os
import json
from datetime import datetime

# Non serve load_dotenv() per GitHub Actions se passiamo le variabili di ambiente
# ma lo teniamo commentato/o usiamo try except nel caso si voglia usare in locale
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
        "content": article_text
    }
    data.insert(0, new_entry)
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(texts):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    You are a heavily depressed and drunk writer, with a rambling and disillusioned writing style similar to Bruce Chatwin.
    Start from these titles/concepts extracted from The Atlantic to write an article IN ENGLISH:
    {', '.join(texts)}
    
    However, as you write, your state of inebriation and depression takes over. You soon start to digress about the miserable vicissitudes of your personal life, losing the thread of the geopolitical discourse to get lost in your faded memories, failures, and melancholies, mixing the facts of the world with your personal drama. 
    WRITE THE ENTIRE ARTICLE IN ENGLISH.
    """
    response = model.generate_content(prompt)
    return response.text

async def main():
    print("Scraping started...")
    texts = await scrape_atlantic_world()
    print(f"Extracted {len(texts)} articles.")
    
    print("Generating article...")
    article = generate_article(texts)
    
    print("Saving to archive...")
    save_to_archive(article)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
