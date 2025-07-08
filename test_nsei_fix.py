#!/usr/bin/env python3
"""
Quick test to verify ^NSEI index data fetching works after the fix.
"""

import sys
sys.path.insert(0, 'src')

from trading_mcp.stock_data import StockDataProvider

def test_nsei_data():
    """Test ^NSEI data fetching."""
    provider = StockDataProvider()
    
    print("Testing ^NSEI (Nifty 50) data fetching...")
    
    # Test with a recent date range
    result = provider.get_stock_chart_data(
        symbol="^NSEI",
        start_date="2024-01-01",
        end_date="2024-01-02",
        interval="1d"
    )
    
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Symbol: {result['metadata']['symbol']}")
        print(f"Data points: {result['metadata']['data_points']}")
        if result['data']:
            print("Sample data point:")
            print(f"  Timestamp: {result['data'][0]['timestamp']}")
            print(f"  Open: {result['data'][0]['open']}")
            print(f"  Close: {result['data'][0]['close']}")
        print("✅ ^NSEI data fetching SUCCESSFUL!")
    else:
        print(f"❌ Error: {result['error']}")
        
    return result['success']

def test_symbol_normalization():
    """Test symbol normalization logic."""
    provider = StockDataProvider()
    
    print("\nTesting symbol normalization...")
    
    # Test cases
    test_cases = [
        ("^NSEI", "^NSEI"),
        ("^nsei", "^NSEI"),
        ("^NSEBANK", "^NSEBANK"),
        ("RELIANCE", "RELIANCE.NS"),
        ("reliance", "RELIANCE.NS"),
        ("RELIANCE.NS", "RELIANCE.NS")
    ]
    
    all_passed = True
    for input_symbol, expected_output in test_cases:
        actual_output = provider._normalize_symbol(input_symbol)
        passed = actual_output == expected_output
        status = "✅" if passed else "❌"
        print(f"  {status} {input_symbol} -> {actual_output} (expected: {expected_output})")
        if not passed:
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ^NSEI INDEX DATA FETCHING FIX")
    print("=" * 60)
    
    # Test symbol normalization
    norm_success = test_symbol_normalization()
    
    # Test actual data fetching
    data_success = test_nsei_data()
    
    print("\n" + "=" * 60)
    if norm_success and data_success:
        print("🎉 ALL TESTS PASSED! ^NSEI fix is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    print("=" * 60)