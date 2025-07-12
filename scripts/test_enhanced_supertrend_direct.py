#!/usr/bin/env python3
"""
Direct test script for Enhanced Supertrend indicator.
Tests the indicator without going through MCP protocol.
"""

import sys
import os
import logging

# Add the src directory to the path so we can import trading_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_mcp.stock_data import StockDataProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_enhanced_supertrend_direct():
    """Test Enhanced Supertrend indicator directly via StockDataProvider."""
    
    logger.info("Initializing StockDataProvider...")
    provider = StockDataProvider()
    
    # Test Enhanced Supertrend with RELIANCE
    logger.info("Testing Enhanced Supertrend with RELIANCE...")
    
    result = provider.calculate_technical_indicator(
        symbol="RELIANCE",
        indicator="ENHANCED_SUPERTREND",
        start_date="2024-01-01",
        end_date="2024-03-01",  # Extended date range for more data
        interval="1d",
        params={
            "atr_period": 10,
            "st_multiplier": 3.0,
            "rsi_period": 14,
            "volume_period": 20,
            "volume_threshold": 1.5
        }
    )
    
    if result["success"]:
        logger.info("✅ Enhanced Supertrend calculation successful!")
        
        data = result["data"]
        logger.info(f"Indicator: {data['indicator']}")
        logger.info(f"Number of data points: {len(data['values'])}")
        
        if data["values"]:
            first_value = data["values"][0]
            logger.info(f"First data point:")
            logger.info(f"  Timestamp: {first_value['timestamp']}")
            logger.info(f"  Supertrend: {first_value['supertrend']}")
            logger.info(f"  Trend: {first_value['trend']}")
            logger.info(f"  Signal Strength: {first_value['signal_strength']}")
            logger.info(f"  Volume Surge: {first_value['volume_surge']}")
            logger.info(f"  RSI: {first_value['rsi']}")
            logger.info(f"  Buy Signal: {first_value['buy_signal']}")
            logger.info(f"  Sell Signal: {first_value['sell_signal']}")
            logger.info(f"  ATR: {first_value['atr']}")
            
            # Check if we have some data with valid RSI
            valid_rsi_count = sum(1 for v in data["values"] if v["rsi"] is not None)
            logger.info(f"Data points with valid RSI: {valid_rsi_count}/{len(data['values'])}")
            
            # Check for buy/sell signals
            buy_signals = sum(1 for v in data["values"] if v["buy_signal"])
            sell_signals = sum(1 for v in data["values"] if v["sell_signal"])
            logger.info(f"Buy signals: {buy_signals}, Sell signals: {sell_signals}")
            
            # Show a few more data points
            logger.info(f"Last data point:")
            last_value = data["values"][-1]
            logger.info(f"  Timestamp: {last_value['timestamp']}")
            logger.info(f"  Supertrend: {last_value['supertrend']}")
            logger.info(f"  Trend: {last_value['trend']}")
            logger.info(f"  Signal Strength: {last_value['signal_strength']}")
            logger.info(f"  RSI: {last_value['rsi']}")
            
        return True
    else:
        logger.error(f"❌ Enhanced Supertrend calculation failed: {result}")
        return False


if __name__ == "__main__":
    success = test_enhanced_supertrend_direct()
    if success:
        logger.info("✅ Enhanced Supertrend direct test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Enhanced Supertrend direct test failed!")
        sys.exit(1)