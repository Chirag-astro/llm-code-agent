import os
from dotenv import load_dotenv
from openai import OpenAI
from constants import MODEL,SYSTEM_PROMPT

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)



def get_chat_response(messages,tools):

    messages_for_api = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + messages
    chat = client.chat.completions.create(
            model=MODEL,
            messages = messages_for_api,
            tools = tools
    )

    return chat