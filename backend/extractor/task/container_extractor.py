import asyncio
from bs4 import BeautifulSoup

from backend.extractor.extractor import (
    find_path,
    find_string_tag,
    lowest_common_ancestor,
)
from backend.extractor.task.extract_task import ExtractTask
from backend.extractor.utils import is_duplicate, parse_html, prepare_html
from backend.logger import get_logger

logger = get_logger()


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


# Asynchronous function to filter non-empty dictionaries
async def filter_non_empty_dicts(data):
    tasks = [(d, is_dict_empty(d)) for d in data]
    results = await asyncio.gather(*[task[1] for task in tasks])
    non_empty_dicts = [
        task[0] for task, is_empty in zip(tasks, results) if not is_empty
    ]
    return non_empty_dicts


class ContainerExtractor(ExtractTask):
    def __init__(self, example_input: dict, html: str, html_list=[]):
        super().__init__(example_input, html, html_list)

    async def prepare_single_website_extract_template(self):
        for label in self.example_template.values():
            results = await asyncio.gather(
                *[self.prepare_extract_item(extract_item) for extract_item in label]
            )
            for extract_item, result in zip(label, results):
                if not result:
                    logger.info(
                        f"1b. Removing item {extract_item.content} from search list"
                    )
                    label.remove(extract_item)

    async def prepare_extract_item(self, extract_item):
        try:
            logger.info(f"1a. Getting the tag for content {extract_item.content}")
            extract_item.tag = find_string_tag(
                soup=self.soup, navigable_string_content=extract_item.content
            )
        except:
            logger.warning(f"Cannot find {extract_item.content}")
            return False
        extract_item.search_path = ""
        extract_item.base_path = ""
        extract_item.attributes = extract_item.tag.attrs
        if "by_class" in extract_item.extract_method:
            if "class" in extract_item.attributes:
                extract_item.search_path = "." + ".".join(
                    extract_item.attributes["class"]
                )
            else:
                logger.info("Tag does not contains class attribute")
        if "by_id" in extract_item.extract_method:
            if "id" in extract_item.attributes:
                extract_item.search_path = "#" + extract_item.attributes["id"]

            else:
                logger.info("Tag does not contain id attribute")

        return True

    async def search_for_containers(self):
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
        self.similar_containers = similar_containers
        return template_structure, similar_containers

    async def container_extract_run_task(self):
        logger.info("STEP 1: SAVING SEARCH STRINGS TO EXTRACT ITEM DICTIONARIES")
        await self.prepare_single_website_extract_template()
        logger.info("STEP 2: SEARCHING FOR SIMILAR CONTAINERS")
        await self.search_for_containers()
        logger.info("STEP 3: EXTRACTING CONTENTS IN SIMILAR CONTAINERS")
        structured_text_containers = (
            await self.extract_structured_text_from_containers()
        )
        # unstructured_text_containers = (
        #     await self.extract_unstructured_text_from_containers()
        # )
        return structured_text_containers

    def find_container_from_examples(self):
        logger.info("2a. Searching for LCA")
        example_tags = []
        text_example = []
        example_tags
        for label in self.example_template.values():
            [text_example.append(extract_item.content) for extract_item in label]
            [example_tags.append(extract_item.tag) for extract_item in label]

        lca = lowest_common_ancestor(
            len(example_tags),
            None,
            *example_tags,
        )
        if lca is None:
            logger.info("Cannot find container from provided examples")
            raise Exception

        path_to_container = find_path(soup=self.soup, content=lca)
        if path_to_container is None:
            logger.info("Cannot find path to container")
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
        logger.info("2.b Setting up item's path in container to get template structure")
        template_structure = {}
        for key, label in self.example_template.items():
            paths = []
            for extract_item in label:
                path = find_path(extract_item.tag, soup=self.lca)
                extract_item.base_path = path.replace(" ", " > ")
                extract_item.search_path = (
                    extract_item.base_path + extract_item.search_path
                )
                if not is_duplicate(extract_item.search_path, paths):
                    logger.info("Adding search path to find list")
                    paths.append(extract_item.search_path)
            template_structure[key] = paths
        self.template_structure = template_structure

    async def find_similar_containers(self, soup=None):
        "Uses the path of an example container, to find other similar containers"
        logger.info("2c. Searching for similar containers from LCA")
        if soup is None:
            soup = self.soup
        selector = self.path_to_lca.replace(" ", " > ")
        res = soup.select(selector)
        logger.info(f"Found {len(res)} containers")
        return res

    async def extract_items_in_container(self, container) -> dict:
        """Receives a container and a template structure, returns a dictionary populated with content in the corresponding keys specified by the template structure
        Example structure:
        extracted_item = {"title": "ABC", "description": "xyz"}
        """
        tasks = []
        for paths in self.template_structure.values():
            tasks.append(self.extract_similar_text_from_example(container, paths))
        results = await asyncio.gather(*tasks)
        return dict(zip(self.template_structure.keys(), results))

    async def extract_similar_text_from_example(self, container, template_paths):
        "Extract texts from a container"
        res = ""
        for path in template_paths:
            content_tags = container.select(path)
            string_values = (
                [content_tag.get_text().strip() for content_tag in content_tags]
                if content_tags is not None
                else ""
            )
            res += " " + " ".join(string_values)
        return res.strip()

    async def extract_structured_text_from_containers(self):
        logger.info(
            "3a. Extracting items from list of containers, this might take a minute"
        )
        found_extracted_contents = []
        found_extracted_contents = await asyncio.gather(
            *[
                self.extract_items_in_container(container=container)
                for container in self.similar_containers
            ]
        )
        structured_texts = await filter_non_empty_dicts(found_extracted_contents)
        return structured_texts

    async def extract_unstructured_text_from_containers(self) -> list:
        logger.info("Extracting text directly from container")
        unextracted_contents = []
        for container in self.similar_containers:
            contents = container.find_all(string=True, recursive=True)
            filtered = [string for string in contents if string.strip()]
            unextracted_contents.append(" ".join(filtered))

        return unextracted_contents

    async def extract_from_one_website(self, html):
        soup = prepare_html(html)
        similar_containers = self.find_similar_containers(soup)
        extracted_items_in_containers = await asyncio.gather(
            *[
                self.extract_items_in_container(container)
                for container in similar_containers
            ]
        )
        res = await filter_non_empty_dicts(extracted_items_in_containers)
        return res

    async def extract_from_multiple_websites(self, html_list):
        res = await asyncio.gather(
            *[self.extract_from_one_website(html) for html in html_list]
        )
        return res
