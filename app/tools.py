import json
import subprocess
import os
from constants import MAX_SEARCH_RESULTS

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
        },

    "ListDirectory": {
        "type": "function",
        "function": {
            "name": "ListDirectory",
            "description": "List all files and directories in a given directory path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path whose contents should be listed"
                    }
                },
                "required": ["path"]
            }
        }
    },

    "Search":{
        "type": "function",
        "function": {
            "name": "Search",
            "description": "Search for a text string inside files under a directory and return matching file paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The text to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "The directory path to search in"
                    }
                },
                "required": ["query", "path"]
            }
        }
    },  
    "Edit": {
        "type": "function",
        "function": {
            "name": "Edit",
            "description": "Replace a specific piece of text in a file. Use this for modifying existing files instead of rewriting the entire file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to edit"
                    },
                    "old_block": {
                        "type": "string",
                        "description": "The exact block of text to replace. The text must match exactly and uniquely within the file"
                    },
                    "new_block": {
                        "type": "string",
                        "description": "The replacement block of text."
                    }
                },
                "required": [
                    "file_path",
                    "old_block",
                    "new_block"
                ]
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
    print("Executing:", command)
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


def listDirectory(messages, args, id):
     dir_args = json.loads(args)
     dir_path = dir_args["path"]
     dir_contents = []
     response = {
        "role": "tool",
        "tool_call_id": id,
        "content": [],
        }      

     try:
        for entry in os.listdir(dir_path):
            if os.path.isdir(entry):
                dir_contents.append(f"[DIR] {entry}")
            if os.path.isfile(entry):
                dir_contents.append(f"[FILE] {entry}")  

        response["content"] = dir_contents

     except Exception as e:
            response["content"] = repr(e)

     messages.append(response)

def search(messages, args, id):
     
     tool_args = json.loads(args)
     search_term = tool_args["query"].lower()
     path  = tool_args["path"]
     ignore_dirs = {'.git', '.venv', '__pycache__', 'node_modules', '.idea', 'build', 'dist'}
     results = []
     response = {
        "role": "tool",
        "tool_call_id": id,
        "content": "",
        }
     
     if not os.path.exists(path):
          response["content"] = f"Path does not exist: {path}"
          messages.append(response)
          return          
    #  print("Searching for:", search_term)
    #  print("Path:", path) 
     for root, dirs, files in os.walk(path):
          if len(results) >= MAX_SEARCH_RESULTS:
               break
          dirs[:] = [d for d in dirs if d not in ignore_dirs]   
          for file in files:
               if len(results) >= MAX_SEARCH_RESULTS:
                    break
               file_path = os.path.join(root,file)
               try:
                    with open(file_path, "r", errors= "ignore") as f:
                         content = f.read()
                         if '\0' in content:
                              continue
                         lines = content.splitlines()
                         for line_num,line in enumerate(lines,1):
                                if search_term in line.lower():
                                  results.append(f"{file_path} : {line_num} : {line}")
                                  if len(results) >= MAX_SEARCH_RESULTS:
                                       break

                                
               except Exception:
                    continue
    #  print("Matches found:", len(results))          
     combined_result = "\n".join(results)
    #  print(f"combined result{combined_result}")
     if results:
        response["content"] = combined_result
     else:    
        response["content"]= "No Matches Found"
     messages.append(response)   


def edit(messages, args, id):
     tool_args = json.loads(args)
     file_path = tool_args["file_path"]
     old_block = tool_args["old_block"]
     new_block = tool_args["new_block"]
     response = {
        "role": "tool",
        "tool_call_id": id,
        "content": "",
        }
     try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            cnt = content.count(old_block)
            if cnt == 1:
                content = content.replace(old_block,new_block,1)
                response["content"] = "Edit Successful. Replaced one occurrence"
                with open(file_path, "w",encoding="utf-8") as f1:
                     f1.write(content)

            elif cnt == 0:
                response["content"] = "Edit Failed: Block Not Found"

            else:
                response["content"] = f"Edit failed: block is not unique. Found {cnt} occurrences."    

     except Exception as e:
          response["content"] = repr(e)


               

                 

     messages.append(response)                    
               



tool_handler = {
     "Read" : read_file,
     "Write": write_file,
     "Bash":bash,
     "ListDirectory": listDirectory,
     "Search": search,
     "Edit": edit
}

