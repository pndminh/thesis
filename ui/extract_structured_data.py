import gradio as gr


def add_input_fields(label_textboxes, data_textboxes):
    label_textboxes.append(gr.Textbox(label="Label"))
    data_textboxes.append(gr.Textbox(laebel="Content"))
    return label_textboxes, data_textboxes


def collect_inputs(label_textboxes, data_textboxes):
    container_structure = {}
    for label, data in zip(label_textboxes, data_textboxes):
        container_structure[label.value] = data.value
    return container_structure


def extract_structured_data_task_interface():

    pass
