from backend.extractor.utils import prepare_html


class ArticleExtractor:
    def __init__(self, html):
        self.soup = prepare_html(html)
    
    def extract_tags