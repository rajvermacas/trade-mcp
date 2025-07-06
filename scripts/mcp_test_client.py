#!/usr/bin/env python3
"""
MCP Test Client for Trading MCP Server

This client mimics Claude Desktop's interaction with the Trading MCP server,
enabling rapid development and testing of MCP functions without needing Claude Desktop.

Usage:
    python scripts/mcp_test_client.py --interactive
    python scripts/mcp_test_client.py --test-all
    python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import argparse
from pathlib import Path

# Configure logging for test client
import os
log_level = os.getenv('TRADING_MCP_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enhanced logging for debugging MCP communication
logger.info(f"MCP Test Client starting with log level: {log_level}")


@dataclass
class MCPRequest:
    """MCP JSON-RPC 2.0 Request"""
    jsonrpc: str = "2.0"
    id: int = 0
    method: str = ""
    params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method
        }
        if self.params:
            result["params"] = self.params
        return result


@dataclass
class MCPResponse:
    """MCP JSON-RPC 2.0 Response"""
    jsonrpc: str
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """Create from dictionary"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id", 0),
            result=data.get("result"),
            error=data.get("error")
        )


class MCPTestClient:
    """
    MCP Test Client for communicating with Trading MCP server over stdio.
    
    This client implements the MCP protocol using JSON-RPC 2.0 over stdio transport,
    mimicking how Claude Desktop interacts with MCP servers.
    """
    
    def __init__(self, server_command: List[str], cwd: Optional[str] = None):
        """
        Initialize MCP test client.
        
        Args:
            server_command: Command to start the MCP server
            cwd: Working directory for server process
        """
        self.server_command = server_command
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.capabilities: Dict[str, Any] = {}
        self.tools: List[Dict[str, Any]] = []
        self.connected = False
        
    async def start(self) -> bool:
        """
        Start the MCP server process and establish connection.
        
        Returns:
            True if successfully connected, False otherwise
        """
        try:
            logger.info(f"Starting MCP server: {' '.join(self.server_command)}")
            
            # Start server process
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
                bufsize=1
            )
            
            # Initialize MCP connection
            await self.initialize()
            
            logger.info("MCP server started and initialized successfully")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            await self.close()
            return False
    
    async def initialize(self) -> None:
        """Initialize MCP connection with handshake"""
        # Send initialize request
        init_request = MCPRequest(
            id=self._next_id(),
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": False
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                }
            }
        )
        
        response = await self._send_request(init_request)
        if response.error:
            raise Exception(f"Initialization failed: {response.error}")
        
        # Store server capabilities
        self.capabilities = response.result.get("capabilities", {})
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self._send_notification(initialized_notification)
        
        # Get available tools
        await self._discover_tools()
        
        logger.info("MCP initialization completed")
    
    async def _discover_tools(self) -> None:
        """Discover available tools from the server"""
        tools_request = MCPRequest(
            id=self._next_id(),
            method="tools/list"
        )
        
        response = await self._send_request(tools_request)
        if not response.error:
            self.tools = response.result.get("tools", [])
            logger.info(f"Discovered {len(self.tools)} tools: {[t.get('name') for t in self.tools]}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.connected:
            raise Exception("MCP client not connected")
        
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        # Measure execution time
        start_time = time.time()
        
        tool_request = MCPRequest(
            id=self._next_id(),
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )
        
        response = await self._send_request(tool_request)
        
        execution_time = time.time() - start_time
        
        if response.error:
            logger.error(f"Tool call failed: {response.error}")
            return {
                "success": False,
                "error": response.error,
                "execution_time": execution_time
            }
        
        result = response.result
        result["execution_time"] = execution_time
        
        logger.info(f"Tool call completed in {execution_time:.2f}s")
        return result
    
    async def get_stock_chart_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """
        Test the get_stock_chart_data function.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            
        Returns:
            Stock chart data response
        """
        arguments = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval
        }
        
        return await self.call_tool("get_stock_chart_data", arguments)
    
    async def _send_request(self, request: MCPRequest) -> MCPResponse:
        """Send a JSON-RPC request and wait for response"""
        if not self.process:
            raise Exception("Server process not started")
        
        # Send request
        request_json = json.dumps(request.to_dict()) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Wait for response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise Exception("No response received from server")
        
        try:
            response_data = json.loads(response_line.strip())
            return MCPResponse.from_dict(response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    async def _send_notification(self, notification: Dict[str, Any]) -> None:
        """Send a JSON-RPC notification (no response expected)"""
        if not self.process:
            raise Exception("Server process not started")
        
        notification_json = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_json)
        self.process.stdin.flush()
    
    def _next_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def close(self) -> None:
        """Close the MCP connection and terminate server process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"Error closing server process: {e}")
            finally:
                self.process = None
        
        self.connected = False
        logger.info("MCP connection closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class TestScenarios:
    """Predefined test scenarios for stock data testing"""
    
    @staticmethod
    def get_basic_scenarios() -> List[Dict[str, Any]]:
        """Get basic test scenarios for stock data"""
        return [
            {
                "name": "RELIANCE Stock - Hourly Data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                }
            },
            {
                "name": "TCS Stock - Daily Data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-05",
                    "interval": "1d"
                }
            },
            {
                "name": "INFY Stock - 5-minute Data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INFY.NS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "5m"
                }
            },
            {
                "name": "Invalid Symbol Test",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INVALID_SYMBOL",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                }
            },
            {
                "name": "Invalid Date Range Test",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-02",
                    "end_date": "2024-01-01",
                    "interval": "1h"
                }
            }
        ]


async def run_test_scenario(client: MCPTestClient, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test scenario"""
    print(f"\n🧪 Running: {scenario['name']}")
    print(f"   Function: {scenario['function']}")
    print(f"   Args: {scenario['args']}")
    
    start_time = time.time()
    
    try:
        result = await client.call_tool(scenario['function'], scenario['args'])
        execution_time = time.time() - start_time
        
        # Extract key information
        success = result.get('content', [{}])[0].get('text', '{}')
        if isinstance(success, str):
            try:
                success_data = json.loads(success)
                is_success = success_data.get('success', False)
                data_points = len(success_data.get('data', []))
                
                if is_success:
                    print(f"   ✅ Success: {data_points} data points retrieved")
                    print(f"   ⏱️  Execution time: {execution_time:.2f}s")
                else:
                    print(f"   ❌ Failed: {success_data.get('error', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print(f"   ⚠️  Response parsing error")
        
        return {
            "scenario": scenario['name'],
            "success": True,
            "result": result,
            "execution_time": execution_time
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Exception: {e}")
        return {
            "scenario": scenario['name'],
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }


async def run_all_tests(project_root: Path) -> None:
    """Run all predefined test scenarios"""
    print("🚀 Starting MCP Test Client - All Tests")
    print("=" * 60)
    
    server_command = [
        "python", "-m", "trading_mcp.server"
    ]
    
    async with MCPTestClient(server_command, str(project_root)) as client:
        scenarios = TestScenarios.get_basic_scenarios()
        results = []
        
        for scenario in scenarios:
            result = await run_test_scenario(client, scenario)
            results.append(result)
            
            # Add delay between tests
            await asyncio.sleep(1)
        
        # Print summary
        print("\n📊 Test Results Summary")
        print("=" * 60)
        
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)
        avg_time = sum(r['execution_time'] for r in results) / len(results)
        
        print(f"Tests Passed: {successful_tests}/{total_tests}")
        print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
        print(f"Average Execution Time: {avg_time:.2f}s")
        
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['scenario']} ({result['execution_time']:.2f}s)")


