from constants import MAX_STEPS
from tools import *
from llm import get_chat_response

def run_agent(messages):
    steps = 0
    while True: 

        steps += 1
        if steps > MAX_STEPS:
            return "Agent stopped: maximum number of steps exceeded."

        chat = get_chat_response(messages, tools=list(tools_definition.values()))


        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")
        
        messages.append(chat.choices[0].message)
            
        calls = chat.choices[0].message.tool_calls

        if not calls:
            if chat.choices[0].message.content:
                return(chat.choices[0].message.content)
            
            return ""

        for call in calls:
            call_type = call.function.name
            print("Tool requested:", call_type)
            print("arguments: " , call.function.arguments)
            tool_handler[call_type](messages,call.function.arguments,call.id)