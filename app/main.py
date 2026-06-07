from llm import get_chat_response
from tools import *
from agent_loop import run_agent

def main():

    messages = []

    while True:

        user_input = input("> ")

        if not user_input.strip():
            continue

        if user_input.strip() == "exit-chat":
            exit()

        messages.append({"role":"user", "content": user_input})

        response = run_agent(messages)
        print(response)



if __name__ == "__main__":
    main()
