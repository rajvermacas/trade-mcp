"""
Validation utilities for Trading MCP Server.

This module provides input validation functions for stock symbols,
dates, intervals, and other parameters.
"""

from datetime import datetime
from typing import Dict, Any


def validate_symbol(symbol: str) -> Dict[str, Any]:
    """Validate stock symbol format."""
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
                    "suggestion": "Please provide a valid NSE symbol (e.g., 'RELIANCE') or index (e.g., '^NSEI', '^NSEBANK')"
                }
            }
        }
    
    return {"valid": True}


def validate_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """Validate date range format and logic."""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Check date range
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
        
        # Check if date range is too far in the future
        current_date = datetime.now()
        if start_dt > current_date:
            return {
                "valid": False,
                "error": {
                    "code": "INVALID_DATE_RANGE",
                    "message": "Start date cannot be in the future",
                    "details": {
                        "start_date": start_date,
                        "current_date": current_date.isoformat()
                    }
                }
            }
        
        return {"valid": True}
        
    except ValueError as e:
        return {
            "valid": False,
            "error": {
                "code": "INVALID_DATE_FORMAT",
                "message": f"Invalid date format: {str(e)}",
                "details": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        }


def validate_interval(interval: str) -> Dict[str, Any]:
    """Validate time interval format."""
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


def normalize_symbol(symbol: str) -> str:
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


def validate_inputs(symbol: str, start_date: str, end_date: str, interval: str, request_id: str = None) -> Dict[str, Any]:
    """Comprehensive input validation."""
    # Validate symbol
    symbol_validation = validate_symbol(symbol)
    if not symbol_validation["valid"]:
        return symbol_validation
    
    # Validate date range
    date_validation = validate_date_range(start_date, end_date)
    if not date_validation["valid"]:
        return date_validation
    
    # Validate interval
    interval_validation = validate_interval(interval)
    if not interval_validation["valid"]:
        return interval_validation
    
    return {"valid": True}