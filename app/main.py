from tools import *
from agent_loop import run_agent
from constants import WORKSPACE_ROOT

def main():

    print(f"Workspace Root: {WORKSPACE_ROOT}")
    print("Launch the agent from the root directory of the project you want to work on.")
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
