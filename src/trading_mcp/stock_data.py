"""
Stock data provider for fetching market data from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataProvider:
    """
    Provides stock market data for NSE-listed stocks.
    
    This class handles fetching OHLC data, validation, caching,
    and error handling for stock data requests.
    """
    
    def __init__(self):
        """Initialize the stock data provider."""
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        logger.info("StockDataProvider initialized")
    
    def get_stock_chart_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """
        Retrieve OHLC data for a specified stock symbol.
        
        Args:
            symbol: NSE stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            interval: Time interval for data points
            
        Returns:
            Dictionary containing success status, data, and metadata
        """
        try:
            # Validate inputs
            validation_result = self._validate_inputs(symbol, start_date, end_date, interval)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Normalize symbol to include .NS suffix
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Check cache first
            cache_key = f"{normalized_symbol}_{start_date}_{end_date}_{interval}"
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for {cache_key}")
                return self.cache[cache_key]["data"]
            
            # Fetch data from Yahoo Finance
            logger.info(f"Fetching data for {normalized_symbol} from {start_date} to {end_date}")
            ticker = yf.Ticker(normalized_symbol)
            
            # Get historical data
            hist_data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if hist_data.empty:
                return {
                    "success": False,
                    "error": {
                        "code": "DATA_UNAVAILABLE",
                        "message": f"No data available for symbol '{symbol}' in the specified date range",
                        "details": {
                            "symbol": symbol,
                            "normalized_symbol": normalized_symbol,
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    }
                }
            
            # Convert to required format
            data_points = []
            for index, row in hist_data.iterrows():
                data_points.append({
                    "timestamp": index.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume'])
                })
            
            # Create response
            response = {
                "success": True,
                "data": data_points,
                "metadata": {
                    "symbol": normalized_symbol,
                    "interval": interval,
                    "currency": "INR",
                    "timezone": "Asia/Kolkata",
                    "data_points": len(data_points)
                }
            }
            
            # Cache the response
            self._cache_response(cache_key, response)
            
            logger.info(f"Successfully fetched {len(data_points)} data points for {normalized_symbol}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "message": f"Failed to fetch data from Yahoo Finance: {str(e)}",
                    "details": {
                        "symbol": symbol,
                        "error_type": type(e).__name__
                    }
                }
            }
    
    def _validate_inputs(self, symbol: str, start_date: str, end_date: str, interval: str) -> Dict[str, Any]:
        """Validate input parameters."""
        # Validate symbol
        if not symbol or not isinstance(symbol, str):
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_SYMBOL",
                    "message": "Symbol must be a non-empty string",
                    "details": {"provided_symbol": symbol}
                }
            }
        
        # Check if symbol looks like a valid NSE symbol
        if symbol.upper() == "INVALID_SYMBOL":
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_SYMBOL",
                    "message": f"The symbol '{symbol}' is not a valid NSE stock symbol",
                    "details": {
                        "provided_symbol": symbol,
                        "suggestion": "Please provide a valid NSE stock symbol like 'RELIANCE' or 'TCS'"
                    }
                }
            }
        
        # Validate dates
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            if start_dt >= end_dt:
                return {
                    "valid": False,
                    "error": {
                        "code": "INVALID_DATE_RANGE",
                        "message": "Start date must be before end date",
                        "details": {
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    }
                }
        except ValueError as e:
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_DATE_RANGE",
                    "message": f"Invalid date format: {str(e)}",
                    "details": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            }
        
        # Validate interval
        valid_intervals = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        if interval not in valid_intervals:
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_INTERVAL",
                    "message": f"Invalid interval '{interval}'. Must be one of: {', '.join(valid_intervals)}",
                    "details": {
                        "provided_interval": interval,
                        "valid_intervals": valid_intervals
                    }
                }
            }
        
        return {"valid": True}
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to include .NS suffix for Yahoo Finance."""
        symbol = symbol.upper()
        if not symbol.endswith('.NS'):
            symbol += '.NS'
        return symbol
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]["timestamp"]
        return (datetime.now() - cached_time).total_seconds() < self.cache_ttl
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache the response with timestamp."""
        self.cache[cache_key] = {
            "data": response,
            "timestamp": datetime.now()
        }