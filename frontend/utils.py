import json
import re
import sys
import tempfile
import uuid
import gradio as gr
import pandas as pd


sys.path.append("./")
from backend.extractor.task.container_extractor import ContainerExtractor
from backend.extractor.task.single_path_extractor import SinglePathElementExtractor
from backend.fetcher.fetcher import fetch_multiple_pages, fetch_page
from backend.extractor.utils import save_crawled_data_to_csv, save_crawled_data_to_json
from backend.extractor.task.nlp_tasks import (
    combine_res,
    create_word_cloud,
    llm_extract_task,
)


async def get_url(
    url: str,
    fetch_options_radio: str,
    fetch_options_checkbox=None,
    scroll_timeout=None,
    expand_text=None,
):
    # print("click triggerd")

    # return await fetch_page(url=url, static_fetch=True)
    static_fetch = True if fetch_options_radio == "Static" else False
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

    url_list = url.split(",")
    url_list = [url.strip() for url in url_list]
    print(url_list)
    # if len(url_list) == 1:
    #     html = await fetch_page(
    #         url=url,
    #         static_fetch=False,
    #         max_duration=max_duration,
    #         scroll=scroll,
    #         expand=expand,
    #         expand_button_text=expand_button_text,
    #     )
    #     return html
    try:
        html = await fetch_multiple_pages(
            url_list,
            static_fetch=static_fetch,
            max_duration=max_duration,
            scroll=scroll,
            expand=expand,
            expand_button_text=expand_button_text,
        )
        gr.Info("Fetched!")
    except Exception as e:
        gr.Error("Fetch failed")
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
        # print(extract_method)

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


async def handle_extract(html_list, contents_to_extract, batch, extract_type):
    if extract_type == "Direct path extract":
        res = await single_path_extract(html_list, contents_to_extract, batch)
    else:
        res = await container_extract(html_list, contents_to_extract, batch)
    return res


async def container_extract(html_list, contents_to_extract, batch):
    html = html_list[0]
    if "True" in batch:
        structured_contents = await container_extract_multiple_websites(
            html, html_list, contents_to_extract
        )
    else:
        # example_container = json.loads(contents_to_extract)
        extractor = ContainerExtractor(contents_to_extract, html, html_list)
        structured_contents = await extractor.container_extract_run_task()
    print(structured_contents)
    # return structured_contents, unstructured_contents
    # json_data = json.dumps(obj=structured_contents, indent=4, ensure_ascii=False)
    df = pd.DataFrame(structured_contents)
    return df


async def single_path_extract(html_list, contents_to_extract, batch):
    html = html_list[0]
    if "True" in batch:
        res = await single_path_extract_multiple_websites(
            html, html_list, contents_to_extract
        )
    else:
        extractor = SinglePathElementExtractor(contents_to_extract, html, html_list)
        res = await extractor.single_element_extract_run_task()

    # json_data = json.dumps(obj=res, indent=4, ensure_ascii=False)
    # print(json_data)
    df = pd.DataFrame(res)
    return df


async def single_path_extract_multiple_websites(html, html_list, contents_to_extract):
    # fresh start, append the first html to the first element
    extractor = SinglePathElementExtractor(contents_to_extract, html)
    await extractor.prepare_single_website_extract_template()
    res = await extractor.extract_from_multiple_websites(html_list)
    return res


async def container_extract_multiple_websites(html, html_list, contents_to_extract):
    extractor = ContainerExtractor(contents_to_extract, html)
    await extractor.prepare_single_website_extract_template()
    await extractor.search_for_containers()
    res = await extractor.extract_from_multiple_websites(html_list)
    return res


def get_page_name(url):
    pattern = r"https?://(?:www\.)?([^./]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def save_to_csv(data, url):
    # if not isinstance(data, list):
    #     data = [json.loads(data)]
    # else:
    #     data = json.loads(data)

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


def load_data_to_table(file):
    if file is None:
        return pd.DataFrame()
    df = pd.read_csv(file.name)
    return df


def load_extract_output(data):
    return data


def get_cloud(
    data, colormap, max_words, columns, regex_patterns, fixed_words, background_color
):
    data.fillna("")
    dictionaries = data.to_dict("records")
    selected_columns = columns.split(",")
    selected_columns = (
        [col.strip() for col in selected_columns] if columns != "" else []
    )
    regex_list = regex_patterns.split(",")
    regex_list = (
        [pattern.strip() for pattern in regex_list] if regex_patterns != "" else []
    )
    fixed_words_list = fixed_words.split(",")
    fixed_words_list = (
        [word.strip() for word in fixed_words_list] if fixed_words != "" else []
    )
    return create_word_cloud(
        dictionaries,
        colormap,
        background_color,
        max_words,
        selected_columns,
        regex_list,
        fixed_words_list,
        save=True,
    )


def add_classify_task(task_name, task_description, tasks):
    string = f"""\"{task_name}\": \"{task_description}\""""
    if tasks == "":
        tasks = string
    else:
        tasks += "," + string
    print(tasks)
    return tasks


async def llm_classify_task(data, tasks, columns):
    data.fillna("")
    # print(tasks)
    dictionaries = data.to_dict("records")
    selected_columns = columns.split(",")
    selected_columns = (
        [col.strip() for col in selected_columns] if columns != "" else []
    )
    print(selected_columns)
    responses = await llm_extract_task(
        data=dictionaries, llm_task_format=tasks, columns=columns
    )
    # print("from ui utils", responses, type(responses))
    result = combine_res(dictionaries, responses, tasks)
    df = pd.DataFrame(result)
    return df
