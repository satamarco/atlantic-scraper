import asyncio
from playwright.async_api import async_playwright

async def scrape_atlantic_world():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.theatlantic.com/world/")
        
        # Attendi che gli articoli siano caricati (seleziona i selettori appropriati)
        # Questo è un esempio generico, andrebbe affinato in base alla struttura del sito
        await page.wait_for_selector('h3')
        
        articles = await page.query_selector_all('h3')
        texts = []
        for article in articles:
            text = await article.text_content()
            texts.append(text.strip())
            
        await browser.close()
        return texts

if __name__ == "__main__":
    texts = asyncio.run(scrape_atlantic_world())
    for text in texts:
        print(text)
