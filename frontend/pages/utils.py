import os
import subprocess
import sys
import time
import pandas as pd
import streamlit as st

sys.path.append("./")
from backend.extractor.task.container_extractor import ContainerExtractor
from backend.extractor.task.single_path_extractor import SinglePathElementExtractor
from backend.fetcher.fetcher import fetch_multiple_pages
from backend.logger import get_logger
from backend.extractor.task.nlp_tasks import (
    create_word_cloud,
    combine_res,
    llm_extract_task,
)

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
        state.extract_method = "Direct Path Extract"
    if "extracted_result_dataframe" not in state:
        state.extracted_result_dataframe = pd.DataFrame()


def init_downstream_analysis_state(state):
    if "analysis_data" not in state:
        state.analysis_data = pd.DataFrame()
    if "select_data_for_analysis" not in state:
        state.select_data_for_analysis = "Use extracted data"
    if "llm_result" not in state:
        state.llm_result = pd.DataFrame()


def clear_fetch_inputs(state):
    state["url_input"] = ""
    state.fetch_method = "Static fetch"
    state.scroll_timeout = 10
    state.expand_button_click = ""
    state.parsed_paths = ""


def clear_extract_settings(state):
    state["label"] = ""
    state.extract_identifier = []
    state.example_content = ""
    state.contents_to_extract = {}


def clear_llm_tasks_inputs(state):
    state["classification_label"] = ""
    state["classification_text"] = ""
    state.llm_tasks = {}


def clear_extract_inputs(state):
    state["label"] = ""
    state["extract_identifier"] = []
    state["example_content"] = ""


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


def add_data(label, example_content, extract_methods, contents_to_extract):
    for i, extract_method in enumerate(extract_methods):
        extract_methods[i] = (
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
        contents_to_extract[label].append((example_content, extract_methods))
    else:
        contents_to_extract[label] = []
        contents_to_extract[label].append((example_content, extract_methods))
    return contents_to_extract


async def handle_extract(html_list, contents_to_extract, batch, extract_type):
    if "Direct Path Extract" in extract_type:
        res = await single_path_extract(html_list, contents_to_extract, batch)
    else:
        res = await container_extract(html_list, contents_to_extract, batch)
    return res


async def single_path_extract(html_list, contents_to_extract, batch):
    html = html_list[0]
    extractor = SinglePathElementExtractor(contents_to_extract, html, html_list)
    if batch:
        await extractor.prepare_single_website_extract_template()
        res = await extractor.extract_from_multiple_websites(html_list)
    else:
        res = await extractor.single_element_extract_run_task()
    df = pd.DataFrame(res)
    return df


async def container_extract(html_list, contents_to_extract, batch):
    html = html_list[0]
    extractor = ContainerExtractor(contents_to_extract, html, html_list)
    if batch:
        await extractor.prepare_single_website_extract_template()
        await extractor.search_for_containers()
        structured_contents = await extractor.extract_from_multiple_websites(html_list)
    else:
        structured_contents = await extractor.container_extract_run_task()
    print(structured_contents)
    df = pd.DataFrame(structured_contents)
    return df


def generate_cloud_handler(
    data, color_map, max_words, columns, regex_patterns, fixed_words, background_color
):
    data = data.fillna("")
    dictionaries = data.to_dict("records")
    print(dictionaries)
    selected_columns = columns.split(",")
    selected_columns = (
        [col.strip() for col in selected_columns] if columns != "" else []
    )
    regex_list = regex_patterns.split(",")
    regex_list = (
        [pattern.strip() for pattern in regex_list] if regex_patterns != "" else []
    )
    fixed_words_list = fixed_words.split(",")
    fixed_words_list = (
        [word.strip() for word in fixed_words_list] if fixed_words != "" else []
    )
    return create_word_cloud(
        dictionaries,
        color_map,
        background_color,
        max_words,
        selected_columns,
        regex_list,
        fixed_words_list,
        save=True,
    )


def add_classification_task(task_name, task_description, llm_tasks):
    llm_tasks[task_name] = task_description
    return llm_tasks


async def handle_llm_task(data, llm_tasks, columns=None):
    data = data.fillna("")
    data = data.astype(str)
    dictionaries = data.to_dict("records")
    print(dictionaries)
    selected_columns = columns.split(",")
    selected_columns = (
        [col.strip() for col in selected_columns] if columns != "" else []
    )
    print(selected_columns)
    responses = await llm_extract_task(dictionaries, llm_tasks, columns)
    result = combine_res(dictionaries, responses, llm_tasks)
    df = pd.DataFrame(result)
    return df
