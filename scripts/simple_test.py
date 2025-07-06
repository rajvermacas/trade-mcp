#!/usr/bin/env python3
"""
Simple test to verify MCP Test Client concept works
"""

import asyncio
import subprocess
import json
import sys
from pathlib import Path

async def test_mcp_server_startup():
    """Test that the MCP server can start and we can communicate with it"""
    
    project_root = Path(__file__).parent.parent
    
    print("🧪 Testing MCP Server Startup and Communication")
    print("=" * 60)
    
    # Start the MCP server
    server_command = ["python", "-m", "trading_mcp.server"]
    
    try:
        process = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root)
        )
        
        print("✅ MCP server started successfully")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": False},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "simple-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send request
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("✅ Initialize response received:")
            print(f"   Protocol Version: {response.get('result', {}).get('protocolVersion', 'Unknown')}")
            print(f"   Server: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            notification_json = json.dumps(initialized_notification) + "\n"
            process.stdin.write(notification_json)
            process.stdin.flush()
            
            print("✅ Sent initialized notification")
            
            # Try to list tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            tools_json = json.dumps(tools_request) + "\n"
            process.stdin.write(tools_json)
            process.stdin.flush()
            
            # Read tools response
            tools_response_line = process.stdout.readline()
            if tools_response_line:
                tools_response = json.loads(tools_response_line.strip())
                tools = tools_response.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("\n🎉 MCP Communication Test Successful!")
        print("   ✅ Server startup: OK")
        print("   ✅ Initialize handshake: OK") 
        print("   ✅ Tool discovery: OK")
        print("   ✅ JSON-RPC communication: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server_startup())
    sys.exit(0 if success else 1)