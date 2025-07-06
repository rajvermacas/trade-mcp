"""
MCP Server for Trading Data.
"""

import asyncio
import logging
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, AnyUrl
from pydantic import BaseModel, Field
from .stock_data import StockDataProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GetStockChartDataArgs(BaseModel):
    """Arguments for get_stock_chart_data tool."""
    symbol: str = Field(description="NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')")
    start_date: str = Field(description="Start date in ISO format (YYYY-MM-DD)")
    end_date: str = Field(description="End date in ISO format (YYYY-MM-DD)")
    interval: str = Field(default="1h", description="Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")


class TradingMCPServer:
    """
    MCP Server for trading data operations.
    
    Provides stock market data through MCP protocol for LLM consumption.
    """
    
    def __init__(self):
        """Initialize the Trading MCP Server."""
        self.server = Server("trading-mcp")
        self.stock_provider = StockDataProvider()
        self._setup_tools()
        logger.info("TradingMCPServer initialized")
    
    def _setup_tools(self):
        """Set up MCP tools."""
        @self.server.call_tool()
        async def get_stock_chart_data(arguments: GetStockChartDataArgs) -> Dict[str, Any]:
            """
            Retrieve OHLC stock chart data for NSE stocks.
            
            Args:
                arguments: GetStockChartDataArgs containing symbol, dates, and interval
                
            Returns:
                Dictionary with success status, data, and metadata
            """
            logger.info(f"get_stock_chart_data called with symbol: {arguments.symbol}")
            
            result = self.stock_provider.get_stock_chart_data(
                symbol=arguments.symbol,
                start_date=arguments.start_date,
                end_date=arguments.end_date,
                interval=arguments.interval
            )
            
            return result
    
    async def get_stock_chart_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """
        Direct method for getting stock chart data (for testing).
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Time interval
            
        Returns:
            Stock data response
        """
        return self.stock_provider.get_stock_chart_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
    
    def get_tools(self) -> List[Tool]:
        """Get list of available tools."""
        return [
            Tool(
                name="get_stock_chart_data",
                description="Retrieve OHLC stock chart data for NSE stocks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in ISO format (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in ISO format (YYYY-MM-DD)"
                        },
                        "interval": {
                            "type": "string",
                            "description": "Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)",
                            "default": "1h"
                        }
                    },
                    "required": ["symbol", "start_date", "end_date"]
                }
            )
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources."""
        return []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        return {
            "tools": True,
            "resources": False,
            "prompts": False
        }
    
    async def run(self, transport_uri: str = "stdio://"):
        """Run the MCP server."""
        logger.info(f"Starting Trading MCP Server on {transport_uri}")
        
        if transport_uri == "stdio://":
            import mcp.server.stdio
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="trading-mcp",
                        server_version="1.0.0",
                        capabilities=self.get_capabilities()
                    )
                )
        else:
            # For other transport types (future enhancement)
            raise NotImplementedError(f"Transport {transport_uri} not implemented yet")


async def main():
    """Main entry point for the server."""
    server = TradingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())