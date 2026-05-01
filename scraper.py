import asyncio
from playwright.async_api import async_playwright

async def scrape_all_sources():
    sources_data = {
        "the_atlantic": [],
        "unione_sarda": [],
        "sardinia_post": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. The Atlantic
        try:
            await page.goto("https://www.theatlantic.com/world/", timeout=60000)
            await page.wait_for_selector('h3', timeout=10000)
            articles = await page.query_selector_all('h3')
            for article in articles[:10]: # prendiamo i primi 10 per non esagerare
                text = await article.text_content()
                if text: sources_data["the_atlantic"].append(text.strip())
        except Exception as e:
            print(f"Errore scraping The Atlantic: {e}")
            
        # 2. L'Unione Sarda
        try:
            await page.goto("https://www.unionesarda.it/", timeout=60000)
            await page.wait_for_selector('h2', timeout=10000) # Spesso i titoli sono in h2 o h1
            articles = await page.query_selector_all('h2')
            for article in articles[:10]:
                text = await article.text_content()
                if text: sources_data["unione_sarda"].append(text.strip())
        except Exception as e:
            print(f"Errore scraping Unione Sarda: {e}")
            
        # 3. Sardinia Post
        try:
            await page.goto("https://www.sardiniapost.it/", timeout=60000)
            await page.wait_for_selector('h3', timeout=10000) # Titoli spesso in h3 o h2
            articles = await page.query_selector_all('h3')
            for article in articles[:10]:
                text = await article.text_content()
                if text: sources_data["sardinia_post"].append(text.strip())
        except Exception as e:
            print(f"Errore scraping Sardinia Post: {e}")
            
        await browser.close()
        return sources_data

if __name__ == "__main__":
    data = asyncio.run(scrape_all_sources())
    for source, texts in data.items():
        print(f"--- {source.upper()} ---")
        for text in texts:
            print(text)
