def extract_related_info_system_prompt(example_container):
    return f"""You are provided an array that contains some information from a website. You will help the user extract the information you are provided into a structured json similar to the example JSON you are provided. Output only the result json with the appropriate information.
example JSON: {example_container}"""


def extract_related_info_user_prompt(info_to_extract):
    return f"""Extract the specified information from the following array
    ---
    Information: {info_to_extract}"""
