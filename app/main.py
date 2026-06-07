import argparse
import os
import sys
import json
import subprocess
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")

Tools = {
    "Read": {
        "type": "function",
        "function": {
            "name": "Read",
            "description": "Read and return the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    },

    "Write": {
        "type": "function",
        "function": {
            "name": "Write",
            "description": "Write content to a file",
            "parameters": {
            "type": "object",
            "required": ["file_path", "content"],
            "properties": {
                "file_path": {
                "type": "string",
                "description": "The path of the file to write to"
                },
                "content": {
                "type": "string",
                "description": "The content to write to the file"
                }
            }
            }
        }
        }
        ,

    "Bash": {
        "type": "function",
        "function": {
            "name": "Bash",
            "description": "Execute a shell command",
            "parameters": {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {
                "type": "string",
                "description": "The command to execute"
                }
            }
            }
        }
        }    
}


def read_file(messages,args, id):
    file_args = json.loads(args)
    file_path = file_args["file_path"]
    with open(file_path, "r") as f:
        content = f.read()
        response = {
            "role": "tool",
            "tool_call_id": id,
            "content":  content
        }
        messages.append(response)

def write_file(messages, args, id):
    file_args =  json.loads(args)
    file_path = file_args["file_path"]
    content = file_args["content"]
    with open(file_path, "w") as f:
        f.write(content)
        response = {
            "role": "tool",
            "tool_call_id": id,
            "content":  content
        }
        messages.append(response)

def bash(messages, args, id):
    command_args = json.loads(args)
    command = command_args["command"]
    
    results =  subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
    ) 
    response = {
        "role": "tool",
        "tool_call_id": id,
        "content":  "",
        }  
     

    if results.stdout:
        response["content"] = results.stdout

    if results.stderr:
        response["content"] = results.stderr

    messages.append(response)        




def main():

    
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [{"role":"user", "content":args.p}]

    while True: 


        chat = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages = messages,
            tools = [Tools["Read"], Tools["Write"], Tools["Bash"]]
        )

        messages.append(chat.choices[0].message)

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")
        
        calls = chat.choices[0].message.tool_calls

        if not calls:
            if chat.choices[0].message.content:
                print(chat.choices[0].message.content)
            exit()

        for call in calls:
            call_type = call.function.name
            if call_type == "Read":
                read_file(messages,call.function.arguments,call.id)
            elif call_type == "Write":
                write_file(messages,call.function.arguments,call.id)  
            elif call_type == "Bash":
                bash(messages, call.function.arguments,call.id)      

                    

        # You can use print statements as follows for debugging, they'll be visible when running tests.
        # print("Logs from your program will appear here!", file=sys.stderr)

        # TODO: Uncomment the following line to pass the first stage
        # if chat.choices[0].message.content:
        #     print(chat.choices[0].message.content)


if __name__ == "__main__":
    main()
