#!/usr/bin/env python3
"""
Test multiple NSE indices to ensure the fix works comprehensively.
"""

import sys
sys.path.insert(0, 'src')

from trading_mcp.stock_data import StockDataProvider

def test_multiple_indices():
    """Test multiple NSE indices."""
    provider = StockDataProvider()
    
    indices = [
        ("^NSEI", "Nifty 50"),
        ("^NSEBANK", "Bank Nifty"),
        ("^NSEIT", "Nifty IT"),
        ("^NSEAUTO", "Nifty Auto"),
        ("^NSEFMCG", "Nifty FMCG")
    ]
    
    print("Testing multiple NSE indices...")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(indices)
    
    for symbol, name in indices:
        print(f"\nTesting {symbol} ({name}):")
        
        result = provider.get_stock_chart_data(
            symbol=symbol,
            start_date="2024-01-01",
            end_date="2024-01-02",
            interval="1d"
        )
        
        if result['success']:
            print(f"  ✅ SUCCESS - {result['metadata']['data_points']} data points")
            print(f"  Symbol normalized to: {result['metadata']['symbol']}")
            if result['data']:
                print(f"  Sample close price: {result['data'][0]['close']}")
            successful_tests += 1
        else:
            print(f"  ❌ FAILED - {result['error']['message']}")
    
    print("\n" + "=" * 50)
    print(f"Results: {successful_tests}/{total_tests} indices tested successfully")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = test_multiple_indices()
    
    if success:
        print("🎉 ALL INDEX TESTS PASSED!")
    else:
        print("⚠️  Some index tests failed.")