# Trading MCP Server

A Model Context Protocol (MCP) server that provides Indian stock market data to LLMs like Claude Desktop. This Stage 1 MVP focuses on reliable OHLC data delivery with comprehensive logging and debugging capabilities.

## Features

- **Stock Data Access**: Real-time NSE stock data via Yahoo Finance
- **MCP Protocol**: Full compatibility with Claude Desktop and other MCP clients
- **Smart Caching**: 5-minute TTL cache for improved performance
- **Comprehensive Logging**: Production-ready logging system for debugging
- **Error Handling**: Structured error responses with detailed context
- **Input Validation**: Robust validation for symbols, dates, and intervals

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd trade-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in development mode
pip install -e ".[dev]"
```

### Running the Server

```bash
# Start MCP server
python -m trading_mcp.server

# Or use the CLI tool
trading-mcp
```

### Testing

```bash
# Run unit tests
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=trading_mcp --cov-report=html

# Interactive testing
python scripts/interactive_client.py

# Test specific functionality
python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE --start-date 2024-01-01 --end-date 2024-01-02
```

## Claude Desktop Integration

Add to your Claude Desktop MCP configuration (`~/Library/Application Support/Claude/mcp_config.json` on macOS):

```json
{
  "mcpServers": {
    "trading-mcp": {
      "command": "python",
      "args": ["-m", "trading_mcp.server"],
      "cwd": "/path/to/trade-mcp",
      "env": {
        "TRADING_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

After configuration, restart Claude Desktop. You'll be able to ask questions like:
- "Get RELIANCE stock data for the last week"
- "Show me TCS stock price movements for January 2024"
- "Compare INFOSYS and WIPRO stock performance"

## Logging and Debugging

### Overview
When integrated with Claude Desktop, the MCP server runs in the background without visible console output. Our comprehensive logging system ensures you can debug any issues.

### Log Files
All logs are written to `resources/logs/`:

- **`trading_mcp.log`** - Human-readable application logs
- **`trading_mcp_structured.jsonl`** - Structured JSON logs for analysis
- **`trading_mcp_errors.log`** - Error-specific logs with stack traces

### Configuration
Configure logging via environment variables:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
TRADING_MCP_LOG_LEVEL=INFO          # DEBUG for detailed logging
TRADING_MCP_LOG_DIR=resources/logs  # Log directory
TRADING_MCP_LOG_CONSOLE=true        # Console output
TRADING_MCP_LOG_FILE=true           # File logging
TRADING_MCP_LOG_JSON=true           # Structured JSON logs
```

### Common Debugging Tasks

**Monitor real-time activity:**
```bash
tail -f resources/logs/trading_mcp.log
```

**Check for errors:**
```bash
tail -f resources/logs/trading_mcp_errors.log
```

**Analyze performance:**
```bash
# Response times and cache performance
cat resources/logs/trading_mcp_structured.jsonl | jq 'select(.response_time)'
```

**Track specific requests:**
```bash
# Follow a specific stock symbol
grep "RELIANCE" resources/logs/trading_mcp.log
```

For detailed debugging instructions, see [`resources/DEBUGGING_GUIDE.md`](resources/DEBUGGING_GUIDE.md).

## API Reference

### Available Tools

#### get_stock_chart_data

Retrieve OHLC stock chart data for NSE stocks.

**Parameters:**
- `symbol` (string): NSE stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
- `start_date` (string): Start date in ISO format (YYYY-MM-DD)
- `end_date` (string): End date in ISO format (YYYY-MM-DD) 
- `interval` (string): Time interval - "1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo" (default: "1h")

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01T09:15:00+05:30",
      "open": 2500.50,
      "high": 2510.75,
      "low": 2495.25,
      "close": 2505.00,
      "volume": 1234567
    }
  ],
  "metadata": {
    "symbol": "RELIANCE.NS",
    "interval": "1h",
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "data_points": 1
  }
}
```

### Data Format Notes

**Volume Data**: Volume values vary by symbol type and date:
- **Stock symbols** (e.g., RELIANCE.NS): Always have trading volume data
- **Index symbols** (e.g., ^NSEI, ^NSEBANK): Volume data varies by date and market conditions
  - Some dates may have volume data (e.g., 154000 for ^NSEI on Jan 1, 2024)
  - Other dates may show zero volume (e.g., 0 for ^NSEI on Jul 1, 2024)
  - This reflects the actual data from Yahoo Finance and market dynamics

**Symbol Formats**:
- NSE stocks: `RELIANCE` or `RELIANCE.NS` (auto-normalized to `RELIANCE.NS`)
- NSE indices: `^NSEI`, `^NSEBANK`, `^NSEIT` (no .NS suffix added)

## Performance

- **Response Time**: < 3 seconds for all queries
- **Cache Performance**: 5-minute TTL, < 0.5s for cache hits
- **Concurrent Requests**: Supports 50+ concurrent requests
- **Rate Limiting**: Handled by yfinance library

## Architecture

### Core Components

- **MCP Server** (`src/trading_mcp/server.py`): Main MCP protocol handler
- **Stock Data Provider** (`src/trading_mcp/stock_data.py`): Yahoo Finance integration
- **Logging System** (`src/trading_mcp/logging_config.py`): Comprehensive logging

### Data Flow

1. Claude Desktop sends MCP tool call via stdio
2. Server validates parameters and logs request
3. StockDataProvider checks cache, fetches from Yahoo Finance if needed
4. Data formatted as OHLC JSON with Asia/Kolkata timezone
5. Response returned with performance metrics logged

### Caching Strategy

- Simple in-memory TTL cache (5 minutes)
- Cache key: `{symbol}_{start_date}_{end_date}_{interval}`
- Cache validation before external API calls
- Cache performance tracked in logs

## Development

### Project Structure
```
src/trading_mcp/           # Main package
├── server.py              # MCP server implementation  
├── stock_data.py          # Yahoo Finance data provider
├── logging_config.py      # Centralized logging system
└── __init__.py

tests/                     # Unit tests
├── test_mcp_server.py     # Server functionality tests
└── test_stock_data.py     # Data provider tests

scripts/                   # Development tools
├── mcp_test_client.py     # Programmatic MCP client
├── interactive_client.py  # Interactive CLI testing
└── test_scenarios.py      # Comprehensive test suites

resources/                 # Documentation and outputs
├── logs/                  # Log files directory
└── DEBUGGING_GUIDE.md     # Detailed debugging guide
```

### Adding New Features

1. Add tool schema to `TradingMCPServer._setup_tools()`
2. Implement tool logic with comprehensive logging
3. Update `get_tools()` method
4. Add unit tests and integration tests
5. Update documentation

### Contributing

1. Follow the coding guidelines in `CLAUDE.md`
2. Ensure comprehensive test coverage
3. Add appropriate logging for debugging
4. Update documentation

## Limitations

- **Data Source**: Yahoo Finance only (Stage 1 MVP)
- **Market Coverage**: NSE stocks only (Indian market)
- **Real-time Data**: 15-20 minute delay
- **Rate Limiting**: Subject to yfinance library limits

## Roadmap

- **Stage 2**: Technical indicators (RSI, MACD, Moving Averages)
- **Stage 3**: Market news integration
- **Stage 4**: Performance optimizations
- **Stage 5**: Advanced features (options, futures, portfolio tracking)

## Troubleshooting

### Common Issues

**Server won't start:**
- Check log files in `resources/logs/`
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Import errors:**
- Run `pip install -e .` in project root
- Check PYTHONPATH includes `src/` directory

**API errors:**
- Validate symbol format (NSE symbols need .NS suffix)
- Check network connectivity
- Review yfinance library updates

**Performance issues:**
- Monitor cache hit rates in logs
- Check API response times
- Ensure log directory has write permissions

For detailed troubleshooting, see [`resources/DEBUGGING_GUIDE.md`](resources/DEBUGGING_GUIDE.md).

## License

[Add your license here]

## Support

When reporting issues, please include:
- Relevant log snippets from `resources/logs/trading_mcp_errors.log`
- Steps to reproduce the issue
- Environment configuration
- Expected vs actual behavior

---

# Execution Flow
Here's the method execution order for the TradingMCPServer:

## Startup Phase
```
1. main()
2. TradingMCPServer.__init__()
3. StockDataProvider.__init__()
4. _setup_tools()
   ├── @server.list_tools() decorator registration
   ├── @server.list_resources() decorator registration  
   ├── @server.list_prompts() decorator registration
   └── @server.call_tool() decorator registration
5. run()
6. mcp.server.stdio.stdio_server() context manager
7. server.run() with streams and InitializationOptions
```

## MCP Protocol Handlers (invoked by client requests)
```
8. handle_list_tools() → get_tools()
9. handle_list_resources() → get_resources()
10. handle_list_prompts() → returns []
11. handle_tool_call() → routes to specific tool handlers
```

## Tool Call Processing (when tools are invoked)
```
12. _handle_get_stock_chart_data() OR _handle_calculate_technical_indicator()
    ├── GetStockChartDataArgs(**arguments) OR CalculateTechnicalIndicatorArgs(**arguments)
    ├── uuid.uuid4() - generate request ID
    ├── time.time() - start timing
    ├── log_tool_call() - log incoming request
    ├── stock_provider.get_stock_chart_data() OR stock_provider.calculate_technical_indicator()
    ├── log_mcp_response() - log response
    └── TextContent() - format response
```

## Error Handling (if exceptions occur)
```
13. Exception handling in tool methods
    ├── logger.error() - log error details
    ├── Error response formatting
    └── TextContent() with error JSON
```

## Supporting Methods (called as needed)
```
- get_capabilities() - returns ServerCapabilities
- configure_from_env() - logging setup (called at module level)
- get_logger() - logger initialization
```

The core flow is: **startup → handler registration → client communication loop → tool execution → response formatting**.

# TradingMCPServer Flow Mapping to General MCP Pattern

## Overview
This maps the specific TradingMCPServer implementation to the general MCP Server execution flow, showing exactly which methods correspond to each phase.

---

## 1. Server Startup Phase

### General MCP Flow → TradingMCPServer Implementation

| General MCP Method | TradingMCPServer Method | Code Location |
|-------------------|-------------------------|---------------|
| `main()` | `main()` | Line ~480 |
| `setupTransport()` | `mcp.server.stdio.stdio_server()` | Line ~459 |
| `registerHandlers()` | `_setup_tools()` | Line ~46-84 |
| `startListening()` | `server.run()` | Line ~465 |

**TradingMCPServer Startup Flow:**
```python
# 1. Entry point
async def main():
    server = TradingMCPServer()  # 2. Initialize server
    await server.run()           # 3. Start server

# 2. Server initialization
def __init__(self):
    self.server = Server("trading-mcp")     # Create MCP server
    self.stock_provider = StockDataProvider()  # Initialize data provider
    self._setup_tools()                     # Register handlers

# 3. Handler registration
def _setup_tools(self):
    @self.server.list_tools()     # Register list_tools handler
    @self.server.list_resources() # Register list_resources handler  
    @self.server.call_tool()      # Register call_tool handler
```

---

## 2. Client Connection & Handshake

### General Flow → TradingMCPServer

| General MCP | TradingMCPServer | Implementation |
|-------------|------------------|----------------|
| `onConnection()` | Handled by MCP SDK | `stdio_server()` context |
| `handleInitialize()` | Handled by MCP SDK | `InitializationOptions` |
| `handleInitialized()` | Handled by MCP SDK | Automatic |

**TradingMCPServer Handshake:**
```python
# Capabilities negotiation
def get_capabilities(self) -> ServerCapabilities:
    return ServerCapabilities(
        tools=ToolsCapability(),  # Declares tool support
        resources=None,           # No resources
        prompts=None             # No prompts
    )

# Initialization options
InitializationOptions(
    server_name="trading-mcp",
    server_version="1.0.0", 
    capabilities=self.get_capabilities()
)
```

---

## 3. Message Processing Loop

### General Flow → TradingMCPServer

| General MCP | TradingMCPServer | Handler Method |
|-------------|------------------|----------------|
| `receiveMessage()` | Handled by MCP SDK | Automatic |
| `parseMessage()` | Handled by MCP SDK | Automatic |
| `routeMessage()` | `handle_tool_call()` | Line ~84-105 |

**TradingMCPServer Message Routing:**
```python
@self.server.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> List[TextContent]:
    if name == "get_stock_chart_data":
        return await self._handle_get_stock_chart_data(arguments)
    elif name == "calculate_technical_indicator":
        return await self._handle_calculate_technical_indicator(arguments)
    else:
        # Return error for unknown tools
```

---

## 4. Handler Execution by Message Type

### 4.1 List Tools Flow

| General MCP | TradingMCPServer |
|-------------|------------------|
| `handleListTools()` | `handle_list_tools()` → `get_tools()` |

```python
@self.server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return self.get_tools()  # Returns tool definitions

def get_tools(self) -> List[Tool]:
    return [
        Tool(name="get_stock_chart_data", ...),
        Tool(name="calculate_technical_indicator", ...)
    ]
```

### 4.2 Call Tool Flow

| General MCP Method | TradingMCPServer Method | Lines |
|-------------------|-------------------------|-------|
| `handleCallTool()` | `handle_tool_call()` | 84-105 |
| `validateToolParams()` | `GetStockChartDataArgs(**arguments)` | 110, 207 |
| `executeToolFunction()` | `stock_provider.get_stock_chart_data()` | 135-141 |
| `sendResponse()` | `TextContent(text=json.dumps(result))` | 151-155 |

**Detailed Tool Execution Flow:**
```python
# 1. Route to specific handler
async def handle_tool_call(name: str, arguments: dict):
    if name == "get_stock_chart_data":
        return await self._handle_get_stock_chart_data(arguments)

# 2. Validate parameters  
async def _handle_get_stock_chart_data(self, arguments: dict):
    validated_args = GetStockChartDataArgs(**arguments)  # Pydantic validation
    
# 3. Execute tool logic
    result = self.stock_provider.get_stock_chart_data(
        symbol=validated_args.symbol,
        start_date=validated_args.start_date,
        end_date=validated_args.end_date,
        interval=validated_args.interval
    )
    
# 4. Format and return response
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

---

## 5. Error Handling

### General Flow → TradingMCPServer

| General MCP | TradingMCPServer | Implementation |
|-------------|------------------|----------------|
| `onError()` | `except Exception as e:` | Lines 157-190, 263-296 |
| `formatErrorResponse()` | Error dict creation | Lines 174-184 |
| `sendError()` | `TextContent` with error | Lines 186-190 |

**TradingMCPServer Error Handling:**
```python
try:
    # Tool execution
    result = self.stock_provider.get_stock_chart_data(...)
except Exception as e:
    # Log error
    logger.error(f"Tool call failed: {str(e)}", ...)
    
    # Format error response
    error_result = {
        "success": False,
        "error": {
            "code": "TOOL_EXECUTION_ERROR", 
            "message": f"Failed to execute tool: {str(e)}",
            "details": {...}
        }
    }
    
    # Return error as TextContent
    return [TextContent(type="text", text=json.dumps(error_result))]
```

---

## 6. Key Method Mappings

### Server Lifecycle Methods

| Phase | General MCP | TradingMCPServer |
|-------|-------------|------------------|
| **Startup** | `main()` | `main()` (line 480) |
| **Init** | `__init__()` | `TradingMCPServer.__init__()` (line 29) |
| **Setup** | `registerHandlers()` | `_setup_tools()` (line 46) |
| **Run** | `startListening()` | `run()` (line 437) |

### Protocol Handlers

| Handler Type | General MCP | TradingMCPServer |
|-------------|-------------|------------------|
| **Tools List** | `handleListTools()` | `handle_list_tools()` → `get_tools()` |
| **Resources List** | `handleListResources()` | `handle_list_resources()` → `get_resources()` |  
| **Tool Call** | `handleCallTool()` | `handle_tool_call()` → tool-specific handlers |

### Tool-Specific Handlers

| Tool | Handler Method | Validation | Execution | Response |
|------|----------------|------------|-----------|----------|
| **Chart Data** | `_handle_get_stock_chart_data()` | `GetStockChartDataArgs()` | `stock_provider.get_stock_chart_data()` | `TextContent` |
| **Indicators** | `_handle_calculate_technical_indicator()` | `CalculateTechnicalIndicatorArgs()` | `stock_provider.calculate_technical_indicator()` | `TextContent` |

---

## 7. Execution Flow Comparison

### General MCP Flow
```
startup → registerHandlers → startListening → 
receiveMessage → routeMessage → executeHandler → sendResponse
```

### TradingMCPServer Flow  
```
main() → TradingMCPServer.__init__() → _setup_tools() → run() →
[MCP SDK handles protocol] → handle_tool_call() → 
_handle_get_stock_chart_data() → stock_provider.get_stock_chart_data() → 
TextContent(json.dumps(result))
```

---

## 8. What MCP SDK Handles vs Custom Code

### MCP SDK Handles Automatically:
- Message parsing (`parseMessage()`)
- Protocol validation (`validateMessage()`) 
- Connection management (`onConnection()`)
- Initialize handshake (`handleInitialize()`)
- JSON-RPC transport

### TradingMCPServer Custom Implementation:
- Tool definitions (`get_tools()`)
- Parameter validation (`GetStockChartDataArgs`)
- Business logic (`stock_provider` methods)
- Error formatting (custom error responses)
- Logging (`log_tool_call`, `log_mcp_response`)

The TradingMCPServer focuses on **business logic** while the MCP SDK handles **protocol mechanics**.