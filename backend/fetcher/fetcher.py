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
                await save_html(url=url, soup=prepare_html(html))
                await browser.close()
                return html


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


async def find_expand_button(page, button_text=None):
    count = 0
    failed_count = 0
    button_text_string = (
        r"(Expand|See more|Xem thêm|Hiển thị)"
        if button_text is None
        else rf"({"|".join(button_text)})"
    )
    logger.info("Locating 'See more' buttons")
    buttons = await page.get_by_role("button").filter(
    has_text=re.compile(button_text_string, re.IGNORECASE)).all()
    for button in buttons:
        try:
            # Attempt to click on the button
            await button.click()
            count += 1
        except Exception:
            # Log a message if a timeout error occurs and continue to the next button
            failed_count +=1
            logger.warning(f"Timeout while trying to click button. Moving to next button.")
            continue
    logger.info(
        f"Successfully clicked {count} out of {count + failed_count}"
    )


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


async def fetch_infinite_page(
    url, max_duration=20, scroll=True, expand=False, expand_button_text=None
):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        # await save_session_storage(page)

        try:
            await page.goto(url)
            logger.info("Getting page")
        except Exception as e:
            print(str(e))
            return

        # This code makes the WebDriver scroll down
        if scroll:
            await scroll_page(page, max_duration=max_duration)
        if expand:
            await find_expand_button(page, expand_button_text)

        # Return the page content regardless of click success
        selector = await page.content()
        # selector = await page.query_selector("div.rq0escxv.l9j0dhe7.du4w35lb")
        # Save HTML code in a variable to parse it with BeautifulSoup
        # html = await selector.inner_html()
        # print(html)
        await browser.close()
        return selector


async def test_see_more_buttons(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False
        )  # Set headless to False to see the browser actions
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url)
            print("Page loaded successfully")
        except Exception as e:
            print("Please, put right link:", str(e))
            return
        # Wait for the page to load content
        await asyncio.sleep(5)

        try:
            item_close = await page.query_selector('[aria-label="Đóng"]')
            logger.info("Closed login popups")
            if item_close is not None:
                await item_close.click()
                await page.mouse.wheel(-1000, 0)
        except Exception as e:
            print("Error closing popup:", str(e))

        # Find and count all "See More" buttons
        see_more_buttons = await page.query_selector_all('button:has-text("Xem thêm")')

        see_more_buttons = await (
            page.get_by_role("button").filter(has_text="See more").all()
        )
        # print(f"Found {len(see_more_buttons)} 'See More' buttons")

        # Optionally, print the buttons' texts to verify they are the correct ones
        # for button in see_more_buttons:
        #     text = await button.inner_text()
        #     print(f"Button text: {text}")
        for li in await page.get_by_role("listitem").all():
            await li.click()

        await browser.close()
        return see_more_buttons


# URL of the Facebook page to test
