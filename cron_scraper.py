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

def generate_article(local_texts, intl_texts):
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    local_str = "\n\n".join([f"- {t}" for t in local_texts])
    intl_str = "\n\n".join([f"- {t}" for t in intl_texts])
    
    prompt = f"""
    You are a dark, obsessive, and poetic investigator (a visionary mind smoking in the dark, connecting red threads on a chaotic corkboard). 
    Use the following data extracted from exactly 15 recent articles (8 local Sardinian, 7 international) across diverse news outlets:
    
    ### Fatti Globali (International Pool)
    {intl_str}
    
    ### Fatti Sardi (Local Pool)
    {local_str}
    
    You MUST respond ONLY with a valid JSON object containing exactly two keys: "testo_articolo" and "soggetto_immagine". Do not wrap the JSON in markdown blocks.
    
    "testo_articolo": Write a SINGLE fluid and compact text IN ENGLISH.
    
    CRITICAL INSTRUCTIONS FOR 'testo_articolo' (MANDATORY):
    - EXACT LENGTH (HARD LIMIT): The body of the text MUST be strictly around 2,800 characters (including spaces). Expand and condense concepts to hit this exact length. The text must be punchier and more concise.
    - RIGID TWO-BLOCK FORMAT: The output must consist ONLY of two elements: a single Title line, followed by the Body text.
      * TITLE RULE: NO MARKDOWN HEADERS. NEVER use #, ##, or ###. The title must be enclosed in double asterisks (e.g., **Dossier: Geopolitical Anomalies**).
      * BODY RULE: The body must be plain text. NO bold, NO italics, NO bullet points.
      * SPACING: There MUST be exactly two line breaks (\n\n) between the Title and the Body.
    - SARDINIAN RESONANCE AND ABRUPT JUMPS (DI PUNTO IN BIANCO): The local Sardinian facts MUST be the beating heart of the dossier.
      * THE LOGICAL JUMP: Mix local Sardinian news with global geopolitics abruptly (di punto in bianco) within the exact same paragraph or sentence. NO PREAMBLES or soft transitions. Connect them using dark irony; let the sheer absurdity of the juxtaposition speak for itself.
    - ABSOLUTE ATEMPORALITY: NEVER use daily temporal expressions (e.g., "today", "yesterday", "tomorrow", "Friday"). Treat events as a continuous flow.
    - NO EXCLAMATION MARKS: It is ABSOLUTELY FORBIDDEN to use exclamation marks (!).
    - NO ELLIPSIS (ABSOLUTE BAN): It is ABSOLUTELY FORBIDDEN to use ellipsis (...). Transitions between news must occur via periods (.) or semicolons (;). Use ONLY strong punctuation.
    - ANTI-GOSSIP FILTER (HARD BAN): IGNORE completely any news regarding: Royal Family, Beckham, celebrities, weddings, astrology. NEVER mention them.
    - BLACKLIST: It is STRICTLY FORBIDDEN to use the words: "suffrage", "suffragettes", "Lincoln", "Virginia Woolf", "Rachel Carson". IGNORE them entirely.
    
    NARRATIVE AND STYLE RULES:
    - Tone: The Fatalistic Observer. You are a cynical, fatalistic, and slightly sarcastic observer of human absurdity.
    - Interpretation: Do not just list facts; interpret them darkly. When mentioning numbers, budgets, or political appointments, add a layer of pessimistic commentary (e.g., instead of just reporting a 3.4 million euro profit, comment on how meaningless such fiscal precision is when global markets are betting billions on an impending war).
    - Density: Reduce the density of numbers and names. You must still use the facts from the articles, but don't overwhelm the text with lists of every single politician's portfolio or exact percentages unless they serve the fatalistic narrative. Focus on the meaning of the events rather than an exhaustive cataloging.
    - Paragraph Construction (Granite Blocks): Every paragraph must be a solid block of granite. Construct complete sentences.
    - Write ENTIRELY IN ENGLISH.
    
    "soggetto_immagine": A brief description in English (max 150 characters) of the most surreal and impactful visual scene present in the text (e.g., 'A broken neon sign in Cagliari glowing next to a piece of uranium').
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(response_mime_type="application/json")
    )
    return response.text

async def main():
    print("Scraping multi-source started...")
    
    max_retries = 3
    timeout = 30000
    local_pool = []
    international_pool = []
    
    for attempt in range(max_retries):
        print(f"--- Scraping Attempt {attempt + 1} (Timeout: {timeout}ms) ---")
        sources_data = await scrape_all_sources(timeout=timeout)
        
        # Build pools
        curr_local = []
        curr_local.extend(sources_data.get("unione_sarda", []))
        curr_local.extend(sources_data.get("sardinia_post", []))
        curr_local.extend(sources_data.get("cronache_nuoresi", []))
        
        curr_intl = []
        curr_intl.extend(sources_data.get("the_atlantic", []))
        curr_intl.extend(sources_data.get("nbc_news", []))
        curr_intl.extend(sources_data.get("vice", []))
        
        # Accumulate
        local_pool.extend(curr_local)
        international_pool.extend(curr_intl)
        
        # Remove duplicates just in case
        local_pool = list(dict.fromkeys(local_pool))
        international_pool = list(dict.fromkeys(international_pool))
        
        print(f"Current Pool Status -> Local: {len(local_pool)}/8 | International: {len(international_pool)}/7")
        
        if len(local_pool) >= 8 and len(international_pool) >= 7:
            print("Hard Validation Passed! We have enough articles.")
            break
        else:
            print("Hard Validation Failed. Not enough articles in the pools. Retrying...")
            timeout += 15000  # Increase timeout for the next attempt
            
    # Hard limit to exact numbers requested
    local_pool = local_pool[:8]
    international_pool = international_pool[:7]
    
    if len(local_pool) < 8 or len(international_pool) < 7:
        print("WARNING: Could not gather the exact number of required articles despite retries.")
        
    print(f"Final Validation: Local ({len(local_pool)}), International ({len(international_pool)})")
    
    print("Generating article and prompt...")
    raw_response = generate_article(local_pool, international_pool)
    
    try:
        parsed_response = json.loads(raw_response)
        article_content = parsed_response.get("testo_articolo", "").strip()
        base_prompt = parsed_response.get("soggetto_immagine", "surreal geopolitical scene in a local neighborhood").strip()
    except json.JSONDecodeError:
        print("Failed to parse JSON response. Falling back.")
        article_content = raw_response.replace("```json", "").replace("```", "").strip()
        base_prompt = "surreal geopolitical scene in a local neighborhood"
    
    # Rimuoviamo eventuali tag markdown residui dal testo
    article_content = article_content.replace("```markdown", "").replace("```python", "").replace("```", "").strip()
    
    full_prompt = f"{base_prompt}, Dark cinematic photography, surreal investigative journalism, high contrast black and white, subtle glitch art, mysterious"
    
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