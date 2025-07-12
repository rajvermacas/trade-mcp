#!/usr/bin/env python3
"""
Test script for new indicators implemented via pandas_ta integration.

This script tests various new indicators to ensure they work correctly
with the unified indicator interface.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_mcp.stock_data import StockDataProvider
import pandas as pd
from unittest.mock import Mock, patch

def create_mock_data():
    """Create sample OHLC data for testing."""
    dates = pd.date_range('2024-01-01', periods=50, freq='1d')
    data = []
    
    for i, date in enumerate(dates):
        base_price = 2500 + i * 2  # Rising trend
        data.append({
            'timestamp': date.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
            'open': base_price,
            'high': base_price + 10,
            'low': base_price - 8,
            'close': base_price + 5,
            'volume': 1000000 + i * 10000
        })
    
    return data

def test_indicator(provider, indicator, params=None):
    """Test a specific indicator."""
    print(f"\n=== Testing {indicator} ===")
    
    with patch('trading_mcp.stock_data.yf.Ticker') as mock_ticker:
        # Mock setup
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=50, freq='1d')
        sample_data = pd.DataFrame({
            'Open': [2500 + i for i in range(50)],
            'High': [2510 + i for i in range(50)],
            'Low': [2490 + i for i in range(50)],
            'Close': [2500 + i for i in range(50)],
            'Volume': [1000000 + i * 10000 for i in range(50)]
        }, index=dates)
        
        mock_ticker_instance.history.return_value = sample_data
        
        # Test the indicator
        result = provider.calculate_technical_indicator(
            symbol="RELIANCE",
            indicator=indicator,
            start_date="2024-01-01",
            end_date="2024-02-20",
            interval="1d",
            params=params or {}
        )
        
        if result["success"]:
            print(f"✅ {indicator} - Success")
            print(f"   Data points: {len(result['data']['values'])}")
            if result['data']['values']:
                first_value = result['data']['values'][0]
                print(f"   First value: {first_value}")
                if isinstance(first_value.get('value'), (int, float)):
                    print(f"   Value: {first_value['value']:.4f}")
            print(f"   Parameters: {result['data']['parameters']}")
        else:
            print(f"❌ {indicator} - Failed")
            print(f"   Error: {result['error']['message']}")
            return False
    
    return True

def main():
    """Test various new indicators."""
    print("Testing New Technical Indicators")
    print("=" * 50)
    
    provider = StockDataProvider()
    
    print(f"Total supported indicators: {len(provider.indicator_registry.get_supported_indicators())}")
    print(f"Supported indicators: {', '.join(provider.indicator_registry.get_supported_indicators())}")
    
    # Test cases for different indicator categories
    test_cases = [
        # Trend Indicators
        ("WMA", {"period": 20}),
        ("DEMA", {"period": 20}),
        ("TEMA", {"period": 20}),
        ("ADX", {"period": 14}),
        ("CCI", {"period": 20}),
        ("CMO", {"period": 14}),
        ("AROON", {"period": 14}),
        
        # Momentum Indicators  
        ("WILLR", {"period": 14}),
        ("MFI", {"period": 14}),
        ("TRIX", {"period": 30}),
        ("ROC", {"period": 10}),
        ("MOM", {"period": 10}),
        
        # Volatility Indicators
        ("NATR", {"period": 14}),
        ("TRANGE", {}),
        ("STDDEV", {"period": 20}),
        
        # Volume Indicators
        ("AD", {}),
        ("ADOSC", {"fast": 3, "slow": 10}),
        ("OBV", {}),
        ("VWAP", {}),
        ("EMV", {"period": 14}),
        ("FI", {"period": 13}),
        
        # Custom Indicators
        ("SUPERTREND", {"period": 10, "multiplier": 3}),
        ("ICHIMOKU", {"conversion": 9, "base": 26, "span": 52}),
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for indicator, params in test_cases:
        try:
            if test_indicator(provider, indicator, params):
                successful_tests += 1
        except Exception as e:
            print(f"❌ {indicator} - Exception: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {successful_tests}/{total_tests} indicators working")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All indicators working correctly!")
        return 0
    else:
        print("⚠️  Some indicators need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())