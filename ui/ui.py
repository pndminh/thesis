from bs4 import BeautifulSoup
import gradio as gr
import sys

sys.path.append("./")
from backend.extractor.extractor import prepare_html
from backend.fetcher.fetcher import fetch_html
from extract_structured_data import (
    add_input_fields,
    collect_inputs,
    extract_structured_data_task_interface,
)


async def get_url(url):
    html = await fetch_html(url)
    soup = prepare_html(html)
    return soup


def to_json(label, content):
    return {}


with gr.Blocks() as demo:
    gr.Markdown("## Fetch HTML")
    with gr.Row():
        url = gr.Textbox(label="Enter URL", placeholder="https://example.com")
        html = gr.Textbox(label="HTML")
    fetch_button = gr.Button("Fetch HTML")
    fetch_button.click(get_url, inputs=url, outputs=html)
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
            extract_output = gr.Textbox(label="Extract Result", scale=2)
        with gr.Row():
            remove_data_button = gr.Button("Remove data from extract list")
            add_data_button = gr.Button("Add data to extract list")
            extract_button = gr.Button("Extract")

        def remove_data(label_input, contents_to_extract: dict):
            if label_input in contents_to_extract.keys():
                del contents_to_extract[label_input]
            return contents_to_extract

        def add_data(label_input, content_input, contents_to_extract: dict):
            contents_to_extract[label_input] = content_input
            return contents_to_extract

        def extract(html, contents_to_extract: dict):
            return contents_to_extract

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
            outputs=[extract_output],
        )

        # with label_container:
        #     for textbox in label_textboxes:
        #         textbox.render()
        # with data_container:
        #     for textbox in data_textboxes:
        #         textbox.render()

        # add_button = gr.Button("Add More Fields")
        # submit_button = gr.Button("Submit")
        # output = gr.JSON(label="Collected Inputs")

        # def add_fields(label_textboxes, data_textboxes):
        #     label_textboxes, data_textboxes = add_input_fields(
        #         label_textboxes, data_textboxes
        #     )
        #     return label_textboxes, data_textboxes

        # def submit_form(label_textboxes, data_textboxes):
        #     return collect_inputs(label_textboxes, data_textboxes)

        # add_button.click(
        #     fn=add_fields,
        #     inputs=[gr.State(label_textboxes), gr.State(data_textboxes)],
        #     outputs=[label_container, data_container],
        # )
        # submit_button.click(
        #     fn=submit_form,
        #     inputs=[gr.State(label_textboxes), gr.State(data_textboxes)],
        #     outputs=output,
        # )
demo.launch()
