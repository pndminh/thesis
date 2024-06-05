import collections
import re
from bs4 import BeautifulSoup
from backend.extractor.utils import clean_html, traverse_and_modify
from backend.logger import get_logger

logger = get_logger()


def find_string_tag(soup, navigable_string_content: str):
    "find the tag that contains the given navigable sttring in the soup"
    string = soup.find(string=re.compile(f"{navigable_string_content}"))
    if string is None:
        raise Exception("Cannot find tag")
    res = string.parent
    logger.info(f"Found string in soup at: {res}")
    return res if string is not None else None


def lowest_common_ancestor(
    NUM_NODES,
    parents=None,
    *args,
):
    "receive a list of tags and output the lowest common parent ancestor tag"
    if parents is None:
        parents = collections.defaultdict(int)
    for tag in args:
        parents[tag] += 1
        if parents[tag] == NUM_NODES:
            return tag
    next_arg_list = [tag.parent for tag in args if tag.parent is not None]

    return lowest_common_ancestor(NUM_NODES, parents, *next_arg_list)


def find_path(
    content,
    soup: BeautifulSoup,
) -> str:
    """return the path from the parent tag (soup) to the content string
    Args:
        content_string (str): the string to find
        soup (BeautifulSoup): the soup to search in
    Returns:
        str: string of tag names indicating path from the parent tag to the content string
    """
    try:
        target_tag = find_string_tag(soup, content) if type(content) is str else content
    except Exception:
        logger.error(f"Cannot find string {content} in soup")
        return None
    if target_tag == None:
        return None
    path = []
    current = target_tag
    parent = current.parent
    path += [current]
    while parent != soup:
        # print(current.name)
        current = parent
        parent = current.parent
        # print(current.name)
        path += [current]

    path = path[::-1]
    path_string = " ".join(tag.name for tag in path)
    logger.info(f"Extract path name: {path_string}")

    return path_string


# def extract_text_from_container(container=None):
#     contents = container.find_all(string=True, recursive=True)
#     filtered = [string for string in contents if string.strip()]
#     unextracted_contents.append(" ".join(filtered))
