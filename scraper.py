import asyncio
from playwright.async_api import async_playwright
import json
import os
import random
from datetime import datetime
from bs4 import BeautifulSoup

USED_LINKS_FILE = "used_links.json"

def load_used_links():
    if os.path.exists(USED_LINKS_FILE):
        try:
            with open(USED_LINKS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    return set()

def save_used_links(links):
    with open(USED_LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(links), f, indent=4)

SOURCES = {
    "the_atlantic": {
        "base_url": "https://www.theatlantic.com",
        "sections": ["/world/", "/politics/", "/science/", "/technology/", "/business/"],
        "link_selector": "a[href*='/archive/']"
    },
    "unione_sarda": {
        "base_url": "https://www.unionesarda.it",
        "sections": ["/news-sardegna/", "/tempo-libero/", "/cultura/"],
        "link_selector": "article a, h2 a, h3 a"
    },
    "sardinia_post": {
        "base_url": "https://www.sardiniapost.it",
        "sections": ["/category/cucina-e-cibo/", "/category/culture/", "/category/eventi/"],
        "link_selector": "h3 a, .entry-title a"
    },
    "nbc_news": {
        "base_url": "https://www.nbcnews.com",
        "sections": ["/world", "/politics", "/tech", "/science", "/business"],
        "link_selector": "h2 a, .v-f a"
    },
    "vice": {
        "base_url": "https://www.vice.com/en",
        "sections": ["/section/news", "/section/tech", "/section/world", "/section/politics"],
        "link_selector": "h3 a, .hdg a"
    },
    "cronache_nuoresi": {
        "base_url": "https://www.cronachenuoresi.it",
        "sections": ["/category/cultura-e-societa/", "/category/eventi/"],
        "link_selector": "h2 a, .entry-title a"
    },
    "indip": {
        "base_url": "https://indip.it",
        "sections": ["/inchieste/", "/ambiente/", "/societa/"],
        "link_selector": "h2 a, h3 a, .entry-title a"
    }
}

async def fetch_article_data(page, url, timeout=30000):
    try:
        await page.goto(url, timeout=timeout)
        await page.wait_for_load_state("domcontentloaded")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Try to find date
        date_str = None
        date_meta = soup.find("meta", {"property": "article:published_time"}) or \
                    soup.find("meta", {"name": "pubdate"}) or \
                    soup.find("meta", {"name": "parsely-pub-date"})
        
        if date_meta:
            date_str = date_meta.get("content")

        # Validate date (within 6 months / 180 days)
        if date_str:
            try:
                clean_date = date_str.split('T')[0]
                dt = datetime.strptime(clean_date, "%Y-%m-%d")
                if (datetime.now() - dt).days > 180:
                    return None # Too old
            except Exception:
                pass # If parsing fails, we keep it

        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])
        # Limit the snippet to roughly 400 words to save Gemini context
        text_snippet = " ".join(text.split()[:400])

        if len(text_snippet) < 100:
            return None

        return text_snippet
    except Exception as e:
        return None

async def scrape_all_sources(timeout=30000):
    used_links = load_used_links()
    new_used_links = set(used_links)
    
    sources_data = {
        "the_atlantic": [],
        "unione_sarda": [],
        "sardinia_post": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Add a realistic user agent to avoid blocking
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for source_name, source_info in SOURCES.items():
            print(f"\n=== Exploring {source_name.upper()} ===")
            valid_articles = []
            
            sections = list(source_info["sections"])
            random.shuffle(sections) # Randomize to get diverse themes
            
            collected_links = set()
            
            # Step 1: Collect potential links from various sections
            for section in sections:
                if len(collected_links) >= 15: # Gather enough candidate links
                    break
                    
                section_url = source_info["base_url"] + section
                print(f"-> Scanning section: {section_url}")
                try:
                    await page.goto(section_url, timeout=timeout)
                    await page.wait_for_timeout(2000)
                    links = await page.query_selector_all(source_info["link_selector"])
                    
                    for link in links:
                        href = await link.get_attribute("href")
                        if href:
                            if href.startswith('/'):
                                href = source_info["base_url"] + href
                            if href.startswith(source_info["base_url"]) and href not in used_links and href not in collected_links:
                                collected_links.add(href)
                except Exception as e:
                    print(f"   [!] Failed scanning section {section_url}")

            # Step 2: Fetch article details until we have exactly 3 (roughly 18 total)
            collected_links = list(collected_links)
            random.shuffle(collected_links)
            
            for url in collected_links:
                if len(valid_articles) >= 3:
                    break
                    
                print(f"   - Testing article: {url}")
                text = await fetch_article_data(page, url, timeout=timeout)
                if text:
                    print(f"     [+] Valid! Added to collection.")
                    valid_articles.append(text)
                    new_used_links.add(url)
                else:
                    print(f"     [-] Discarded (Too old, short, or inaccessible).")
                    # Add to used_links so we don't try again next time
                    new_used_links.add(url)
                    
            sources_data[source_name] = valid_articles
            print(f"-> Completed {source_name}: {len(valid_articles)}/3 articles collected.")
            
        await browser.close()
        
    save_used_links(new_used_links)
    return sources_data

if __name__ == "__main__":
    data = asyncio.run(scrape_all_sources())
    for s, t in data.items():
        print(f"Final count {s}: {len(t)}")
