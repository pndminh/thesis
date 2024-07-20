import asyncio
import time
import pandas as pd
import streamlit as st
import sys

sys.path.append("./")
from frontend.utils import get_page_name
from pages.utils import add_data
from frontend.pages.multi_lvl_utils import (
    clear_extract_inputs,
    clear_fetch_inputs,
    init_fetch_state,
    start_pipeline,
)

# All input state of every level is stored in a list at the corresponding lvl idx
if "curr_lvl" not in st.session_state:
    st.session_state.curr_lvl = 0
if "fetch_setups" not in st.session_state:
    st.session_state.fetch_setups = [{}]
if "extract_setups" not in st.session_state:
    st.session_state.extract_setups = [{}]
if "curr_fetch_inputs" not in st.session_state:
    st.session_state.curr_fetch_inputs = {}
if "curr_extract_inputs" not in st.session_state:
    st.session_state.curr_extract_inputs = {}
if "rerun_count" not in st.session_state:
    st.session_state.rerun_count = 0
if "curr_contents_to_extract" not in st.session_state:
    st.session_state.curr_contents_to_extract = {}
if "pipeline_started" not in st.session_state:
    st.session_state.pipeline_started = False
if "extracted_result" not in st.session_state:
    st.session_state.extracted_result = pd.DataFrame()


def click_start_btn():
    st.session_state.pipeline_started = True


def fetch_component(container, key):
    with container:
        st.markdown("#### Fetch")
        url = st.text_input("URL", key=f"url")
        fetch_method = st.selectbox(
            "How should your website be fetched",
            ("Static fetch", "Dynamic fetch"),
            key=f"m_fetch_method",
        )
        if fetch_method == "Dynamic fetch":
            col1, col2 = st.columns(2)
            scroll_timeout_slider = col1.slider(
                label="Scroll timeout",
                min_value=0,
                max_value=180,
                value=0,
                key=f"m_scroll_timeout",
            )
            expand_text = col2.text_input(
                label="Expand button texts", key=f"m_expand_text"
            )
        col1, col2 = st.columns(2)
        clear_fetch_btn = col1.button(
            "Clear fetch setting",
            key=f"clear_fetch_btn",
            use_container_width=True,
            on_click=clear_fetch_inputs,
            args=[st.session_state],
        )
        setup_fetch_btn = col2.button(
            "Set up fetch task",
            type="primary",
            use_container_width=True,
            key=f"setup_fetch_btn",
        )
        st.session_state.curr_fetch_inputs = {
            "urls": url,
            "fetch_method": fetch_method,
            "infinite_scroll": (
                scroll_timeout_slider if fetch_method == "Dynamic fetch" else 0
            ),
            "expand_button_click": (
                expand_text if fetch_method == "Dynamic fetch" else ""
            ),
        }
        if setup_fetch_btn:
            st.session_state.fetch_setups[key] = st.session_state.curr_fetch_inputs
            st.session_state.curr_fetch_inputs = {}


def extract_component(container, key):
    with container:
        # with st.container():
        st.markdown("#### Extract")
        col1, body_col2 = st.columns(2)
        with col1:
            with st.expander("Example contents", expanded=True):
                label_input = st.text_input("Label", key="m_label_input")
                example_content = st.text_input(
                    "Example content", key="m_example_content"
                )
                extract_identifier = st.multiselect(
                    "Select extract identifier",
                    ["Select by class", "Select by ID"],
                    key="m_extract_identifier",
                )
                add_content_btn = st.button("Add content", key="m_add_content_btn")
                if add_content_btn:
                    st.session_state.curr_contents_to_extract = add_data(
                        label_input,
                        example_content,
                        extract_identifier,
                        st.session_state.curr_contents_to_extract,
                    )
                with body_col2:
                    st.write("###### Contents to extract preview")
                    st.write(st.session_state.curr_contents_to_extract)
            extract_method = st.selectbox(
                "Select extract method",
                options=["Direct Path Extract", "Container Extract", "Extract Links"],
                key=f"m_extract_method",
            )
            col1, col2 = st.columns([0.4, 0.6], vertical_alignment="bottom")
            batch_checkbox = col2.checkbox("Extract from all HTMLs", key="m_batch")
            st.session_state.curr_extract_inputs = {
                "extract_method": extract_method,
                "batch": batch_checkbox,
                "contents_to_extract": st.session_state.curr_contents_to_extract,
            }

        col1, col2 = st.columns(2)
        clear_extract_btn = col1.button(
            "Clear",
            use_container_width=True,
            key="clear_extract_btn",
            on_click=clear_extract_inputs,
            args=[st.session_state],
        )
        setup_extract_btn = col2.button(
            "Set up extract task",
            use_container_width=True,
            type="primary",
            key="extract_btn",
        )
        if setup_extract_btn:
            st.session_state.extract_setups[key] = st.session_state.curr_extract_inputs
            st.session_state.curr_extract_inputs = {}


