import gradio as gr

container_extract_task_tab = gr.Tab("Container Tab")
with container_extract_task_tab:
    gr.Markdown("## Task 2: Extract data in specified structure")
    with gr.Row():
        contents_to_extract = gr.State({})
        with gr.Column():
            label_container = gr.Textbox(label="Label", scale=1)
            content_container = gr.Textbox(label="Content Example", scale=1)
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
            unstructured_extracted_output = gr.Textbox(
                label="Unstructured extracted text", max_lines=20
            )
