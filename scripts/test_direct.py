#!/usr/bin/env python3
"""
Direct test script for Trading MCP server functionality.
Run this to test the server without MCP protocol.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trading_mcp.server import TradingMCPServer

async def test_stock_data():
    """Test the stock data retrieval function directly."""
    print("Testing Trading MCP Server...")
    
    # Create server instance
    server = TradingMCPServer()
    
    # Test parameters
    test_cases = [
        {
            "symbol": "RELIANCE",
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "interval": "1h"
        },
        {
            "symbol": "TCS.NS",
            "start_date": "2024-01-01", 
            "end_date": "2024-01-02",
            "interval": "1d"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Testing: {test_case}")
        
        try:
            result = await server.get_stock_chart_data(
                symbol=test_case["symbol"],
                start_date=test_case["start_date"],
                end_date=test_case["end_date"],
                interval=test_case["interval"]
            )
            
            print(f"Success: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', [])
                print(f"Data points: {len(data)}")
                if data:
                    print(f"First data point: {data[0]}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Exception: {e}")
    
    print("\nTesting completed!")

if __name__ == "__main__":
    asyncio.run(test_stock_data())