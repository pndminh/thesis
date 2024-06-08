class ExtractItem:

    def __init__(
        self,
        content=None,
        tag=None,
        attributes=None,
        base_path=None,
        label=None,
        extract_method=None,
        search_path=None,
    ):
        self.content = content
        self.tag = tag
        self.attributes = attributes
        self.base_path = ""
        self.label = label
        self.extract_method = extract_method
        self.search_path = ""

    content: str
    tag: str
    attributes: dict
    base_path: str
    label: str
    extract_method: list[str]
    search_path: str
