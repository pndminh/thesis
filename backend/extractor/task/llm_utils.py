import asyncio
import json
import string
import uuid
from backend.llm.llm import LLM
from backend.llm.utils import parse_llm_response_data
from backend.logger import get_logger
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from underthesea import word_tokenize
from langdetect import detect

logger = get_logger()


async def extract(
    prompt,
    response_format,
    system_prompt=None,
):
    prompt_token = llm.get_usage(prompt)

    llm = LLM(
        system_instruction=(
            system_prompt
            if system_prompt is not None
            else """Your job is to process the following text and extract relevant information for various tasks.
    Output only the answers in requested format. Output the answer solely based on the text you are provided"""
        ),
        response_mime_type="application/json",
    )
    logger.info("Getting summary")
    response = await llm.generate(prompt)
    output_token = llm.get_usage(response)
    parsed_response = parse_llm_response_data(response)
    logger.info(
        f"Token count: prompt_token = {prompt_token}, output_token = {output_token}"
    )
    return parsed_response


async def llm_task(text, tasks):
    llm = LLM(
        system_instruction=(
            """Your job is to process the following text and extract relevant information for various tasks. 
    Output only the answers in requested format and the same language of the provided text. Output the answer solely based on the text you are provided"""
        ),
        response_mime_type="application/json",
    )
    prompt = f"""Extract the required information from the following text and output in the following JSON format:
             {tasks}
             ---
             - Follow the instructions to extract the information as requested
             - The value of the JSON should be in Vietnamese, keep the key of the output JSON in English as requested.
             - Output only the JSON object.
             ---
             Text: {text}"""
    response = await llm.generate(prompt)
    parsed_response = parse_llm_response_data(response)[0]
    return parsed_response


def get_task_dict(task):
    task_dict = json.loads(task)
    res = {}
    for key in task_dict.keys():
        res[key] = ""
    return res


def get_summarize_prompt(text):
    prompt = f"""Summarize this text and output in the following JSON format:
             {{
             "summary": "Summarize the text with no more than 5 sentences. Keep only the main ideas, and the final message of the text. Aware that you are extracting information from newspaper articles, make sure that the summary contains the important information and all opinions present in the text without bias",
             "mentions": "List all name of people, subjects, organizations, that the text mentions in keywords"
             }}
             ---
             - Follow the instructions to extract the information as requested
             - The value of the JSON should be kept in the language of the text, keep the key of the output JSON as requested.
             - Output only the JSON object.
             ---
             Text: {text}"""
    return prompt


def extract_custom_info(article, extracts):
    extract_dict = json.dumps(extracts)
    prompt = f"""Extract the following information from the text and output in the following json format:
    {extract_dict}
    ---
    - Follow the instructions to extract the information as requested
    - The value of the JSON should be kept in the language of the text, keep the key of the output JSON as requested.
    - Output only the JSON object.
    ---
    Text: {article}"""
    return prompt


def remove_regex_patterns(text, regex_patterns):
    combined_pattern = "|".join(regex_patterns)
    filtered_text = re.sub(combined_pattern, "", text)
    return filtered_text


def draw_word_cloud(
    data,
    stopwords,
    colormap,
    background_color,
    max_words,
    save=False,
):
    logger.info("Generating word cloud")
    wordcloud = WordCloud(
        width=500,
        height=500,
        background_color=background_color,
        stopwords=stopwords,
        min_font_size=5,
        font_step=3,
        normalize_plurals=True,
        colormap=colormap,
        max_words=max_words,
    ).generate(data)

    # Display WordCloud
    plt.figure(figsize=(12, 12), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=10)
    img_id = str(uuid.uuid4())
    logger.info("Drawn word cloud")
    save_path = ""
    if save:
        save_path = f"results/word_cloud/wordcloud_{img_id}.png"
        plt.savefig(save_path)
    return plt, save_path


def prepare_word_cloud(
    data,
    selected_columns: list = [],
    regex_patterns=None,
    fixed_words=None,
):
    test = "".join([value for value in data[0].values()])
    lang_detect = detect(test)
    if lang_detect == "vi":
        with open(
            "backend/llm/vietnamese_stopwords.txt", "r", encoding="utf-8"
        ) as file:
            stopwords = set(file.read().splitlines())
    else:
        with open("backend/llm/english_stopwords.txt", "r") as file:
            stopwords = set(file.read().splitlines())
    if len(selected_columns) == 0:
        select_columns = list(data[0].keys())
    else:
        select_columns = selected_columns
    corpus = ""
    logger.info("Preprocessing data")
    for row in data:
        for key, val in row.items():
            row[key] = "" if val is None else val
            if key in select_columns:
                text = val
                text = text.lower()
                if len(regex_patterns) != 0:
                    text = remove_regex_patterns(text, regex_patterns)
                text = word_tokenize(text, format="text", fixed_words=fixed_words)
                text = text.translate(
                    str.maketrans("", "", """!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~""")
                )
                tokens = text.split()
                corpus += " ".join(tokens) + " "
    return corpus, stopwords
