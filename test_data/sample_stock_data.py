"""
Sample test data for stock market testing.
"""

import pandas as pd
from datetime import datetime, timedelta

def create_sample_stock_data():
    """Create sample OHLC data for testing."""
    dates = pd.date_range(
        start='2024-01-01 10:00:00',
        end='2024-01-01 16:00:00',
        freq='1H',
        tz='Asia/Kolkata'
    )
    
    data = {
        'Open': [2450.50, 2460.25, 2455.75, 2465.00, 2470.25, 2475.50, 2480.00],
        'High': [2465.75, 2470.50, 2468.25, 2475.75, 2485.00, 2490.25, 2485.75],
        'Low': [2445.00, 2455.25, 2450.00, 2460.75, 2465.50, 2470.00, 2475.25],
        'Close': [2460.25, 2455.75, 2465.00, 2470.25, 2475.50, 2480.00, 2482.75],
        'Volume': [1250000, 1100000, 1350000, 1225000, 1175000, 1300000, 1050000]
    }
    
    return pd.DataFrame(data, index=dates)

def create_empty_stock_data():
    """Create empty DataFrame for testing no data scenarios."""
    return pd.DataFrame()

SAMPLE_RELIANCE_DATA = create_sample_stock_data()
EMPTY_DATA = create_empty_stock_data()