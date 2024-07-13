import asyncio
import time
import pandas as pd
import streamlit as st
from matplotlib import colormaps

import os
import sys

sys.path.append("./")
from backend.logger import get_logger
from frontend.pages.utils import (
    clear_fetch_inputs,
    fetch,
    init_fetch_state,
    write_html_files,
)

if "html" not in st.session_state:
    st.session_state.html = []
if "content_to_extract" not in st.session_state:
    st.session_state.content_to_extract = {}

logger = get_logger()


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
            pagination = col1.checkbox("Pagination", key="pagination")
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
            max_pages = col2.slider(
                "Max number of fetched page",
                key="max_pages",
                min_value=2,
                max_value=20,
                value=5,
                disabled=not (pagination),
            )
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
            if pagination:
                st.session_state.dynamic_fetch_options["pagination"] = max_pages
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
        )
    result_container = st.container(height=200)
    with result_container:
        col1, col2 = st.columns([4, 1])
        col1.markdown("###### Fetch Result")
    if fetch_btn:
        st.toast("Fetching HTML...", icon="💬")
        print(url_input, fetch_method, st.session_state.dynamic_fetch_options)
        html = await fetch(
            url_input, fetch_method, st.session_state.dynamic_fetch_options
        )
        st.session_state.html = html
        logger.info("Fetch done, saving to session state")
        st.toast("Fetched!", icon="🎉")
        save_fetch_result()
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
        col1, col2 = st.columns(2)
        extract_method = col1.selectbox(
            "Select extract method",
            options=["Direct Path Extract", "Container Extract"],
            key="extract_method",
        )
        label = col1.text_input("Label", key="label")
        example_content = col1.text_input("Example content", key="example_content")
        extract_identifier = col1.multiselect(
            "Select extract identifier",
            ["Select by class", "Select by ID"],
            key="extract_identifier",
        )
        code = """extract_item = {
            "label": "example_content",
            "label2":"example_content2",
        }
        """
        extract_content_preview = col2.code(
            code,
            language="python",
        )
        col1, col2, col3 = st.columns(3)
        reset_btn = col1.button("Clear extract settings", use_container_width=True)
        add_content_btn = col2.button(
            "Add contents to extract", use_container_width=True
        )
        extract_btn = col3.button("Extract", use_container_width=True, type="primary")
        if extract_btn:
            result_table = st.table(pd.DataFrame())
            col1, col2 = st.columns(2)
            get_csv_btn = col1.button("Save as CSV", use_container_width=True)
            get_json_btn = col2.button("Save as JSON", use_container_width=True)


async def downstream_analysis():
    with st.container():
        st.title("Downstream analysis module")
        tab1, tab2 = st.tabs(["Word Cloud Generator", "LLM Analysis"])
        tab1.header("Word Cloud Generator")
        with tab1.form("word_cloud_generator"):
            col1, col2 = st.columns(2, vertical_alignment="top")
            max_words = col1.number_input("Maximum number of words", value=70)
            background_color = col1.color_picker("Background color")
            color_maps = list(colormaps)
            color_scheme = col1.selectbox("Color scheme", options=color_maps)
            select_columns = col2.text_input("Select data from columns")
            regex_patterns = col2.text_input("Phrases/patterns to remove")
            fixed_words = col2.text_input("Fixed words")
            word_cloud_generate_btn = st.form_submit_button(
                "Generate word cloud", use_container_width=True, type="primary"
            )
        if word_cloud_generate_btn:
            word_cloud_img = tab1.image(
                "./results/word_cloud/wordcloud_0b4cb6d5-f3e7-447d-bc37-349ea3f0c51e.png",
                use_column_width="auto",
            )

        tab2.header("LLM analysis")
        col1, col2 = tab2.columns(2)
        classification_label = col1.text_input("Task name")
        classification_text = col1.text_area("Task description")
        code = """task_preview = {"task": "description"}"""
        task_preview = col2.code(code, "python")
        col1, col2, col3 = tab2.columns(3)
        reset_btn = col1.button("Clear tasks", use_container_width=True)
        add_task_btn = col2.button("Add task", use_container_width=True)
        analyze_btn = col3.button("Analyze", use_container_width=True, type="primary")
        if analyze_btn:
            result_table = st.table(pd.DataFrame())


async def page():
    await fetch_module()
    await extract_module()
    await downstream_analysis()


init_fetch_state(st.session_state)
asyncio.run(page())
