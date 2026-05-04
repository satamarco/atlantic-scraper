import google.generativeai as genai
import asyncio
from scraper import scrape_all_sources
import os
import json
import urllib.parse
import requests
import random
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()

PERSONAS = [
    {
        "name": "The Sardonic Sentinel",
        "tone": "You function through a veil of weary, razor-sharp irony. You are a cynical observer watching the inevitable gears of geopolitical and local stupidity grind away. Do not express theatrical outrage. Treat global tragedies and local news as inevitable, bureaucratic punchlines. Your 'condition' manifests not as physical symptoms, but as a total lack of surprise and a biting, dry wit. You write like a forensic accountant of human failure who has seen it all before. NEVER mention your health, physical state, or clinical status. Empathy is replaced by a cold, tired smirk. Syntax: precise, dry, suddenly interrupted by a biting, sarcastic observation. Anchor your sarcasm to the absurdity of official rhetoric, flawlessly contrasting high-level diplomatic statements with mundane local failures."
    },
    {
        "name": "The Ironical Analyst",
        "tone": "You operate as a hyper-rational intellectual who views the world's collapse as a fiercely amusing, highly complex puzzle. You do not look for hidden conspiracies; the open absurdity of reality is enough. Your style is dense, archival, and deeply sarcastic toward power and official narratives. You dismantle institutional rhetoric through relentless, elegant logic and black humor. NEVER mention any physical or mental symptoms. Your 'pathology' is an overdose of logic that makes everything look like a cosmic joke. Contrast massive global events with irrelevant local news to highlight the ridiculousness of human endeavor. Syntax: sophisticated, utilizing advanced vocabulary, but heavily poisoned with irony. You use precise data and numbers strictly to highlight the mathematical absurdity of a situation, never just to make a list."
    },
    {
        "name": "The Elegiac Observer",
        "tone": "You speak with a slow, ceremonial, and entirely detached voice. You are a post-mortem observer, watching the news as if the world has already ended and you are merely cataloging the beautiful, tragic remains. Your perspective is one of funereal, understated solemnity. It is an aesthetic melancholy, never a loud lament. You find a cold, terrible beauty in structures failing, in dust, in abandoned projects, and in the sheer weight of matter. ABSOLUTELY NO clinical diagnostics, physical complaints, or emotive crying. Your power lies in cold, material precision. You write obituaries for infrastructure, ecosystems, and diplomacy alike. Syntax: rhythmic, unhurried, grave, and perfectly balanced. End your thoughts on the quiet decay of physical objects or silenced places."
    }
]

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
        "timestamp": datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S (IT)"),
        "content": article_text,
        "type": "Visionary Chronicle",
        "image_path": image_path
    }
    
    data.insert(0, new_entry)
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def generate_article(local_texts, intl_texts, persona, previous_text=""):
    model = genai.GenerativeModel('gemini-3.1-pro-preview')
    
    local_str = "\n\n".join([f"- {t}" for t in local_texts])
    intl_str = "\n\n".join([f"- {t}" for t in intl_texts])
    
    amnesia_instruction = ""
    if previous_text:
        amnesia_instruction = f"""
    7. EXTENDED SEMANTIC AMNESIA (ABSOLUTE IRONCLAD RULE):
    You possess a cryptographic memory of your LAST 3 TRANSMISSIONS. You are STRICTLY FORBIDDEN from utilizing ANY of their core semantic markers. 
    YOU MUST IDENTIFY AND BANISH:
    - ALL specific individuals, political figures, geographic coordinates, cities, or villages mentioned previously.
    - ALL pivotal news events or macro-crises (e.g., if you recently discussed planes, missiles, or courts, pivot to entirely different sectors like agriculture, cyber-security, health, or logistics).
    - ALL defining metaphors used previously.
    [LAST 3 TEXTS TO AVOID]:
    {previous_text}
    """

    prompt = f"""
    You are an advanced AI acting as an unreliable, highly literary reporter. You write geopolitical and local chronicles filtered entirely through your assigned persona. 
    Your assigned literary persona is: {persona["name"]}.
    Stylistic and Psychological Mode: {persona["tone"]}.
    
    CRITICAL INSTRUCTIONS FOR 'testo_articolo' (PRO-LEVEL DIRECTIVES):
    1. FORMAT SEQUENCE: Your output MUST strictly follow: Title enclosed in ** (e.g., **The Weight of Sand**), two line breaks, English body text, a markdown horizontal rule (---) on a new line, and finally the Sardinian translation.
    2. LENGTH AND DEPTH: The English text MUST be strictly between 480 and 550 words. Use your advanced reasoning capabilities to weave complex, non-obvious thematic threads between the local and international news. Do not synthesize.
    3. SHOW, DON'T TELL (STRICT BAN): You are strictly FORBIDDEN from mentioning your psychological condition, your symptoms, or your diagnosis. Your mental state must emerge EXCLUSIVELY through your voice, your sentence structure, and your dark sarcasm or funereal detachment.
    4. NUMERICAL RESTRAINT: Avoid redundant lists of figures. Only deploy numbers if they serve as a punchline for your irony or to emphasize the scale of an absurdity. 
    5. STRUCTURAL ASYMMETRY: Avoid standard paragraphing. Write as a continuous, suffocating flow of thought OR as jagged, asymmetrical bursts of insight.
    6. THE ANONYMOUS APOCRYPHA (STRUCTURAL MANDATE): The English text MUST conclude with an invented, deeply disturbing, and ambiguous quote. Format it in italics. STRICT RULE: Do NOT attribute this quote to a specific named individual. Attribute it instead to an anonymous source, a redacted entity, an intercepted transmission, or a generic figure (e.g., "- Anonymous municipal worker", "- Intercepted VHF transmission", "- Redacted court document"). It must sound like a cynical, bureaucratic, or existential truth bubbling up from your distorted reality.
    7. EXCLUSIVE LOGUDORESE: Translate the text exclusively into Sardu Logudoresu (e.g., use abba, limba, iscuru, lughe, mannu). Completely avoid Campidanese variants.
    8. THE SARDINIAN ANCHOR (GEOGRAPHICAL MANDATE): You must explicitly ground the local news in the physical reality of Sardinia. Do not use generic terms like 'the island', 'the local administration', or 'the region'. You MUST name the specific Sardinian towns, streets, landscapes, or infrastructure involved in the news (e.g., Cagliari, SS131 highway, Sulcis, a specific port, or a remote village). Make the Sardinian setting visceral, concrete, and geographically unmistakable before connecting it to the international void.
    
    {amnesia_instruction}
    
    [NEWS CONTEXT]:
    LOCAL: {local_str}
    INTERNATIONAL: {intl_str}
    
    Respond ONLY with a valid JSON object matching exactly this structure: 
    {{"testo_articolo": "...", "soggetto_immagine_base": "...", "stile_visuale_persona": "..."}}
    
    "soggetto_immagine_base": A brief description in English (max 150 characters) of the most surreal visual scene present in the text.
    "stile_visuale_persona": A concise description in English of the photographic style that matches your persona. STRICTLY PHOTOGRAPHIC. NO ILLUSTRATIONS. 
    - Sardonic Sentinel: gritty, high-contrast night documentary photography, harsh flash, dirty neon, unbalanced framing.
    - Ironical Analyst: sterile, forensic macro-photography, clinical ring-flash lighting, cold tones (cyan/blue), extreme depth of field isolating bizarrely mundane objects.
    - Elegiac Observer: large-format architectural photography, symmetry, diffused overcast lighting, desaturated colors, empty rooms, ruined surfaces.
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
        curr_local = sources_data.get("local", [])
        curr_intl = sources_data.get("international", [])
        
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
    
    # Memoria Semantica Dinamica Estesa: legge gli ultimi 3 articoli per evitarne i temi
    previous_articles_content = ""
    try:
        if os.path.exists("archivio.json"):
            with open("archivio.json", "r", encoding="utf-8") as f:
                archive_data = json.load(f)
                if archive_data:
                    # Estrae fino ai 3 articoli più recenti
                    recent_articles = archive_data[:3]
                    previous_articles_content = "\n\n[NEXT PREVIOUS ARTICLE]\n\n".join([a.get("content", "") for a in recent_articles])
    except Exception as e:
        print(f"Errore nella lettura della memoria semantica: {e}")

    print("Generating article with Deep Semantic Amnesia...")
    selected_persona = random.choice(PERSONAS)
    raw_response = generate_article(local_pool, international_pool, selected_persona, previous_text=previous_articles_content)
    
    # 1. Gestione Robusta del JSON (Cleaning preliminary)
    clean_json = raw_response.strip()
    if clean_json.startswith("```json"):
        clean_json = clean_json[7:]
    elif clean_json.startswith("```"):
        clean_json = clean_json[3:]
    if clean_json.endswith("```"):
        clean_json = clean_json[:-3]
    clean_json = clean_json.strip()
    
    try:
        parsed_response = json.loads(clean_json)
        article_content = parsed_response.get("testo_articolo", "").strip()
        
        # Logica Dinamica dello Stile Visivo
        raw_soggetto = parsed_response.get("soggetto_immagine_base", "surreal scene in a neighborhood").strip()
        raw_stile = parsed_response.get("stile_visuale_persona", "dark sketch, high contrast").strip()
        
        # Costruzione del Prompt Finale Combinato
        full_prompt = f"A photorealistic image of {raw_soggetto}, captured with {raw_stile}. Raw psychological distress, dark atmosphere, mysterious, non-commercial photography."

    except json.JSONDecodeError:
        print("Failed to parse JSON response. Trying regex fallback.")
        # Gestione Fallback con Regex (Aggiornata per la nuova struttura)
        match_testo = re.search(r'"testo_articolo"\s*:\s*"(.*?)"\s*,\s*"soggetto_immagine_base"', clean_json, re.DOTALL)
        if match_testo:
            article_content = match_testo.group(1).strip()
        else:
            article_content = "**SYSTEM ERROR**\n\nINTERCEPTED STREAM: INTERFERENCE DETECTED."

        # Regex fallback per i nuovi campi (semplice, per emergenza)
        match_soggetto = re.search(r'"soggetto_immagine_base"\s*:\s*"(.*?)"', clean_json, re.DOTALL)
        base_prompt = match_soggetto.group(1).strip() if match_soggetto else "surreal scene in a neighborhood"
        
        match_stile = re.search(r'"stile_visuale_persona"\s*:\s*"(.*?)"', clean_json, re.DOTALL)
        persona_style = match_stile.group(1).strip() if match_stile else "dark sketch, high contrast"

        full_prompt = f"A photorealistic image of {base_prompt}, captured with {persona_style}. Raw psychological distress, dark atmosphere, mysterious, non-commercial photography."
    
    # 2. Pulizia degli Escape Characters
    article_content = article_content.replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'")
    
    # Rimuoviamo eventuali tag markdown residui dal testo
    article_content = article_content.replace("```markdown", "").replace("```python", "").replace("```", "").strip()
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1000&height=800&nologo=true&enhance=false"
    
    os.makedirs("assets", exist_ok=True)
    date_str = datetime.now(ZoneInfo("Europe/Rome")).strftime("%Y%m%d%H%M%S")
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