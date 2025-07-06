"""
Tests for stock data retrieval functionality.
Following TDD principles: RED -> GREEN -> REFACTOR
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pandas as pd

from trading_mcp.stock_data import StockDataProvider


class TestStockDataProvider:
    """Test suite for StockDataProvider class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = StockDataProvider()
        self.sample_date_start = "2024-01-01"
        self.sample_date_end = "2024-01-02"
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_valid_symbol(self, mock_ticker):
        """Test get_stock_chart_data with valid NSE symbol."""
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data for testing
        sample_data = pd.DataFrame({
            'Open': [2450.50, 2460.25],
            'High': [2465.75, 2470.50],
            'Low': [2445.00, 2455.25],
            'Close': [2460.25, 2455.75],
            'Volume': [1250000, 1100000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=2, freq='1h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        result = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end,
            interval="1h"
        )
        
        # Expected response structure from PRD
        assert result["success"] is True
        assert "data" in result
        assert "metadata" in result
        assert len(result["data"]) > 0
        
        # Check data structure
        first_data_point = result["data"][0]
        assert "timestamp" in first_data_point
        assert "open" in first_data_point
        assert "high" in first_data_point
        assert "low" in first_data_point
        assert "close" in first_data_point
        assert "volume" in first_data_point
        
        # Check metadata structure
        metadata = result["metadata"]
        assert "symbol" in metadata
        assert "interval" in metadata
        assert "currency" in metadata
        assert "timezone" in metadata
        assert "data_points" in metadata
        assert metadata["symbol"] == "RELIANCE.NS"
        assert metadata["currency"] == "INR"
        assert metadata["timezone"] == "Asia/Kolkata"
        
    def test_get_stock_chart_data_invalid_symbol(self):
        """Test get_stock_chart_data with invalid symbol."""
        result = self.provider.get_stock_chart_data(
            symbol="INVALID_SYMBOL",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end
        )
        
        # Should return error response
        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "INVALID_SYMBOL"
        assert "message" in result["error"]
        
    def test_get_stock_chart_data_invalid_date_range(self):
        """Test get_stock_chart_data with invalid date range."""
        result = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date="2024-01-02",
            end_date="2024-01-01"  # End before start
        )
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_DATE_RANGE"
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_default_interval(self, mock_ticker):
        """Test get_stock_chart_data with default interval."""
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Open': [2450.50],
            'High': [2465.75],
            'Low': [2445.00],
            'Close': [2460.25],
            'Volume': [1250000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=1, freq='h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        result = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end
        )
        
        assert result["success"] is True
        assert result["metadata"]["interval"] == "1h"  # Default from PRD
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_various_intervals(self, mock_ticker):
        """Test get_stock_chart_data with various supported intervals."""
        intervals = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data for testing
        sample_data = pd.DataFrame({
            'Open': [2450.50],
            'High': [2465.75],
            'Low': [2445.00],
            'Close': [2460.25],
            'Volume': [1250000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=1, freq='h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        for interval in intervals:
            result = self.provider.get_stock_chart_data(
                symbol="RELIANCE",
                start_date=self.sample_date_start,
                end_date=self.sample_date_end,
                interval=interval
            )
            
            assert result["success"] is True
            assert result["metadata"]["interval"] == interval
            
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_symbol_formats(self, mock_ticker):
        """Test get_stock_chart_data with different symbol formats."""
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Open': [2450.50],
            'High': [2465.75],
            'Low': [2445.00],
            'Close': [2460.25],
            'Volume': [1250000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=1, freq='h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        # Test both "RELIANCE" and "RELIANCE.NS" formats
        for symbol in ["RELIANCE", "RELIANCE.NS"]:
            result = self.provider.get_stock_chart_data(
                symbol=symbol,
                start_date=self.sample_date_start,
                end_date=self.sample_date_end
            )
            
            assert result["success"] is True
            assert result["metadata"]["symbol"] == "RELIANCE.NS"
            
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_response_time(self, mock_ticker):
        """Test that get_stock_chart_data responds within acceptable time limit."""
        import time
        
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Open': [2450.50],
            'High': [2465.75],
            'Low': [2445.00],
            'Close': [2460.25],
            'Volume': [1250000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=1, freq='h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        start_time = time.time()
        result = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end
        )
        end_time = time.time()
        
        assert result["success"] is True
        assert (end_time - start_time) < 3.0  # Under 3 seconds per PRD
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_get_stock_chart_data_caching(self, mock_ticker):
        """Test that repeated calls use caching."""
        # Mock the yfinance ticker
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Open': [2450.50],
            'High': [2465.75],
            'Low': [2445.00],
            'Close': [2460.25],
            'Volume': [1250000]
        }, index=pd.date_range('2024-01-01 10:00:00+05:30', periods=1, freq='h'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        # First call
        result1 = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end
        )
        
        # Second call (should be cached)
        result2 = self.provider.get_stock_chart_data(
            symbol="RELIANCE",
            start_date=self.sample_date_start,
            end_date=self.sample_date_end
        )
        
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["data"] == result2["data"]
        
        # Verify that yfinance was only called once (caching worked)
        assert mock_ticker_instance.history.call_count == 1
        
    def test_stock_data_provider_initialization(self):
        """Test that StockDataProvider initializes correctly."""
        provider = StockDataProvider()
        assert provider is not None
        assert hasattr(provider, 'get_stock_chart_data')