# pygdbmi-mcp-server

English | [中文](README.md)

This is an MCP (Model Context Protocol) server developed based on [pygdbmi](https://github.com/cs01/pygdbmi), designed to invoke GDB for dynamic debugging via the MCP protocol.

Part of the code is referenced from [pwnomcp](https://github.com/pwno-io/pwno-mcp).

## Features

This server provides a set of MCP tools for interacting with GDB:

### Debug Control
- `execute`: Execute arbitrary GDB/pwndbg command.
- `run`: Run the loaded binary.
- `interrupt`: Interrupt the running inferior.
- `finish`: Run until the current function returns.
- `step_control`: Execute stepping commands (continue, next, step, nexti, stepi).

### File & Session Management
- `set_file`: Load a binary file for debugging.
- `set_poc_file`: Set the PoC file (passed to the binary via `set args`).
- `get_session_info`: Get current debugging session information.

### Breakpoint Management
- `set_breakpoint`: Set a breakpoint at the specified location.
- `list_breakpoints`: List all breakpoints.
- `delete_breakpoint`: Delete a breakpoint by number.
- `toggle_breakpoint`: Toggle a breakpoint's enabled/disabled state.

### State Inspection
- `get_context`: Get debugging context (registers, stack, disassembly, code, backtrace).
- `get_memory`: Read memory at the specified address.
- `disassemble`: Disassemble the specified address.

## Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/cnitlrt/pygdbmi-mcp-server
cd pygdbmi-mcp-server
```

### 2. Configure Environment

Create or modify the `.env` file in the project root directory to configure the server listening address and transport mode:

```bash
PORT=1111
HOST="0.0.0.0"
# TRANSPORT can be "sse" (Server-Sent Events) or "stdio" (Standard Input/Output)
# If unset, the server auto-selects stdio when stdin is non-interactive (e.g. Codex MCP).
TRANSPORT="sse"
```

### 3. Install Dependencies

This project recommends using `uv` for dependency management and environment configuration.

```bash
# Create virtual environment (Python 3.13 or higher recommended)
uv venv --python 3.13

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

# Install project and dependencies
uv pip install -e .
```

### 4. Run Server

```bash
uv run pygdbmi-mcp-server
```

You can also force the transport via CLI flags:

```bash
uv run pygdbmi-mcp-server --transport streamable-http
uv run pygdbmi-mcp-server --transport stdio
```

#### Remote access (SSE/HTTP)

Expose the server over the network with SSE:

```bash
uv run pygdbmi-mcp-server --transport sse --host 0.0.0.0 --port 1111
```

By default, the SSE endpoint is `/sse` and the message endpoint is `/messages/`,
so the remote URL is typically:

```
http://<server-ip>:1111/sse
http://<server-ip>:1111/mcp
```
