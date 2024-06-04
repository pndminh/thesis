import asyncio
import requests
from playwright.async_api import async_playwright


async def fetch_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(5000)  # Adjust this selector as needed
        html = await page.content()
        await browser.close()
        return html


async def fetch_html_request(url):
    html = requests.get(url).content
    return html
