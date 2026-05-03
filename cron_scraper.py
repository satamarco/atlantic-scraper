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

def generate_article(local_texts, intl_texts):
    selected_persona = random.choice(PERSONAS)
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
    
    You MUST respond ONLY with a valid JSON object containing exactly three keys: "testo_articolo", "soggetto_immagine_base", and "stile_visuale_persona". Do not wrap the JSON in markdown blocks.
    
    "testo_articolo": Write the text FIRST in English, then insert a markdown horizontal rule (---), and then provide a dark, visceral translation of the EXACT same text in SARDINIAN (Limba Sarda).
    
    CRITICAL INSTRUCTIONS FOR 'testo_articolo' (IRONCLAD RULES):
    
    1. EXACT FORMAT SEQUENCE: Your output MUST strictly follow this sequence, with nothing else:
       - FIRST: A single, visceral Title enclosed in ** (e.g., **Metallic Tastes and Burning Forests**). NO markdown headers (#).
       - SECOND: Two line breaks (\n\n).
       - THIRD: The English body text. It MUST be between 350 and 450 words (a target of 400 words with a 50-word margin) to allow for deep, rambling clinical argumentation.
       - FOURTH: A markdown horizontal rule (---) on a new line.
       - FIFTH: The Sardinian translation of the EXACT same body text. No titles in the Sardinian section.
       
    2. CLINICAL STRUCTURAL ENTROPY (MANDATORY): You MUST absolutely avoid standard, symmetrical paragraph structures. The English text (and its Sardinian translation) must be written as ONE massive, suffocating block of text OR a series of heavily fragmented, asymmetrical short bursts. Do not write neat, equal-sized paragraphs. Interrupt your geopolitical analysis abruptly and frequently to describe your assigned physical symptoms in deep detail.
    
    3. THE SARDINIAN TRANSLATION: Translate your manic, clinical English text into Sardinian (Limba Sarda). Use an archaic, dark, and visceral vocabulary. Mixing campidanese and logudorese variants is perfectly fine to reflect your fractured clinical persona.
    
    4. ABSOLUTE BANS: NO exclamation marks (!). NO ellipsis (...). NO repetitive title formulas like 'Dossier:'. Ignore news about Royal Family, Beckham, celebrities, weddings, astrology. Do NOT use the words: "suffrage", "suffragettes", "Lincoln", "Virginia Woolf", "Rachel Carson".
    
    NARRATIVE AND STYLE RULES:
    - Tone: {selected_persona['tone']}
    - SARDINIAN RESONANCE AND ABRUPT JUMPS: Mix local Sardinian news with global geopolitics abruptly (di punto in bianco) within the exact same paragraph or sentence. NO PREAMBLES or soft transitions. Connect them using dark irony; let the sheer absurdity of the juxtaposition speak for itself.
    - ABSOLUTE ATEMPORALITY: NEVER use daily temporal expressions (e.g., "today", "yesterday", "tomorrow", "Friday"). Treat events as a continuous flow.
    - AGGRESSIVE EDITING & DISCARDING: I am giving you 15 articles, but you MUST NOT use all of them. You MUST DISCARD at least 10 articles. Select ONLY the 4 or 5 most potent and absurd events to create exactly 3 dark juxtapositions. Ignore the rest entirely. Less is more.
    - The Absurdist Juxtaposition (Folklore vs Global Collapse): When merging Sardinian news with international geopolitics, you must intentionally juxtapose massive global crises (war, technology, economic collapse) with hyper-local, seemingly trivial Sardinian events (e.g., an artichoke festival, a local game of 'la murra', a village procession, or food news). Treat these local folkloric events with dark, fatalistic gravity. A village festival is not a happy event; it is a desperate, absurd human ritual to ignore the impending apocalypse. A game of 'murra' in Mandas is as cutthroat and meaningless as a UN summit. Use this stark contrast to highlight the profound absurdity of human existence.
    
    "soggetto_immagine_base": A brief description in English (max 150 characters) of the most surreal and impactful visual scene present in the text (e.g., 'A broken neon sign glowing next to a piece of uranium'). Do not include style keywords.
    
    "stile_visuale_persona": A concise description in English of the medical/neuro-visual style that manifests due to your specific assigned persona's clinical pathology.
    - If you are the Burnout Sentinel: Describe a visual style of insomnia-induced sketches, German Expressionist film, shaky cam, high-contrast monochrome, random noise, microsleep blurs, and raw, incomplete outlines.
    - If you are the Apophenic Scholar: Describe a visual style of dense conspiracy maps, occult diagrams, hidden Symbolism, interconnected red threads, hyper-detailed drawings, diagrammatic chaos, and "flight of ideas" collage.
    - If you are the Cotard Aesthete: Describe a visual style of grand, macabre Decadent art, 19th-century Daguerreotypes of ruins, Symbolist decay, morbid beauty, melancholic apathy, smooth, unrealistic realism, and a complete loss of color/volition.
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
    
    print("Generating article and prompt...")
    raw_response = generate_article(local_pool, international_pool)
    
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
        full_prompt = f"{raw_soggetto}, illustrated in the style of {raw_stile}. Unfiltered stream of consciousness, raw psychological distress, dark atmosphere, mysterious, non-commercial art."

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

        full_prompt = f"{base_prompt}, in the style of {persona_style}. Unfiltered stream of consciousness, raw psychological distress, dark atmosphere, mysterious, non-commercial art."
    
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