import json
import re
import sys
import tempfile
import uuid


sys.path.append("./")
from backend.extractor.task.container_extractor import ContainerExtractor
from backend.extractor.task.single_path_extractor import SinglePathElementExtractor
from backend.fetcher.fetcher import fetch_page
from backend.extractor.utils import save_crawled_data_to_csv, save_crawled_data_to_json


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


def add_data(label_input, content_input, extract_methods, contents_to_extract: dict):
    if len(extract_methods) == 0:
        extract_methods = [""]
    for extract_method in extract_methods:
        extract_method = (
            extract_method.replace(
                "Extract",
                "",
            )
            .lower()
            .strip()
            .replace(" ", "_")
        )
        print(extract_method)

    if label_input in contents_to_extract.keys():
        print(
            contents_to_extract[label_input][0],
            type(contents_to_extract[label_input][0]),
        )
        contents_to_extract[label_input].append((content_input, extract_method))
    else:
        contents_to_extract[label_input] = []
        contents_to_extract[label_input].append((content_input, extract_method))
    print(contents_to_extract)
    return contents_to_extract


async def extract(html, contents_to_extract):
    # example_container = json.loads(contents_to_extract)
    extractor = ContainerExtractor(
        contents_to_extract,
        html,
    )
    structured_contents = await extractor.container_extract_run_task()

    # return structured_contents, unstructured_contents
    json_data = json.dumps(obj=structured_contents, indent=4, ensure_ascii=False)
    print(json_data)
    return json_data


async def single_path_extract(html, contents_to_extract):
    print(contents_to_extract)
    print(type(contents_to_extract))
    # print(example_container)
    extractor = SinglePathElementExtractor(
        contents_to_extract,
        html,
    )
    res = await extractor.single_element_extract_run_task()

    json_data = json.dumps(obj=res, indent=4, ensure_ascii=False)
    print(json_data)
    return json_data


def get_page_name(url):
    pattern = r"https?://(?:www\.)?([^./]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def save_to_csv(data, url):
    if not isinstance(data, list):
        data = [json.loads(data)]
    else:
        data = json.loads(data)

    uid = str(uuid.uuid4())[::8]
    page_name = get_page_name(url)
    save_path = f"./results/csv/{page_name}_{uid}.csv"
    save_crawled_data_to_csv(data, save_path)
    return save_path
    # temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")


def save_to_json(data, url):
    uid = str(uuid.uuid4())[::8]
    page_name = get_page_name(url)
    save_path = f"./results/json/{page_name}_{uid}.json"
    save_crawled_data_to_json(data, save_path)
    return save_path
