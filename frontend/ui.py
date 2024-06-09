import os
import gradio as gr
import sys

from utils import (
    add_data,
    extract,
    get_url,
    save_to_csv,
    save_to_json,
    single_path_extract,
)

sys.path.append("./")

css = """
#html_output {overflow: scroll}"""

with gr.Blocks(theme="step-3-profit/Midnight-Deep", css=css) as demo:
    gr.Markdown("## Fetch HTML")
    with gr.Row():
        with gr.Column(scale=1):
            url = gr.Textbox(label="Enter URL", placeholder="https://example.com")
            with gr.Row():
                fetch_options_radio = gr.Radio(
                    ["Static", "Dynamic"], label="Website type", scale=1
                )
                fetch_options_checkbox = gr.CheckboxGroup(
                    ["Infinite Scroll", "Element expand"],
                    label="Dynamic fetch options",
                    interactive=False,
                    scale=1.5,
                )

                def change_fetch_options_interactivity(radio):
                    if radio == "Dynamic":
                        checkbox = gr.CheckboxGroup(interactive=True)
                    else:
                        checkbox = gr.CheckboxGroup(interactive=False, value=None)
                    return checkbox

            with gr.Column(scale=2):
                scroll_timeout_slider = gr.Slider(
                    5,
                    180,
                    value=20,
                    label="Scroll timeout",
                    info="Set a timeout limit for scroll",
                    interactive=False,
                )
                expand_text_input = gr.Textbox(
                    label="Text in expand buttons",
                    value="Show more, See more, Expand",
                    interactive=False,
                )
                fetch_options_radio.change(
                    fn=change_fetch_options_interactivity,
                    inputs=fetch_options_radio,
                    outputs=fetch_options_checkbox,
                )

                def change_dynamic_options_interactivity(checkbox):
                    scroll = (
                        gr.Slider(interactive=True)
                        if "Infinite Scroll" in checkbox
                        else gr.Slider(interactive=False)
                    )
                    expand = (
                        gr.Textbox(interactive=True)
                        if "Element expand" in checkbox
                        else gr.Textbox(interactive=False)
                    )
                    return scroll, expand

                fetch_options_checkbox.change(
                    change_dynamic_options_interactivity,
                    fetch_options_checkbox,
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
                fetch_options_checkbox,
                fetch_options_radio,
                scroll_timeout_slider,
                expand_text_input,
                html,
            ]
        )
        fetch_button = gr.Button("Fetch HTML", elem_classes="button", variant="primary")
        fetch_button.click(
            get_url,
            inputs=[
                url,
                fetch_options_radio,
                fetch_options_checkbox,
                scroll_timeout_slider,
                expand_text_input,
            ],
            outputs=html,
        )
    gr.Markdown("## Extract tasks")
    with gr.Tab("Basic data extraction"):
        gr.Markdown("## Task 1: Extract data using element path")
        with gr.Row():
            single_path_contents_to_extract = gr.State({})
            with gr.Column():
                single_path_label_container = gr.Textbox(label="Label", scale=1)
                single_path_content_container = gr.Textbox(
                    label="Content Example", scale=1
                )
                single_path_extract_method_checkbox = gr.CheckboxGroup(
                    ["Extract by class", "Extract by ID"], label="Extract method"
                )
            with gr.Column():
                single_path_output_field = gr.JSON(label="Output", scale=2)
        with gr.Row():
            extract_clear_button = gr.ClearButton(
                components=[single_path_contents_to_extract, single_path_output_field]
            )
            add_item_button = gr.Button("Add extract item")
            extract_button = gr.Button("Extract", variant="primary")
        with gr.Row():
            single_path_extracted_output = gr.Textbox(
                label="Extracted Result", max_lines=20, scale=2
            )
        with gr.Row():
            get_csv_button = gr.Button("Get CSV file")
            get_json_button = gr.Button("Get JSON file")
        with gr.Row():
            csv_file = gr.File(label="Output CSV", visible=False)
            json_file = gr.File(label="Output JSON", visible=False)

            def change_file_visibility():
                return gr.File(visible=True)

            get_csv_button.click(fn=change_file_visibility, outputs=csv_file).then(
                fn=save_to_csv,
                inputs=[single_path_extracted_output, url],
                outputs=[csv_file],
            )
            get_json_button.click(fn=change_file_visibility, outputs=json_file).then(
                fn=save_to_json,
                inputs=[single_path_extracted_output, url],
                outputs=[json_file],
            )
        add_item_button.click(
            fn=add_data,
            inputs=[
                single_path_label_container,
                single_path_content_container,
                single_path_extract_method_checkbox,
                single_path_contents_to_extract,
            ],
            outputs=[single_path_output_field],
        )
        extract_button.click(
            fn=single_path_extract,
            inputs=[html, single_path_contents_to_extract],
            outputs=[single_path_extracted_output],
        )

    with gr.Tab("Container Task") as tasks:
        gr.Markdown("## Task 2: Extract data in specified structure")
        with gr.Row():
            contents_to_extract = gr.State({})
            with gr.Column():
                label_container = gr.Textbox(label="Label", scale=1)
                content_container = gr.Textbox(label="Content Example", scale=1)
                extract_method_checkbox = gr.CheckboxGroup(
                    ["Extract by class", "Extract by ID"], label="Extract method"
                )
            with gr.Column():
                output_field = gr.JSON(label="Output", scale=2)
        with gr.Row():
            extract_clear_button = gr.ClearButton(
                components=[contents_to_extract, output_field]
            )
            add_item_button = gr.Button("Add extract item")
            extract_button = gr.Button("Extract", variant="primary")
        with gr.Row():
            with gr.Column():
                structured_extracted_output = gr.Textbox(
                    label="Extracted Result", max_lines=20
                )
        with gr.Row():
            get_csv_button = gr.Button("Get CSV file")
            get_json_button = gr.Button("Get JSON file")
        with gr.Row():
            csv_file = gr.File(label="Output CSV", visible=False)
            json_file = gr.File(label="Output JSON", visible=False)

            def change_file_visibility():
                return gr.File(visible=True)

            get_csv_button.click(fn=change_file_visibility, outputs=csv_file).then(
                fn=save_to_csv,
                inputs=[structured_extracted_output, url],
                outputs=[csv_file],
            )
            get_json_button.click(fn=change_file_visibility, outputs=json_file).then(
                fn=save_to_json,
                inputs=[single_path_extracted_output, url],
                outputs=[json_file],
            )
        add_item_button.click(
            fn=add_data,
            inputs=[
                label_container,
                content_container,
                extract_method_checkbox,
                contents_to_extract,
            ],
            outputs=[output_field],
        )
        extract_button.click(
            fn=extract,
            inputs=[html, contents_to_extract],
            outputs=[structured_extracted_output],
        )

demo.launch()
