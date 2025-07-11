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
| `main()` | `main()` | Line 528-531 |
| `setupTransport()` | `mcp.server.stdio.stdio_server()` | Line 492 |
| `registerHandlers()` | `_setup_tools()` | Line 62-110 |
| `startListening()` | `server.run()` | Line 498 |

**TradingMCPServer Startup Flow:**
```python
# 1. Entry point (line 528)
async def main():
    server = TradingMCPServer()  # 2. Initialize server
    await server.run()           # 3. Start server

# 2. Server initialization (line 52)
def __init__(self):
    self.server = Server("trading-mcp")     # Create MCP server
    self.stock_provider = StockDataProvider()  # Initialize data provider
    self._setup_tools()                     # Register handlers

# 3. Handler registration (line 62)
def _setup_tools(self):
    @self.server.list_tools()     # Register list_tools handler (line 65)
    @self.server.list_resources() # Register list_resources handler (line 70)
    @self.server.list_prompts()   # Register list_prompts handler (line 75)
    @self.server.call_tool()      # Register call_tool handler (line 80)
```

### Detailed Server Initialization Process

**Step 1: Configuration and Logging Setup**
- Module-level `configure_from_env()` called (line 21)
- Logger initialization with `get_logger(__name__)` (line 22)

**Step 2: Server Object Creation**
- `TradingMCPServer()` constructor called (line 52)
- Creates MCP Server instance with name "trading-mcp" (line 54)
- Initializes `StockDataProvider` instance (line 55)
- Calls `_setup_tools()` for handler registration (line 56)

**Step 3: Handler Registration via Decorators**
- `@self.server.list_tools()` → `handle_list_tools()` (line 65-68)
- `@self.server.list_resources()` → `handle_list_resources()` (line 70-73)
- `@self.server.list_prompts()` → `handle_list_prompts()` (line 75-78)
- `@self.server.call_tool()` → `handle_tool_call()` (line 80-110)

**Step 4: Server Startup**
- `run()` method called with stdio transport (line 478)
- Creates stdio server context manager (line 492)
- Initializes with `InitializationOptions` (line 501-506)
- Begins listening for MCP protocol messages

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
| `handleCallTool()` | `handle_tool_call()` | 80-110 |
| `validateToolParams()` | `GetStockChartDataArgs(**arguments)` | 124, 234 |
| `executeToolFunction()` | `stock_provider.get_stock_chart_data()` | 158-164 |
| `sendResponse()` | `TextContent(text=json.dumps(result))` | 179-184 |

**Detailed Tool Execution Flow:**
```python
# 1. Route to specific handler (line 80)
async def handle_tool_call(name: str, arguments: dict):
    if name == "get_stock_chart_data":
        return await self._handle_get_stock_chart_data(arguments)
    elif name == "calculate_technical_indicator":
        return await self._handle_calculate_technical_indicator(arguments)

# 2. Validate parameters (line 124)
async def _handle_get_stock_chart_data(self, arguments: dict):
    validated_args = GetStockChartDataArgs(**arguments)  # Pydantic validation
    
# 3. Generate request tracking (line 141-142)
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
# 4. Log incoming request (line 145-155)
    log_tool_call(logger, tool_name="get_stock_chart_data", ...)
    
# 5. Execute tool logic (line 158-164)
    result = self.stock_provider.get_stock_chart_data(
        symbol=validated_args.symbol,
        start_date=validated_args.start_date,
        end_date=validated_args.end_date,
        interval=validated_args.interval,
        request_id=request_id
    )
    
# 6. Log response metrics (line 166-176)
    response_time = (time.time() - start_time) * 1000
    log_mcp_response(logger, method="get_stock_chart_data", ...)
    
# 7. Format and return response (line 179-184)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

### Complete Tool Handler Method Structure

**get_stock_chart_data Handler (`_handle_get_stock_chart_data` - line 112):**
1. Parameter validation using `GetStockChartDataArgs` (line 124)
2. Request ID generation and timing start (line 141-142)
3. Structured logging of incoming request (line 145-155)
4. Stock data provider execution (line 158-164)
5. Response time calculation and logging (line 166-176)
6. JSON response formatting (line 179-184)
7. Exception handling with detailed error logging (line 186-220)

**calculate_technical_indicator Handler (`_handle_calculate_technical_indicator` - line 222):**
1. Parameter validation using `CalculateTechnicalIndicatorArgs` (line 234)
2. Request ID generation and timing start (line 251-252)
3. Structured logging of incoming request (line 255-267)
4. Technical indicator calculation (line 270-278)
5. Response time calculation and logging (line 280-290)
6. JSON response formatting (line 293-298)
7. Exception handling with detailed error logging (line 300-336)

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

## 8. Supporting Methods and Utilities

### Method Execution Context

**Direct Access Methods (for testing):**
- `fetch_stock_chart_data()` (line 339-363) - Direct access to stock data
- `compute_technical_indicator()` (line 365-395) - Direct access to indicators

**Configuration Methods:**
- `get_tools()` (line 398-464) - Returns tool definitions with JSON schemas
- `get_resources()` (line 466-468) - Returns empty resources list
- `get_capabilities()` (line 470-476) - Returns server capabilities

**Pydantic Models for Validation:**
- `GetStockChartDataArgs` (line 25-31) - Validates stock data parameters
- `CalculateTechnicalIndicatorArgs` (line 33-41) - Validates indicator parameters

### Request Lifecycle Methods

**Per-Request Execution Flow:**
```python
# 1. MCP client request received
handle_tool_call(name, arguments)

