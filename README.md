# 🧮 MCP Calculator Server with CrewAI - Complete Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Setup Instructions](#setup-instructions)
5. [Understanding the Components](#understanding-the-components)
6. [Running the Application](#running-the-application)
7. [How It Works](#how-it-works)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

---

## 🎯 Overview

This project demonstrates how to integrate **Model Context Protocol (MCP)** with **CrewAI** to create AI agents that can perform mathematical calculations through a remote server. The system consists of:

- **MCP Calculator Server**: Provides calculator tools via SSE (Server-Sent Events) transport
- **CrewAI Agent**: Consumes MCP tools to perform calculations
- **SSE Protocol**: Enables real-time bidirectional communication

### What You'll Build
An AI-powered calculator system where CrewAI agents automatically discover and use calculator tools (add, subtract, multiply, divide) exposed by an MCP server.

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                              │
│              "Calculate 15 + 27 and multiply by 3"              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CrewAI System                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Calculator Agent (crew.py)                              │  │
│  │  • Receives user requests                                │  │
│  │  • Plans calculation steps                               │  │
│  │  • Uses MCPServerAdapter to access tools                 │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │  MCPServerAdapter (crewai_tools)                         │  │
│  │  • Connects to MCP server via SSE                        │  │
│  │  • Discovers available tools                             │  │
│  │  • Translates tool calls to MCP protocol                 │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         │ SSE Connection
                         │ (HTTP/SSE Transport)
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│               MCP Calculator Server                              │
│               (mcp_calculator_server.py)                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastMCP Server                                          │  │
│  │  • Exposes calculator tools via MCP protocol             │  │
│  │  • Handles SSE connections                               │  │
│  │  • Processes tool execution requests                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  🔧 Available Tools:                                             │
│     ├─ add_numbers(a, b)                                        │
│     ├─ subtract_numbers(a, b)                                   │
│     ├─ multiply_numbers(a, b)                                   │
│     └─ divide_numbers(a, b)                                     │
│                                                                   │
│  📡 Endpoints:                                                   │
│     ├─ GET  /sse              → SSE stream (responses)          │
│     └─ POST /messages → Tool calls (requests) │
└───────────────────────────────────────────────────────────────────┘
```
---
## 🔧 Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Operating System**: macOS, Linux, or Windows
- **Terminal**: Access to command line

### Required API Keys
- **OpenAI API Key**: Required for CrewAI agent (uses GPT models)
  - Get it from: https://platform.openai.com/api-keys
  - Or use alternative LLM providers (see Advanced Usage)

---

## 📦 Setup Instructions

### Step 1: Project Structure

Create the project directory:
```bash
mkdir -p ~/Desktop/AI-agent/calculater
cd ~/Desktop/AI-agent/calculater
```

Your project should have this structure:
```
calculater/
├── mcp_calculator_server.py    # MCP server with calculator tools
├── crew.py                      # CrewAI agent that uses MCP tools
├── interactive_calculator.py    # Interactive CLI version
├── requirements.txt             # Python dependencies
```

### Step 2: Create Virtual Environment

```bash
cd ~/Desktop/AI-agent/calculater

# Create virtual environment named 'vecal'
python3 -m venv vecal

# Activate it
source vecal/bin/activate

# Verify activation (you should see (vecal) in your prompt)
which python
# Should output: /Users/[username]/Desktop/AI-agent/calculater/vecal/bin/python
```

### Step 3: Install Dependencies

pip install -r requirements.txt


### Step 4: Set Up Environment Variables

Create `.env` file:
```bash
cat > .env << 'EOF'
# OpenAI API Key (required for CrewAI)
OPENAI_API_KEY=your-api-key-here

# Optional: Model configuration
OPENAI_MODEL_NAME=gpt-4o-mini

EOF
```

**Important**: Replace `your-api-key-here` with your actual OpenAI API key!

Load environment variables:
```bash
# Option 1: Export manually
export OPENAI_API_KEY="your-actual-api-key"

# Option 2: Use dotenv (automatically loaded by crew.py)
# Just make sure .env file exists with correct values
```

## 🎓 Understanding the Components

### Component 1: MCP Calculator Server

**File**: `mcp_calculator_server.py`

**Key Elements**:

1. **FastMCP Server Initialization**
```python
mcp = FastMCP("calculator-server")
```
Creates an MCP server instance.

2. **Tool Definitions**
```python
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```
Each function decorated with `@mcp.tool()` becomes an MCP tool.

3. **SSE Transport Setup**
```python
sse = SseServerTransport("/messages/")
```
Creates SSE transport that handles bidirectional communication.

4. **Route Configuration**
```python
routes=[
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse.handle_post_message),
]
```
- `/sse`: Client connects here to receive responses
- `/messages/`: Client posts tool execution requests here

### Component 2: CrewAI Agent

**File**: `crew.py`

**Key Elements**:

1. **MCPServerAdapter**
```python
with MCPServerAdapter(server_params) as tools:
```
Automatically:
- Connects to MCP server via SSE
- Discovers available tools
- Converts them to CrewAI-compatible tools

2. **Agent Definition**
```python
calculator_agent = Agent(
    role="Mathematical Calculator",
    goal="Perform calculations...",
    tools=tools,  # MCP tools injected here
    ...
)
```

3. **Task Definition**
```python
calculator_task = Task(
    description="Calculate X + Y...",
    agent=calculator_agent,
    ...
)
```

4. **Crew Execution**
```python
calculator_crew.kickoff()
```
Starts the agent, which automatically uses MCP tools as needed.
---

## 🚀 Running the Application

### Terminal Setup

You'll need **TWO terminal**:

#### Terminal 1: MCP Server

```bash
# Navigate to project directory
cd ~/Desktop/AI-agent/calculater

# Activate virtual environment
source vecal/bin/activate

# Start MCP server
python mcp_calculator_server.py
```

**Expected Output**:
```
======================================================================
🧮 MCP Calculator Server (SSE Transport)
======================================================================

✅ Using FastMCP with SSE over HTTP
📡 Server running on: http://localhost:8000

🔧 Available Tools:
  • add_numbers(a, b)
  • subtract_numbers(a, b)
  • multiply_numbers(a, b)
  • divide_numbers(a, b)

💡 This is a proper MCP server with SSE transport!
   Can be used with CrewAI MCPServerAdapter

Press Ctrl+C to stop
======================================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Server is ready when you see "Uvicorn running..."**

#### Terminal 2: CrewAI Agent

```bash
# Open NEW terminal tab/window
cd ~/Desktop/AI-agent/calculater

# Activate virtual environment
source vecal/bin/activate

# Set API key (if not in .env)
export OPENAI_API_KEY="your-api-key-here"

# Run CrewAI agent
python crew.py
```

**Expected Output**:
```
Available tools from MCP server: ['add_numbers', 'subtract_numbers', 'multiply_numbers', 'divide_numbers']

🚀 Starting calculation tasks...

[Agent: Mathematical Calculator]
[Task: Perform calculations...]

Working on: Add 15 and 27...
Using tool: add_numbers
Tool result: 42

Working on: Subtract 10 from 50...
Using tool: subtract_numbers
Tool result: 40

Working on: Multiply 8 by 6...
Using tool: multiply_numbers
Tool result: 48

Working on: Divide 100 by 4...
Using tool: divide_numbers
Tool result: 25.0

======================================================================
✨ FINAL RESULT
======================================================================
# Calculation Results

1. **Addition**: 15 + 27 = 42
2. **Subtraction**: 50 - 10 = 40
3. **Multiplication**: 8 × 6 = 48
4. **Division**: 100 ÷ 4 = 25.0

All calculations completed successfully!
======================================================================
```

### Interactive Mode

For an interactive calculator experience, create `interactive_calculator.py`:

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter

def run_interactive_calculator():
    server_params = {
        "url": "http://localhost:8000/sse",
        "transport": "sse" 
    }

    print("\n" + "="*70)
    print("🧮 Interactive Calculator Agent")
    print("="*70 + "\n")
    
    try:
        with MCPServerAdapter(server_params) as tools:
            calculator_agent = Agent(
                role="Mathematical Calculator Assistant",
                goal="Help users perform calculations using MCP calculator tools.",
                backstory="A friendly calculator AI with arithmetic capabilities.",
                tools=tools,
                reasoning=True,
                verbose=True,
            )

            while True:
                print("\n📝 Enter your calculation (or 'quit' to exit):")
                user_input = input("> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                if not user_input:
                    continue
                
                task = Task(
                    description=f"Calculate: {user_input}",
                    expected_output="The calculation result with explanation.",
                    agent=calculator_agent,
                )
                
                crew = Crew(
                    agents=[calculator_agent],
                    tasks=[task],
                    verbose=False,
                    process=Process.sequential
                )
                
                result = crew.kickoff()
                print(f"\n✨ Result: {result}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    run_interactive_calculator()
```

Run it:
```bash
python interactive_calculator.py
```

---

## 🔍 How It Works

### Complete Request Flow

Let's trace what happens when the agent calculates **15 + 27**:

#### 1. Initialization Phase

```python
# crew.py starts
with MCPServerAdapter(server_params) as tools:
```

**What happens**:
1. MCPServerAdapter connects to `http://localhost:8000/sse`
2. Server creates session: `session_id=abc-123`
3. Server sends: `data: /messages/?session_id=abc-123`
4. Adapter extracts session ID and keeps SSE connection open
5. Adapter requests tool list: `{"method": "tools/list"}`
6. Server returns: `["add_numbers", "subtract_numbers", ...]`
7. Adapter creates CrewAI tools from MCP tool schemas

#### 2. Agent Execution Phase

```python
calculator_crew.kickoff()
```

**What happens**:
1. CrewAI reads task description: "Add 15 and 27"
2. Agent (powered by GPT) decides to use `add_numbers` tool
3. Agent generates tool call: `add_numbers(a=15, b=27)`

#### 3. Tool Execution Phase

**In MCPServerAdapter**:
```python
# Adapter intercepts tool call
tool_call = {
    "name": "add_numbers",
    "arguments": {"a": 15, "b": 27}
}

# Converts to MCP protocol
mcp_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "add_numbers",
        "arguments": {"a": 15, "b": 27}
    }
}

# POSTs to /messages/?session_id=abc-123
response = requests.post(url, json=mcp_request)
```

**On Server Side**:
```python
# Server receives request at /messages/?session_id=abc-123
# Looks up session by ID
# Routes message through SSE transport streams
# Calls the actual Python function:
result = add_numbers(15, 27)  # Returns 42

# Sends result back via SSE stream
sse_response = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [{"type": "text", "text": "42"}]
    }
}
```

**Back in MCPServerAdapter**:
```python
# Listens on SSE stream
# Receives result: "42"
# Converts to CrewAI format
# Returns to agent
```

#### 4. Response Phase

```python
# Agent receives: 42
# Agent uses result to formulate answer
# Agent continues with next calculation
```

### Data Flow Diagram

```
User Input: "Add 15 and 27"
     ↓
CrewAI Agent (decides to use tool)
     ↓
MCPServerAdapter.add_numbers(15, 27)
     ↓
[Converts to JSON-RPC]
     ↓
POST /messages/?session_id=abc-123
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {"name": "add_numbers", "arguments": {"a": 15, "b": 27}}
}
     ↓
MCP Server receives & processes
     ↓
Python function: add_numbers(15, 27) → 42
     ↓
[Formats as MCP response]
     ↓
SSE Stream ══════════════════════════>
event: message
data: {"result": {"content": [{"text": "42"}]}}
     ↓
MCPServerAdapter receives via SSE
     ↓
[Extracts result: 42]
     ↓
Returns 42 to Agent
     ↓
Agent: "The sum of 15 and 27 is 42"
```

---

## 🐛 Troubleshooting

### Issue 1: Server Won't Start

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
# In mcp_calculator_server.py, change:
uvicorn.run(app, host="0.0.0.0", port=8001)
# And in crew.py:
"url": "http://localhost:8001/sse"
```

### Issue 2: CrewAI Can't Connect

**Error**: `Error connecting to Calculator MCP server`

**Checklist**:
```bash
# 1. Is server running?
curl http://localhost:8000/sse
# Should connect and stream data

# 2. Check server logs in Terminal 1
# Look for errors or connection attempts

# 3. Verify URL in crew.py
server_params = {
    "url": "http://localhost:8000/sse",  # Must match server port
    "transport": "sse"
}

# 4. Test server manually
curl -N http://localhost:8000/sse
# Should see: event: endpoint, data: /messages/?session_id=...
```

### Issue 3: Missing OpenAI API Key

**Error**: `OPENAI_API_KEY is required`

**Solution**:
```bash
# Option 1: Set in terminal
export OPENAI_API_KEY="sk-..."

# Option 2: Create .env file
echo 'OPENAI_API_KEY=sk-...' > .env

# Option 3: Use alternative LLM (see Advanced Usage)
```

### Issue 4: Tool Calls Fail

**Error**: `Invalid request parameters`

**Debug Steps**:
```bash
# 1. Check server logs for detailed error
# 2. Verify tool exists
curl http://localhost:8000/sse
# Wait for initialization, then check available tools

# 3. Test tool manually
# Get session ID from SSE connection, then:
curl -X POST "http://localhost:8000/messages/?session_id=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add_numbers",
      "arguments": {"a": 5, "b": 3}
    }
  }'
```

### Issue 5: Dependencies Not Found

**Error**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**:
```bash
# Ensure virtual environment is activated
source vecal/bin/activate

# Verify activation
which python
# Must show path to vecal/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import mcp; import crewai; print('All good!')"
```

---

## 📚 Summary

### What You Built

1. **MCP Calculator Server**: Exposes mathematical operations via standardized protocol
2. **CrewAI Integration**: AI agents automatically discover and use remote tools
3. **SSE Transport**: Efficient real-time communication between components

### Key Takeaways

✅ **MCP enables tool standardization** - Any client can use your calculator  
✅ **SSE provides real-time communication** - Low latency, persistent connections  
✅ **CrewAI makes AI agents easy** - Automatic tool discovery and usage  
✅ **Modular architecture** - Server and agents are independent  

### Next Steps

1. **Extend Tools**: Add more mathematical operations
2. **Build UI**: Create web interface for the calculator
3. **Deploy**: Host server on cloud platform
4. **Create More Servers**: Build MCP servers for other domains (weather, database, etc.)
5. **Combine Servers**: Use MCPServerAdapter to connect to multiple MCP servers

---

## 📖 Additional Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **FastMCP Documentation**: https://gofastmcp.com/
- **CrewAI Documentation**: https://docs.crewai.com/
- **SSE Specification**: https://html.spec.whatwg.org/multipage/server-sent-events.html

---
