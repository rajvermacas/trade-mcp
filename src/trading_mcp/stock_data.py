"""
Stock data provider for fetching market data from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .logging_config import (
    get_logger, log_cache_event, log_api_call
)


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
        self.logger = get_logger(__name__, {"component": "stock_data_provider"})
        self.logger.info(
            "StockDataProvider initialized",
            extra={"cache_ttl": self.cache_ttl}
        )
    
    def get_stock_chart_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1h",
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Retrieve OHLC data for a specified stock symbol.
        
        Args:
            symbol: NSE stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            interval: Time interval for data points
            request_id: Optional request ID for tracking
            
        Returns:
            Dictionary containing success status, data, and metadata
        """
        start_time = time.time()
        
        self.logger.info(
            f"Processing stock data request: {symbol} ({start_date} to {end_date}, {interval})",
            extra={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
                "mcp_request_id": request_id
            }
        )
        
        try:
            # Validate inputs
            validation_result = self._validate_inputs(symbol, start_date, end_date, interval, request_id)
            if not validation_result["valid"]:
                self.logger.warning(
                    f"Input validation failed for {symbol}",
                    extra={
                        "symbol": symbol,
                        "error": validation_result["error"],
                        "mcp_request_id": request_id
                    }
                )
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Normalize symbol to include .NS suffix
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Check cache first
            cache_key = f"{normalized_symbol}_{start_date}_{end_date}_{interval}"
            if self._is_cache_valid(cache_key):
                log_cache_event(self.logger, cache_key, hit=True, request_id=request_id)
                
                response_time = (time.time() - start_time) * 1000
                self.logger.info(
                    f"Cache hit for {symbol}, response in {response_time:.2f}ms",
                    extra={
                        "symbol": normalized_symbol,
                        "response_time": response_time,
                        "cache_hit": True,
                        "mcp_request_id": request_id
                    }
                )
                return self.cache[cache_key]["data"]
            
            log_cache_event(self.logger, cache_key, hit=False, request_id=request_id)
            
            # Fetch data from Yahoo Finance
            api_start_time = time.time()
            self.logger.info(
                f"Fetching data from Yahoo Finance: {normalized_symbol}",
                extra={
                    "symbol": normalized_symbol,
                    "date_range": f"{start_date} to {end_date}",
                    "interval": interval,
                    "mcp_request_id": request_id
                }
            )
            
            ticker = yf.Ticker(normalized_symbol)
            
            # Get historical data
            hist_data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            api_response_time = (time.time() - api_start_time) * 1000
            log_api_call(
                self.logger,
                provider="yahoo_finance",
                symbol=normalized_symbol,
                response_time=api_response_time,
                success=not hist_data.empty,
                request_id=request_id
            )
            
            if hist_data.empty:
                self.logger.warning(
                    f"No data available for {symbol}",
                    extra={
                        "symbol": normalized_symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "interval": interval,
                        "mcp_request_id": request_id
                    }
                )
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
            
            total_response_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Successfully fetched {len(data_points)} data points for {symbol} in {total_response_time:.2f}ms",
                extra={
                    "symbol": normalized_symbol,
                    "data_points": len(data_points),
                    "response_time": total_response_time,
                    "cache_hit": False,
                    "mcp_request_id": request_id
                }
            )
            return response
            
        except Exception as e:
            total_response_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error fetching data for {symbol}: {str(e)}",
                extra={
                    "symbol": symbol,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "response_time": total_response_time,
                    "mcp_request_id": request_id
                },
                exc_info=True
            )
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "message": f"Failed to fetch data from Yahoo Finance: {str(e)}",
                    "details": {
                        "symbol": symbol,
                        "error_type": type(e).__name__,
                        "request_id": request_id
                    }
                }
            }
    
    def _validate_inputs(self, symbol: str, start_date: str, end_date: str, interval: str, request_id: str = None) -> Dict[str, Any]:
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
        
        self.logger.debug(
            f"Cached response for key: {cache_key}",
            extra={
                "cache_key": cache_key,
                "cache_size": len(self.cache)
            }
        )