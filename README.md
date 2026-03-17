# AI Agent Function Calling - Debug Challenge

## Overview

This project demonstrates an AI agent system built with OpenAI's function calling capabilities. The agent reads content from files, processes it, and writes summaries back to the filesystem. The system uses an asynchronous message broker pattern to handle communication between the AI agent and the terminal UI.

## Project Structure

```
AiInterviewProjectSample/
├── main.py                          # Application entry point
├── ai/
│   ├── openai_agent.py             # Core AI agent implementation
│   └── tool.py                     # Tool decorator for function metadata
├── middleware/
│   └── broker.py                   # Asynchronous message broker
├── terminal_ui/
│   └── format_agent_output.py      # Terminal output formatting
├── tooling/
│   └── common/
│       └── file_ops.py             # File operation tools
├── utils/
│   ├── logger_config.py            # Logging configuration
│   └── utils.py                    # Utility functions
└── resources/
    ├── input/                       # Input files for processing. Summary will written back to this directory
    ├── output/                      # Agent Histories output
    ├── prompt/
    │   └── summary_agent_prompt.md  # Agent instructions
    └── logs/                        # Application logs
```

## How It Works

1. **Agent Initialization**: The `SummaryAgent` is configured with:
   - OpenAI's `gpt-5.1-2025-11-13` model
   - Two file operation tools: `read_from_file` and `write_to_file`
   - Custom instructions from `summary_agent_prompt.md`

2. **Message Broker**: 
   - Agents communicate through an async message broker
   - Messages are consumed and displayed in the terminal with color-coded output
   - Supports function calls, results, reasoning, and text messages

3. **Function Calling Flow**:
   - Agent receives a prompt with a file location
   - Agent plans its approach and calls `read_from_file` to access content
   - Agent processes/summarizes the content
   - Agent calls `write_to_file` to save the summary
   - Results are logged and displayed in the terminal

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

## Setup

1. **Install uv** (if not already installed):
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository** and navigate to the project directory

3. **Create a `.env` file** in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   LOG_LEVEL=DEBUG
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

## Running the Project

```bash
uv run main.py
```

The agent will:
- Read the file at `resources/input/function_calling.md`
- Generate a summary
- Attempt to write the summary to `resources/output/function_calling_summary.md`

## Task #1: Debug the Agent

### Problem Statement

The AI agent is supposed to read a file, summarize its content, and write the summary to a new file. However, **the `write_to_file` function is not working correctly** with the agent.

When you run the project, you'll observe that:
- The agent successfully reads the input file
- The agent generates a summary
- **The agent fails to write the summary to the output file**

### Your Mission

1. **Run the project** and observe the behavior
2. **Review the logs** in `resources/logs/app.log` and terminal output
3. **Identify why** the `write_to_file` function call is failing
4. **Fix the bug** so that the agent can successfully write files
5. **Verify** that the summary file is created in the expected location

## Key Files to Review

1. **`ai/openai_agent.py`** - The main agent implementation

2. **`tooling/common/file_ops.py`** - The file operation tools
   - Review the `@tool` decorated functions
   - Verify both `read_from_file` and `write_to_file` are properly defined

3. **`main.py`** - Application entry point
   - See how the agent is configured with tools
   - Note which tools are passed to the agent

4. **`resources/logs/app.log`** - Runtime logs
   - Check for error messages
   - Track the flow of function calls

## Understanding the Code

### The @tool Decorator

Functions decorated with `@tool` automatically generate OpenAI function calling schema:

```python
@tool
def read_from_file(file_path: str) -> dict:
    """Read content from a file."""
    # Implementation
```

This creates `_tool_metadata` with JSON schema for OpenAI's function calling API.

### Agent Function Execution

The agent receives function call requests from OpenAI and dispatches them through the `_function_call` method. This is where the integration between the AI's function calls and actual Python function execution happens.

### Async Message Flow

```
Agent → Broker.put_threadsafe() → Queue → Consumer.get() → Terminal Display
```

