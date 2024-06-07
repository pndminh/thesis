import asyncio
from copy import deepcopy
from backend.extractor.extractor import find_path, find_string_tag
from backend.extractor.task.extract_task import ExtractTask
from backend.extractor.utils import prepare_html
from backend.logger import get_logger

logger = get_logger()


def is_duplicate(new_path, existing_paths):
    for path in existing_paths:
        if path in new_path:
            return True
    return False


class SingleElementExtractor(ExtractTask):
    def __init__(self, example_input: dict, html: str):
        super().__init__(example_input, html)

    async def prepare_single_website_extract_template(self):
        for label in self.example_template.values():
            results = await asyncio.gather(
                *[self.prepare_extract_item(extract_item) for extract_item in label]
            )
            for extract_item, result in zip(label, results):
                if not result:
                    label.remove(extract_item)

    async def prepare_extract_item(self, extract_item):
        try:
            extract_item.tag = find_string_tag(
                soup=self.soup, navigable_string_content=extract_item.content
            )
        except:
            logger.warning(f"Cannot find {extract_item.content}")
            return False
        logger.info("Get item tags")
        extract_item.base_path = find_path(soup=self.soup, content=extract_item.tag)
        selector = extract_item.base_path.replace(" ", " > ")
        extract_item.search_path = selector
        extract_item.attributes = extract_item.tag.attrs
        if extract_item.extract_method == "by_class":
            if "class" in extract_item.attributes:
                extract_item.search_path = (
                    selector + "." + ".".join(extract_item.attributes["class"])
                )
            else:
                logger.info("Tag does not contains class attribute")
        elif extract_item.extract_method == "by_id":
            if "id" in extract_item.attributes:
                extract_item.search_path = (
                    selector + "#" + extract_item.attributes["id"]
                )
            else:
                logger.info("Tag does not contain id attribute")
        logger.info(f"Extracted search path: {extract_item.search_path}")

        return True

    def get_html(self, html):
        return prepare_html(html)

    async def extract_similar_text_from_example(self, soup, extract_items) -> str:
        """Handles extraction of contents with similar paths in a single extraction label. Result in a string containing all text with similar path.
        If multiple example tags with different paths are provided, will also append them to the result array
        """
        search_paths = []
        for extract_item in extract_items:
            search_path = extract_item.search_path
            if not is_duplicate(search_path, search_paths):
                logger.info("Adding search path to find list")
                search_paths.append(search_path)
        logger.info("Getting extract items paths")
        res = ""
        for path in search_paths:
            print("searching path: ", path)
            similar_tags = soup.select(path)
            string_values = (
                [tag.get_text().strip() for tag in similar_tags]
                if similar_tags is not None
                else ""
            )
            print("string found: ", string_values)
            res = res + " " + " ".join(string_values)
            # res.append(string_values)
        return res.strip()

    async def extract_task(self, soup, example_template) -> str:
        tasks = []
        for key, label in example_template.items():
            tasks.append(self.extract_similar_text_from_example(soup, label))
        results = await asyncio.gather(*tasks)
        return dict(zip(example_template.keys(), results))
        # res = {}
        # for key, label in self.example_template.items():
        #     res[key] = await self.extract_similar_text_from_example(self.soup, label)
        # return res

    async def extract_website(self, html, example_template):
        soup = prepare_html(html)
        return await self.extract_task(soup, example_template)

    async def extract_from_multiple_website(self, html_list, example_template=None):
        if example_template is None:
            example_template = self.example_template
        res = await asyncio.gather(
            *[self.extract_website(html, example_template) for html in html_list]
        )
        return res
