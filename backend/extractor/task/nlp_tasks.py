import asyncio
import json
import uuid
from charset_normalizer import detect
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from underthesea import word_tokenize

# from backend.extractor.task.llm_utils import (
#     draw_word_cloud,
#     llm_task,
#     prepare_word_cloud,
# )
from backend.extractor.task.llm_utils import llm_task
from backend.logger import get_logger

logger = get_logger()


def create_word_cloud(
    data,
    colormap="viridis",
    background_color="white",
    max_words=200,
    selected_columns: list = None,
    regex_patterns=None,
    fixed_words=None,
    save=True,
):
    corpus, stopwords = prepare_word_cloud(
        data, selected_columns, regex_patterns, fixed_words
    )
    logger.info("done prepare")
    word_cloud, save_path = draw_word_cloud(
        corpus, stopwords, colormap, background_color, max_words, save
    )
    return save_path


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
        collocations=False,
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
    logger.info("Identifying language")
    test = "".join([value for value in data[0].values()])
    lang_detect = detect(str.encode(test))
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
                text = text.lower() if isinstance(text, str) else text
                if len(regex_patterns) != 0:
                    text = remove_regex_patterns(text, regex_patterns)
                text = word_tokenize(text, format="text", fixed_words=fixed_words)
                text = text.translate(
                    str.maketrans("", "", """!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~""")
                )
                tokens = text.split()
                corpus += " ".join(tokens) + " "
    return corpus, stopwords


async def llm_extract_task(
    data, llm_task_format, columns=None, batch_size=12, delay=65
):
    llm_task_json = json.dumps(llm_task_format)
    to_classify = []
    logger.info("Getting texts")
    if len(columns) == 0:
        selected_columns = list(data[0].keys())
    else:
        selected_columns = columns

    for row in data:
        text = "\n".join(value for key, value in row.items() if key in selected_columns)
        to_classify.append(text)

    def chunks(data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    batches = list(chunks(to_classify, batch_size))
    print(batches)
    responses = []
    print(llm_task_json)
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch number: {i + 1}")
        tasks = [llm_task(text, llm_task_json) for text in batch]
        try:
            batch_responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in batch_responses:
                responses.append(response)
        except Exception as e:
            print(f"Error processing batch number: {i + 1}, Error: {e}")
            # If the whole batch fails, add empty responses for the entire batch
            # responses.extend([get_task_dict(llm_task_format) for _ in batch])
        finally:
            if i < len(batches) - 1:
                await asyncio.sleep(delay)
    # print("from llm extract tag class ", responses)
    return responses


def combine_res(data, responses, tasks):
    for i, record in enumerate(data):
        record.update(responses[i])
    # for record, response in zip(data, responses):
    #     print("from combine_res", response, type(response))
    #     record.update(response)
    return data
