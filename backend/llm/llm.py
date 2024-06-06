from abc import ABC, abstractmethod
import google.generativeai as genai
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from IPython.display import Markdown
import textwrap

load_dotenv()


def to_gpt_message_template(content, role="system"):
    return [{"content": content, "role": role}]


def to_gemini_message_template(parts, role="system"):
    return [{"parts": [parts], "role": role}]


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class LLM:
    # /https://ai.google.dev/gemini-api/docs/get-started/python
    def __init__(
        self,
        top_p=0.1,
        top_k=40,
        temperature=0.1,
        max_output_tokens=4096,
        system_instruction=None,
        **args,
    ):
        self.top_p = top_p
        self.top_k = top_k
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.system_instruction = system_instruction
        configs = {
            "top_p": self.top_p,
            "top_k": self.top_k,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            **args,
        }
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=configs,
        )

    async def generate(self, prompt: str) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text

    def chat_complete(self, message, history=[]):
        chat = [*history]
        chat.append(to_gemini_message_template(message))
        return self.model.generate_content(history).text

    def get_usage(self, message):
        return self.model.count_tokens(message)

    def to_markdown(self, text):
        text = text.replace("•", "  *")
        return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))

    def function_calling(self, prompt, function_schema):
        response = self.model.generate_content(
            to_gemini_message_template(prompt),
            tools=[function_schema],
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=self.max_output_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            ),
        )
        return response.candidates[0].content

    def get_function_args(self, response):
        params = {}
        for key, value in response.parts[0].function_call.args.items():
            params[key[9:]] = value

        return params
