#!/usr/bin/env python3
"""
Integration test to verify MCP server returns CSV file paths instead of large datasets.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trading_mcp.server import TradingMCPServer


async def test_mcp_csv_integration():
    """Test MCP server integration with CSV output."""
    print("🔧 Testing MCP Server CSV Integration")
    print("=" * 50)
    
    # Initialize MCP server
    server = TradingMCPServer()
    
    # Test 1: Stock chart data
    print("\n1. Testing get_stock_chart_data MCP tool...")
    stock_args = {
        "symbol": "RELIANCE",
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
        "interval": "1d"
    }
    
    stock_result = await server._handle_get_stock_chart_data(stock_args)
    stock_json = json.loads(stock_result[0].text)
    
    print(f"Stock data response keys: {list(stock_json.keys())}")
    if stock_json.get("success"):
        print(f"✅ File path returned: {stock_json.get('file_path')}")
        print(f"✅ Row count: {stock_json.get('metadata', {}).get('row_count')}")
        print(f"✅ File size: {stock_json.get('metadata', {}).get('file_size_bytes')} bytes")
        
        # Verify no large 'data' field in response
        if 'data' in stock_json:
            print("❌ Response still contains 'data' field - should be file_path only")
        else:
            print("✅ Large 'data' field removed from response")
    else:
        print(f"❌ Stock data failed: {stock_json.get('error')}")
    
    # Test 2: Technical indicator
    print("\n2. Testing calculate_technical_indicator MCP tool...")
    indicator_args = {
        "symbol": "RELIANCE",
        "indicator": "SMA",
        "start_date": "2024-01-01",
        "end_date": "2024-02-15",
        "interval": "1d",
        "params": {"period": 20}
    }
    
    indicator_result = await server._handle_calculate_technical_indicator(indicator_args)
    indicator_json = json.loads(indicator_result[0].text)
    
    print(f"Indicator response keys: {list(indicator_json.keys())}")
    if indicator_json.get("success"):
        print(f"✅ File path returned: {indicator_json.get('file_path')}")
        print(f"✅ Row count: {indicator_json.get('metadata', {}).get('row_count')}")
        print(f"✅ File size: {indicator_json.get('metadata', {}).get('file_size_bytes')} bytes")
        print(f"✅ Indicator: {indicator_json.get('metadata', {}).get('indicator')}")
        
        # Verify no large 'data' field in response
        if 'data' in indicator_json:
            print("❌ Response still contains 'data' field - should be file_path only")
        else:
            print("✅ Large 'data' field removed from response")
    else:
        print(f"❌ Indicator data failed: {indicator_json.get('error')}")
    
    # Calculate response size reduction
    print("\n📊 Response Size Analysis:")
    stock_response_size = len(json.dumps(stock_json))
    indicator_response_size = len(json.dumps(indicator_json))
    
    print(f"Stock data response size: {stock_response_size} characters")
    print(f"Indicator response size: {indicator_response_size} characters")
    print(f"Total response size: {stock_response_size + indicator_response_size} characters")
    
    # Estimate original size (would be much larger with raw data)
    estimated_original_stock = stock_json.get('metadata', {}).get('row_count', 1) * 100  # ~100 chars per row
    estimated_original_indicator = indicator_json.get('metadata', {}).get('row_count', 1) * 150  # ~150 chars per row
    estimated_original_total = estimated_original_stock + estimated_original_indicator
    
    if estimated_original_total > 0:
        reduction_percentage = ((estimated_original_total - (stock_response_size + indicator_response_size)) / estimated_original_total) * 100
        print(f"Estimated size reduction: {reduction_percentage:.1f}%")
    
    print("\n" + "=" * 50)
    print("✅ MCP CSV Integration Test Complete!")
    
    return stock_json.get("success", False) and indicator_json.get("success", False)


if __name__ == "__main__":
    success = asyncio.run(test_mcp_csv_integration())
    sys.exit(0 if success else 1)