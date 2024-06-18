import asyncio
from copy import deepcopy
from backend.extractor.extractor import find_path, find_string_tag
from backend.extractor.task.extract_task import ExtractTask
from backend.extractor.utils import is_dict_empty, is_duplicate, prepare_html
from backend.logger import get_logger

logger = get_logger()


async def filter_non_empty_dicts(data):
    tasks = [(d, is_dict_empty(d)) for d in data]
    results = await asyncio.gather(*[task[1] for task in tasks])
    non_empty_dicts = [
        task[0] for task, is_empty in zip(tasks, results) if not is_empty
    ]
    return non_empty_dicts


class SinglePathElementExtractor(ExtractTask):
    def __init__(self, example_input: dict, html: str, html_list=[]):
        super().__init__(example_input, html, html_list)

    async def prepare_single_website_extract_template(self):
        for label in self.example_template.values():
            results = await asyncio.gather(
                *[self.prepare_extract_item(extract_item) for extract_item in label]
            )
            for extract_item, result in zip(label, results):
                if not result:
                    logger.info("Removing item from search list")
                    label.remove(extract_item)

    async def prepare_extract_item(self, extract_item):
        try:
            logger.info("1a. Get item tags")
            extract_item.tag = find_string_tag(
                soup=self.soup, navigable_string_content=extract_item.content
            )
        except:
            logger.warning(f"Cannot find {extract_item.content}")
            return False
        logger.info("1b. Getting item's path")
        extract_item.base_path = find_path(soup=self.soup, content=extract_item.tag)
        selector = extract_item.base_path.replace(" ", " > ")
        extract_item.search_path = selector
        extract_item.attributes = extract_item.tag.attrs
        if "by_class" in extract_item.extract_method:
            if "class" in extract_item.attributes:
                logger.info("Adding class to search path")
                extract_item.search_path += "." + ".".join(
                    extract_item.attributes["class"]
                )
            else:
                logger.info("Tag does not contains class attribute")
        if "by_id" in extract_item.extract_method:
            if "id" in extract_item.attributes:
                logger.info("Adding class to search path")
                extract_item.search_path += "#" + extract_item.attributes["id"]
            else:
                logger.info("Tag does not contain id attribute")
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
                search_paths.append(search_path)
        res = ""
        for path in search_paths:
            similar_tags = soup.select(path)
            string_values = (
                [tag.get_text().strip() for tag in similar_tags]
                if similar_tags is not None
                else ""
            )
            res = res + " " + " ".join(string_values)
        return res.strip()

    async def extract_task(self, soup, example_template) -> str:
        tasks = []
        for label in example_template.values():
            tasks.append(self.extract_similar_text_from_example(soup, label))
        results = await asyncio.gather(*tasks)
        return [dict(zip(example_template.keys(), results))]
        # res = {}
        # for key, label in self.example_template.items():
        #     res[key] = await self.extract_similar_text_from_example(self.soup, label)
        # return res

    async def single_element_extract_run_task(self):
        logger.info("STEP 1: PREPARING EXTRACT ITEMS WITH EXTRACT PATHS")
        await self.prepare_single_website_extract_template()
        logger.info("STEP 2: EXTRACTING TEXT WITH PATH")
        res = await self.extract_task(self.soup, self.example_template)
        return res

    async def extract_from_one_website(self, html, example_template):
        soup = prepare_html(html)
        res = await self.extract_task(soup, example_template)
        return res[0]

    async def extract_from_multiple_websites(self, html_list):
        await self.prepare_single_website_extract_template()
        found_contents = await asyncio.gather(
            *[
                self.extract_from_one_website(html, self.example_template)
                for html in html_list
            ]
        )
        # res = await self.extract_from_one_website(html_list[0], self.example_template)
        res = await filter_non_empty_dicts(found_contents)
        return res

    async def extract_links(self, soup=None):
        if soup is None:
            soup = self.soup
        logger.info("STEP 1: PREPARING EXTRACT ITEMS WITH EXTRACT PATHS")
        await self.prepare_single_website_extract_template()
        logger.info("STEP 2: EXTRACTING LINKS")

        async def extract_link_from_single_tag(label):
            search_paths = []
            for extract_item in label:
                search_path = extract_item.search_path
                if not is_duplicate(search_path, search_paths):
                    search_paths.append(search_path)
            links = []
            for path in search_paths:
                similar_tags = soup.select(path)
                for tag in similar_tags:

                    if "href" in tag.attrs:
                        links.append(tag["href"])
            return links

        tasks = []
        for label in self.example_template.values():
            tasks.append(extract_link_from_single_tag(label))
        results = await asyncio.gather(*tasks)
        return dict(zip(self.example_template.keys(), results))
