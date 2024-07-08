import pandas as pd
import streamlit as st
from matplotlib import colormaps

import os
import sys

sys.path.append("./")

if "fetch_method" not in st.session_state:
    st.session_state.fetch_method = "Static fetch"

with st.container():
    st.title("Fetch Module")
    url_input = st.text_input("Input Url")
    fetch_method = st.selectbox(
        "How should your website be fetched",
        ("Static fetch", "Dynamic fetch"),
        key="fetch_method",
    )
    if fetch_method == "Dynamic fetch":
        col1, col2 = st.columns(2)
        col1.slider(
            label="Scroll timeout",
            min_value=0,
            max_value=180,
            value=10,
        )
        col2.text_input(label="Expand button texts")
    col1, col2 = st.columns(2)
    clear_btn = col1.button("Clear fetch", use_container_width=True)
    fetch_btn = col2.button("Fetch", type="primary", use_container_width=True)

with st.container():
    st.title("Extract Module")
    col1, col2 = st.columns(2)
    extract_method = col1.selectbox(
        "Select extract method", options=["Direct Path Extract", "Container Extract"]
    )
    label_input = col1.text_input("Label")
    example_content = col1.text_input("Example content")
    extract_identifier = col1.multiselect(
        "Select extract identifier", ["Select by class", "Select by ID"]
    )
    code = """extract_item = {
        "label": "example_content",
        "label2":"example_content2",
    }
    
    """
    extract_content_preview = col2.code(code, language="python")
    col1, col2, col3 = st.columns(3)
    reset_btn = col1.button("Clear extract settings", use_container_width=True)
    add_content_btn = col2.button("Add contents to extract", use_container_width=True)
    extract_btn = col3.button("Extract", use_container_width=True, type="primary")
    if extract_btn:
        result_table = st.table(pd.DataFrame())
        col1, col2 = st.columns(2)
        get_csv_btn = col1.button("Save as CSV", use_container_width=True)
        get_json_btn = col2.button("Save as JSON", use_container_width=True)

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
    word_cloud_img = tab1.image(
        "./results/word_cloud/wordcloud_0b4cb6d5-f3e7-447d-bc37-349ea3f0c51e.png",
        use_column_width="auto",
    )
