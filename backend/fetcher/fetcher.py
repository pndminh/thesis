import asyncio
import requests
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

db = init_db()
async def fetch_html(url):
    db
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            timeout = 30000
            await asyncio.wait_for(
                page.goto(url, wait_until="networkidle"),
                timeout=timeout / 1000,  # Convert milliseconds to seconds
            )
        except asyncio.TimeoutError:
            # If the custom timeout occurs, catch the error and proceed to capture HTML
            print(
                f"Timeout occurred after {timeout / 1000} seconds. Capturing the available content."
            )
        except PlaywrightTimeoutError as e:
            # Handle Playwright-specific timeout error if needed
            print(f"Playwright timeout error: {str(e)}")
        finally:
            # Capture the HTML content that is available at this point
            html = await page.content()
            await browser.close()
            return html


async def fetch_html_request(url):
    html = requests.get(url).content
    return html
