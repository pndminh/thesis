import collections
import re
from bs4 import BeautifulSoup
from backend.extractor.utils import clean_html, traverse_and_modify
from backend.logger import get_logger

logger = get_logger()


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup


def prepare_html(html):
    "clean html of"
    soup = parse_html(html)
    soup = clean_html(soup)
    soup = traverse_and_modify(soup)
    return soup


def find_string_tag(navigable_string_content: str, soup=None):
    "find the tag that contains the given navigable sttring in the soup"
    string = soup.find(string=re.compile(f"""{navigable_string_content}"""))
    res = string.parent
    logger.info(f"Found string in soup at: {res}")
    return res if string is not None else None


def lowest_common_ancestor(parents=None, *args):
    "receive a list of tags and output the lowest common parent ancestor tag"
    if parents is None:
        parents = collections.defaultdict(int)
    for tag in args:
        parents[tag] += 1
        if parents[tag] == 2:
            return tag
    next_arg_list = [tag.parent for tag in args if tag.parent is not None]

    return lowest_common_ancestor(parents, *next_arg_list)


def find_path(content, soup=None) -> str:
    """return the path from the parent tag (soup) to the content string
    Args:
        content_string (str): the string to find
        soup (BeautifulSoup): the soup to search in
    Returns:
        str: string of tag names indicating path from the parent tag to the content string
    """
    target_tag = find_string_tag(content) if type(content) is str else content
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
        path += [current]

    path = path[::-1]
    path_string = " ".join(tag.name for tag in path)
    # logger.info(f"Extract path name: {path_string}")

    return path_string


def find_similar_items_from_example(content_string: str, soup=None) -> list[list[str]]:
    "find all similar items with target tag in an html soup tree"
    path_string = find_path(content_string, soup=soup)
    # path_string = " ".join(tag.name for tag in path)
    similar_items = soup.select(path_string)
    logger.info("Found similar items")
    # print(similar_items)
    res = []
    for tag in similar_items:
        # Find all navigable strings within the tag
        string_values = [
            string.strip()
            for string in tag.find_all(string=True, recursive=True)
            if string.strip()
        ]
        if string_values:
            res += [string_values]
    return res


def find_container_from_examples(examples: list[str]):
    example_tags = [find_string_tag(string) for string in examples]
    lca = lowest_common_ancestor(None, *example_tags)
    if lca is None:
        return None
    path_to_container = find_path(content=lca)
    logger.info(
        f"Found common parent of target tags: {lca.name}, at path: {' -> '.join(path for path in path_to_container.split(' '))}"
    )
    return lca, path_to_container


def find_similar_containers(path_to_container, soup):
    logger.info("Getting list of similar containers")
    return soup.select(path_to_container)


def set_up_container_template_structure(
    self, example_container_structure: list[dict], lca
):
    logger.info("Setting up template structure for container extraction")
    template_structure = []
    for text_item in example_container_structure:
        label = text_item["label"]
        path = self.find_path(content=text_item["content"], soup=lca)
        template_structure += [{"label": label, "path": path}]
    return template_structure


def get_items_in_similar_container_by_structure(
    self,
    found_containers,
    template_structure,
):
    logger.info("Getting similar contents in predefined structure")
    container_items_with_labels = []
    for container in found_containers:
        # matched_contents = []
        res_dict = {}
        for text_item in template_structure:
            string_values = []
            content_tags = container.select(text_item["path"])
            string_values += [
                content_tag.get_text().strip() for content_tag in content_tags
            ]
            label = text_item["label"]
            res_dict[label] = string_values
            # matched_contents += [{"label": label, "content": string_values}]
        container_items_with_labels += [res_dict]

    # for item in container_items_with_labels:
    #     if self.check_empty_structured_result_row(item) is False:
    #         print(item)

    return container_items_with_labels


def extract_by_container(example_container_structure):
    text_examples = [item["content"] for item in example_container_structure]
    lca, path_to_container = find_container_from_examples(text_examples)
    template_structure = set_up_container_template_structure(
        example_container_structure, lca
    )
    similar_containers = find_similar_containers(path_to_container)
    found_contents = get_items_in_similar_container_by_structure(
        similar_containers, template_structure
    )
    return found_contents
