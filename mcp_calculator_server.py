"""
MCP Calculator Server with SSE Transport
Uses FastMCP with HTTP/SSE for CrewAI integration
"""

from mcp.server.fastmcp import FastMCP
import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import logging  
import asyncio

# Initialize MCP server
mcp = FastMCP("calculator-server")

#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("mcp-server")


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        The sum of a and b
    """
    logger.info(f"Tool called: add_numbers | a={a}, b={b}")
    result = a + b
    logger.info(f"Tool completed: add_numbers | result={result}")
    return result


@mcp.tool()
def subtract_numbers(a: int, b: int) -> int:
    """
    Subtract second number from first number.
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
    
    Returns:
        The difference of a - b
    """
    logger.info(f"Tool called: subtract_numbers | a={a}, b={b}")
    result = a - b
    logger.info(f"Tool completed: subtract_numbers | result={result}")
    return result


@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """
    Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        The product of a and b
    """
    logger.info(f"Tool called: multiply_numbers | a={a}, b={b}")
    result = a * b
    logger.info(f"Tool completed: multiply_numbers | result={result}")
    return result


@mcp.tool()
def divide_numbers(a: float, b: float) -> float:
    """
    Divide first number by second number.
    
    Args:
        a: Numerator
        b: Denominator
    
    Returns:
        The quotient of a / b
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    logger.info(f"Tool called: divide_numbers | a={a}, b={b}")
    result = a / b
    logger.info(f"Tool completed: divide_numbers | result={result}")
    return result


if __name__ == "__main__":
    print("="*70)
    print("🧮 MCP Calculator Server (SSE Transport)")
    print("="*70)
    print()
    print("✅ Using FastMCP with SSE over HTTP")
    print("📡 Server running on: http://localhost:8000")
    print()
    print("🔧 Available Tools:")
    print("  • add_numbers(a, b)")
    print("  • subtract_numbers(a, b)")
    print("  • multiply_numbers(a, b)")
    print("  • divide_numbers(a, b)")
    print()
    print("💡 This is a proper MCP server with SSE transport!")
    print("   Can be used with CrewAI MCPServerAdapter")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()
    
    # Create SSE transport
    sse = SseServerTransport("/messages/")
    
    # Create SSE endpoint
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp._mcp_server.run(
                streams[0], 
                streams[1], 
                mcp._mcp_server.create_initialization_options()
            )
        return Response()
    
    # Create Starlette app with SSE endpoint
    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
