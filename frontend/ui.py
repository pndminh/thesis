import os
import gradio as gr
import sys

from utils import add_data, extract, get_url, process_dataframe, remove_data

sys.path.append("./")

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

    with gr.Row():
        fetch_clear_button = gr.ClearButton(
            components=[
                url,
                fetch_option_checkbox,
                scroll_timeout_slider,
                expand_text_input,
            ]
        )
        fetch_button = gr.Button("Fetch HTML", elem_classes="button", variant="primary")
        fetch_button.click(
            get_url,
            inputs=[
                url,
                fetch_option_checkbox,
                scroll_timeout_slider,
                expand_text_input,
            ],
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
                output_field = gr.Textbox(label="Output", scale=2)

        with gr.Row():
            dataframe = gr.DataFrame(
                row_count=(1, "dynamic"),
                col_count=(1, "dynamic"),
                label="Example extract items",
            )

        with gr.Row():
            extract_clear_button = gr.ClearButton(components=[dataframe])
            print_button = gr.Button("Print")
            extract_button = gr.Button("Extract", variant="primary")
        with gr.Row():
            with gr.Column():
                structured_extracted_output = gr.Textbox(
                    label="Extracted Result", max_lines=20
                )
                unstructured_extracted_output = gr.Textbox(
                    label="Unstructured extracted text", max_lines=20
                )
        print_button.click(
            fn=process_dataframe, inputs=dataframe, outputs=[output_field]
        )
        extract_button.click(
            fn=extract,
            inputs=[label_container, content_container, contents_to_extract],
            outputs=[output_field],
        )
        extract_button.click(
            fn=extract,
            inputs=[html, contents_to_extract],
            outputs=[structured_extracted_output, unstructured_extracted_output],
        )

demo.launch()
