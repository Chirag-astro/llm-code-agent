import json
import subprocess
import os
from constants import MAX_DIFF_CHARS, MAX_SEARCH_RESULTS, WORKSPACE_ROOT, IGNORE_DIRS, MAX_DEPTH, GIT_ROOT
from pathlib import Path
import shutil
from datetime import datetime


tools_definition = {
    "Read": {
        "type": "function",
        "function": {
            "name": "Read",
            "description": (
                        "Read and return the contents of a file. "
                        "Use this when detailed file contents are required. "
                        "Prefer Search first when the file location is unknown."
                    ),
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
            "description": ("Create a new file or replace the entire contents of an existing file. "
            "Use this when creating a file from scratch, generating a new source file, "
            "or completely rewriting a file. Prefer Edit when modifying only part of an existing file."),
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
            "description": (
                    "Execute a shell command and return the exit code, stdout, and stderr. "
                    "Use this for compilation, testing, running programs, or shell operations "
                    "that cannot be performed using dedicated tools."
                ),
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
            "description": (
                    "Search for text, identifiers, functions, classes, variables, "
                    "configuration values, or code references across the workspace. "
                    "Prefer this tool before Read when locating code."
                ),
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
            "description": (
                    "Modify an existing file by replacing a specific block of text. "
                    "Use this for targeted changes to existing files. "
                    "Prefer Edit over Write when only part of a file should change."
                ),
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
    },

    "GetWorkspaceRoot": {
        "type": "function",
        "function": {
            "name": "GetWorkspaceRoot",
            "description": "Returns the root directory of the current workspace.",
            "parameters": {
            "type": "object",
            "properties": {}
            }
        }
        },

    "Tree": {
        "type": "function",
        "function": {
            "name": "Tree",
            "description": (
                "Returns the hierarchical structure of a directory and its "
                "subdirectories. Use this tool when you need to understand "
                "project structure, repository layout, file organization, or "
                "directory hierarchy. Prefer this tool over repeated "
                "ListDirectory calls when a recursive view is needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "The root directory whose structure should be displayed."
                        )
                    }
                },
                "required": [
                    "path"
                ]
            }
        }
    },

    # "Undo": {
    #     "type": "function",
    #     "function": {
    #         "name": "Undo",
    #         "description": (
    #             "Restore a file from its most recent backup. "
    #             "Use this tool when the user wants to undo, revert, "
    #             "or roll back the latest change made to a file."
    #         ),
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "file_path": {
    #                     "type": "string",
    #                     "description": (
    #                         "Path of the file whose most recent change "
    #                         "should be undone."
    #                     )
    #                 }
    #             },
    #             "required": [
    #                 "file_path"
    #             ]
    #         }
    #     }
    # },
    # 
    "GitStatus": {
        "type": "function",
        "function": {
            "name": "GitStatus",
            "description": (
                "Show the current git repository status. "
                "Returns modified files, staged files, deleted files, "
                "untracked files, branch information, and whether there "
                "are uncommitted changes. Use this whenever the user asks "
                "about repository state, changed files, pending changes, "
                "working tree status, staged files, branch status, or "
                "uncommitted work."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }, 

    "GitDiff": {
        "type": "function",
        "function": {
            "name": "GitDiff",
            "description": (
                "Show the git diff for the repository or for a specific file. "
                "Returns the exact modifications that have not yet been committed. "
                "Use this when the user asks what changed, wants to inspect "
                "modifications, review edits, explain a diff, or see changes "
                "made to a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Optional. Restrict the diff to a specific file."
                        )
                    }
                }
            }
        }
    },

    "GitCommit": {
        "type": "function",
        "function": {
            "name": "GitCommit",
            "description": (
                "Create a git commit. "
                "Before using this tool, verify any code changes when practical. "
                "If compilation, tests, or verification fail, fix the issues before committing. "
                "By default all modified, staged, "
                "deleted, and untracked files are committed. "
                "Optionally commit only a specific set of files. "
                "Use this when the user asks to commit changes, create "
                "a commit, save work in git, or record modifications "
                "in the repository."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": (
                            "The commit message to use."
                        )
                    },
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": (
                            "Optional list of files to commit. "
                            "If omitted or empty, all repository "
                            "changes will be committed."
                        )
                    }
                },
                "required": [
                    "message"
                ]
            }
        }
    },            
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
    file_args = json.loads(args)

    file_path = file_args["file_path"]
    content = file_args["content"]

    response = {
        "role": "tool",
        "tool_call_id": id,
        "content": ""
    }

    try:
        backup_created = False

        if os.path.exists(file_path):
            create_backup(file_path)
            backup_created = True

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        if backup_created:
            response["content"] = (
                "Write successful. Backup created."
            )
        else:
            response["content"] = (
                "Write successful. New file created."
            )

    except Exception as e:
        response["content"] = (
            f"Write failed: {repr(e)}"
        )

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
            timeout = 15,
        ) 

        
        output = []

        if results.stdout:
            output.append("STDOUT:\n" + results.stdout)

        if results.stderr:
            output.append("STDERR:\n" + results.stderr)

        if not output:
            output_text = "Command completed successfully."
        else:
            output_text = "\n\n".join(output) 

        response["content"] = (
            f"Exit Code: {results.returncode}\n\n"
            + output_text
        )

    except subprocess.TimeoutExpired:
        response["content"] = ("Command timed out after 15 seconds."
                               "The process may be interactive or long-running.")

    except Exception as e:
        response["content"] = f"Command failed: {repr(e)}"


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
          dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]   
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
        "content": ""
    }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        cnt = content.count(old_block)

        if cnt == 0:
            response["content"] = (
                "Edit failed: block not found."
            )

        elif cnt > 1:
            response["content"] = (
                f"Edit failed: block is not unique. Found {cnt} occurrences."
            )

        else:
            create_backup(file_path)

            updated_content = content.replace(
                old_block,
                new_block,
                1
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            response["content"] = (
                "Edit successful. Replaced one occurrence. Backup created."
            )

    except Exception as e:
        response["content"] = (
            f"Edit failed: {repr(e)}"
        )

    messages.append(response)


def getworkspaceroot(messages, args, id):
     response = {
        "role": "tool",
        "tool_call_id": id,
        "content": WORKSPACE_ROOT,
        }
     messages.append(response)


def tree(messages, args, id):
        dir_args = json.loads(args)
        dir_path = dir_args["path"]
        base_path = Path(dir_path).resolve()
        tree_dict = tree_helper(dir_path, base_path)
        response = {
            "role": "tool",
            "tool_call_id": id,
            "content": json.dumps(tree_dict, indent=4),
            }
        
        messages.append(response)


def tree_helper(current_path, base_path, depth = 0):

     current_path = Path(current_path).resolve()   
     structure = {
                "name": current_path.name,
                "type": "directory" if current_path.is_dir() else "file",
                "path": str(current_path.relative_to(base_path))
            }
     
     if current_path.is_dir() and depth >= MAX_DEPTH:
          structure["truncated"] = True
          return structure
     
     if current_path.is_dir():
          structure["children"] = []
          try:
            for entry in current_path.iterdir():
                entry = entry.resolve()
                if entry.name in IGNORE_DIRS:
                        continue
                if entry.is_dir():
                    structure["children"].append(tree_helper(entry, base_path ,depth+1))

                else:
                    structure["children"].append({
                            "name" : entry.name,
                            "type": "file",
                            "path" : str(entry.relative_to(base_path))
                                })
          except Exception as e:
               structure["error"] = repr(e)         

     return structure   


def create_backup(file_path):
    file_name = Path(file_path).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = (
        Path(WORKSPACE_ROOT)
        / ".backups"
        / f"{file_name}.{timestamp}.bak"
    )
    backup_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

    shutil.copy2(file_path, backup_path)

    return backup_path

# TODO:
# Undo currently behaves as "restore latest backup".
# Proper Undo/Redo requires history tracking and version pointers.
# Revisit in a future milestone.
# def undo(messages, args, id):
#     file_args = json.loads(args)
#     file_path = file_args["file_path"]
#     file_name = Path(file_path).name
#     backup_dir = Path(WORKSPACE_ROOT) / ".backups"
#     search_pattern = f"{file_name}.*.bak"
#     matches = list(backup_dir.glob(search_pattern))

#     response = {
#         "role": "tool",
#         "tool_call_id": id,
#         "content": "",
#         }

#     if not matches:
#         response["content"] = (
#             f"No backups found for {file_name}"
#         )
#         messages.append(response)
#         return    

#     latest_backup = max(
#         matches,
#         key=lambda p: p.stat().st_mtime
#     )

#     try:
#         create_backup(file_path)
#         shutil.copy2(latest_backup, file_path)
#         response["content"] = f"Success: Restored {file_name} from {latest_backup.name}"

#     except Exception as e:
#         response["content"]= f"Failed to restore file. Error: {repr(e)}"


#     messages.append(response)   
# 

def git_status(messages, args, id):
    response = {
        "role": "tool",
        "tool_call_id": id,
        "content": ""
            }
    
    if GIT_ROOT is None:
        response["content"] = (
            "No git repository found inside workspace."
        )
        messages.append(response)
        return
    
    try:
        results = subprocess.run(
            ["git","status", "-sb"],
            cwd= GIT_ROOT,
            text=True,
            capture_output=True,
            timeout= 15
        )

        output = []

        if results.stdout:
            output.append("STDOUT:\n" + results.stdout)

        if results.stderr:
            output.append("STDERR:\n" + results.stderr)

        if not output:
            output_text = "Working tree clean."
        else:
            output_text = "\n\n".join(output) 

        response["content"] = (
            f"Exit Code: {results.returncode}\n\n"
            + output_text
        )

    except Exception as e:
        response["content"] = f"Failed to Execute Git Status: {repr(e)}"  

    messages.append(response)

def git_diff(messages, args, id):

    response = {
        "role": "tool",
        "tool_call_id": id,
        "content": ""
            }   
    
    tool_args = json.loads(args)

    file_path = tool_args.get("file_path")

    cmd = ["git", "diff"]

    if file_path:
        cmd.extend(["--", file_path])    

    if GIT_ROOT is None:
        response["content"] = (
            "No git repository found inside workspace."
        )
        messages.append(response)
        return

    try:
        results = subprocess.run(
            cmd,
            cwd=GIT_ROOT,
            text=True,
            capture_output=True,
            timeout=15,
        )

        output = []

        diff_text = results.stdout

        if diff_text:
            if len(diff_text) > MAX_DIFF_CHARS:
                    diff_text = (
                        diff_text[:MAX_DIFF_CHARS]
                        + "\n\n[Diff truncated]"
                    )
            output.append("STDOUT:\n" + diff_text)        

        if results.stderr:
            output.append("STDERR:\n" + results.stderr)

        if not output:
            output_text = "No changes detected."
        else:
            output_text = "\n\n".join(output) 

        response["content"] = (
            f"Exit Code: {results.returncode}\n\n"
            + output_text
        )

    except Exception as e:
        response["content"] =   f"Failed to Execute git diff: {repr(e)}" 

    messages.append(response)  

def git_commit(messages, args, id):

    response = {
        "role": "tool",
        "tool_call_id": id,
        "content": ""
    }

    if GIT_ROOT is None:
        response["content"] = (
            "No git repository found inside workspace."
        )
        messages.append(response)
        return

    try:
        tool_args = json.loads(args)

        file_list = tool_args.get("files", [])
        commit_message = tool_args["message"]

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=GIT_ROOT,
            text=True,
            capture_output=True,
            timeout=15,
        )

        if not status.stdout.strip():
            response["content"] = (
                "Nothing to commit. Working tree clean."
            )
            messages.append(response)
            return

        if file_list:
            add_cmd = ["git", "add"] + file_list
        else:
            add_cmd = ["git", "add", "-A"]

        add_result = subprocess.run(
            add_cmd,
            cwd=GIT_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )

        if add_result.returncode != 0:
            response["content"] = (
                f"git add failed.\n\n"
                f"Exit Code: {add_result.returncode}\n\n"
                f"{add_result.stderr}"
            )
            messages.append(response)
            return

        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=GIT_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )

        output = []

        if commit_result.stdout:
            output.append(
                "STDOUT:\n" + commit_result.stdout
            )

        if commit_result.stderr:
            output.append(
                "STDERR:\n" + commit_result.stderr
            )

        output_text = (
            "\n\n".join(output)
            if output
            else "Commit completed successfully."
        )

        response["content"] = (
            f"Exit Code: {commit_result.returncode}\n\n"
            + output_text
        )

    except Exception as e:
        response["content"] = (
            f"Failed to execute git commit: {repr(e)}"
        )

    messages.append(response)
     


tool_handler = {
     "Read" : read_file,
     "Write": write_file,
     "Bash":bash,
     "ListDirectory": listDirectory,
     "Search": search,
     "Edit": edit,
     "GetWorkspaceRoot": getworkspaceroot,
     "Tree" : tree,
     "GitStatus": git_status,
     "GitDiff": git_diff,
     "GitCommit": git_commit,
}

