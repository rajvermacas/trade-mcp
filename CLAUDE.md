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
# Run unit tests with TDD approach
pytest tests/ -v

# Run unit tests with coverage
pytest tests/ --cov=trading_mcp --cov-report=html

# Run comprehensive MCP integration tests
python scripts/test_scenarios.py --scenario all

# Run performance benchmarks
python scripts/test_scenarios.py --scenario performance

# Interactive testing with MCP client
python scripts/interactive_client.py

# Test specific stock data functionality  
python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE --start-date 2024-01-01 --end-date 2024-01-02

# Test technical indicators (Enhanced Supertrend)
python scripts/test_enhanced_supertrend.py
python scripts/mcp_test_client.py --function calculate_technical_indicator --symbol RELIANCE --indicator ENHANCED_SUPERTREND --start-date 2024-01-01 --end-date 2024-01-02

# Test NSE indices and volume patterns
python scripts/test_known_indices.py
python scripts/test_volume_patterns.py
```

### Development and Debugging
```bash
# Start MCP server for testing
python -m trading_mcp.server

# Run MCP server as CLI tool
trading-mcp

# Monitor real-time MCP activity
tail -f resources/logs/trading_mcp.log

# Debug MCP protocol communication
python scripts/simple_test.py

# Direct testing bypassing MCP protocol
python scripts/test_direct.py

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
- Implements advanced caching strategy with LRU cache (100 entries, 5-minute TTL)
- Circuit breaker pattern for API resilience (5 failure threshold, 30s recovery)
- Performance monitoring with response time tracking and cache statistics
- Provides NSE stock and index data with automatic symbol normalization
  - Stock symbols: adds .NS suffix (e.g., RELIANCE → RELIANCE.NS)
  - Index symbols: preserves ^ prefix without .NS suffix (e.g., ^NSEI remains ^NSEI)
- Returns structured JSON responses with metadata
- Volume data handling: varies by symbol type and date (stocks always have volume, indices may have zero or non-zero volume depending on market conditions)

**Technical Indicators System** (`src/trading_mcp/indicators/`):
- **38+ Technical Indicators** across 5 categories (Trend, Momentum, Volatility, Volume, Custom)
- **IndicatorRegistry** with unified interface for all indicator calculations
- **Enhanced Supertrend** indicator with ML-based signal strength scoring (0-8 scale)
- **pandas_ta Integration** providing industry-standard calculations
- **Parameter Validation** with automatic type conversion and default parameter application
- **Data Requirements Validation** ensuring proper column availability before calculation
- Supported indicators include: RSI, SMA, EMA, WMA, DEMA, TEMA, MACD, ADX, AROON, CCI, CMO, WILLR, MFI, TRIX, ROC, BBANDS, ATR, NATR, STDDEV, AD, ADOSC, OBV, VWAP, EMV, FI, SUPERTREND, ICHIMOKU, and more
- Configurable parameters for all indicators via the `params` field
- Returns time-series data with buy/sell signals and trend analysis

**Logging System** (`src/trading_mcp/logging_config.py`):
- Structured logging with JSON format for analysis
- Multiple output streams: console, file, and structured JSONL
- Performance metrics tracking (response times, cache hit rates)
- Error tracking with stack traces and context
- Real-time monitoring capabilities for debugging MCP communication

### MCP Protocol Integration

This is an MCP (Model Context Protocol) server that enables LLMs to access Indian stock market data:

- **Transport**: Stdio-based communication (JSON-RPC 2.0)
- **Tools**: Dual tool support (`get_stock_chart_data` and `calculate_technical_indicator`)
- **Capabilities**: Tools capability only (no resources or prompts)
- **Data Format**: Returns OHLC data and indicator values with timestamps in Asia/Kolkata timezone
- **Request Tracking**: UUID-based request tracking with performance metrics
- **Error Handling**: Structured error responses with machine-readable error codes

### Data Flow

1. MCP client (Claude Desktop) sends tool call via stdio
2. Server validates parameters using Pydantic models
3. Request tracking initiated (UUID, start time, structured logging)
4. StockDataProvider checks LRU cache with circuit breaker validation
5. On cache miss, fetches from Yahoo Finance with error handling
6. For technical indicators, processes data through indicator calculations
7. Data formatted as JSON with metadata and performance metrics
8. Response returned via MCP protocol with timing information logged

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

### Adding New Technical Indicators

1. Create indicator class in `src/trading_mcp/indicators/` following `EnhancedSupertrendIndicator` pattern
2. Implement `calculate()` method with proper parameter validation
3. Add indicator to `SUPPORTED_INDICATORS` mapping in `stock_data.py`
4. Create test file in `tests/` with comprehensive test cases
5. Add integration tests in `scripts/test_scenarios.py`
6. Update tool schema in `get_tools()` method documentation

### Adding New MCP Tools

1. Add Pydantic model for arguments (e.g., `NewToolArgs` class)
2. Add tool handler method (e.g., `_handle_new_tool()`) with logging
3. Update `handle_tool_call()` routing in `_setup_tools()`
4. Add tool definition to `get_tools()` method with JSON schema
5. Add unit tests in `tests/test_mcp_server.py` with mocked dependencies
6. Add integration test scenarios in `scripts/test_scenarios.py`

### MCP Debugging Workflow

1. **Check MCP Protocol Communication**:
   ```bash
   python scripts/simple_test.py  # Basic MCP connectivity
   python scripts/interactive_client.py  # Interactive debugging
   ```

2. **Monitor Real-time Activity**:
   ```bash
   tail -f resources/logs/trading_mcp.log  # Human-readable logs
   tail -f resources/logs/trading_mcp_structured.jsonl  # JSON logs
   ```

3. **Analyze Performance Issues**:
   ```bash
   cat resources/logs/trading_mcp_structured.jsonl | jq 'select(.response_time > 1000)'  # Slow requests
   cat resources/logs/trading_mcp_structured.jsonl | jq 'select(.cache_hit == true)'  # Cache performance
   ```

4. **Test Without MCP Protocol**:
   ```bash
   python scripts/test_direct.py  # Direct function calls
   python scripts/test_enhanced_supertrend_direct.py  # Indicator testing
   ```

### Adding New Data Sources

1. Create new provider class following `StockDataProvider` pattern
2. Implement same interface (`get_stock_chart_data` method)
3. Add comprehensive error handling and validation
4. Implement caching strategy with circuit breaker
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

### Key Technical Dependencies
- **yfinance**: Primary data source, may change APIs
- **pandas**: Data manipulation and time series handling  
- **pandas_ta**: Technical analysis indicators library
- **mcp**: Official MCP Python SDK for protocol implementation
- **pydantic**: Data validation and serialization
- **cachetools**: Advanced caching with LRU strategy
- **psutil**: System performance monitoring

### Configuration Files
- **pyproject.toml**: Package configuration with dependencies and entry points
- **CLAUDE.md**: Development guidance (this file)
- **resources/logs/**: Runtime logs directory for debugging

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

**Current Status**: Stage 2+ Implementation
- ✅ **Stage 1**: Stock data access and MCP protocol integration
- ✅ **Stage 2**: Technical indicators (Enhanced Supertrend, RSI, MACD, Moving Averages)
- ✅ **Stage 2+**: Advanced caching, logging, and performance optimization

**Future Roadmap**:
- **Stage 3**: Market news integration
- **Stage 4**: Real-time data streaming  
- **Stage 5**: Advanced features (options, futures, portfolio tracking)

Refer to `resources/development_plan/trading_mcp_agile_mvp_plan_2025-01-06.md` for detailed roadmap.