# LLM-Code-Agent

A terminal-based AI coding agent built in Python using OpenRouter and tool calling.

The project implements the core architecture behind modern coding assistants: an LLM-driven agent loop capable of interacting with its environment through tools. The agent can reason about tasks, invoke tools when needed, process the results, and continue iterating until it produces a final response.

## Features

* Agent loop implementation
* OpenRouter integration
* Read tool (read file contents)
* Write tool (create and modify files)
* Bash tool (execute shell commands)
* Multi-step tool execution
* Conversation history management

## Architecture

The agent follows a simple reasoning cycle:

User Prompt → LLM → Tool Call → Tool Execution → Tool Result → LLM → Final Response

This allows the model to gather information, perform actions, and solve tasks that require multiple steps.

## Technologies

* Python
* OpenRouter API
* OpenAI Python SDK
* JSON-based tool calling

## Current Capabilities

* Inspect files in a project
* Create and update files
* Execute shell commands
* Handle multi-step workflows through an agent loop

## Roadmap

Planned improvements include:

* Search tool
* File editing tool
* Project-wide code search
* Long-term conversation memory
* Web search integration
* Better codebase understanding
* Additional developer-focused tools

## Motivation

This project was built to understand the internals of modern AI agents by implementing the core components from scratch instead of relying on higher-level frameworks. The focus is on learning how LLMs, tool calling, and agent loops work together to create autonomous coding assistants.
