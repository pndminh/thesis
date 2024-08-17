# No-Code Web Crawler and Data Extraction System

This project is a No-Code Web Crawler and Data Extraction System designed to help non-technical users efficiently extract and analyze data from both static and dynamic websites. The system is capable of handling complex web pages, managing multi-level fetch and extraction operations, and performing downstream analysis tasks like word cloud generation and text classification.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Limitations](#limitations)
- [Contributing](#contributing)

## Features

- **Fetch Module**: Supports fetching static and dynamic content, including handling infinite scrolling and expanding hidden elements.
- **Extract Module**: Allows both Direct Path and Container Extraction for structured data from different website layouts.
- **Analyze Module**: Offers downstream analysis, including word cloud generation and text classification.
- **Multi-Level Extraction Pipeline**: Enables recursive fetching and extraction from URLs within the fetched content.
- **Streamlit UI**: User-friendly interface for setting up and executing web crawling tasks without coding.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pndminh/thesis.git
   cd thesis
   ```
2. **Create a Virtual Environment (Optional but recommended)**
   ```conda create -n no_code_crawler python=3.11
   conda activate no_code_crawler
   ```
3. **Install requirement packages**

   ```pip install -r requirements.txt

   ```

4. **Run the application**

   ```streamlit run frontend/streamlit_app.py

   ```

## Usage

### Fetch Module

- **Static Content**: Input a list of URLs and choose the static fetch method.
- **Dynamic Content**: Configure options for infinite scrolling or content behind expand buttons.

### Extract Module

- **Direct Path Extraction**: Specify HTML element paths for simple, list-like layouts.
- **Container Extraction**: Set up extraction for nested, grid-like layouts.

### Analyze Module

- **Word Cloud**: Input text data to generate a word cloud for visualizing common themes.
- **Text Classification**: Perform sentiment analysis or other classification tasks on extracted text.

### Multi-Level Extraction Pipeline

- Set up multi-level operations where extracted links can be recursively fed back into the Fetch Module.
- The final data is processed and analyzed using the downstream LLM tasks.

## Limitations

- **Fetch**: Expand buttons can only be identified if they are text-based.
- **Extract module**: Relies solely on the structure of the HTML, tag is selected via the text contained within an element, thus and the algorithm does not guarantee that the correct tag is always identified.
- **Word Cloud Module**: Limited support for non-English languages.
- **LLM Analysis**: Possibility of incorrect outputs; careful parsing and retry mechanisms are advised.

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change
