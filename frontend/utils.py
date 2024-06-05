import json

import pandas as pd
import sys

sys.path.append("./")
from backend.extractor.task.container_extractor import ContainerExtractor
from backend.fetcher.fetcher import fetch_infinite_page


async def get_url(url, fetch_option_checkbox, scroll_timeout, expand_text):
    if "Infinite Scroll" in fetch_option_checkbox:
        scroll = True
        max_duration = scroll_timeout
    else:
        scroll = False
        max_duration = 0

    if "Element expand" in fetch_option_checkbox:
        expand = True
        expand_button_text = expand_text.split(", ")
    else:
        expand = False
        expand_button_text = None
    html = await fetch_infinite_page(
        url=url,
        max_duration=max_duration,
        scroll=scroll,
        expand=expand,
        expand_button_text=expand_button_text,
    )
    return html


def process_dataframe(df: pd.DataFrame):
    # TODO
    dictionary = {}
    for col in df.columns:
        if col != "":
            dictionary[col] = df[col].values.tolist()

    return dictionary


def remove_data(label_input, contents_to_extract: dict):
    if label_input in contents_to_extract.keys():
        del contents_to_extract[label_input]
    return contents_to_extract


def add_data(label_input, content_input, contents_to_extract: dict):
    contents_to_extract[label_input] = content_input
    return contents_to_extract


async def extract(html, dataframe):
    contents_to_extract = process_dataframe(dataframe)
    # example_container = json.loads(contents_to_extract)
    extractor = ContainerExtractor(html, contents_to_extract)
    structured_contents, unstructured_contents = (
        await extractor.container_extract_run_task()
    )

    # return structured_contents, unstructured_contents
    return json.dumps(obj=structured_contents, indent=4), unstructured_contents
