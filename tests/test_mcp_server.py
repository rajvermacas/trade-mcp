"""
Tests for MCP server functionality.
Following TDD principles: RED -> GREEN -> REFACTOR
"""

import pytest
from unittest.mock import Mock, patch
import asyncio
import pandas as pd

from trading_mcp.server import TradingMCPServer
from mcp.types import ToolsCapability


class TestTradingMCPServer:
    """Test suite for TradingMCPServer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = TradingMCPServer()
        
    def test_server_initialization(self):
        """Test that TradingMCPServer initializes correctly."""
        server = TradingMCPServer()
        assert server is not None
        assert hasattr(server, 'get_stock_chart_data')
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    @pytest.mark.asyncio
    async def test_get_stock_chart_data_tool(self, mock_ticker):
        """Test get_stock_chart_data as MCP tool."""
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
        
        # Test MCP tool call
        result = await self.server.get_stock_chart_data(
            symbol="RELIANCE",
            start_date="2024-01-01",
            end_date="2024-01-02",
            interval="1h"
        )
        
        assert result["success"] is True
        assert "data" in result
        assert "metadata" in result
        
    def test_get_stock_chart_data_tool_invalid_symbol(self):
        """Test get_stock_chart_data tool with invalid symbol."""
        # Test the validation logic directly
        result = self.server.stock_provider.get_stock_chart_data(
            symbol="INVALID_SYMBOL",  # Use the special test symbol
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_SYMBOL"
        
    def test_server_tools_registration(self):
        """Test that server tools are properly registered."""
        tools = self.server.get_tools()
        assert len(tools) > 0
        
        # Check that get_stock_chart_data is registered
        tool_names = [tool.name for tool in tools]
        assert "get_stock_chart_data" in tool_names
        
    def test_server_resources(self):
        """Test that server resources are properly configured."""
        resources = self.server.get_resources()
        assert isinstance(resources, list)
        
    def test_server_capabilities(self):
        """Test server capabilities."""
        capabilities = self.server.get_capabilities()
        assert capabilities.tools is not None
        assert isinstance(capabilities.tools, ToolsCapability)
        
    @patch('trading_mcp.stock_data.yf.Ticker')
    @pytest.mark.asyncio
    async def test_calculate_technical_indicator_tool(self, mock_ticker):
        """Test calculate_technical_indicator as MCP tool."""
        # Mock the yfinance ticker to provide sufficient data for RSI calculation
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        
        # Create sample data with enough points for RSI (need 14+ days)
        sample_data = pd.DataFrame({
            'Open': [2450.50 + i for i in range(20)],
            'High': [2465.75 + i for i in range(20)],
            'Low': [2445.00 + i for i in range(20)],
            'Close': [2460.25 + i for i in range(20)],
            'Volume': [1250000] * 20
        }, index=pd.date_range('2024-01-01', periods=20, freq='D'))
        
        mock_ticker_instance.history.return_value = sample_data
        
        # Test MCP tool call for RSI indicator
        result = await self.server.calculate_technical_indicator(
            symbol="RELIANCE",
            indicator="RSI",
            start_date="2024-01-01",
            end_date="2024-01-20",
            interval="1d",
            params={"period": 14}
        )
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["indicator"] == "RSI"
        assert "values" in result["data"]
        assert "parameters" in result["data"]
        assert result["data"]["parameters"]["period"] == 14
        assert "metadata" in result
        
    def test_calculate_technical_indicator_tool_invalid_indicator(self):
        """Test calculate_technical_indicator tool with invalid indicator."""
        # This test should fail initially (RED phase)
        # Test the validation logic directly
        result = self.server.stock_provider.calculate_technical_indicator(
            symbol="RELIANCE",
            indicator="INVALID_INDICATOR",
            start_date="2024-01-01",
            end_date="2024-01-20"
        )
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_INDICATOR"
        
    def test_calculate_technical_indicator_registration(self):
        """Test that calculate_technical_indicator tool is properly registered."""
        tools = self.server.get_tools()
        
        # Check that calculate_technical_indicator is registered
        tool_names = [tool.name for tool in tools]
        assert "calculate_technical_indicator" in tool_names

    @pytest.mark.asyncio
    async def test_get_market_news_tool(self):
        """Test get_market_news as MCP tool."""
        # RED: This test should fail since get_market_news tool doesn't exist yet
        result = await self.server.get_market_news(
            query_type="company",
            query="RELIANCE",
            limit=5
        )
        
        assert result["success"] is True
        assert "articles" in result
        assert "metadata" in result
        assert len(result["articles"]) <= 5
        assert result["metadata"]["query_type"] == "company"
        
    @pytest.mark.asyncio
    async def test_get_market_news_tool_market_query(self):
        """Test get_market_news tool with market query."""
        # RED: This test should fail since get_market_news tool doesn't exist yet
        result = await self.server.get_market_news(
            query_type="market",
            limit=10
        )
        
        assert result["success"] is True
        assert "articles" in result
        assert "metadata" in result
        assert result["metadata"]["query_type"] == "market"
        
    def test_get_market_news_tool_registration(self):
        """Test that get_market_news tool is properly registered."""
        # RED: This test should fail since get_market_news tool doesn't exist yet
        tools = self.server.get_tools()
        
        # Check that get_market_news is registered
        tool_names = [tool.name for tool in tools]
        assert "get_market_news" in tool_names
        
    def test_get_market_news_tool_invalid_query_type(self):
        """Test get_market_news tool with invalid query type."""
        # RED: This test should fail since get_market_news tool doesn't exist yet
        result = self.server.stock_provider.get_market_news(
            query_type="invalid_type",
            query="test"
        )
        
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_PARAMETERS"