# 2. Route to handler
if name == "get_stock_chart_data":
    _handle_get_stock_chart_data(arguments)

# 3. Validate and track
GetStockChartDataArgs(**arguments)  # Pydantic validation
request_id = str(uuid.uuid4())      # Generate tracking ID
start_time = time.time()            # Start timing

# 4. Log request
log_tool_call(logger, tool_name, symbol, params, request_id)

# 5. Execute business logic
stock_provider.get_stock_chart_data(...)

# 6. Log response
response_time = (time.time() - start_time) * 1000
log_mcp_response(logger, method, response_time, success, request_id)

# 7. Format response
TextContent(type="text", text=json.dumps(result, indent=2))
```

---

## 9. What MCP SDK Handles vs Custom Code

### MCP SDK Handles Automatically:
- Message parsing (`parseMessage()`)
- Protocol validation (`validateMessage()`) 
- Connection management (`onConnection()`)
- Initialize handshake (`handleInitialize()`)
- JSON-RPC transport
- Stdio stream management
- Request/response correlation

### TradingMCPServer Custom Implementation:
- Tool definitions (`get_tools()`)
- Parameter validation (`GetStockChartDataArgs`, `CalculateTechnicalIndicatorArgs`)
- Business logic (`stock_provider` methods)
- Error formatting (custom error responses)
- Logging (`log_tool_call`, `log_mcp_response`)
- Request tracking (UUID generation, timing)
- Response formatting (JSON structure)

The TradingMCPServer focuses on **business logic** while the MCP SDK handles **protocol mechanics**.

---

## 10. Complete Method Execution Order

### Server Startup Sequence:
```
1. main() (528)
2. TradingMCPServer.__init__() (52)
3. Server("trading-mcp") (54)
4. StockDataProvider() (55)
5. _setup_tools() (56)
6. @server.list_tools() decorator (65)
7. @server.list_resources() decorator (70)
8. @server.list_prompts() decorator (75)
9. @server.call_tool() decorator (80)
10. run() (478)
11. stdio_server() context (492)
12. server.run() with InitializationOptions (498)
```

### Per-Request Execution (get_stock_chart_data):
```
1. handle_tool_call() (80)
2. _handle_get_stock_chart_data() (112)
3. GetStockChartDataArgs(**arguments) (124)
4. uuid.uuid4() (141)
5. time.time() (142)
6. log_tool_call() (145)
7. stock_provider.get_stock_chart_data() (158)
8. response_time calculation (166)
9. log_mcp_response() (170)
10. TextContent(json.dumps(result)) (179)
```

### Error Handling Flow:
```
1. Exception caught in try/except (186)
2. logger.error() with structured data (189)
3. Error response dict creation (202)
4. TextContent(json.dumps(error_result)) (215)
```