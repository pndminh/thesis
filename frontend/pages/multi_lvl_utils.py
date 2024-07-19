import streamlit as st


def init_fetch_state(state):
    if "m_fetch_method" not in state:
        state.m_fetch_method = "Static fetch"
    if "m_infinite_scroll" not in state:
        state.m_infinite_scroll = False
    if "m_scroll_timeout" not in state:
        state.m_scroll_timeout = 0
    if "m_expand_button_click" not in state:
        state.m_expand_button_click = False
    if "m_expand_button_text" not in state:
        state.m_expand_button_text = ""
    if "m_dynamic_fetch_options" not in state:
        state.m_dynamic_fetch_options = {
            "infinite_scroll": 0,
            "expand_button_click": "",
            "pagination": 0,
        }


def clear_fetch_inputs(state):
    state["url_input"] = ""
    state.m_fetch_method = "Static fetch"
    state.m_scroll_timeout = 10
    state.m_expand_button_click = ""
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
    state.extract_setups[state.curr_lvl] = {}
