import gradio as gr

from backend.extractor.task.container_extractor import ExtractorTask


def extract_structured_data_task(html):
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
            remove_data_button = gr.Button("Remove data from extract list")
            add_data_button = gr.Button("Add data to extract list")
            extract_button = gr.Button("Extract")
        with gr.Row():
            with gr.Column():
                structured_extracted_output = gr.Textbox(
                    label="Extracted Result", max_lines=20
                )
                unstructured_extracted_output = gr.Textbox(
                    label="Unstructured extracted text", max_lines=20
                )

        def remove_data(label_input, contents_to_extract: dict):
            if label_input in contents_to_extract.keys():
                del contents_to_extract[label_input]
            return contents_to_extract

        def add_data(label_input, content_input, contents_to_extract: dict):
            contents_to_extract[label_input] = content_input
            return contents_to_extract

        async def extract(html, contents_to_extract):
            # example_container = json.loads(contents_to_extract)
            extractor = await ExtractorTask(html, contents_to_extract)
            structured_contents, unstructured_contents = (
                await extractor.container_extract_run_task()
            )
            return structured_contents, unstructured_contents

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
    return tasks
