import json
import sys

sys.path.append("./")
from backend.extractor.task.container_extractor import ContainerExtractor
from backend.fetcher.fetcher import fetch_page


async def get_url(
    url: str,
    fetch_options_radio: str,
    fetch_options_checkbox=None,
    scroll_timeout=None,
    expand_text=None,
):
    if fetch_options_radio == "Static":
        return await fetch_page(url=url, static_fetch=True)
    if "Infinite Scroll" in fetch_options_checkbox:
        scroll = True
        max_duration = scroll_timeout
    else:
        scroll = False
        max_duration = 0

    if "Element expand" in fetch_options_checkbox:
        expand = True
        expand_button_text = expand_text.split(", ")
    else:
        expand = False
        expand_button_text = None
    html = await fetch_page(
        url=url,
        static_fetch=False,
        max_duration=max_duration,
        scroll=scroll,
        expand=expand,
        expand_button_text=expand_button_text,
    )
    return html


def remove_data(label_input, contents_to_extract: dict):
    if label_input in contents_to_extract.keys():
        del contents_to_extract[label_input]
    return contents_to_extract


def add_data(label_input, content_input, contents_to_extract: dict):
    contents_to_extract[label_input] = content_input
    return contents_to_extract


async def extract(html, contents_to_extract):
    # example_container = json.loads(contents_to_extract)
    extractor = ContainerExtractor(html, contents_to_extract)
    structured_contents, unstructured_contents = await extractor.run_extractor_task()

    # return structured_contents, unstructured_contents
    json_data = json.dumps(obj=structured_contents, indent=4, ensure_ascii=False)
    print(json_data)
    return (
        json_data,
        unstructured_contents,
    )
