#!/usr/bin/env python
"""Test server imports and initialization."""

import sys
import traceback

try:
    print("Testing imports...", file=sys.stderr)
    from trading_mcp.server import TradingMCPServer
    print("✓ Server import successful", file=sys.stderr)
    
    print("Creating server instance...", file=sys.stderr)
    server = TradingMCPServer()
    print("✓ Server instance created", file=sys.stderr)
    
    print("Testing tool setup...", file=sys.stderr)
    tools = server.get_tools()
    print(f"✓ Found {len(tools)} tools", file=sys.stderr)
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}", file=sys.stderr)
    
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("All tests passed!", file=sys.stderr)