import os
import sys
import time
import streamlit as st

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
    if "dynamic_fetch_options" not in state:
        state.dynamic_fetch_options = {
            "infinite_scroll": 0,
            "expand_button_click": "",
            "pagination": 0,
        }


def init_extract_state(state):
    if "extract_method" not in state:
        state.extract_method = [""]


def clear_fetch_inputs(state):
    state["url_input"] = ""
    state.fetch_method = "Static fetch"
    state.scroll_timeout = 10
    state.expand_button_click = ""


async def fetch(url, fetch_method, dynamic_fetch_options):
    # dynamic_fetch_options = {"infinite_scroll": 0, "expand_button_text": "", "pagination": 0}
    static_fetch = True if fetch_method == "Static fetch" else False
    infinite_scroll = False if dynamic_fetch_options["infinite_scroll"] == 0 else True
    expand_button_click = (
        False if dynamic_fetch_options["expand_button_click"] == "" else True
    )
    pagination = False if dynamic_fetch_options["pagination"] == 0 else True

    expand_texts = dynamic_fetch_options["expand_button_click"].split(", ")
    expand_texts = [expand_text.strip() for expand_text in expand_texts]
    url_list = url.split(",")
    url_list = [url.strip() for url in url_list]
    print(url_list)
    try:
        html = await fetch_multiple_pages(
            url_list,
            static_fetch=static_fetch,
            scroll=infinite_scroll,
            max_duration=dynamic_fetch_options["infinite_scroll"],
            expand=expand_button_click,
            expand_button_text=expand_texts,
        )
    except Exception as e:
        logger.info("Error while fetching URL")
    return html


def write_html_files(html_list):
    for i, html in enumerate(html_list):
        st.info("Writing file", icon="📝")
        with open(f"results/html/html_{i}_{int(time.time())}.html", "w") as f:
            f.write(html)


def add_data(label, example_content, extract_methods, contents_to_extract: dict):
    for extract_method in extract_methods:
        extract_method = (
            extract_method.replace(
                "Select ",
                "",
            )
            .lower()
            .strip()
            .replace(" ", "_")
        )
        # print(extract_method)

    if label in contents_to_extract.keys():
        print(
            contents_to_extract[label][0],
            type(contents_to_extract[label][0]),
        )
        contents_to_extract[label].append((example_content, extract_method))
    else:
        contents_to_extract[label] = []
        contents_to_extract[label].append((example_content, extract_method))
    print(contents_to_extract)
    return contents_to_extract
