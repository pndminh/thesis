import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from underthesea import word_tokenize
from backend.extractor.task.llm_utils import draw_word_cloud, prepare_word_cloud
from backend.logger import get_logger

logger = get_logger()


def create_word_cloud(
    data,
    selected_columns: list = None,
    regex_patterns=None,
    fixed_words=None,
    save=True,
):
    corpus, stopwords = prepare_word_cloud(
        data, selected_columns, regex_patterns, fixed_words
    )
    word_cloud, save_path = draw_word_cloud(corpus, stopwords, save)
    return word_cloud, save_path


async def llm_extract_task(
    data, extract_task, selected_columns=None, batch_size=10, delay=65
):
    to_classify = []
    logger.info("Getting texts")
    for row in data:
        text = "\n".join(value for key, value in row.items() if key in selected_columns)
        to_classify.append(text)

    def chunks(data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    batches = list(chunks(to_classify, 10))
    responses = []
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch number: {i + 1}")
        try:
            tasks = [extract_task(text) for text in batch]
            batch_responses = await asyncio.gather(*tasks)
            responses.extend(batch_responses)
            # logger.info([response] for response in responses)
        except Exception as e:
            logger.warning(e)
        finally:
            await asyncio.sleep(delay)
    return responses
