### `app.py`

```python
import streamlit as st
import json
import os
from datetime import datetime, timezone, timedelta
import time

@st.cache_resource
def install_playwright_browsers():
    os.system("playwright install chromium")

install_playwright_browsers()

from dotenv import load_dotenv
load_dotenv()

ARCHIVE_FILE = "archivio.json"

st.set_page_config(page_title="Geopolitical Synthesizer", layout="centered")

st.markdown("""
<style>
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden !important;}

    /* Swiss Minimalist Typography & Colors */
    *, html, body, [class*="css"], .stApp, .block-container {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        color: #000000 !important;
        font-weight: bold !important;
        letter-spacing: -0.05em !important;
    }
    
    .main-title {
        font-size: 3.5rem !important;
        font-weight: bold;
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0 !important;
        letter-spacing: -0.05em;
    }
    
    hr {
        border: none !important;
        border-top: 1px solid #000000 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Countdown style */
    .countdown-text {
        font-size: 5rem;
        font-weight: bold;
        color: #000000;
        text-align: left;
        letter-spacing: -0.05em;
        line-height: 1;
        margin-bottom: 0 !important;
    }
    
    /* Article Title Styling (which is rendered as h1 by Markdown) */
    .article-container h1 {
        font-size: 4rem !important;
        line-height: 1.1 !important;
        border-bottom: none !important;
        padding-bottom: 0 !important;
        margin-bottom: 2rem !important;
        margin-top: 1rem !important;
    }
    
    /* Image styling */
    [data-testid="stImage"] img {
        filter: grayscale(100%) !important;
        border-radius: 0 !important;
        margin-bottom: 2rem !important;
    }
    
    /* Archive Date styling */
    .archive-date {
        font-size: 1rem;
        font-weight: bold;
        color: #000000;
        text-transform: uppercase;
        display: block;
        margin-bottom: 1rem;
    }
    
    /* Spacing & Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 800px !important;
    }
    
    p, div {
        line-height: 1.6 !important;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>Geopolitical Synthesizer</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
countdown_placeholder = st.empty()
st.markdown("<hr>", unsafe_allow_html=True)

article_placeholder = st.empty()

# Render the entire cumulative archive
def render_article():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                archive_data = json.load(f)
                
            if archive_data and len(archive_data) > 0:
                with article_placeholder.container():
                    for i, entry in enumerate(archive_data):
                        st.markdown(f"<div class='archive-date'>{entry.get('timestamp', '')}</div>", unsafe_allow_html=True)
                        if entry.get("image_path") and os.path.exists(entry["image_path"]):
                            st.image(entry["image_path"], use_column_width=True)
                        st.markdown(f"<div class='article-container'>{entry['content']}</div>", unsafe_allow_html=True)
                        if i < len(archive_data) - 1:
                            st.markdown("<hr>", unsafe_allow_html=True)
            else:
                article_placeholder.info("No article available yet.")
        except json.JSONDecodeError:
            article_placeholder.error("Error reading archivio.json")
    else:
        article_placeholder.info("No article available yet.")

render_article()

# Update countdown every second
while True:
    now = datetime.now(timezone.utc)
    # Calculate next milestone (00:00 or 12:00 UTC)
    if now.hour < 12:
        next_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
    diff = next_time - now
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    countdown_placeholder.markdown(f"<div class='countdown-text'>{time_str}</div>", unsafe_allow_html=True)
    time.sleep(1)
```

### `cron_scraper.py`

```python
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
    - At the VERY END of your response, on a new line, write exactly "IMAGE_PROMPT: " followed by a single line of text in English describing an image that captures the essence of your article.
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
        
    full_prompt = f"{base_prompt}, Minimalist Swiss Graphic Design, brutalist, abstract shapes, black and white, high contrast, ink bleed style, no text"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=false"
    
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
```