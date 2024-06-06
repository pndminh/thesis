import re, yaml, json, regex  # type: ignore
from typing import Any, Callable


def extract_markdown(string) -> str:
    # Use regex to find the markdown section
    if string is None:
        raise ValueError("Input string cannot be None")
    markdown_regex = r"```(.*?)```"
    markdown_match = re.search(markdown_regex, string, re.DOTALL)

    if markdown_match:
        markdown = markdown_match.group(1)
        return "```" + markdown + "```"
    return string


def extract_json_objects(text) -> list:
    pattern = r"\{(?:[^{}]|(?R))*\}"
    json_strings = regex.findall(pattern, text)
    json_objects = [_sanitize_json(i) for i in json_strings]
    json_objects = [i for i in json_objects if i not in ["", [], {}]]

    if len(json_objects) == 0:
        return []
    # if there's only one object
    if len(json_objects) == 1:
        # and it's a dict with only one key, return the value
        if type(json_objects[0]) == dict and len(json_objects[0].keys()) == 1:
            return list(json_objects[0].values())[0]

    return json_objects


def _sanitize_json(json_str: str):
    def localize_json_error(lineno: int, json_str: str) -> str:
        lines: list[str] = json_str.split("\n")
        start_line_idx: int = lineno - 1 if lineno > 1 else 0
        end_line_idx: int = lineno + 1 if lineno < len(lines) else len(lines)
        return "\n".join(lines[start_line_idx:end_line_idx]).strip()

    if json_str == "":
        raise json.JSONDecodeError("Tried my best, didn't work.", doc="", pos=0)

    # remove new lines to avoid errors
    # json_str = json_str.replace("\n", "")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # TODO can use this to get LLM to fix JSON
        # error_lines: str = localize_json_error(e.lineno, json_str)
        # print(f"Error {e}: {error_lines}")
        return _sanitize_json(json_str[: e.pos] + json_str[e.pos + 1 :])


def parse_llm_response_data(
    data,
) -> Any:
    """
    Parses the response data from the LLM server.

    Args:
        data: The response data from the LLM server.
        llm_output_format (LLMOutputFormat): The output format of the LLM server.
            Defaults to the value specified in the config.

    Returns:
        Any: The parsed response data.
    """

    if data is None:
        raise ValueError("Data cannot be None")

    return extract_json_objects(data)
