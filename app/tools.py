import json
import subprocess

tools_definition = {
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
    try:    
        with open(file_path, "r") as f:
            content = f.read()
            response = {
                "role": "tool",
                "tool_call_id": id,
                "content":  content
            }
    except Exception as e:
            response = {
                "role": "tool",
                "tool_call_id": id,
                "content":  repr(e)
            }
            
    messages.append(response)




def write_file(messages, args, id):
    file_args =  json.loads(args)
    file_path = file_args["file_path"]
    content = file_args["content"]
    try:
        with open(file_path, "w") as f:
            f.write(content)
            response = {
                "role": "tool",
                "tool_call_id": id,
                "content":  content
            }

    except Exception as e:
            response = {
                "role": "tool",
                "tool_call_id": id,
                "content":  repr(e)
            }

    messages.append(response)



def bash(messages, args, id):
    command_args = json.loads(args)
    command = command_args["command"]
    response = {
        "role": "tool",
        "tool_call_id": id,
        "content":  "",
        }  

    try:
    
        results =  subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
        ) 

        

        if results.stdout:
            response["content"] = results.stdout

        if results.stderr:
            response["content"] = results.stderr

    except Exception as e:
        response["content"] = repr(e)


    messages.append(response)        


tool_handler = {
     "Read" : read_file,
     "Write": write_file,
     "Bash":bash,
}

