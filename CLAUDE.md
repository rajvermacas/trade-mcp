# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install package in development mode with dev dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Run unit tests
pytest tests/ -v

# Run unit tests with coverage
pytest tests/ --cov=trading_mcp --cov-report=html

# Run MCP integration tests
python scripts/test_scenarios.py --scenario all

# Interactive testing with MCP client
python scripts/interactive_client.py

# Test specific stock data functionality  
python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE --start-date 2024-01-01 --end-date 2024-01-02
```

### Development
```bash
# Start MCP server for testing
python -m trading_mcp.server

# Run MCP server as CLI tool
trading-mcp

# Install package locally
pip install -e .
```

### Linting and Formatting
```bash
# Note: Per global instructions, this project does NOT use black, flake8, or mypy
# Code formatting and linting is handled manually following the style guide
```

## Architecture Overview

### Core Components

**MCP Server** (`src/trading_mcp/server.py`):
- Main MCP server implementation following Model Context Protocol
- Provides `get_stock_chart_data` tool for retrieving OHLC stock data
- Handles tool registration, capabilities, and MCP protocol communication
- Uses asyncio for concurrent request handling

**Stock Data Provider** (`src/trading_mcp/stock_data.py`):
- Abstracts Yahoo Finance API integration via yfinance library
- Implements caching, validation, and error handling
- Provides NSE stock and index data with automatic symbol normalization
  - Stock symbols: adds .NS suffix (e.g., RELIANCE → RELIANCE.NS)
  - Index symbols: preserves ^ prefix without .NS suffix (e.g., ^NSEI remains ^NSEI)
- Returns structured JSON responses with metadata
- Volume data handling: varies by symbol type and date (stocks always have volume, indices may have zero or non-zero volume depending on market conditions)

### MCP Protocol Integration

This is an MCP (Model Context Protocol) server that enables LLMs to access Indian stock market data:

- **Transport**: Stdio-based communication (JSON-RPC 2.0)
- **Tools**: Single `get_stock_chart_data` tool with structured schema
- **Capabilities**: Tools capability only (no resources or prompts)
- **Data Format**: Returns OHLC data with timestamps in Asia/Kolkata timezone

### Data Flow

1. MCP client (Claude Desktop) sends tool call via stdio
2. Server validates parameters (symbol, dates, interval)
3. StockDataProvider checks cache, then fetches from Yahoo Finance
4. Data is formatted as OHLC JSON with metadata
5. Response returned via MCP protocol

## Project Structure

```
src/trading_mcp/           # Main package
├── server.py              # MCP server implementation
├── stock_data.py          # Yahoo Finance data provider
└── __init__.py

tests/                     # Unit tests
├── test_mcp_server.py     # Server functionality tests
└── test_stock_data.py     # Data provider tests

scripts/                   # Development and testing tools
├── mcp_test_client.py     # Programmatic MCP client
├── interactive_client.py  # Interactive CLI testing
├── test_scenarios.py      # Comprehensive test suites
└── README.md             # Testing documentation

test_data/                 # Test data generation
resources/                 # Documentation and reports
```

## Key Development Patterns

### Error Handling
All functions return structured error responses with:
- `success: false`
- `error.code`: Machine-readable error code
- `error.message`: Human-readable description  
- `error.details`: Additional context for debugging

### Caching Strategy
- Simple in-memory TTL cache (5 minutes) in StockDataProvider
- Cache key includes symbol, date range, and interval
- Cache validation before Yahoo Finance API calls

### Symbol Normalization
NSE symbols are automatically normalized:
- Input: "RELIANCE" → Output: "RELIANCE.NS"
- Required for Yahoo Finance API compatibility

### Testing Approach
- **Unit Tests**: Mock external APIs, test individual components
- **Integration Tests**: Real MCP protocol communication in scripts/
- **Test Scenarios**: Comprehensive test cases for validation and performance
- **Interactive Testing**: Manual exploration via CLI client

## Common Development Workflows

### Adding New MCP Tools

1. Add tool schema to `TradingMCPServer._setup_tools()`
2. Implement tool logic in server class
3. Update `get_tools()` method with tool definition
4. Add unit tests in `tests/test_mcp_server.py`
5. Add test scenarios in `scripts/test_scenarios.py`

### Adding New Data Sources

1. Create new provider class following `StockDataProvider` pattern
2. Implement same interface (`get_stock_chart_data` method)
3. Add comprehensive error handling and validation
4. Implement caching strategy
5. Add unit tests and integration tests

### Performance Optimization

Current targets:
- Response time < 3 seconds for all queries
- Cache hit reduces response to < 0.5 seconds
- Support 50+ concurrent requests

Use `scripts/test_scenarios.py --scenario performance` to validate.

## Integration Notes

### Claude Desktop Setup
Add to Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "trading-mcp": {
      "command": "python",
      "args": ["-m", "trading_mcp.server"],
      "cwd": "/path/to/trade-mcp"
    }
  }
}
```

### API Dependencies
- **yfinance**: Primary data source, may change APIs
- **pandas**: Data manipulation and time series handling
- **mcp**: Official MCP Python SDK for protocol implementation

### Data Limitations
- Yahoo Finance data only (Stage 1 MVP)
- NSE stocks only (Indian market focus)
- No real-time quotes (15-20 minute delay)
- Rate limiting handled by yfinance library

## Troubleshooting

### Common Issues

**Server won't start**: Ensure `pip install -e .` and virtual environment activated

**Import errors**: Check PYTHONPATH includes `src/` directory

**Yahoo Finance errors**: Validate symbol format and check yfinance library updates

**MCP communication errors**: Test with `scripts/interactive_client.py` for debugging

### Development Stage
This is a Stage 1 MVP implementation focused on basic stock data retrieval. Future stages will add:
- Technical indicators (Stage 2)
- Market news integration (Stage 3)  
- Performance optimizations (Stage 4)
- Advanced features (Stage 5)

Refer to `resources/development_plan/trading_mcp_agile_mvp_plan_2025-01-06.md` for detailed roadmap.