async def run_single_test(project_root: Path, function: str, **kwargs) -> None:
    """Run a single test with specified parameters"""
    print(f"🧪 Testing {function} with parameters: {kwargs}")
    print("=" * 60)
    
    server_command = [
        "python", "-m", "trading_mcp.server"
    ]
    
    async with MCPTestClient(server_command, str(project_root)) as client:
        result = await client.call_tool(function, kwargs)
        
        print(f"Result: {json.dumps(result, indent=2)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Test Client for Trading MCP Server")
    parser.add_argument("--test-all", action="store_true", help="Run all predefined test scenarios")
    parser.add_argument("--function", help="Function to test")
    parser.add_argument("--symbol", help="Stock symbol")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--interval", default="1h", help="Time interval")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent
    
    if args.test_all:
        asyncio.run(run_all_tests(project_root))
    elif args.function:
        kwargs = {}
        if args.symbol:
            kwargs['symbol'] = args.symbol
        if args.start_date:
            kwargs['start_date'] = args.start_date
        if args.end_date:
            kwargs['end_date'] = args.end_date
        if args.interval:
            kwargs['interval'] = args.interval
            
        asyncio.run(run_single_test(project_root, args.function, **kwargs))
    elif args.interactive:
        print("Interactive mode - use scripts/interactive_client.py instead")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()