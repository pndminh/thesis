import asyncio
import json
import os
from re import Pattern
import re
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

# from playwright.sync_api import sync_playwright
from backend.extractor.utils import prepare_html, save_html
from backend.extractor.db import init_db
from backend.logger import get_logger
import asyncio
from playwright.async_api import async_playwright

load_dotenv()
logger = get_logger()
db = init_db()

async def get_page_content(page, url, browser):
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
        # html = await page.content()
        # await save_html(url=url, soup=prepare_html(html))
        # await browser.close()
        # return html
        return page

async def scroll_page(page, max_duration):
    await page.evaluate(
        """
            var intervalID = setInterval(function () {
                var scrollingElement = (document.scrollingElement || document.body);
                scrollingElement.scrollTop = scrollingElement.scrollHeight;
            }, 200);
            """
    )
    prev_height = None
    start_time = time.time()

    # Handle potential login popups
    try:
        item_close = await page.query_selector('[aria-label="Đóng"]')
        if item_close is not None:
            await item_close.click()
            logger.info("Closed login popups")
            await page.mouse.wheel(-1000, 0)
    except Exception as e:
        print("Error closing popup:", str(e))
    while True:
        logger.info("Handling scrolls")
        curr_height = await page.evaluate("(window.innerHeight + window.scrollY)")
        elapsed_time = time.time() - start_time
        if elapsed_time > max_duration:
            print(f"Reached maximum scroll duration of {max_duration} seconds.")
            await page.evaluate("clearInterval(intervalID)")
        if not prev_height:
            prev_height = curr_height
            await asyncio.sleep(15)
        elif prev_height == curr_height:
            logger.info("No more new content, stopping fetcher")
            await page.evaluate("clearInterval(intervalID)")
            break
        else:
            prev_height = curr_height
            await asyncio.sleep(15)

async def click_button(button):
    try:
        # Attempt to click on the button
        await button.click()
        return True
    except Exception as e:
        # Log a message if an error occurs and continue to the next button
        logger.warning("Timeout occurred")
        return False
    
async def find_expand_button(page, button_text=None):
    button_text_string = (
        r"(Expand|See more|Xem thêm|Hiển thị)"
        if button_text is None
        else rf"({"|".join(button_text)})"
    )
    logger.info("Locating 'See more' buttons")
    buttons = await page.get_by_role("button").filter(has_text=re.compile(button_text_string, re.IGNORECASE)).all()
    results = await asyncio.gather(*(click_button(button) for button in buttons))
    count = sum(1 for result in results if result)
    logger.info(f"Clicked {count} 'See more' buttons out of {len(buttons)}")

async def fetch_static_page(url):
    html = requests.get(url).content
    return html.decode("utf-8")

def load_html_from_db(url):
    "Return a html of website from databse in parsed beautiful soup format"
    doc_ref = db.collection("crawl-result").where("url", "==", url).stream()
    for doc in doc_ref:
        html = doc.to_dict()["soup"]
        if html is None:
            return None
        logger.info("Getting HTML from firebase")
        return html

async def fetch_dynamic_page(url, max_duration=20, scroll=True, expand=False, expand_button_text=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        # await save_session_storage(page)
        if not scroll:
            page = await get_page_content(page=page, url=url, browser=browser)
        else: 
            try:
                await page.goto(url)
                logger.info("Getting page")
            except Exception as e:
                print(str(e))
                return
            await scroll_page(page, max_duration=max_duration)
        if expand:
            await find_expand_button(page, expand_button_text)

        html = await page.content()
        await browser.close()
    return html

async def fetch_page(
    url, static_fetch = False, max_duration=20, scroll=True, expand=False, expand_button_text=None
):
    if static_fetch:
        html = await fetch_static_page(url)
        return html
    else:
        html = await fetch_dynamic_page(url, max_duration, scroll, expand, expand_button_text)
        return html

async def fetch_multiple_pages(urls, static_fetch = False, max_duration=20, scroll=True, expand=False, expand_button_text=None):
    html_list = await asyncio.gather(*[fetch_page(url, static_fetch, max_duration, scroll, expand, expand_button_text) for url in urls])
    return html_list
    
