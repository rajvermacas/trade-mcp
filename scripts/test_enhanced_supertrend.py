#!/usr/bin/env python3
"""
Test script for Enhanced Supertrend indicator via MCP server.
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_enhanced_supertrend():
    """Test Enhanced Supertrend indicator via MCP server."""
    
    # Start MCP server
    logger.info("Starting MCP server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "trading_mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        logger.info("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        response_line = process.stdout.readline()
        logger.info(f"Initialize response: {response_line.strip()}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Test Enhanced Supertrend
        enhanced_supertrend_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "calculate_technical_indicator",
                "arguments": {
                    "symbol": "RELIANCE",
                    "indicator": "ENHANCED_SUPERTREND",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "interval": "1d",
                    "params": {
                        "atr_period": 10,
                        "st_multiplier": 3.0,
                        "rsi_period": 14,
                        "volume_period": 20,
                        "volume_threshold": 1.5
                    }
                }
            }
        }
        
        logger.info("Testing Enhanced Supertrend indicator...")
        process.stdin.write(json.dumps(enhanced_supertrend_request) + "\n")
        process.stdin.flush()
        
        # Read response (may need to skip log lines)
        response_line = None
        max_attempts = 10
        
        for attempt in range(max_attempts):
            line = process.stdout.readline()
            logger.debug(f"Attempt {attempt + 1}: {line.strip()}")
            
            # Try to parse as JSON - if successful, it's our response
            try:
                test_json = json.loads(line)
                response_line = line
                break
            except json.JSONDecodeError:
                # This is probably a log line, continue reading
                continue
        
        if response_line is None:
            logger.error("Failed to find valid JSON response after multiple attempts")
            return False
            
        logger.info(f"Enhanced Supertrend response received: {len(response_line)} characters")
        
        try:
            response_data = json.loads(response_line)
            
            if "error" in response_data:
                logger.error(f"Error in response: {response_data['error']}")
                return False
            
            if "result" in response_data:
                result = response_data["result"]
                
                # Parse the nested JSON content
                if isinstance(result.get("content"), list) and len(result["content"]) > 0:
                    content = json.loads(result["content"][0]["text"])
                    
                    if content.get("success"):
                        logger.info("✅ Enhanced Supertrend calculation successful!")
                        
                        data = content["data"]
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
                            
                        return True
                    else:
                        logger.error(f"Enhanced Supertrend calculation failed: {content}")
                        return False
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return False
            else:
                logger.error(f"No result in response: {response_data}")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            logger.error(f"Raw response: {response_line}")
            return False
            
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False
        
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        logger.info("MCP server stopped")


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_supertrend())
    if success:
        logger.info("✅ Enhanced Supertrend test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Enhanced Supertrend test failed!")
        sys.exit(1)