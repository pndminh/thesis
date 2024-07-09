import streamlit as st

if "curr_lvl" not in st.session_state:
    st.session_state.curr_lvl = 1


def fetch_component(column, key):
    with column:
        url = st.text_input("URL", key=f"url_level{key}")
        fetch_method = st.selectbox(
            "How should your website be fetched",
            ("Static fetch", "Dynamic fetch"),
            key=f"fetch_method_level{key}",
        )
        if fetch_method == "Dynamic fetch":
            col1, col2 = st.columns(2)
            scroll_timeout_slider = col1.slider(
                label="Scroll timeout",
                min_value=0,
                max_value=180,
                value=10,
                key=f"scroll_timeout_level{key}",
            )
            expand_text = col2.text_input(
                label="Expand button texts", key=f"expand_text_level{key}"
            )
        col1, col2 = st.columns(2)
        clear_fetch_btn = col1.button(
            "Clear", key=f"clear_fetch_btn_level{key}", use_container_width=True
        )
        fetch_btn = col2.button(
            "Fetch",
            type="primary",
            use_container_width=True,
            key=f"fetch_btn_level{key}",
        )


def extract_component(column, key):
    with column:
        col1, col2 = st.columns(2, vertical_alignment="bottom")
        extract_method = col1.selectbox(
            "Select extract method",
            options=["Direct Path Extract", "Container Extract"],
            key=f"extract_method_level{key}",
        )
        get_link_checkbox = col2.checkbox(
            "Get links", key=f"get_link_checkbox_level{key}"
        )
        with st.expander("Example contents"):
            label_input = st.text_input("Label", key=f"label_input_level{key}")
            example_content = st.text_input(
                "Example content", key=f"example_content_level{key}"
            )
            extract_identifier = st.multiselect(
                "Select extract identifier",
                ["Select by class", "Select by ID"],
                key=f"extract_identifier_level{key}",
            )
            add_content_btn = st.button(
                "Add content", key=f"add_content_btn_level{key}"
            )

        with st.expander("Preview"):
            code = """extract_item = {
                "label": "example_content",
                "label2":"example_content2",
            }
            """
            extract_item_preview = st.code(code, language="python")
        col1, col2 = st.columns(2)
        clear_extract_btn = col1.button(
            "Clear", use_container_width=True, key=f"clear_extract_btn_level{key}"
        )
        extract_btn = col2.button(
            "Extract",
            use_container_width=True,
            type="primary",
            key=f"extract_btn_level{key}",
        )


def level(key):
    level = st.container(border=True)
    level.markdown(f"### Level {key}")
    col1, col2 = level.columns(2)
    fetch_component(col1, key)
    level = st.container(border=True)
    extract_component(col2, key)


for lvl in range(1, st.session_state.curr_lvl + 1):
    level(lvl)

# Button to add new level
add_level_btn = st.button("Add fetch - extract level", type="primary")
if add_level_btn:
    st.session_state.curr_lvl += 1
