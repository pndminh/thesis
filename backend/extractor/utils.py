import datetime
import os

import pandas as pd
from backend.extractor.db import init_db
from backend.logger import get_logger
from bs4 import BeautifulSoup
import csv
import json

logger = get_logger()


def clean_html(soup, tags=[], use_default_tags=True):
    default_tags = ["script", "style", "link", "nav", "meta", "head"]
    tags += [*default_tags] if use_default_tags or len(tags) == 0 else tags
    """Receives a list of elements to remove from the soup."""
    for data in soup(tags):
        data.decompose()
    logger.info(
        "Cleaning HTML, removing all path that does not contains navigable string"
    )
    return soup


def traverse_and_modify(current_tag, current_path=None):
    """Traverse an html soup, starting form the first tag of the soup to the leaf node (navigable string).
    Remove all paths that does not leads to a navigable strin. Return a modified version of the beautiful soup tree.
    """

    if current_path is None:
        current_path = [current_tag.name]

    children_to_traverse = []
    # traverse all child tags of the current tag
    for child_tag in current_tag.find_all(recursive=False):
        # if cannot find any children, we are at the leaf node,
        if not child_tag.find():
            # if we could find a string at the leaf node, print it out
            if (
                child_tag.find(string=True)
                and not child_tag.find(string=True).strip() == ""
            ):
                string_value = child_tag.find(string=True).strip()
                # current_tag.append(tag)i
                print(
                    " -> ".join(
                        current_path
                        + [child_tag.name, string_value.replace("\n", "").strip()]
                    )
                )
            else:
                child_tag.decompose()
        else:
            children_to_traverse.append(child_tag)
    for child_tag in children_to_traverse:
        traverse_and_modify(
            current_tag=child_tag,
            current_path=current_path + [child_tag.name],
        )

    return current_tag


db = init_db()


async def save_html(url, soup: BeautifulSoup):
    doc_ref = db.collection("crawl-result").document()
    last_modified = str(datetime.date.today())
    doc_ref.set(
        {
            "url": url,
            "soup": str(soup),
            "last_modified": last_modified,
        }
    )

    logger.info("Saved soup to firebase")


def parse_html(html):
    logger.info("Parsing HTML string to BeautifulSoup object")
    soup = BeautifulSoup(html, "html.parser")
    return soup


def prepare_html(html, clean_tags=[]):
    "clean and parse html to prepare it for extraction"
    if type(html) is str:
        soup = parse_html(html)
    else:
        soup = html
    soup = clean_html(soup, clean_tags)
    soup = traverse_and_modify(soup)
    return soup


def is_duplicate(new_path, existing_paths):
    for path in existing_paths:
        if path in new_path:
            return True
    return False


async def is_dict_empty(d):
    def is_empty(value):
        if isinstance(value, str):
            return not value.strip()  # Empty string or string with only spaces
        elif isinstance(value, list):
            return all(
                is_empty(item) for item in value
            )  # All items in the list are empty
        else:
            return not value  # Other types (None, False, etc.)

    return all(is_empty(value) for value in d.values())


def save_crawled_data_to_csv(data, file_path):
    # Extract column headers from the keys of the first dictionary
    data = pd.DataFrame(data)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        save_df = pd.concat([df, data], ignore_index=True)
    else:
        save_df = data

    save_df.to_csv(f"{file_path}", mode="w", header=True, index=False)
    # if isinstance(data, list):
    #     headers = data[0].keys() if data else []
    # else:
    #     headers = data.keys()
    # with open(f"{file_name}", "w") as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=headers)
    #     writer.writeheader()
    #     writer.writerows(data)


def save_crawled_data_to_db(db, url, page_name, extracted_info_name, data):
    crawl_stats_ref = db.collection("crawl-stats")
    res = crawl_stats_ref.where("page_name", "==", page_name).limit(1).get()
    if res:
        website_doc_ref = res[0].reference
    else:
        website_doc_ref = crawl_stats_ref.document()
        website_doc_ref.set({"page_name": page_name})
    # add nested collection
    extracted_info_collection_ref = website_doc_ref.collection(extracted_info_name)
    save_data = {**data}
    if "id" in data.keys():
        doc_id = data["id"]
        del data["id"]
        extracted_info_collection_ref.document(doc_id).set(save_data)
    else:
        extracted_info_collection_ref.add(save_data)


def save_crawled_data_to_json(data, file_path):
    data.to_json(f"{file_path}")
    # with open(f"{file_name}", "w") as outfile:
    #     outfile.write(json)
