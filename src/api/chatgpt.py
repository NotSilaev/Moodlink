import sys
sys.path.append('..')

from config import settings
from logs import addLog

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage


client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)


async def sendPromtMessages(messages: list[dict], max_tokens: int) -> ChatCompletionMessage:
    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        max_tokens=max_tokens
    )

    return completion.choices[0].message