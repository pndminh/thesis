import asyncio
from bs4 import BeautifulSoup

from backend.extractor.extractor import (
    find_path,
    find_string_tag,
    lowest_common_ancestor,
)
from backend.extractor.utils import prepare_html
from backend.logger import get_logger

logger = get_logger()


class ContainerExtractor:
    def __init__(self, html, example_container):
        self.soup = prepare_html(html)
        self.input_container = example_container
        self.process_container = {}
        for key, value in example_container.items():
            self.process_container[key] = {"content": value}

    async def container_extract_run_task(self) -> list[dict]:
        # example_dict: {"title": "ABC", "price": 123, "details": "xyz"}
        self.find_container_from_examples()
        # parallel
        set_up_container_task = asyncio.create_task(
            self.set_up_container_template_structure()
        )
        get_similar_containers_task = asyncio.create_task(
            self.find_similar_containers()
        )
        template_structure, similar_containers = await asyncio.gather(
            set_up_container_task, get_similar_containers_task
        )
        # parallel
        found_contents = []
        tasks = []
        for container in similar_containers:
            tasks.append(
                asyncio.create_task(
                    self.extract_items_in_containers(
                        container=container, template_structure=template_structure
                    )
                )
            )
        found_contents = await asyncio.gather(*tasks)
        cleaned_found_contents = await filter_non_empty_dicts(found_contents)

        return cleaned_found_contents

    def find_container_from_examples(self):
        example_tags = []
        for key in self.process_container:
            text_example = self.process_container[key]["content"]
            example_tag = find_string_tag(self.soup, text_example)
            example_tags.append(example_tag)

            # save found tags for later usage
            self.process_container[key]["content_tag"] = example_tag

        lca = lowest_common_ancestor(
            len(example_tags),
            None,
            *example_tags,
        )
        if lca is None:
            logger.info("Cannot find container from provided examples")
            raise Exception
        path_to_container = find_path(soup=self.soup, content=lca)
        logger.info(
            f"""Found container tag: {lca.name}
                Found path to container: {' -> '.join(path for path in path_to_container.split(' '))}"""
        )
        self.lca = lca
        self.path_to_lca = path_to_container
        return lca, path_to_container

    async def set_up_container_template_structure(
        self,
    ) -> dict:
        """Receive a dictionary of user input examples, define a schema consisting of element paths and labels within the container.
        The returned structure will serve as an instruction to how information will be extracted across containers
        Example structure:
        template_structure = {"title": "a h3", "description": "a p"}
        """
        logger.info("Setting up template structure for container extraction")
        template_structure = {}
        for key, value in self.process_container.items():
            path = find_path(value["content_tag"], soup=self.lca)
            template_structure[key] = path
        return template_structure

    async def find_similar_containers(self):
        "Uses the path of an example container, to find other similar containers"
        logger.info("Getting list of similar containers")
        return self.soup.select(self.path_to_lca)

    async def extract_items_in_containers(self, container, template_structure) -> dict:
        """Receives a container and a template structure, returns a dictionary populated with content in the corresponding keys specified by the template structure
        Example structure:
        extracted_item = {"title": "ABC", "description": "xyz"}
        """
        res_dict = {}
        for key, value in template_structure.items():
            string_values = []
            content_tags = container.select(value)
            string_values += (
                [content_tag.get_text().strip() for content_tag in content_tags]
                if content_tags is not None
                else ""
            )
            res_dict[key] = string_values
        return res_dict
    
async def is_dict_empty(d):
return all(not value for value in d.values())

# Asynchronous function to filter non-empty dictionaries
async def filter_non_empty_dicts(data):
    tasks = [(d, is_dict_empty(d)) for d in data]
    results = await asyncio.gather(*[task[1] for task in tasks])
    non_empty_dicts = [task[0] for task, is_empty in zip(tasks, results) if not is_empty]
    return non_empty_dicts
