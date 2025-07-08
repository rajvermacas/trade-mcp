"""
MCP Server for Trading Data.
"""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, ServerCapabilities, ToolsCapability, TextContent
from pydantic import BaseModel, Field
from .stock_data import StockDataProvider
from .logging_config import (
    get_logger, log_mcp_request, log_mcp_response, 
    log_tool_call, configure_from_env
)

# Configure logging
configure_from_env()
logger = get_logger(__name__)


class GetStockChartDataArgs(BaseModel):
    """Arguments for get_stock_chart_data tool."""
    symbol: str = Field(description="NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')")
    start_date: str = Field(description="Start date in ISO format (YYYY-MM-DD)")
    end_date: str = Field(description="End date in ISO format (YYYY-MM-DD)")
    interval: str = Field(default="1h", description="Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")


class CalculateTechnicalIndicatorArgs(BaseModel):
    """Arguments for calculate_technical_indicator tool."""
    symbol: str = Field(description="NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')")
    indicator: str = Field(description="Technical indicator name (e.g., 'RSI', 'MACD', 'SMA')")
    start_date: str = Field(description="Start date in ISO format (YYYY-MM-DD)")
    end_date: str = Field(description="End date in ISO format (YYYY-MM-DD)")
    interval: str = Field(default="1d", description="Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Optional parameters for the indicator")




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
        logger.info(
            "TradingMCPServer initialized",
            extra={"component": "server", "action": "init"}
        )
    
    def _setup_tools(self):
        """Set up MCP tools."""
        # Register list handlers
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return self.get_tools()
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Dict[str, Any]]:
            """List available resources."""
            return self.get_resources()
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Dict[str, Any]]:
            """List available prompts."""
            return []
        
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: dict) -> List[TextContent]:
            """
            Handle tool calls by routing to appropriate handlers based on tool name.
            
            Args:
                name: Tool name to call
                arguments: Tool arguments dictionary
                
            Returns:
                List of text content items with JSON response
            """
            if name == "get_stock_chart_data":
                return await self._handle_get_stock_chart_data(arguments)
            elif name == "calculate_technical_indicator":
                return await self._handle_calculate_technical_indicator(arguments)
            else:
                error_result = {
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_TOOL",
                        "message": f"Unknown tool: {name}",
                        "details": {"tool_name": name}
                    }
                }
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(error_result, indent=2)
                    )
                ]
    
    async def _handle_get_stock_chart_data(self, arguments: dict) -> List[TextContent]:
        """
        Handle get_stock_chart_data tool calls.
        
        Args:
            arguments: Tool arguments dictionary
                
        Returns:
            List of text content items with JSON response
        """
        try:
            # Validate arguments using Pydantic model
            validated_args = GetStockChartDataArgs(**arguments)
        except Exception as e:
            error_result = {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENTS",
                    "message": f"Invalid arguments for get_stock_chart_data: {str(e)}",
                    "details": {"arguments": arguments}
                }
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(error_result, indent=2)
                )
            ]
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log the incoming tool call
        log_tool_call(
            logger,
            tool_name="get_stock_chart_data",
            symbol=validated_args.symbol,
            params={
                "start_date": validated_args.start_date,
                "end_date": validated_args.end_date,
                "interval": validated_args.interval
            },
            request_id=request_id
        )
        
        try:
            result = self.stock_provider.get_stock_chart_data(
                symbol=validated_args.symbol,
                start_date=validated_args.start_date,
                end_date=validated_args.end_date,
                interval=validated_args.interval,
                request_id=request_id
            )
            
            response_time = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            # Log the response
            log_mcp_response(
                logger,
                method="get_stock_chart_data",
                response_time=response_time,
                success=success,
                request_id=request_id
            )
            
            # Return in MCP content format
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            logger.error(
                f"Tool call failed: {str(e)}",
                extra={
                    "mcp_request_id": request_id,
                    "tool_name": "get_stock_chart_data",
                    "symbol": validated_args.symbol,
                    "response_time": response_time,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Return error response
            error_result = {
                "success": False,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": f"Failed to execute tool: {str(e)}",
                    "details": {
                        "tool": "get_stock_chart_data",
                        "symbol": validated_args.symbol,
                        "request_id": request_id
                    }
                }
            }
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(error_result, indent=2)
                )
            ]
    
    async def _handle_calculate_technical_indicator(self, arguments: dict) -> List[TextContent]:
        """
        Handle calculate_technical_indicator tool calls.
        
        Args:
            arguments: Tool arguments dictionary
                
        Returns:
            List of text content items with JSON response
        """
        try:
            # Validate arguments using Pydantic model
            validated_args = CalculateTechnicalIndicatorArgs(**arguments)
        except Exception as e:
            error_result = {
                "success": False,
                "error": {
                    "code": "INVALID_ARGUMENTS",
                    "message": f"Invalid arguments for calculate_technical_indicator: {str(e)}",
                    "details": {"arguments": arguments}
                }
            }
            return [
                TextContent(
                    type="text",
                    text=json.dumps(error_result, indent=2)
                )
            ]
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log the incoming tool call
        log_tool_call(
            logger,
            tool_name="calculate_technical_indicator",
            symbol=validated_args.symbol,
            params={
                "indicator": validated_args.indicator,
                "start_date": validated_args.start_date,
                "end_date": validated_args.end_date,
                "interval": validated_args.interval,
                "params": validated_args.params
            },
            request_id=request_id
        )
        
        try:
            result = self.stock_provider.calculate_technical_indicator(
                symbol=validated_args.symbol,
                indicator=validated_args.indicator,
                start_date=validated_args.start_date,
                end_date=validated_args.end_date,
                interval=validated_args.interval,
                params=validated_args.params,
                request_id=request_id
            )
            
            response_time = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            # Log the response
            log_mcp_response(
                logger,
                method="calculate_technical_indicator",
                response_time=response_time,
                success=success,
                request_id=request_id
            )
            
            # Return in MCP content format
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            logger.error(
                f"Tool call failed: {str(e)}",
                extra={
                    "mcp_request_id": request_id,
                    "tool_name": "calculate_technical_indicator",
                    "symbol": validated_args.symbol,
                    "indicator": validated_args.indicator,
                    "response_time": response_time,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Return error response
            error_result = {
                "success": False,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": f"Failed to execute tool: {str(e)}",
                    "details": {
                        "tool": "calculate_technical_indicator",
                        "symbol": validated_args.symbol,
                        "indicator": validated_args.indicator,
                        "request_id": request_id
                    }
                }
            }
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(error_result, indent=2)
                )
            ]
        
    
    async def fetch_stock_chart_data(
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
    
    async def compute_technical_indicator(
        self,
        symbol: str,
        indicator: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Direct method for calculating technical indicators (for testing).
        
        Args:
            symbol: Stock symbol
            indicator: Indicator name
            start_date: Start date
            end_date: End date
            interval: Time interval
            params: Optional indicator parameters
            
        Returns:
            Technical indicator response
        """
        return self.stock_provider.calculate_technical_indicator(
            symbol=symbol,
            indicator=indicator,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            params=params
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
            ),
            Tool(
                name="calculate_technical_indicator",
                description="Calculate technical indicators for NSE stocks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "NSE stock symbol (e.g., 'RELIANCE' or 'RELIANCE.NS')"
                        },
                        "indicator": {
                            "type": "string",
                            "description": "Technical indicator name (e.g., 'RSI', 'MACD', 'SMA')"
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
                            "default": "1d"
                        },
                        "params": {
                            "type": "object",
                            "description": "Optional parameters for the indicator",
                            "default": {}
                        }
                    },
                    "required": ["symbol", "indicator", "start_date", "end_date"]
                }
            ),
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources."""
        return []
    
    def get_capabilities(self) -> ServerCapabilities:
        """Get server capabilities."""
        return ServerCapabilities(
            tools=ToolsCapability(),
            resources=None,
            prompts=None
        )
    
    async def run(self, transport_uri: str = "stdio://"):
        """Run the MCP server."""
        logger.info(
            f"Starting Trading MCP Server on {transport_uri}",
            extra={
                "component": "server",
                "action": "start",
                "transport": transport_uri
            }
        )
        
        try:
            if transport_uri == "stdio://":
                import mcp.server.stdio
                async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                    logger.info(
                        "MCP Server ready for stdio communication",
                        extra={"component": "server", "action": "ready"}
                    )
                    
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
                logger.error(
                    f"Unsupported transport type: {transport_uri}",
                    extra={"component": "server", "transport": transport_uri}
                )
                raise NotImplementedError(f"Transport {transport_uri} not implemented yet")
                
        except Exception as e:
            logger.error(
                f"Server failed to start: {str(e)}",
                extra={
                    "component": "server",
                    "action": "start_failed",
                    "error": str(e)
                },
                exc_info=True
            )
            raise


async def main():
    """Main entry point for the server."""
    server = TradingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())