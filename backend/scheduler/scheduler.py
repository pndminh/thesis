import schedule
from backend.extractor.task.extract_task import ExtractTask
from backend.extractor.task.single_path_extractor import SinglePathElementExtractor
from backend.fetcher.fetcher import fetch_multiple_pages, fetch_page
from frontend.utils import single_path_extract


async def fetch_multiple_website_job(
    urls,
    example_container,
    to_do,
    static_fetch=False,
    max_duration=20,
    scroll=True,
    expand=False,
    expand_button_text=None,
    extract_task=SinglePathElementExtractor,
):

    html_list = await fetch_multiple_pages(
        urls, static_fetch, max_duration, scroll, expand, expand_button_text
    )
    return to_do(html_list[0], html_list, example_container)


async def fetch_single_website_job(
    url,
    example_container,
    to_do,
    static_fetch=False,
    max_duration=20,
    scroll=True,
    expand=False,
    expand_button_text=None,
):
    html = await fetch_page(
        url,
        static_fetch,
        max_duration,
        scroll,
        expand,
        expand_button_text,
    )
    return to_do(html, example_container)
