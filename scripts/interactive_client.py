#!/usr/bin/env python3
"""
Interactive MCP Test Client for Trading MCP Server

This provides an interactive command-line interface for testing MCP functions
during development. It allows manual testing, debugging, and exploration of
the Trading MCP server functionality.

Usage:
    python scripts/interactive_client.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_test_client import MCPTestClient, TestScenarios


class InteractiveMCPClient:
    """Interactive CLI for MCP Testing"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.client: Optional[MCPTestClient] = None
        self.connected = False
        
    async def start(self) -> bool:
        """Start the MCP client connection"""
        server_command = ["python", "-m", "trading_mcp.server"]
        
        try:
            self.client = MCPTestClient(server_command, str(self.project_root))
            success = await self.client.start()
            self.connected = success
            return success
        except Exception as e:
            print(f"❌ Failed to start MCP client: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the MCP client connection"""
        if self.client:
            await self.client.close()
            self.connected = False
    
    def print_welcome(self) -> None:
        """Print welcome message and available commands"""
        print("🚀 Interactive MCP Test Client for Trading MCP Server")
        print("=" * 60)
        print("Available Commands:")
        print("  1. Test stock data retrieval")
        print("  2. Run predefined test scenarios")
        print("  3. Show server capabilities")
        print("  4. Show available tools")
        print("  5. Custom tool call")
        print("  6. Performance benchmark")
        print("  h. Show this help")
        print("  q. Quit")
        print("=" * 60)
    
    def print_tools(self) -> None:
        """Print available tools"""
        if not self.client or not self.client.tools:
            print("❌ No tools available")
            return
        
        print("\n🔧 Available Tools:")
        print("-" * 40)
        
        for tool in self.client.tools:
            print(f"📊 {tool.get('name', 'Unknown')}")
            print(f"   Description: {tool.get('description', 'No description')}")
            
            # Show input schema
            schema = tool.get('inputSchema', {})
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            if properties:
                print("   Parameters:")
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    is_required = param_name in required
                    req_marker = " (required)" if is_required else " (optional)"
                    print(f"     • {param_name} ({param_type}){req_marker}: {param_desc}")
            print()
    
    def print_capabilities(self) -> None:
        """Print server capabilities"""
        if not self.client:
            print("❌ Client not connected")
            return
        
        print("\n⚙️  Server Capabilities:")
        print("-" * 40)
        print(json.dumps(self.client.capabilities, indent=2))
        print()
    
    async def test_stock_data(self) -> None:
        """Interactive stock data testing"""
        print("\n📈 Stock Data Testing")
        print("-" * 40)
        
        # Get input parameters
        symbol = input("Enter stock symbol (e.g., RELIANCE, TCS.NS): ").strip()
        if not symbol:
            print("❌ Symbol is required")
            return
        
        start_date = input("Enter start date (YYYY-MM-DD, e.g., 2024-01-01): ").strip()
        if not start_date:
            print("❌ Start date is required")
            return
        
        end_date = input("Enter end date (YYYY-MM-DD, e.g., 2024-01-02): ").strip()
        if not end_date:
            print("❌ End date is required")
            return
        
        interval = input("Enter interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo) [default: 1h]: ").strip()
        if not interval:
            interval = "1h"
        
        print(f"\n🔄 Fetching data for {symbol} from {start_date} to {end_date} with {interval} interval...")
        
        try:
            result = await self.client.get_stock_chart_data(symbol, start_date, end_date, interval)
            
            # Format and display result
            self.format_stock_result(result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def format_stock_result(self, result: Dict[str, Any]) -> None:
        """Format and display stock data result"""
        print("\n📊 Result:")
        print("-" * 40)
        
        # Extract content from MCP response
        content = result.get('content', [])
        if not content:
            print("❌ No content in response")
            return
        
        # Parse the text content
        text_content = content[0].get('text', '{}')
        try:
            data = json.loads(text_content) if isinstance(text_content, str) else text_content
        except json.JSONDecodeError:
            print(f"❌ Failed to parse response: {text_content}")
            return
        
        # Display results
        if data.get('success', False):
            print("✅ Success!")
            
            # Show metadata
            metadata = data.get('metadata', {})
            print(f"   Symbol: {metadata.get('symbol', 'N/A')}")
            print(f"   Data Points: {len(data.get('data', []))}")
            print(f"   Interval: {metadata.get('interval', 'N/A')}")
            print(f"   Date Range: {metadata.get('start_date', 'N/A')} to {metadata.get('end_date', 'N/A')}")
            
            # Show execution time
            exec_time = result.get('execution_time', 0)
            print(f"   Execution Time: {exec_time:.2f}s")
            
            # Show sample data
            data_points = data.get('data', [])
            if data_points:
                print(f"\n   Sample Data (first 3 points):")
                for i, point in enumerate(data_points[:3]):
                    print(f"     {i+1}. {point.get('timestamp', 'N/A')}")
                    print(f"        Open: {point.get('open', 'N/A')}")
                    print(f"        High: {point.get('high', 'N/A')}")
                    print(f"        Low: {point.get('low', 'N/A')}")
                    print(f"        Close: {point.get('close', 'N/A')}")
                    print(f"        Volume: {point.get('volume', 'N/A')}")
        else:
            print("❌ Failed!")
            error = data.get('error', 'Unknown error')
            print(f"   Error: {error}")
        
        print()
    
    async def run_test_scenarios(self) -> None:
        """Run predefined test scenarios"""
        print("\n🧪 Running Predefined Test Scenarios")
        print("-" * 40)
        
        scenarios = TestScenarios.get_basic_scenarios()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            print(f"   Function: {scenario['function']}")
            print(f"   Args: {scenario['args']}")
            
            try:
                result = await self.client.call_tool(scenario['function'], scenario['args'])
                
                # Parse result
                content = result.get('content', [])
                if content:
                    text_content = content[0].get('text', '{}')
                    try:
                        data = json.loads(text_content) if isinstance(text_content, str) else text_content
                        if data.get('success', False):
                            data_points = len(data.get('data', []))
                            print(f"   ✅ Success: {data_points} data points")
                        else:
                            print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Response parsing error")
                else:
                    print("   ❌ No content in response")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
            
            # Add delay between tests
            await asyncio.sleep(0.5)
    
    async def custom_tool_call(self) -> None:
        """Allow custom tool calls"""
        print("\n🔧 Custom Tool Call")
        print("-" * 40)
        
        # Show available tools
        if not self.client.tools:
            print("❌ No tools available")
            return
        
        print("Available tools:")
        for i, tool in enumerate(self.client.tools, 1):
            print(f"  {i}. {tool.get('name', 'Unknown')}")
        
        # Get tool selection
        try:
            tool_idx = int(input("\nSelect tool number: ")) - 1
            if tool_idx < 0 or tool_idx >= len(self.client.tools):
                print("❌ Invalid tool selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        selected_tool = self.client.tools[tool_idx]
        tool_name = selected_tool.get('name', 'Unknown')
        
        print(f"\n🔧 Selected: {tool_name}")
        
        # Get tool parameters
        schema = selected_tool.get('inputSchema', {})
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        arguments = {}
        
        if properties:
            print("Enter parameters:")
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'string')
                param_desc = param_info.get('description', 'No description')
                is_required = param_name in required
                req_marker = " (required)" if is_required else " (optional)"
                
                prompt = f"  {param_name} ({param_type}){req_marker}: "
                value = input(prompt).strip()
                
                if value:
                    # Basic type conversion
                    if param_type == 'number':
                        try:
                            value = float(value)
                        except ValueError:
                            print(f"    ⚠️  Invalid number format, using as string")
                    elif param_type == 'integer':
                        try:
                            value = int(value)
                        except ValueError:
                            print(f"    ⚠️  Invalid integer format, using as string")
                    elif param_type == 'boolean':
                        value = value.lower() in ('true', 'yes', '1', 'on')
                    
                    arguments[param_name] = value
                elif is_required:
                    print(f"❌ {param_name} is required")
                    return
        
        print(f"\n🔄 Calling {tool_name} with arguments: {arguments}")
        
        try:
            result = await self.client.call_tool(tool_name, arguments)
            print(f"\n📊 Result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def performance_benchmark(self) -> None:
        """Run performance benchmarks"""
        print("\n⚡ Performance Benchmark")
        print("-" * 40)
        
        # Test scenarios for benchmarking
        benchmark_scenarios = [
            {
                "name": "Quick Test (1 day, 1h interval)",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                }
            },
            {
                "name": "Medium Test (1 week, 1d interval)",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "interval": "1d"
                }
            },
            {
                "name": "Detailed Test (1 day, 5m interval)",
                "args": {
                    "symbol": "INFY",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "5m"
                }
            }
        ]
        
        results = []
        
        for scenario in benchmark_scenarios:
            print(f"\n🔄 Running: {scenario['name']}")
            
            # Run test multiple times
            times = []
            for i in range(3):
                try:
                    result = await self.client.get_stock_chart_data(**scenario['args'])
                    exec_time = result.get('execution_time', 0)
                    times.append(exec_time)
                    print(f"   Run {i+1}: {exec_time:.2f}s")
                except Exception as e:
                    print(f"   Run {i+1}: Error - {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results.append({
                    "scenario": scenario['name'],
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "runs": len(times)
                })
                
                print(f"   Average: {avg_time:.2f}s")
                print(f"   Min: {min_time:.2f}s")
                print(f"   Max: {max_time:.2f}s")
        
        # Summary
        print(f"\n📈 Benchmark Summary:")
        print("-" * 40)
        for result in results:
            print(f"{result['scenario']}: {result['avg_time']:.2f}s avg ({result['runs']} runs)")
    
    async def run_interactive_loop(self) -> None:
        """Main interactive loop"""
        self.print_welcome()
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'q' or command == 'quit':
                    print("👋 Goodbye!")
                    break
                elif command == 'h' or command == 'help':
                    self.print_welcome()
                elif command == '1':
                    await self.test_stock_data()
                elif command == '2':
                    await self.run_test_scenarios()
                elif command == '3':
                    self.print_capabilities()
                elif command == '4':
                    self.print_tools()
                elif command == '5':
                    await self.custom_tool_call()
                elif command == '6':
                    await self.performance_benchmark()
                else:
                    print("❓ Unknown command. Type 'h' for help.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    interactive_client = InteractiveMCPClient(project_root)
    
    print("🔄 Starting MCP client...")
    
    if await interactive_client.start():
        print("✅ Connected to MCP server!")
        
        try:
            await interactive_client.run_interactive_loop()
        finally:
            await interactive_client.stop()
    else:
        print("❌ Failed to connect to MCP server")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())