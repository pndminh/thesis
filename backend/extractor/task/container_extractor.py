from bs4 import BeautifulSoup

from backend.extractor.extractor import (
    find_path,
    find_string_tag,
    lowest_common_ancestor,
)
from backend.logger import get_logger

logger = get_logger()


def run_task(soup: BeautifulSoup, example_container: dict):
    # example_dict: {"title": "ABC", "price": 123, "details": "xyz"}
    text_examples = [example_container[key] for key in example_container]
    lca, path_to_container = find_container_from_examples(text_examples)
    # parallel
    template_structure = set_up_container_template_structure(
        example_container_structure=example_container, lca=lca
    )
    similar_containers = find_similar_containers(path_to_container)
    # parallel
    found_contents = []
    for container in similar_containers:
        found_content += extract_items_in_containers(container)

    return found_contents


def find_container_from_examples(text_examples: list[str]):
    example_tags = [find_string_tag(string) for string in text_examples]
    lca = lowest_common_ancestor(None, *example_tags)
    if lca is None:
        logger.info("Cannot find container from provided examples")
        raise Exception
    path_to_container = find_path(content=lca)
    logger.info(
        f"""Found container tag: {lca.name}
            Found path to container: {' -> '.join(path for path in path_to_container.split(' '))}"""
    )
    return lca, path_to_container


def set_up_container_template_structure(
    example_container_structure: list[dict], lca
) -> dict:
    """Receive a dictionary of user input examples, define a schema consisting of element paths and labels within the container.
    The returned structure will serve as an instruction to how information will be extracted across containers
    Example structure:
    template_structure = {"title": "a h3", "description": "a p"}
    """
    logger.info("Setting up template structure for container extraction")
    template_structure = {}
    for extract_item in example_container_structure:
        path = find_path(content=extract_item["content"], soup=lca)
        template_structure[extract_item.key] = path
    return template_structure


def find_similar_containers(soup, path_to_container):
    "Uses the path of an example container, to find other similar containers"
    logger.info("Getting list of similar containers")
    return soup.select(path_to_container)


def extract_items_in_containers(container, template_structure) -> dict:
    """Receives a container and a template structure, returns a dictionary populated with content in the corresponding keys specified by the template structure
    Example structure:
    extracted_item = {"title": "ABC", "description": "xyz"}
    """
    res_dict = {}
    for extract_item in template_structure:
        string_values = []
        content_tags = container.select(extract_item["path"])
        string_values += [
            content_tag.get_text().strip() for content_tag in content_tags
        ]
        res_dict[extract_item.key] = string_values
    return res_dict
