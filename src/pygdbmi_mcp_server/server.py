# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
from functools import wraps
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.prompts import base
from mcp.server.session import ServerSession

from .helper import PwndbgTools

logger = logging.getLogger(__name__)

load_dotenv()

# Some codes are referenced from https://github.com/pwno-io/pwno-mcp


def catch_errors(tuple_on_error: bool = False):
    """Decorator to standardize exception handling for GDB-related MCP tools."""

    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                logger.exception("tool error in {}", fn.__name__)
                if tuple_on_error:
                    return {
                        "success": False,
                        "error": str(e),
                        "type": type(e).__name__,
                    }, []
                return {"success": False, "error": str(e), "type": type(e).__name__}

        return wrapper

    return decorator


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 1111

mcp = FastMCP(
    "GDB MCP Server",
    port=int(os.getenv("PORT", str(DEFAULT_PORT))),
    host=os.getenv("HOST", DEFAULT_HOST),
)
session_dict: Dict[ServerSession, PwndbgTools] = {}


async def get_unit_session(session: ServerSession):
    if session not in session_dict:
        logger.info("{} not in session_dict, Please set_file first.", session)
        return None
    return session_dict[session]


@mcp.tool()
@catch_errors()
async def execute(command: str, context: Context) -> Dict[str, Any]:
    """
    Execute arbitrary GDB/pwndbg command.

    :param command: GDB command to execute
    :returns: Command output and state information
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.execute(command)


@mcp.tool()
@catch_errors()
async def set_file(binary_path: str, context: Context) -> Dict[str, Any]:
    """
    Load a binary file for debugging.

    :param binary_path: Path to the binary to load
    :returns: Loading status and binary information
    """
    if context.session not in session_dict:
        logger.info("create new session...")
        session_dict[context.session] = PwndbgTools()
    pwndbg_tools = session_dict[context.session]
    return pwndbg_tools.set_file(binary_path)


@mcp.tool()
@catch_errors()
async def set_poc_file(poc_file_path: str, context: Context) -> Dict[str, Any]:
    """
    Use `set args poc_file` to set the proof-of-concept (PoC) file for the loaded binary.

    :param poc_file_path: Path to the PoC file to set
    :returns: Status of the operation
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.set_poc_file(poc_file_path)


@mcp.tool()
@catch_errors()
async def run(
    args: str = "", start: bool = False, context: Context = None
) -> Dict[str, Any]:
    """
    Run the loaded binary.

    Requires at least one enabled breakpoint to be set before running.

    :param args: Arguments to pass to the binary
    :param start: Optional - stop at program entry (equivalent to --start)
    :returns: Execution results and state
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.run(args, start)


@mcp.tool()
@catch_errors()
async def step_control(command: str, context: Context) -> Dict[str, Any]:
    """
    Execute stepping commands (continue, next, step, nexti, stepi).

    :param command: Stepping command (c, n, s, ni, si or full name)
    :returns: Execution results and new state
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.step_control(command)


@mcp.tool()
@catch_errors()
async def finish(context: Context) -> Dict[str, Any]:
    """
    Run until the current function returns.

    :returns: Execution results and new state
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.finish()


@mcp.tool()
@catch_errors()
async def get_context(
    context_type: str = "all", context: Context = None
) -> Dict[str, Any]:
    """
    Get debugging context (registers, stack, disassembly, code, backtrace).

    :param context_type: Type of context (all, regs, stack, disasm, code, backtrace)
    :returns: Requested context information
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.get_context(context_type)


@mcp.tool()
@catch_errors()
async def set_breakpoint(
    location: str, condition: Optional[str] = None, context: Context = None
) -> Dict[str, Any]:
    """
    Set a breakpoint at the specified location.

    :param location: Address or symbol for breakpoint
    :param condition: Optional breakpoint condition
    :returns: Breakpoint information
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.set_breakpoint(location, condition)


@mcp.tool()
@catch_errors()
async def list_breakpoints(context: Context = None) -> Dict[str, Any]:
    """
    List all breakpoints.

    :returns: List of breakpoints
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.list_breakpoints()


