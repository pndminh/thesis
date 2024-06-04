import asyncio
from playwritght.async_api import async_playwright

async def fetch_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)# Adjust this selector as needed
        html = await page.content()
        await browser.close()
        return html