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
    # print(prompt)
    parsed_response = json.loads(response)
    print(parsed_response)
    return parsed_response


def get_task_dict(task):
    res = {}
    for key in task.keys():
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
