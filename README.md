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