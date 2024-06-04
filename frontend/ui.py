import json
import os
from bs4 import BeautifulSoup
import gradio as gr
import sys

sys.path.append("./")

from backend.extractor.task.container_extractor import (
    ContainerExtractor,
)
from backend.extractor.utils import prepare_html
from backend.fetcher.fetcher import fetch_html, fetch_infinite_page


async def get_url(url, fetch_option_checkbox, scroll_timeout, expand_text):
    if "Infinite Scroll" in fetch_option_checkbox:
        scroll = True
        max_duration = scroll_timeout
    else:
        scroll = False
        max_duration = 0

    if "Element expand" in fetch_option_checkbox:
        expand = True
        expand_button_text = expand_text.split(", ")
    else:
        expand = False
        expand_button_text = None
    html = await fetch_infinite_page(
        url=url,
        max_duration=max_duration,
        scroll=scroll,
        expand=expand,
        expand_button_text=expand_button_text,
    )
    return html


def remove_data(label_input, contents_to_extract: dict):
    if label_input in contents_to_extract.keys():
        del contents_to_extract[label_input]
    return contents_to_extract


def add_data(label_input, content_input, contents_to_extract: dict):
    contents_to_extract[label_input] = content_input
    return contents_to_extract


async def extract(html, contents_to_extract):
    # example_container = json.loads(contents_to_extract)
    extractor = ContainerExtractor(html, contents_to_extract)
    structured_contents, unstructured_contents = (
        await extractor.container_extract_run_task()
    )

    # return structured_contents, unstructured_contents
    return json.dumps(obj=structured_contents, indent=4), unstructured_contents


css = """
#html_output {overflow: scroll}"""

with gr.Blocks(theme="step-3-profit/Midnight-Deep", css=css) as demo:
    gr.Markdown("## Fetch HTML")
    with gr.Row():
        with gr.Column(scale=1):
            url = gr.Textbox(label="Enter URL", placeholder="https://example.com")
            fetch_option_checkbox = gr.CheckboxGroup(
                ["Infinite Scroll", "Element expand"], label="Fetch options"
            )
            with gr.Row():
                scroll_timeout_slider = gr.Slider(
                    5,
                    180,
                    value=20,
                    label="Scroll timeout",
                    info="Set a timeout limit for scroll",
                    visible=False,
                )
                expand_text_input = gr.Textbox(
                    label="Text in expand buttons",
                    value="Show more, See more, Expand",
                    visible=False,
                )

            def change_visibility(checkbox):
                scroll = (
                    gr.Slider(visible=True)
                    if "Infinite Scroll" in checkbox
                    else gr.Slider(visible=False)
                )
                expand = (
                    gr.Textbox(visible=True)
                    if "Element expand" in checkbox
                    else gr.Textbox(visible=False)
                )
                return scroll, expand

            fetch_option_checkbox.change(
                change_visibility,
                fetch_option_checkbox,
                [scroll_timeout_slider, expand_text_input],
            )
        with gr.Column(scale=1):
            html = gr.Code(
                label="HTML", language="html", lines=12, elem_id="html_output", scale=1
            )
    fetch_button = gr.Button("Fetch HTML", elem_classes="button")
    fetch_button.click(
        get_url,
        inputs=[url, fetch_option_checkbox, scroll_timeout_slider, expand_text_input],
        outputs=html,
    )
    gr.Markdown("## Extract tasks")
    with gr.Tab("Extract structured data") as tasks:
        gr.Markdown("## Task 1: Extract data with structure")
        with gr.Row():
            contents_to_extract = gr.State({})
            with gr.Column():
                label_container = gr.Textbox(label="Label", scale=1)
                content_container = gr.Textbox(label="Content Example", scale=1)
            with gr.Column():
                output_field = gr.JSON(label="Output", scale=2)
        with gr.Row():
            remove_data_button = gr.Button(
                "Remove data from extract list", elem_classes="button"
            )
            add_data_button = gr.Button(
                "Add data to extract list", elem_classes="button"
            )
            extract_button = gr.Button("Extract", elem_classes="button")
        with gr.Row():
            with gr.Column():
                structured_extracted_output = gr.Textbox(
                    label="Extracted Result", max_lines=20
                )
                unstructured_extracted_output = gr.Textbox(
                    label="Unstructured extracted text", max_lines=20
                )

        remove_data_button.click(
            remove_data,
            [label_container, contents_to_extract],
            [output_field],
        )
        add_data_button.click(
            fn=add_data,
            inputs=[label_container, content_container, contents_to_extract],
            outputs=[output_field],
        )
        extract_button.click(
            fn=extract,
            inputs=[html, contents_to_extract],
            outputs=[structured_extracted_output, unstructured_extracted_output],
        )

demo.launch()
