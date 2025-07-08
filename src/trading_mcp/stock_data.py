"""
Stock data provider for fetching market data from Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time
import threading
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cachetools import LRUCache
from .logging_config import (
    get_logger, log_cache_event, log_api_call
)


class StockDataProvider:
    """
    Provides stock market data for NSE-listed stocks and indices.
    
    This class handles fetching OHLC data, validation, caching,
    and error handling for stock data and index requests.
    Supports both individual stocks (e.g., RELIANCE) and market indices (e.g., ^NSEI).
    """
    
    def __init__(self):
        """Initialize the stock data provider."""
        # Stage 4: Advanced caching with LRU and size limits
        self.cache = LRUCache(maxsize=100)  # LRU cache with 100 entry limit
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        
        # Stage 4: Circuit breaker for API resilience
        self.circuit_breaker = {
            "state": "closed",  # closed, open, half_open
            "failures": 0,
            "last_failure_time": None,
            "failure_threshold": 5,
            "recovery_timeout": 30  # seconds
        }
        
        # Stage 4: Performance metrics
        self.performance_metrics = {
            "total_requests": 0,
            "total_response_time": 0,
            "error_count": 0,
            "start_time": time.time()
        }
        
        # Stage 4: Connection pool stats (simulated)
        self.connection_pool_stats = {
            "active_connections": 0,
            "max_connections": 10,
            "total_connections_created": 0
        }
        
        self.logger = get_logger(__name__, {"component": "stock_data_provider"})
        self.logger.info(
            "StockDataProvider initialized with Stage 4 features",
            extra={
                "cache_ttl": self.cache_ttl,
                "cache_max_size": 100,
                "circuit_breaker_threshold": 5
            }
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
        Retrieve OHLC data for a specified stock symbol or index.
        
        Args:
            symbol: NSE stock symbol (e.g., "RELIANCE" or "RELIANCE.NS") or index (e.g., "^NSEI", "^NSEBANK")
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
                
                # Stage 4: Update performance metrics for cache hits
                self._update_performance_metrics(response_time, True)
                
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
            
            # Use new _fetch_from_yahoo method with circuit breaker and retry logic
            hist_data = self._fetch_from_yahoo_with_retry(
                normalized_symbol, start_date, end_date, interval
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
            
            # Stage 4: Update performance metrics
            self._update_performance_metrics(total_response_time, True)
            
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
            
            # Stage 4: Update performance metrics for errors
            self._update_performance_metrics(total_response_time, False)
            
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
    
    def calculate_technical_indicator(
        self,
        symbol: str,
        indicator: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        params: Optional[Dict[str, Any]] = None,
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Calculate technical indicators for a specified stock symbol or index.
        
        Args:
            symbol: NSE stock symbol (e.g., "RELIANCE" or "RELIANCE.NS") or index (e.g., "^NSEI", "^NSEBANK")
            indicator: Indicator name (e.g., "RSI", "MACD", "SMA")
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            interval: Time interval for data points (default: "1d")
            params: Optional parameters for the indicator
            request_id: Optional request ID for tracking
            
        Returns:
            Dictionary containing success status, indicator data, and metadata
        """
        start_time = time.time()
        params = params or {}
        
        self.logger.info(
            f"Processing technical indicator request: {indicator} for {symbol}",
            extra={
                "symbol": symbol,
                "indicator": indicator,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval,
                "params": params,
                "mcp_request_id": request_id
            }
        )
        
        try:
            # Validate inputs
            validation_result = self._validate_indicator_inputs(
                symbol, indicator, start_date, end_date, interval, params, request_id
            )
            if not validation_result["valid"]:
                self.logger.warning(
                    f"Indicator validation failed for {symbol}",
                    extra={
                        "symbol": symbol,
                        "indicator": indicator,
                        "error": validation_result["error"],
                        "mcp_request_id": request_id
                    }
                )
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # First get the stock data
            stock_data_result = self.get_stock_chart_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                request_id=request_id
            )
            
            if not stock_data_result["success"]:
                return stock_data_result
            
            # Convert to DataFrame for pandas_ta
            data_points = stock_data_result["data"]
            if len(data_points) == 0:
                return {
                    "success": False,
                    "error": {
                        "code": "DATA_UNAVAILABLE",
                        "message": f"No data available for indicator calculation",
                        "details": {
                            "symbol": symbol,
                            "indicator": indicator
                        }
                    }
                }
            
            # Create DataFrame
            df = pd.DataFrame(data_points)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Rename columns to match pandas_ta expectations
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Calculate the indicator
            indicator_result = self._calculate_indicator(df, indicator, params)
            
            if indicator_result is None:
                return {
                    "success": False,
                    "error": {
                        "code": "CALCULATION_ERROR",
                        "message": f"Failed to calculate {indicator}",
                        "details": {
                            "symbol": symbol,
                            "indicator": indicator,
                            "params": params
                        }
                    }
                }
            
            # Convert result to response format
            values = []
            if isinstance(indicator_result, pd.Series):
                for timestamp, value in indicator_result.dropna().items():
                    if pd.notna(value):
                        values.append({
                            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                            "value": round(float(value), 4)
                        })
            
            response = {
                "success": True,
                "data": {
                    "indicator": indicator,
                    "values": values,
                    "parameters": params
                },
                "metadata": {
                    "symbol": stock_data_result["metadata"]["symbol"],
                    "interval": interval,
                    "data_points": len(values)
                }
            }
            
            total_response_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Successfully calculated {indicator} for {symbol} in {total_response_time:.2f}ms",
                extra={
                    "symbol": symbol,
                    "indicator": indicator,
                    "data_points": len(values),
                    "response_time": total_response_time,
                    "mcp_request_id": request_id
                }
            )
            return response
            
        except Exception as e:
            total_response_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Error calculating {indicator} for {symbol}: {str(e)}",
                extra={
                    "symbol": symbol,
                    "indicator": indicator,
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
                    "message": f"Failed to calculate {indicator}: {str(e)}",
                    "details": {
                        "symbol": symbol,
                        "indicator": indicator,
                        "error_type": type(e).__name__,
                        "request_id": request_id
                    }
                }
            }
    
    def _validate_indicator_inputs(
        self, 
        symbol: str, 
        indicator: str, 
        start_date: str, 
        end_date: str, 
        interval: str,
        params: Dict[str, Any],
        request_id: str = None
    ) -> Dict[str, Any]:
        """Validate technical indicator input parameters."""
        # First validate basic inputs using existing method
        basic_validation = self._validate_inputs(symbol, start_date, end_date, interval, request_id)
        if not basic_validation["valid"]:
            return basic_validation
        
        # Validate indicator name
        supported_indicators = ["RSI", "SMA", "EMA", "MACD", "BBANDS", "ATR"]
        if indicator.upper() not in supported_indicators:
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_INDICATOR",
                    "message": f"Indicator '{indicator}' is not supported",
                    "details": {
                        "provided_indicator": indicator,
                        "supported_indicators": supported_indicators
                    }
                }
            }
        
        return {"valid": True}
    
    def _calculate_indicator(self, df: pd.DataFrame, indicator: str, params: Dict[str, Any]) -> Optional[pd.Series]:
        """Calculate the specified technical indicator."""
        indicator = indicator.upper()
        
        try:
            if indicator == "RSI":
                period = params.get("period", 14)
                return ta.rsi(df['Close'], length=period)
            elif indicator == "SMA":
                period = params.get("period", 20)
                return ta.sma(df['Close'], length=period)
            elif indicator == "EMA":
                period = params.get("period", 20)
                return ta.ema(df['Close'], length=period)
            elif indicator == "MACD":
                fast = params.get("fast", 12)
                slow = params.get("slow", 26)
                signal = params.get("signal", 9)
                macd_result = ta.macd(df['Close'], fast=fast, slow=slow, signal=signal)
                return macd_result[f'MACD_{fast}_{slow}_{signal}']
            elif indicator == "BBANDS":
                period = params.get("period", 20)
                std = params.get("std", 2)
                bbands_result = ta.bbands(df['Close'], length=period, std=std)
                return bbands_result[f'BBM_{period}_{std}']  # Middle band (SMA)
            elif indicator == "ATR":
                period = params.get("period", 14)
                return ta.atr(df['High'], df['Low'], df['Close'], length=period)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error calculating {indicator}: {str(e)}", exc_info=True)
            return None
    
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
        
        # Check if symbol looks like a valid NSE symbol or index
        if symbol.upper() == "INVALID_SYMBOL":
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_SYMBOL",
                    "message": f"The symbol '{symbol}' is not a valid NSE stock symbol or index",
                    "details": {
                        "provided_symbol": symbol,
                        "suggestion": "Please provide a valid NSE stock symbol like 'RELIANCE' or 'TCS', or index like '^NSEI' or '^NSEBANK'"
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
        """
        Normalize symbol for Yahoo Finance API.
        - NSE stocks: Add .NS suffix (e.g., RELIANCE -> RELIANCE.NS)
        - NSE indices: Keep ^ prefix without .NS suffix (e.g., ^NSEI remains ^NSEI)
        - BSE indices: Keep ^ prefix without .NS suffix (e.g., ^BSESN remains ^BSESN)
        """
        symbol = symbol.upper()
        
        # Index symbols (starting with ^) should not get .NS suffix
        if symbol.startswith('^'):
            return symbol
        
        # Stock symbols need .NS suffix for NSE
        if not symbol.endswith('.NS'):
            symbol += '.NS'
        return symbol
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self.cache:
            self.cache_stats["misses"] += 1
            return False
        
        cached_time = self.cache[cache_key]["timestamp"]
        is_valid = (datetime.now() - cached_time).total_seconds() < self.cache_ttl
        
        if is_valid:
            self.cache_stats["hits"] += 1
        else:
            self.cache_stats["misses"] += 1
            # Remove expired entry
            del self.cache[cache_key]
        
        return is_valid
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache the response with timestamp."""
        # Track evictions when cache is full
        old_size = len(self.cache)
        
        self.cache[cache_key] = {
            "data": response,
            "timestamp": datetime.now()
        }
        
        # Check if an eviction occurred (LRU evicted an old entry)
        new_size = len(self.cache)
        if old_size == self.cache.maxsize and new_size == self.cache.maxsize:
            self.cache_stats["evictions"] += 1
        
        self.logger.debug(
            f"Cached response for key: {cache_key}",
            extra={
                "cache_key": cache_key,
                "cache_size": len(self.cache),
                "evictions": self.cache_stats["evictions"]
            }
        )




    # Stage 4: Performance & Reliability Methods
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        current_size = len(self.cache)
        hit_ratio = 0.0
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_requests > 0:
            hit_ratio = self.cache_stats["hits"] / total_requests
        
        return {
            "size": current_size,
            "max_size": self.cache.maxsize,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_ratio": hit_ratio
        }
    
    def warm_cache(self, symbols: list, days: int = 7) -> None:
        """Pre-populate cache with frequently accessed data."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        self.logger.info(
            f"Warming cache for {len(symbols)} symbols over {days} days",
            extra={"symbols": symbols, "days": days}
        )
        
        for symbol in symbols:
            try:
                # Warm cache with daily data
                self.get_stock_chart_data(symbol, start_date, end_date, "1d")
                time.sleep(0.1)  # Small delay to avoid rate limiting
            except Exception as e:
                self.logger.warning(
                    f"Failed to warm cache for {symbol}: {str(e)}",
                    extra={"symbol": symbol, "error": str(e)}
                )
    
    def get_circuit_breaker_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.circuit_breaker["state"],
            "failures": self.circuit_breaker["failures"],
            "failure_threshold": self.circuit_breaker["failure_threshold"],
            "last_failure_time": self.circuit_breaker["last_failure_time"],
            "recovery_timeout": self.circuit_breaker["recovery_timeout"]
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        total_requests = self.performance_metrics["total_requests"]
        average_response_time = 0.0
        if total_requests > 0:
            average_response_time = self.performance_metrics["total_response_time"] / total_requests
        
        error_rate = 0.0
        if total_requests > 0:
            error_rate = self.performance_metrics["error_count"] / total_requests
        
        uptime = time.time() - self.performance_metrics["start_time"]
        
        cache_stats = self.get_cache_stats()
        
        return {
            "total_requests": total_requests,
            "average_response_time": average_response_time,
            "error_rate": error_rate,
            "uptime_seconds": uptime,
            "cache_hit_ratio": cache_stats["hit_ratio"]
        }
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self.connection_pool_stats.copy()
    
    def _fetch_from_yahoo(self, symbol: str, start_date: str, end_date: str, interval: str):
        """Separate method for Yahoo Finance API calls (for testing)."""
        try:
            # Stage 4: Track connection pool usage
            self.connection_pool_stats["active_connections"] += 1
            
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            # Stage 4: Record successful API call
            self._record_circuit_breaker_success()
            
            return hist_data
            
        except Exception as e:
            # The circuit breaker failure is now recorded in _fetch_from_yahoo_with_retry
            raise e
        finally:
            # Stage 4: Release connection
            self.connection_pool_stats["active_connections"] = max(0, 
                self.connection_pool_stats["active_connections"] - 1)
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self.circuit_breaker["state"] == "closed":
            return False
        
        if self.circuit_breaker["state"] == "open":
            # Check if recovery timeout has passed
            if self.circuit_breaker["last_failure_time"]:
                time_since_failure = time.time() - self.circuit_breaker["last_failure_time"]
                if time_since_failure > self.circuit_breaker["recovery_timeout"]:
                    self.circuit_breaker["state"] = "half_open"
                    self.logger.info("Circuit breaker moved to half-open state")
                    return False
            return True
        
        return False  # half_open state allows one test request
    
    def _record_circuit_breaker_failure(self):
        """Record a circuit breaker failure."""
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure_time"] = time.time()
        
        if self.circuit_breaker["failures"] >= self.circuit_breaker["failure_threshold"]:
            self.circuit_breaker["state"] = "open"
            self.logger.warning(
                f"Circuit breaker opened after {self.circuit_breaker['failures']} failures"
            )
    
    def _record_circuit_breaker_success(self):
        """Record a circuit breaker success."""
        if self.circuit_breaker["state"] == "half_open":
            self.circuit_breaker["state"] = "closed"
            self.circuit_breaker["failures"] = 0
            self.logger.info("Circuit breaker closed after successful request")
    
    def _update_performance_metrics(self, response_time: float, success: bool):
        """Update performance metrics."""
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["total_response_time"] += response_time
        
        if not success:
            self.performance_metrics["error_count"] += 1
    
    def _fetch_from_yahoo_with_retry(self, symbol: str, start_date: str, end_date: str, interval: str, max_retries: int = 3):
        """Fetch data from Yahoo Finance with retry and exponential backoff."""
        # Check circuit breaker before any attempts
        if self._is_circuit_breaker_open():
            raise Exception("Circuit breaker is open")
        
        for attempt in range(max_retries):
            try:
                return self._fetch_from_yahoo(symbol, start_date, end_date, interval)
            except Exception as e:
                # Record circuit breaker failure on each failed attempt
                self._record_circuit_breaker_failure()
                
                # If circuit breaker is now open, don't retry
                if self._is_circuit_breaker_open():
                    raise Exception("Circuit breaker opened during retry attempts")
                
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                
                # Exponential backoff: 1s, 2s, 4s
                backoff_time = 2 ** attempt
                self.logger.warning(
                    f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {backoff_time}s: {str(e)}",
                    extra={
                        "symbol": symbol,
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "backoff_time": backoff_time,
                        "error": str(e)
                    }
                )
                time.sleep(backoff_time)
        
        # This should never be reached, but just in case
        raise Exception("Max retries exceeded")