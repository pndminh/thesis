import os
import sys

sys.path.append(",/")
from backend.fetcher.fetcher import fetch_multiple_pages
from backend.logger import get_logger

logger = get_logger()


def init_fetch_state(state):
    if "fetch_method" not in state:
        state.fetch_method = "Static fetch"
    if "infinite_scroll" not in state:
        state.infinite_scroll = False
    if "scroll_timeout" not in state:
        state.scroll_timeout = 0
    if "expand_button_click" not in state:
        state.expand_button_click = False
    if "expand_button_text" not in state:
        state.expand_button_text = ""
    if "pagination" not in state:
        state.pagination = False
    if "max_pages" not in state:
        state.max_pages = 0


def clear_fetch_inputs(state):
    state["url_input"] = ""
    state.fetch_method = "Static fetch"
    state.scroll_timeout = 10
    state.expand_button_text = ""


async def fetch_url(state):
    url = state.url_input
    fetch_method = state.fetch_method
    infinite_scroll = state.infinite_scroll
    scroll_timeout = state.scroll_timeout
    expand_button_click = state.expand_button_click
    expand_button_text = state.expand_button_text
    pagination = state.pagination
    max_pages = state.max_pages

    static_fetch = True if fetch_method == "Static fetch" else False
    max_duration = scroll_timeout if infinite_scroll else 0
    if expand_button_click:
        expand_texts = expand_button_text.split(", ")
        expand_texts = [expand_text.strip() for expand_text in expand_texts]
    else:
        expand_texts = None
    pages = int(max_pages) if pagination else 0

    url_list = url.split(",")
    url_list = [url.strip() for url in url_list]
    print(url_list)
    try:
        html = await fetch_multiple_pages(
            url_list,
            static_fetch=static_fetch,
            max_duration=max_duration,
            scroll=infinite_scroll,
            expand=expand_button_click,
            expand_button_text=expand_texts,
        )
    except Exception as e:
        logger.info("Error while fetching URL")
    return html
