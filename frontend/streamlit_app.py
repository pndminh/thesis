import streamlit as st

home_page = st.Page("pages/home.py", title="Home", icon=":material/home:")
component_page = st.Page(
    "pages/components_demo.py", title="Components Demo", icon=":material/cards:"
)
full_flow_page = st.Page(
    "pages/multi_level.py", title="Multi Level Demo", icon=":material/model_training:"
)

navigation = st.navigation([home_page, component_page, full_flow_page])
st.set_page_config(page_title="Home page", layout="centered", page_icon="👋")

navigation.run()
