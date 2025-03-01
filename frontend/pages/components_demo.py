import asyncio
import json
import time
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from matplotlib import colormaps

import os
import sys


sys.path.append("./")
from backend.extractor.utils import prepare_html_ui
from frontend.utils import get_page_name
from backend.logger import get_logger
from frontend.pages.utils import (
    add_classification_task,
    add_data,
    clear_extract_inputs,
    clear_extract_settings,
    clear_fetch_inputs,
    clear_llm_tasks_inputs,
    fetch,
    generate_cloud_handler,
    handle_extract,
    handle_llm_task,
    init_downstream_analysis_state,
    init_extract_state,
    init_fetch_state,
    write_html_files,
)

if "html" not in st.session_state:
    st.session_state.html = []
if "contents_to_extract" not in st.session_state:
    st.session_state.contents_to_extract = {}
if "parsed_html" not in st.session_state:
    st.session_state.parsed_html = BeautifulSoup()
if "parsed_paths" not in st.session_state:
    st.session_state.parsed_paths = ""


logger = get_logger()


def click_fetch_btn():
    st.session_state.fetched = True


def click_extract_btn():
    st.session_state.extracted = True


def click_cloud_generate_btn():
    st.session_state.word_cloud_generated = True


def click_llm_analyze_btn():
    st.session_state.llm_analyzed = True


async def fetch_module():
    with st.container():
        st.markdown("# Fetch Module")
        url_input = st.text_input("Input Url", key="url_input")
        fetch_method = st.selectbox(
            "How should your website be fetched",
            ("Static fetch", "Dynamic fetch"),
            key="fetch_method",
        )
        if fetch_method == "Dynamic fetch":
            dynamic_fetch_options = st.expander("Dynamic fetch options", expanded=True)
            col1, col2 = dynamic_fetch_options.columns(
                [0.4, 0.6], vertical_alignment="top"
            )
            infinite_scroll = col1.checkbox("Infinite Scroll", key="infinite_scroll")
            expand_button_click = col1.checkbox(
                "Click expand buttons", key="expand_button"
            )
            scroll_timeout = col2.slider(
                label="Scroll timeout",
                min_value=0,
                max_value=180,
                value=10,
                disabled=not (infinite_scroll),
            )
            # max_pages = col2.slider(
            #     "Max number of fetched page",
            #     key="max_pages",
            #     min_value=2,
            #     max_value=20,
            #     value=5,
            #     disabled=not (pagination),
            # )
            expand_text = col2.text_input(
                label="Expand button texts",
                key="expand_button_text",
                disabled=not (expand_button_click),
            )
            if infinite_scroll:
                st.session_state.dynamic_fetch_options["infinite_scroll"] = (
                    scroll_timeout
                )
            if expand_button_click:
                st.session_state.dynamic_fetch_options["expand_button_click"] = (
                    expand_text
                )
            # if pagination:
            #     st.session_state.dynamic_fetch_options["pagination"] = max_pages
        col1, col2 = st.columns(2)
        clear_btn = col1.button(
            "Clear fetch",
            use_container_width=True,
            on_click=clear_fetch_inputs,
            args=[st.session_state],
        )
        fetch_btn = col2.button(
            "Fetch",
            type="primary",
            use_container_width=True,
            on_click=click_fetch_btn,
        )
        result_container = st.container(height=200)
        result_container.markdown("###### Fetch Result")

        if fetch_btn:
            st.toast("Fetching HTML...", icon="💬")
            print(url_input, fetch_method, st.session_state.dynamic_fetch_options)
            html = await fetch(
                url_input, fetch_method, st.session_state.dynamic_fetch_options
            )
            st.session_state.html = html
            logger.info("Fetch done, saving to session state")
            st.toast("Fetched!", icon="🎉")
            try:
                st.session_state.parsed_html, paths = prepare_html_ui(
                    st.session_state.html[0]
                )
                st.session_state.parsed_paths = "\n".join(paths)
            except Exception as e:
                logger.info(f"An error occurred while parsing HTML: {e}")

        if st.session_state.fetched:
            if st.session_state.parsed_paths != "":
                result_container.text(st.session_state.get("parsed_paths"))
            else:
                result_container.error("Error parsing HTML")
            # save_fetch_result()
            # try:
            #     result_container.code(html[0], "html")
            # except:
            #     logger.info("An error occurred while displaying your result preview")


@st.experimental_dialog("Save fetch result")
def save_fetch_result():
    st.write("Do you want to save fetch results locally?")
    _, col1, col2, _ = st.columns(4)
    if col1.button("No", use_container_width=True):
        st.rerun()
    if col2.button("Yes", type="primary", use_container_width=True):
        write_html_files(st.session_state.html)
        st.success("Finished saving fetched HTML files", icon="🗂️")
        time.sleep(1)
        st.rerun()


