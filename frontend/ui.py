import json
import os
import gradio as gr
import sys
from matplotlib import colormaps


from utils import (
    add_classify_task,
    add_data,
    get_cloud,
    get_url,
    handle_extract,
    llm_classify_task,
    load_data_to_table,
    load_extract_output,
    save_to_csv,
    save_to_json,
)

sys.path.append("./")

css = """
#html_output {overflow: scroll}"""


def clear_extract_content_state():
    return {}


def clear_html_list_state():
    return []


with gr.Blocks(css=css) as demo:
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
            html_list = gr.State([])

    with gr.Row():
        fetch_clear_button = gr.ClearButton(
            components=[
                url,
                fetch_options_checkbox,
                fetch_options_radio,
                scroll_timeout_slider,
                expand_text_input,
                html_list,
            ]
        )
        fetch_button = gr.Button("Fetch HTML", elem_classes="button", variant="primary")

        def output_code(html_list):
            # print(len(html_list))
            return gr.Code(html_list[0])

        fetch_button.click(
            get_url,
            inputs=[
                url,
                fetch_options_radio,
                fetch_options_checkbox,
                scroll_timeout_slider,
                expand_text_input,
            ],
            outputs=html_list,
        ).then(output_code, inputs=html_list, outputs=html)

        fetch_clear_button.click(clear_html_list_state, outputs=html_list)
    gr.Markdown("## Extractor")
    # with gr.Tab("Basic data extraction"):
    #     gr.Markdown("## Task 1: Extract data using element path")
    #     with gr.Row():
    #         single_path_contents_to_extract = gr.State({})
    #         with gr.Column():
    #             single_path_label_container = gr.Textbox(label="Label", scale=1)
    #             single_path_content_container = gr.Textbox(
    #                 label="Content Example", scale=1
    #             )
    #             single_path_extract_method_checkbox = gr.CheckboxGroup(
    #                 ["Extract by class", "Extract by ID"], label="Extract method"
    #             )
    #             batch_extract_checkbox = gr.Checkbox(
    #                 label="Extract from website list", scale=1, interactive=True
    #             )

    #         with gr.Column():
    #             single_path_output_field = gr.JSON(label="Output", scale=2)
    #     with gr.Row():
    #         extract_clear_button = gr.ClearButton(
    #             components=[
    #                 single_path_label_container,
    #                 single_path_content_container,
    #                 single_path_extract_method_checkbox,
    #                 batch_extract_checkbox,
    #                 single_path_contents_to_extract,
    #                 single_path_output_field,
    #             ]
    #         )
    #         add_item_button = gr.Button("Add extract item")
    #         single_path_extract_button = gr.Button("Extract", variant="primary")
    #     add_item_button.click(
    #         fn=add_data,
    #         inputs=[
    #             single_path_label_container,
    #             single_path_content_container,
    #             single_path_extract_method_checkbox,
    #             single_path_contents_to_extract,
    #         ],
    #         outputs=[single_path_output_field],
    #     )
    #     extract_clear_button.click(
    #         fn=clear_extract_content_state,
    #         # inputs=single_path_contents_to_extract,
    #         outputs=single_path_contents_to_extract,
    #     )

    # with gr.Tab("Container task") as tasks:
    # gr.Markdown("## Task 2: Extract data in specified structure")
    with gr.Row():
        contents_to_extract = gr.State({})
        with gr.Column():
            label_container = gr.Textbox(label="Label", scale=1)
            content_container = gr.Textbox(label="Content Example", scale=1)
            extract_method_checkbox = gr.CheckboxGroup(
                ["Extract by class", "Extract by ID"], label="Add identifier"
            )
            with gr.Row():
                extract_type_checkbox = gr.Radio(
                    ["Direct path extract", "Container extract"],
                    label="Extract method",
                )
                batch_extract_checkbox = gr.CheckboxGroup(
                    ["True"],
                    label="Extract from webiste lists",
                    info="If unchecked, result will only contain content extracted from the first website",
                    scale=1,
                    interactive=True,
                )
        with gr.Column():
            output_field = gr.JSON(label="Output", scale=2)
    with gr.Row():
        extract_clear_button = gr.ClearButton(
            components=[
                label_container,
                content_container,
                output_field,
                batch_extract_checkbox,
                extract_method_checkbox,
            ]
        )
        add_item_button = gr.Button("Add extract item")
        container_extract_button = gr.Button("Extract", variant="primary")
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
    extract_clear_button.click(
        fn=clear_extract_content_state, outputs=contents_to_extract
    )

    extracted_output = gr.DataFrame(wrap=True)
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
            inputs=[extracted_output, url],
            outputs=[csv_file],
        )
        get_json_button.click(fn=change_file_visibility, outputs=json_file).then(
            fn=save_to_json,
            inputs=[extracted_output, url],
            outputs=[json_file],
        )
    container_extract_button.click(
        fn=handle_extract,
        inputs=[
            html_list,
            contents_to_extract,
            batch_extract_checkbox,
            extract_type_checkbox,
        ],
        outputs=[extracted_output],
    )
    # single_path_extract_button.click(
    #     fn=single_path_extract,
    #     inputs=[html_list, single_path_contents_to_extract, batch_extract_checkbox],
    #     outputs=[extracted_output],
    # )
    gr.Markdown("## Downstream analysis tasks")
    gr.Markdown("Choose a file to upload or use extracted data")
    with gr.Row():
        use_extracted_data_button = gr.Button("Use extracted data")
        upload_file = gr.UploadButton("Upload file for analysis")
    analysis_table = gr.Dataframe(scale=2, wrap=True)
    upload_file.upload(load_data_to_table, upload_file, analysis_table)
    use_extracted_data_button.click(
        load_extract_output,
        [extracted_output],
        analysis_table,
    )
    # file.upload(load_data_to_table)
    with gr.Tab("Word Cloud Generator"):
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    max_words = gr.Number(
                        label="Max number of words",
                        value=150,
                        interactive=True,
                        minimum=0,
                    )
                    color_picker = gr.ColorPicker(label="Background color")
                    color_maps = list(colormaps)[:15]
                    color_scheme = gr.Dropdown(
                        choices=color_maps,
                        label="Color scheme",
                        allow_custom_value=False,
                        filterable=True,
                        value="magma",
                        interactive=True,
                    )
                    selected_columns_input = gr.Textbox(label="Get data from columns")
                    regex_patterns_input = gr.Textbox(
                        label="Phrases or Regex patterns to remove"
                    )
                    fixed_words_input = gr.Textbox(label="Fixed words")

                wordcloud_result = gr.Image(
                    height=700, width=700, label="Result", show_download_button=True
                )
            wordcloud_button = gr.Button(
                "Generate Word Cloud",
                variant="primary",
            )

        wordcloud_button.click(
            get_cloud,
            [
                analysis_table,
                color_scheme,
                max_words,
                selected_columns_input,
                regex_patterns_input,
                fixed_words_input,
                color_picker,
            ],
            wordcloud_result,
        )

    with gr.Tab("Classification"):
        with gr.Row():
            with gr.Column():
                task_name = gr.Textbox(label="Task name")
                task_description = gr.Textbox(label="Task description")
                select_columns_input = gr.Textbox(label="Select columns")
            task_list = gr.State("")
            task_list_output = gr.JSON(label="Task list")
        with gr.Row():
            add_task_button = gr.Button("Add task")
            analyze_button = gr.Button("Analyze", variant="primary")
        analysis_result = gr.DataFrame(wrap=True, visible=True)

    def convert_to_json(task_list):
        res = json.loads(f"{{{task_list}}}")
        return gr.JSON(res)

    add_task_button.click(
        add_classify_task,
        inputs=[task_name, task_description, task_list],
        outputs=task_list,
    ).then(convert_to_json, inputs=task_list, outputs=task_list_output)

    analyze_button.click(
        llm_classify_task,
        inputs=[analysis_table, task_list_output, select_columns_input],
        outputs=analysis_result,
    )

demo.launch()
