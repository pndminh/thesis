import datetime
from backend.logger import get_logger
from bs4 import BeautifulSoup


logger = get_logger()


def clean_html(soup, tags=["script", "style", "link", "meta", "nav"]):
    """Receives a list of elements to remove from the soup."""
    for data in soup(tags):
        data.decompose()
    logger.info(
        "Cleaning HTML, removing all path that does not contains navigable string"
    )
    return soup.body


def traverse_and_modify(current_tag, current_path=None):
    """Traverse an html soup, starting form the first tag of the soup to the leaf node (navigable string).
    Remove all paths that does not leads to a navigable strin. Return a modified version of the beautiful soup tree.
    """

    if current_path is None:
        current_path = [current_tag.name]

    children_to_traverse = []
    # traverse all child tags of the current tag
    for child_tag in current_tag.find_all(recursive=False):
        # if cannot find any children, we are at the leaf node,
        if not child_tag.find():
            # if we could find a string at the leaf node, print it out
            if (
                child_tag.find(string=True)
                and not child_tag.find(string=True).strip() == ""
            ):
                string_value = child_tag.find(string=True).strip()
                # current_tag.append(tag)i
                print(
                    " -> ".join(
                        current_path
                        + [child_tag.name, string_value.replace("\n", "").strip()]
                    )
                )
            else:
                child_tag.decompose()
        else:
            children_to_traverse.append(child_tag)
    for child_tag in children_to_traverse:
        traverse_and_modify(
            current_tag=child_tag,
            current_path=current_path + [child_tag.name],
        )

    return current_tag


def save_html(db, url, soup: BeautifulSoup):
    doc_ref = db.collection("crawl-result").document()
    last_modified = str(datetime.date.today())
    doc_ref.set(
        {
            "url": url,
            "soup": str(soup),
            "last_modified": last_modified,
        }
    )
    logger.info("Saved soup to firebase")


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup


def prepare_html(html):
    "clean and parse html to prepare it for extraction"
    if type(html) is not BeautifulSoup:
        soup = parse_html(html)
    else:
        soup = html
    soup = clean_html(soup)
    soup = traverse_and_modify(soup)
    return soup
