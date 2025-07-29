#!/usr/bin/env python3
"""
Test script to verify CSV output functionality for both MCP functions.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trading_mcp.stock_data import StockDataProvider
from trading_mcp.csv_utils import get_csv_metadata


def test_stock_chart_data_csv():
    """Test get_stock_chart_data CSV output."""
    print("Testing get_stock_chart_data CSV output...")
    
    provider = StockDataProvider()
    
    # Test with a known symbol
    result = provider.get_stock_chart_data(
        symbol="RELIANCE",
        start_date="2024-01-01",
        end_date="2024-01-02",
        interval="1d",
        request_id="test_stock_csv"
    )
    
    print(f"Stock data result: {json.dumps(result, indent=2)}")
    
    if result["success"]:
        file_path = result["file_path"]
        print(f"✅ CSV file created: {file_path}")
        
        # Verify file exists and get metadata
        csv_meta = get_csv_metadata(file_path)
        print(f"CSV metadata: {json.dumps(csv_meta, indent=2)}")
        
        # Read first few lines of CSV
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()[:5]
                print("First 5 lines of CSV:")
                for i, line in enumerate(lines):
                    print(f"  {i+1}: {line.strip()}")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    else:
        print(f"❌ Stock data failed: {result}")
    
    return result


def test_technical_indicator_csv():
    """Test calculate_technical_indicator CSV output."""
    print("\nTesting calculate_technical_indicator CSV output...")
    
    provider = StockDataProvider()
    
    # Test with SMA indicator (simple and reliable)
    result = provider.calculate_technical_indicator(
        symbol="RELIANCE",
        indicator="SMA",
        start_date="2024-01-01",
        end_date="2024-02-15",  # Extended date range for sufficient data
        interval="1d",
        params={"period": 20},  # Simple Moving Average with 20 periods
        request_id="test_indicator_csv"
    )
    
    print(f"Indicator result: {json.dumps(result, indent=2)}")
    
    if result["success"]:
        file_path = result["file_path"]
        print(f"✅ CSV file created: {file_path}")
        
        # Verify file exists and get metadata  
        csv_meta = get_csv_metadata(file_path)
        print(f"CSV metadata: {json.dumps(csv_meta, indent=2)}")
        
        # Read first few lines of CSV
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()[:5]
                print("First 5 lines of CSV:")
                for i, line in enumerate(lines):
                    print(f"  {i+1}: {line.strip()}")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    else:
        print(f"❌ Indicator data failed: {result}")
    
    return result


def test_enhanced_supertrend_csv():
    """Test Enhanced Supertrend CSV output (complex indicator)."""
    print("\nTesting Enhanced Supertrend CSV output...")
    
    provider = StockDataProvider()
    
    # Test with Enhanced Supertrend indicator
    result = provider.calculate_technical_indicator(
        symbol="RELIANCE",
        indicator="ENHANCED_SUPERTREND",
        start_date="2024-01-01",
        end_date="2024-03-01",  # Extended date range for sufficient data (need 30+ periods)
        interval="1d",
        params={"length": 10, "multiplier": 3.0},
        request_id="test_supertrend_csv"
    )
    
    print(f"Enhanced Supertrend result: {json.dumps(result, indent=2)}")
    
    if result["success"]:
        file_path = result["file_path"]
        print(f"✅ CSV file created: {file_path}")
        
        # Verify file exists and get metadata
        csv_meta = get_csv_metadata(file_path)
        print(f"CSV metadata: {json.dumps(csv_meta, indent=2)}")
        
        # Read first few lines of CSV
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()[:5]
                print("First 5 lines of CSV:")
                for i, line in enumerate(lines):
                    print(f"  {i+1}: {line.strip()}")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    else:
        print(f"❌ Enhanced Supertrend failed: {result}")
    
    return result


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTesting error handling...")
    
    provider = StockDataProvider()
    
    # Test with invalid symbol
    result = provider.get_stock_chart_data(
        symbol="INVALID_SYMBOL",
        start_date="2024-01-01",
        end_date="2024-01-02",
        interval="1d",
        request_id="test_error"
    )
    
    print(f"Error test result: {json.dumps(result, indent=2)}")
    
    if not result["success"]:
        print("✅ Error handling works correctly")
    else:
        print("❌ Expected error but got success")
    
    return result


def main():
    """Run all tests."""
    print("🧪 Testing CSV Output Implementation")
    print("=" * 50)
    
    # Test 1: Stock chart data CSV
    stock_result = test_stock_chart_data_csv()
    
    # Test 2: Technical indicator CSV (simple)
    indicator_result = test_technical_indicator_csv()
    
    # Test 3: Enhanced Supertrend CSV (complex)
    supertrend_result = test_enhanced_supertrend_csv()
    
    # Test 4: Error handling
    error_result = test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"Stock data CSV: {'✅ PASS' if stock_result.get('success') else '❌ FAIL'}")
    print(f"Indicator CSV: {'✅ PASS' if indicator_result.get('success') else '❌ FAIL'}")
    print(f"Enhanced Supertrend CSV: {'✅ PASS' if supertrend_result.get('success') else '❌ FAIL'}")
    print(f"Error handling: {'✅ PASS' if not error_result.get('success') else '❌ FAIL'}")
    
    # List generated files
    print("\n📁 Generated CSV Files:")
    reports_dir = Path(__file__).parent.parent / "resources" / "reports"
    if reports_dir.exists():
        csv_files = list(reports_dir.glob("*.csv"))
        for csv_file in sorted(csv_files):
            print(f"  - {csv_file.name}")
    else:
        print("  No CSV files found")


if __name__ == "__main__":
    main()