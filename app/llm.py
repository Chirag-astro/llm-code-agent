import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)



def get_chat_response(messages,tools):


    chat = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages = messages,
            tools = tools
    )

    return chat