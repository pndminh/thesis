import streamlit as st

# Set the title of the app
st.title("🕸️ No-Code Web Data Extraction System")

# Introduction section
st.markdown(
    """
Welcome! 🚀 This app allows you to crawl, extract and analyze websites effortlessly without any coding skills required. Whether you're fetching data, extracting specific information, or analyzing it for insights, this tool simplifies the entire process.
"""
)
# Features section
st.subheader("Features")
st.markdown(
    """
- 🌐 **Fetch Data**: Retrieve content from websites with ease.
- 🛠️ **Extract Information**: Parse and organize data efficiently across multiple websites.
- 📊 **Analyze Data**: Generate word clouds and perform classification tasks seamlessly.
"""
)

# How to Use section
st.subheader("How to Use")

st.markdown(
    """
### Fetch Component

1. **URL Input**: Enter a single URL or a list of URLs to crawl multiple websites.
2. **Fetch Options**: Choose between static or dynamic fetch tasks.

### Extract Component

1. **Example Content**: Provide sample content for extraction guidance.
2. **Label Names**: Define labels for the extracted data.
3. **Direct Path Extraction**: Extract data using straightforward paths.
4. **Container Extraction**: Extract data from specified containers or sections of the web page.
5. **Cross-Site Extraction**: Extract data across different websites using the defined labels and paths.

### Analyze Component

1. **Word Cloud Generator**: Input text to visualize word frequency.
2. **Classification Tab**: Perform customizable data classification tasks.
"""
)

# Getting Started section
st.subheader("Get Started")
st.markdown(
    """
Simply interact with each component to explore its functionalities. Start by entering one or more website URLs in the Fetch component, define extraction parameters in the Extract component, and analyze results in the Analyze component.
"""
)