async def extract_module():
    with st.container():
        st.title("Extract Module")
        col1, body_col2 = st.columns([0.5, 0.5])
        expander = col1.expander("Example contents", expanded=True)
        label = expander.text_input("Label", key="label")
        example_content = expander.text_area(
            "Example content", key="example_content", height=10
        )
        extract_identifier = expander.multiselect(
            "Select extract identifier",
            ["Select by class", "Select by ID"],
            key="extract_identifier",
        )
        extract_method = col1.selectbox(
            "Select extract method",
            options=("Direct Path Extract", "Container Extract"),
            key="extract_method",
        )
        batch = col1.checkbox(
            "Extract from all fetched HTMLs", value=False, key="batch"
        )
        col1, col2 = st.columns(2)
        reset_btn = col1.button(
            "Clear extract settings",
            use_container_width=True,
            on_click=clear_extract_settings,
            args=[st.session_state],
        )

        add_content_btn = expander.button(
            "Add contents to extract",
        )
        if add_content_btn:
            st.session_state.contents_to_extract = add_data(
                label,
                example_content,
                extract_identifier,
                st.session_state.contents_to_extract,
            )
        with body_col2:
            st.write("###### Contents to extract preview")
            if not st.session_state.contents_to_extract:
                st.write({"example_label": ("example_content", ["identifier"])})
            else:
                st.write(st.session_state.contents_to_extract)

        extract_btn = col2.button(
            "Extract",
            use_container_width=True,
            type="primary",
            on_click=click_extract_btn,
        )
        if extract_btn:
            result = await handle_extract(
                st.session_state.html,
                st.session_state.contents_to_extract,
                batch,
                extract_method,
            )
            st.session_state.extracted_result_dataframe = result
        if st.session_state.extracted:
            if not st.session_state.extracted_result_dataframe.empty:
                result_table = st.dataframe(
                    st.session_state.extracted_result_dataframe,
                    height=600,
                    use_container_width=True,
                    hide_index=True,
                    on_select="ignore",
                )
                col1, col2 = st.columns(2)
                page_name = get_page_name(st.session_state.url_input)
                get_csv_btn = col1.download_button(
                    "Save as CSV",
                    st.session_state.extracted_result_dataframe.to_csv().encode(
                        "utf-8"
                    ),
                    f"{page_name}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                get_json_btn = col2.download_button(
                    "Save as JSON",
                    st.session_state.extracted_result_dataframe.to_json().encode(
                        "utf-8"
                    ),
                    f"{page_name}.json",
                    mime="application/json",
                    use_container_width=True,
                )


async def downstream_analysis(allow_select_data=True):
    st.title("Downstream analysis module")
    if allow_select_data:
        select_data = st.selectbox(
            "Get data from",
            options=["Use extracted data", "Upload data"],
            key="select_data_for_analysis",
        )
        if st.session_state.get("select_data_for_analysis") == "Upload data":
            expander = st.expander("Upload data", expanded=True)
            uploaded_file = expander.file_uploader(
                "Select data for analysis", label_visibility="collapsed"
            )
            if uploaded_file is not None:
                st.session_state.analysis_data = pd.read_csv(uploaded_file)
                analysis_table = expander.dataframe(
                    st.session_state.analysis_data,
                    height=200,
                    use_container_width=True,
                    hide_index=True,
                    on_select="ignore",
                )
    else:
        select_data = "Use extracted data"
    with st.expander("### Word Cloud generator"):
        st.header("Word Cloud Generator")
        col1, col2 = st.columns(2, vertical_alignment="top")
        max_words = col1.number_input("Maximum number of words", value=70)
        background_color = col1.color_picker("Background color")
        color_maps = list(colormaps)
        color_map = col1.selectbox("Color scheme", options=color_maps)
        select_columns = col2.text_input("Select data from columns")
        regex_patterns = col2.text_input("Phrases/patterns to remove")
        fixed_words = col2.text_input("Fixed words")
        word_cloud_generate_btn = st.button(
            "Generate word cloud",
            use_container_width=True,
            type="primary",
            on_click=click_cloud_generate_btn,
        )
        if word_cloud_generate_btn:
            if select_data == "Use extracted data":
                data = st.session_state.extracted_result_dataframe
            else:
                data = st.session_state.analysis_data
            st.session_state.word_cloud_img = generate_cloud_handler(
                data=data,
                color_map=color_map,
                max_words=max_words,
                columns=select_columns,
                regex_patterns=regex_patterns,
                fixed_words=fixed_words,
                background_color=background_color,
            )

        if st.session_state.word_cloud_generated:
            if st.session_state.word_cloud_img != "":
                st.image(
                    st.session_state.word_cloud_img,
                    use_column_width="auto",
                )
    with st.expander("### LLM analysis"):
        st.header("LLM analysis")
        col1, code_col2 = st.columns(2)
        classification_label = col1.text_input("Task name", key="classification_label")
        classification_text = col1.text_area(
            "Task description", key="classification_text", height=10
        )
        columns = col1.text_input("Columns", key="classification_select_columns")
        col1, col2, col3 = st.columns(3)
        reset_btn = col1.button(
            "Clear tasks",
            use_container_width=True,
            on_click=clear_llm_tasks_inputs,
            args=[st.session_state],
        )
        add_task_btn = col2.button("Add task", use_container_width=True)
        if add_task_btn:
            st.session_state.llm_tasks = add_classification_task(
                classification_label, classification_text, st.session_state.llm_tasks
            )

            print(st.session_state.llm_tasks)
        with code_col2:
            st.write("###### LLM tasks preview")
            if not st.session_state.llm_tasks:
                st.write({"example_task": "description"})
            else:
                st.write(st.session_state.llm_tasks)
        analyze_btn = col3.button(
            "Analyze",
            use_container_width=True,
            type="primary",
            on_click=click_llm_analyze_btn,
        )
        if analyze_btn:
            if select_data == "Use extracted data":
                data = st.session_state.extracted_result_dataframe
            else:
                data = st.session_state.analysis_data
            result = await handle_llm_task(
                data, llm_tasks=st.session_state.llm_tasks, columns=columns
            )
            st.session_state.llm_result = result
        if st.session_state.llm_analyzed:
            if not st.session_state.llm_result.empty:
                result_table = st.dataframe(st.session_state.llm_result)


async def page():
    init_fetch_state(st.session_state)
    init_extract_state(st.session_state)
    init_downstream_analysis_state(st.session_state)
    await fetch_module()
    await extract_module()
    await downstream_analysis(allow_select_data=True)


asyncio.run(page())
