from backend.extractor.extractor import find_path, find_string_tag
from backend.extractor.utils import prepare_html
from backend.logger import get_logger

logger = get_logger()


def is_duplicate(new_path, existing_paths):
    for path in existing_paths:
        if path in new_path:
            return True
    return False


class SingleElementExtractor:
    def __init__(self, example_container, html):

        self.input_container = example_container
        self.process_container = {}
        for key, value in example_container.items():
            self.process_container[key] = {"content": value}

    def get_html(self, html):
        return prepare_html(html)

    def extract_similar_text_from_example(self, soup, extract_item):
        """Extract contents with similar paths. Result in 1 array containing all text with similar path.
        If multiple example tags with different paths are provided, will also append them in the array
        """
        logger.info("Getting tags")
        content_tags = []
        for string in extract_item:
            content_tags.append(
                find_string_tag(soup=soup, navigable_string_content=string["content"])
            )

        paths = []
        for content_tag in content_tags:
            print(content_tag)
            path = find_path(soup=soup, content=content_tag)
            if not is_duplicate(path, paths):
                paths.append(path)
        print(paths)
        logger.info("Getting extract items paths")
        res = []
        for path in paths:
            selector = path.replace(" ", " > ")
            similar_tags = soup.select(selector)
            string_values = (
                [tag.get_text().strip() for tag in similar_tags]
                if similar_tags is not None
                else ""
            )
            res.append(string_values)
        return res

    def extract_task(self, html):
        soup = prepare_html(html)
        res = {}
        for key, values in self.process_container.items():
            extract_items = self.extract_similar_text_from_example(soup, values)
            print(values["content"])
            res[key] = extract_items
        return res
