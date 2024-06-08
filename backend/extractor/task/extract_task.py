from abc import ABC
from backend.extractor.extractor import find_path, find_string_tag
from backend.extractor.task.extract_item import ExtractItem
from backend.extractor.utils import prepare_html
from backend.logger import get_logger


logger = get_logger()


class ExtractTask(ABC):
    def __init__(self, example_input: dict, html: str, html_list: list = None):
        """example_extract = {"label": [("content1", "method"), ("content2")], "label2": ["content1", "content2"]}
        - For Container extract, this specifies the container that the agent will look for across the page
        - For Single Path extract, this is all of the information that the agent will look for in the page using the path of each content
        """
        self.example_template = {}
        for key, values in example_input.items():
            self.example_template[key] = [
                ExtractItem(content=value[0], extract_method=value[1])
                for value in values
            ]
        self.soup = prepare_html(html)
        self.html_list = html_list if html_list is not None else []

    def run_extract_task(self):
        pass
