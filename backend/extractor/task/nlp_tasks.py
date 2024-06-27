import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from underthesea import word_tokenize
from backend.extractor.task.llm_utils import (
    draw_word_cloud,
    get_task_dict,
    llm_task,
    prepare_word_cloud,
)
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


async def llm_extract_task(
    data, llm_task_format, columns=None, batch_size=12, delay=65
):
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
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch number: {i + 1}")
        tasks = [llm_task(text, llm_task_format) for text in batch]
        try:
            batch_responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in batch_responses:
                if isinstance(response, Exception):
                    print("Successful response")
                    responses.append(response)
                    print(response)
                else:
                    print(response)
                    responses.append(response)
        except Exception as e:
            print(f"Error processing batch number: {i + 1}, Error: {e}")
            # If the whole batch fails, add empty responses for the entire batch
            # responses.extend([get_task_dict(llm_task_format) for _ in batch])
        finally:
            if i < len(batches) - 1:
                await asyncio.sleep(delay)
    return responses


def combine_res(data, responses, tasks):
    for record, response in zip(data, responses):
        if isinstance(response, dict):
            record.update(response)
        else:
            record.update(get_task_dict(tasks))