All agent outputs (messages, function calls, reasoning) flow through the broker for consistent handling and display.

## Expected Output

When working correctly, you should see terminal output similar to:

```
[SummaryAgent] Planning approach...
[SummaryAgent ▶ function_call] read_from_file(file_path=resources/input/function_calling.md)
[SummaryAgent ✔ function_call_result] read_from_file -> status=success, file_contents=...
[SummaryAgent] Generating summary...
[SummaryAgent ▶ function_call] write_to_file(file_path=resources/output/function_calling_summary.md, content=...)
[SummaryAgent ✔ function_call_result] write_to_file -> status=success, message=Content written to...
[SummaryAgent] Summary successfully written to file.
```

## Task #2: Implement a New Tool

### Problem Statement

Now that you've fixed the `write_to_file` bug, let's extend the agent's capabilities by implementing a new tool. The agent currently can read and write individual files, but it cannot explore directories to discover what files are available.

### Your Task

Implement a `list_directory` tool that allows the agent to list files in a directory with optional filtering by file extension.

#### Requirements

1. **Function Signature** (already provided in `tooling/common/file_ops.py`):
   ```python
   @tool
   def list_directory(directory_path: str, file_extension: Optional[str] = None) -> dict:
       """
       List files in a directory, optionally filtered by extension.
       
       Args:
           directory_path (str): Path to the directory to list. Can be absolute or relative.
           file_extension (str, optional): Filter files by extension (e.g., ".md", ".txt"). 
                                          If None, return all files.
       
       Returns:
           dict: A dictionary containing:
               - "status" (str): "success" if the operation succeeded, "error" otherwise.
               - "files" (list[str]): List of filenames (not full paths) if successful.
               - "total_count" (int): Number of files found.
               - "directory_path" (str): The absolute path of the directory.
               - "message" (str): An error message if the operation failed.
       """
   ```

2. **Implementation Details**:
   - Use `pathlib.Path` for file system operations
   - Handle the case where the directory doesn't exist (return error status)
   - Handle the case where the path is a file, not a directory (return error)
   - Return only files, not subdirectories
   - If `file_extension` is provided, filter files (e.g., `".md"` should match `"file.md"`)
   - Return filenames only, not full paths
   - Use proper error handling with try/except
   - Follow the same logging pattern as `read_from_file` and `write_to_file`

3. **Integration Steps**:
   - Complete the implementation in `tooling/common/file_ops.py`
   - Add the tool to the agent in `main.py`:
     ```python
     tools = [read_from_file._tool_metadata, write_to_file._tool_metadata, list_directory._tool_metadata]
     ```
   - Register the function call handler in `ai/openai_agent.py`
   - Update the agent prompt to instruct it to list the `resources/input/` directory before processing

4. **Testing**:
   - Run the agent and verify it can list files in `resources/input/`
   - Test with a non-existent directory path
   - Test with filtering by `.md` extension
   - Check that the agent uses this information to decide which file to summarize

### Success Criteria

- The `list_directory` function is fully implemented with proper error handling
- The function is registered with the agent and can be called successfully
- The agent can list files in a directory and display the results
- Error cases (non-existent directory, not a directory) are handled gracefully
- The function follows the same patterns as existing tools (`read_from_file`, `write_to_file`)

### Example Usage

When working correctly, you should see output like:

```
[SummaryAgent ▶ function_call] list_directory(directory_path=resources/input, file_extension=.md)
[SummaryAgent ✔ function_call_result] list_directory -> status=success, files=['function_calling.md', 'function_calling_summary.md'], total_count=2
```

## Additional Notes

- The project uses Pydantic for data validation and serialization
- Logging is configured with context-aware adapters (see `utils/logger_config.py`)
- Color-coded terminal output can be disabled by setting `NO_COLOR=1` environment variable
- Agent conversation history is saved to `resources/output/` as JSON files
- When implementing new tools, always use the `@tool` decorator and follow the existing patterns for consistency