@mcp.tool()
@catch_errors()
async def delete_breakpoint(number: int, context: Context = None) -> Dict[str, Any]:
    """
    Delete a breakpoint by number.

    :param number: Breakpoint number to delete
    :returns: Deletion status
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.delete_breakpoint(number)


@mcp.tool()
@catch_errors()
async def toggle_breakpoint(
    number: int, enable: bool, context: Context = None
) -> Dict[str, Any]:
    """
    Toggle a breakpoint's state.

    :param number: Breakpoint number to toggle
    :param enable: New enabled state
    :returns: Toggled breakpoint information
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.toggle_breakpoint(number, enable)


@mcp.tool()
@catch_errors()
async def get_memory(
    address: str, size: int = 64, format: str = "hex", context: Context = None
) -> Dict[str, Any]:
    """
    Read memory at the specified address.

    :param address: Memory address to read
    :param size: Number of bytes to read
    :param format: Output format (hex, string, int)
    :returns: Memory contents in the requested format
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.get_memory(address, size, format)


@mcp.tool()
@catch_errors()
async def disassemble(address: str, context: Context = None) -> Dict[str, Any]:
    """
    Disassemble the specified address.

    :param address: Address to disassemble
    :returns: Disassembly of the specified address
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.disassemble(address)


@mcp.tool()
@catch_errors()
async def get_session_info(context: Context = None) -> Dict[str, Any]:
    """
    Get current debugging session information.

    :returns: Session state and debugging artifacts
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.get_session_info()

@mcp.tool()
@catch_errors()
async def interrupt(context: Context = None) -> Dict[str, Any]:
    """
    Interrupt the running inferior.

    :returns: Interrupt status and debugging artifacts
    """
    pwndbg_tools = await get_unit_session(context.session)
    if pwndbg_tools is None:
        return {"success": False, "error": "Please set_file first."}
    return pwndbg_tools.interrupt()


def _resolve_transport(cli_transport: str | None) -> str:
    if cli_transport:
        return cli_transport
    env_transport = os.getenv("MCP_TRANSPORT") or os.getenv("TRANSPORT")
    if env_transport:
        return env_transport
    # If running under a parent process (e.g., Codex MCP), default to stdio.
    if not sys.stdin.isatty():
        return "stdio"
    return "sse"


def main():
    parser = argparse.ArgumentParser(description="pygdbmi MCP server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio", "streamable-http"],
        help="Transport to use for MCP (default: auto-detect)",
    )
    parser.add_argument("--stdio", action="store_true", help="Alias for --transport stdio")
    parser.add_argument("--sse", action="store_true", help="Alias for --transport sse")
    parser.add_argument(
        "--mount-path",
        default=os.getenv("MOUNT_PATH", None),
        help="Mount path prefix for SSE (e.g. /mcp).",
    )
    parser.add_argument(
        "--sse-path",
        default=os.getenv("SSE_PATH", None),
        help="SSE endpoint path (default: /sse).",
    )
    parser.add_argument(
        "--message-path",
        default=os.getenv("MESSAGE_PATH", None),
        help="POST message endpoint path (default: /messages/).",
    )
    parser.add_argument(
        "--streamable-http-path",
        default=os.getenv("STREAMABLE_HTTP_PATH", None),
        help="Streamable HTTP endpoint path (default: /mcp).",
    )
    parser.add_argument("--host", default=os.getenv("HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", str(DEFAULT_PORT))))

    args = parser.parse_args()
    if args.stdio:
        args.transport = "stdio"
    if args.sse:
        args.transport = "sse"

    transport = _resolve_transport(args.transport)
    # Keep host/port updated for HTTP transports when args override env defaults.
    if transport in ("sse", "streamable-http"):
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        if args.sse_path:
            mcp.settings.sse_path = args.sse_path
        if args.message_path:
            mcp.settings.message_path = args.message_path
        if args.streamable_http_path:
            mcp.settings.streamable_http_path = args.streamable_http_path

    if transport == "sse":
        mcp.run(transport=transport, mount_path=args.mount_path)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