def preview():
    # with st.expander("Flow setup preview", expanded=True):
    for lvl in range(0, st.session_state.curr_lvl + 1):
        expand = True if lvl == st.session_state.curr_lvl else False
        expander = st.expander(f"### Level {lvl+1}", expanded=expand)
        col1, col2 = st.columns(2)
        with expander:
            st.write("##### Fetch_setups", st.session_state.fetch_setups[lvl])
            st.write("##### Extract_setups", st.session_state.extract_setups[lvl])


# for lvl in range(1, st.session_state.curr_lvl + 1):
#     level(lvl)
async def page():
    init_fetch_state(st.session_state)
    level = st.container()
    st.markdown(f"### Level {st.session_state.curr_lvl+1}")
    container = st.container(border=True)
    fetch_component(container, st.session_state.curr_lvl)
    extract_component(container, st.session_state.curr_lvl)

    # Button to add new level
    col1, col2, col3 = st.columns(3)
    clear_level_btn = col1.button("Reset pipeline setup", use_container_width=True)
    add_level_btn = col2.button("Add fetch - extract level", use_container_width=True)
    start_btn = col3.button(
        "Start", type="primary", use_container_width=True, on_click=click_start_btn
    )
    st.write(f"Rerun count: {st.session_state.rerun_count}")
    st.session_state.rerun_count += 1
    preview()

    if add_level_btn:
        if not st.session_state.fetch_setups[st.session_state.curr_lvl]:
            st.session_state.fetch_setups[st.session_state.curr_lvl] = {
                "urls": "",
                "fetch_method": "Dynamic fetch",
                "infinite_scroll": 0,
                "expand_button_click": "",
            }
        st.session_state.curr_lvl += 1
        st.session_state.curr_fetch_inputs = {}
        st.session_state.curr_extract_inputs = {}
        st.session_state.curr_contents_to_extract = {}
        st.session_state.fetch_setups.append({})
        st.session_state.extract_setups.append({})

        st.rerun()
    if clear_level_btn:
        st.session_state.curr_lvl = 0
        st.session_state.fetch_setups = [{}]
        st.session_state.extract_setups = [{}]
        st.rerun()
    if start_btn:
        extracted_result = await start_pipeline(st.session_state)
        st.session_state.extracted_result = extracted_result
    if st.session_state.pipeline_started:
        if not st.session_state.extracted_result.empty:
            result_table = st.dataframe(
                st.session_state.extracted_result,
                height=200,
                use_container_width=True,
                hide_index=True,
                on_select="ignore",
            )
            col1, col2 = st.columns(2)
            page_name = get_page_name(st.session_state.fetch_setups[0]["urls"])
            get_csv_btn = col1.download_button(
                "Save as CSV",
                st.session_state.extracted_result.to_csv().encode("utf-8"),
                f"{page_name}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            get_json_btn = col2.download_button(
                "Save as JSON",
                st.session_state.extracted_result.to_json().encode("utf-8"),
                f"{page_name}.json",
                mime="application/json",
                use_container_width=True,
            )


asyncio.run(page())
