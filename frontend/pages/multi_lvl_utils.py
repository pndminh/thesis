import time
import streamlit as st
import sys
import os
from pages.utils import fetch, handle_extract

sys.path.append("./")
from backend.extractor.task.single_path_extractor import SinglePathElementExtractor
from backend.fetcher.fetcher import fetch_multiple_pages
from backend.logger import get_logger

logger = get_logger()


def init_fetch_state(state):
    if "m_fetch_method" not in state:
        state.m_fetch_method = "Dynamic fetch"
    if "m_infinite_scroll" not in state:
        state.m_infinite_scroll = False
    if "m_expand_button_click" not in state:
        state.m_expand_button_click = False
    if "m_expand_button_text" not in state:
        state.m_expand_button_text = ""
    if "m_dynamic_fetch_options" not in state:
        state.m_dynamic_fetch_options = {
            "infinite_scroll": 0,
            "expand_button_click": "",
        }


def clear_fetch_inputs(state):
    state["url_input"] = ""
    state.m_fetch_method = "Dynamic fetch"
    state.m_scroll_timeout = 0
    state.m_expand_button_click = ""
    state.curr_fetch_inputs = {}
    state.fetch_setups[state.curr_lvl] = {}


def init_extract_state(state):
    if "m_extract_method" not in state:
        state.m_extract_method = "Direct Path Extract"
    if "m_get_links" not in state:
        state.m_get_links = False
    if "m_batch" not in state:
        state.m_batch = False


def clear_extract_inputs(state):
    state["extract_method"] = "Direct Path Extract"
    state["m_get_links"] = False
    state["m_batch"] = False
    state.curr_contents_to_extract = {}
    state.curr_extract_inputs = {}
    state.extract_setups[state.curr_lvl] = {}


async def handle_get_links_extract(
    html_list, contents_to_extract, batch, extract_method
):
    extractor = SinglePathElementExtractor(
        example_input=contents_to_extract, html=html_list[0], html_list=html_list
    )
    links = await extractor.extract_links()
    res = []
    for value in links.values():
        res += [*value]
    return ", ".join(res)


async def start_pipeline(state):
    extracted_links = ""
    extracted_contents = {}
    progress_bar = st.progress(0, text=f"{0}%: Fetching urls from level {1}")
    lvls = len(state.extract_setups)
    for i, extract_inputs in enumerate(state.extract_setups):
        fetch_inputs = state.fetch_setups[i]
        extract_inputs = state.extract_setups[i]
        if i == 0:
            urls = fetch_inputs["urls"]
        else:
            urls = fetch_inputs["urls"] + ", " + extracted_links
            print("combined urls: ", urls, type(urls))
        fetch_method = fetch_inputs["fetch_method"]
        extract_method = extract_inputs["extract_method"]
        contents_to_extract = extract_inputs["contents_to_extract"]
        batch = extract_inputs["batch"]
        print(
            urls,
            fetch_method,
            {
                "infinite_scroll": fetch_inputs["infinite_scroll"],
                "expand_button_click": fetch_inputs["expand_button_click"],
            },
        )
        html = await fetch(
            urls,
            fetch_method,
            {
                "infinite_scroll": fetch_inputs["infinite_scroll"],
                "expand_button_click": fetch_inputs["expand_button_click"],
            },
        )
        percent_complete = (2 * i + 1) / (2 * lvls)
        progress_bar.progress(
            percent_complete,
            text=f"{percent_complete*100}%: Extracting HTMLs from level {i+1}",
        )
        if extract_method == "Extract Links":
            extracted_contents = await handle_get_links_extract(
                html, contents_to_extract, batch, extract_method
            )
            extracted_links = extracted_contents
            print("extracted_links", extracted_links)
            print(f"Extract links lvl {i+1}")
            percent_complete = (2 * i + 2) / (2 * lvls)
            progress_bar.progress(
                percent_complete,
                text=f"{percent_complete*100}%: Fetching urls from lvl {i+2}",
            )
        else:
            logger.info("html list:", html, type(html))
            try:
                extracted_contents = await handle_extract(
                    html, contents_to_extract, batch, extract_method
                )
                progress_bar.progress(
                    1.0,
                    text=f"{percent_complete*100}%: Extracted urls from level {i+1}",
                )
                time.sleep(0.1)
            except Exception as e:
                logger.info(
                    f"Error while extracting contents from page at lvl {i+1}: {e}"
                )
    progress_bar.empty()

    return extracted_contents
