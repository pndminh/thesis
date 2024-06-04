import asyncio
from bs4 import BeautifulSoup
import requests
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
import sys

from backend.extractor.utils import save_html

sys.path.append("./")
from backend.extractor.db import init_db
from backend.logger import get_logger

logger = get_logger()
db = init_db()


async def fetch_html(url):
    html = load_html_from_db(url)
    if html is not None:
        return html
    else:
        async with async_playwright() as p:
            logger.info("Downloading html via headless browser")
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
                save_html(url=url, soup=html)
                await browser.close()
                return html


async def fetch_html_request(url):
    html = requests.get(url).content
    return html


def load_html_from_db(url):
    "Return a html of website from databse in parsed beautiful soup format"
    doc_ref = db.collection("crawl-result").where("url", "==", url).stream()
    for doc in doc_ref:
        html = doc.to_dict()["soup"]
        if html is None:
            return None
        logger.info("Getting HTML from firebase")
        return html
