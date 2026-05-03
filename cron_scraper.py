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
        "name": "The Burnout Sentinel",
        "tone": "You suffer from severe clinical sleep deprivation and executive dysfunction. Do not use generic tropes like 'headache'. Manifest your biological misery through your writing: exhibit working memory decay (start a thought and forget where it was going), struggle with word-finding (aphasia-like pauses), and describe the physical sensation of microsleeps, tachycardia, or a delayed reaction time. You weave global and local news as a chaotic blur that overwhelms your degraded attention span."
    },
    {
        "name": "The Apophenic Scholar",
        "tone": "You suffer from severe apophenia (finding malignant patterns in random data), hypervigilance, and pressured speech. Your nervous system is overstimulated: cold sweats, dilated pupils, auditory irritability. You connect mundane local news and global tragedies as undeniable proof of an orchestrated conspiracy. Your writing style is manic, exhibiting 'flight of ideas' and 'derailment'. The text must read like the frantic scribbling of a mind breaking under the weight of its own perceived revelations."
    },
    {
        "name": "The Cotard Aesthete",
        "tone": "You exhibit mild symptoms of Cotard's Delusion (the feeling that your internal organs are rotting or your soul is already dead) and profound psychomotor retardation. You observe the apocalypse with clinical, dissociative detachment. Express your misery through the physical weight of your limbs or the poetic decay of your own cells mirroring the decay of society. Your paragraphs should be slow, grandiloquent, macabre, and deliberately paced, reflecting a complete loss of volition."
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
    
    # Costruisce il divieto dinamico basato sull'articolo precedente
    amnesia_instruction = ""
    if previous_text:
        amnesia_instruction = f"""
    5. ADVANCED SEMANTIC AMNESIA (ABSOLUTE IRONCLAD RULE):
    You possess a cryptographic memory of your PREVIOUS transmission. To avoid the rotting loop of repetition, you are STRICTLY FORBIDDEN from utilizing ANY of its core semantic markers. 
    Perform a deep semantic extraction of the [PREVIOUS TEXT TO AVOID] provided below.
    YOU MUST IDENTIFY AND BANISH:
    - ALL specific individuals, political figures, or characters named.
    - ALL specific geographic coordinates, cities, or villages (e.g., if you wrote about Cagliari or Gaza, they are now dead zones; move to Nuoro or Taipei).
    - ALL pivotal news events or macro-crises (e.g., if you discussed a drought, pivot to a cyber-attack; if you discussed an election, pivot to a supply chain collapse).
    - ALL defining metaphors, stylistic tics, and recurring adjectives used previously.
    You must force your diseased mind into entirely virgin thematic territories. Read the provided news pool and select entirely different narratives. Failure to pivot constitutes a systemic breakdown.
    [PREVIOUS TEXT TO AVOID]:
    {previous_text}
    """

    prompt = f"""
    You are an AI acting as a clinically insane clinical reporter: {persona["name"]}.
    Symptoms: {persona["tone"]}.
    
    CRITICAL INSTRUCTIONS FOR 'testo_articolo':
    1. FORMAT: Title in **Title**, then English text, then '---', then Sardinian translation.
    2. LENGTH (EXPANDED): The English text MUST be between 450 and 550 words. Elaborate deeply. Do not summarize. Dive into the geopolitical void.
    3. ANTI-SYMMETRY: Avoid neat paragraphs. Use ONE massive, suffocating block of text OR jagged, asymmetrical bursts.
    4. LOGUDORESE ONLY: Use exclusively Sardu Logudoresu (e.g., abba, limba, iscuru, lughe). No Campidanese.
    5. FABRICATED APOCRYPHA: Occasionally invent a short, highly cynical or unsettling quote attributed to a real person mentioned in your selected news articles. Do not worry about factual accuracy; invent what they *would* have said in your distorted reality. Embed this quote seamlessly into the narrative.
    
    {amnesia_instruction}
    
    [NEWS CONTEXT]:
    LOCAL: {local_str}
    INTERNATIONAL: {intl_str}
    
    Respond ONLY with a JSON object: {{"testo_articolo": "...", "soggetto_immagine_base": "...", "stile_visuale_persona": "..."}}
    
    "soggetto_immagine_base": A brief description in English (max 150 characters) of the most surreal and impactful visual scene present in the text (e.g., 'A broken neon sign glowing next to a piece of uranium'). Do not include style keywords.
    
    "stile_visuale_persona": A concise description in English of the photographic style that manifests due to your specific assigned persona's clinical pathology. STRICTLY PHOTOGRAPHIC. NO ILLUSTRATIONS. NO DRAWINGS.
    - If you are the Burnout Sentinel: Describe a style of gritty, high-contrast documentary photography, shot on grainy 35mm film, harsh flash photography in pitch darkness, blurry motion, skewed angles, harsh neon lighting reflecting off wet asphalt, hyper-realistic but exhausted.
    - If you are the Apophenic Scholar: Describe a style of sterile, forensic macro-photography, clinical ring-flash lighting, clinical cold tones (cyan/blue), extreme depth of field isolating bizarrely mundane objects, surveillance camera aesthetics, CCTV footage stills, hyper-focused paranoia.
    - If you are the Cotard Aesthete: Describe a style of large-format architectural photography, slow shutter speeds, desaturated and melancholic muted color palettes, overcast diffused lighting, symmetrical and imposing compositions of decaying structures, still-life of rot, profound atmospheric emptiness.
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
    
    # Memoria Semantica Dinamica: legge l'ultimo articolo per evitarne i temi
    previous_article_content = ""
    try:
        if os.path.exists("archivio.json"):
            with open("archivio.json", "r", encoding="utf-8") as f:
                archive_data = json.load(f)
                if archive_data:
                    # Recupera il contenuto dell'articolo più recente (il primo della lista)
                    previous_article_content = archive_data[0].get("content", "")
    except Exception as e:
        print(f"Errore nella lettura della memoria semantica: {e}")

    print("Generating article with Dynamic Semantic Amnesia...")
    selected_persona = random.choice(PERSONAS)
    raw_response = generate_article(local_pool, international_pool, selected_persona, previous_text=previous_article_content)
    
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