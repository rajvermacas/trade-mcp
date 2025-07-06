# MCP Test Client for Trading MCP Server

This directory contains comprehensive testing tools for the Trading MCP server that enable rapid development and testing without requiring Claude Desktop.

## Overview

The MCP Test Client provides three main tools:

1. **Core Test Client** (`mcp_test_client.py`) - Programmatic MCP client implementation
2. **Interactive Client** (`interactive_client.py`) - Interactive CLI for manual testing
3. **Test Scenarios** (`test_scenarios.py`) - Comprehensive automated test suites

## Quick Start

### 1. Install Dependencies

First, ensure you have the development dependencies installed:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dev dependencies (includes rich and click for test clients)
pip install -e ".[dev]"
```

### 2. Start Interactive Testing

For manual testing and exploration:

```bash
python scripts/interactive_client.py
```

This opens an interactive menu where you can:
- Test stock data retrieval with custom parameters
- Run predefined test scenarios
- View server capabilities and available tools
- Perform custom tool calls
- Run performance benchmarks

### 3. Run Automated Tests

For comprehensive automated testing:

```bash
# Run all test scenarios
python scripts/test_scenarios.py --scenario all

# Run specific category
python scripts/test_scenarios.py --scenario basic
python scripts/test_scenarios.py --scenario validation
python scripts/test_scenarios.py --scenario performance

# List available scenarios
python scripts/test_scenarios.py --list
```

### 4. Programmatic Testing

For custom testing or integration into CI/CD:

```bash
# Run all predefined tests
python scripts/mcp_test_client.py --test-all

# Test specific function
python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE --start-date 2024-01-01 --end-date 2024-01-02
```

## Detailed Usage

### Interactive Client (`interactive_client.py`)

The interactive client provides a menu-driven interface for testing:

```
🚀 Interactive MCP Test Client for Trading MCP Server
============================================================
Available Commands:
  1. Test stock data retrieval
  2. Run predefined test scenarios
  3. Show server capabilities
  4. Show available tools
  5. Custom tool call
  6. Performance benchmark
  h. Show this help
  q. Quit
```

**Features:**
- Real-time parameter input with validation
- Formatted output display with rich formatting
- Performance timing for each request
- Error handling and debugging information
- Session logging and history

**Example Usage:**
1. Select option `1` to test stock data
2. Enter symbol: `RELIANCE`
3. Enter dates: `2024-01-01` to `2024-01-02`
4. Select interval: `1h`
5. View formatted results with timing information

### Test Scenarios (`test_scenarios.py`)

Comprehensive test suites organized by category:

#### Available Categories

1. **Basic** - Core functionality tests
   - Valid symbol retrieval (RELIANCE, TCS, INFY)
   - Default parameter handling
   - Different time intervals

2. **Validation** - Input validation tests
   - Invalid symbols
   - Invalid date ranges
   - Invalid date formats
   - Invalid intervals
   - Empty parameters

3. **Intervals** - Time interval testing
   - 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
   - Interval-specific validation

4. **Performance** - Response time benchmarks
   - Quick response tests (< 3 seconds)
   - Medium dataset tests (< 5 seconds)
   - Large dataset tests (< 10 seconds)

5. **Edge Cases** - Boundary condition testing
   - Weekend dates (no trading)
   - Holiday dates
   - Future dates
   - Very short time ranges

6. **Caching** - Cache functionality validation
   - Cache hit testing
   - Cache miss testing
   - Performance improvements

#### Running Specific Categories

```bash
# Basic functionality tests
python scripts/test_scenarios.py --scenario basic

# Input validation tests
python scripts/test_scenarios.py --scenario validation

# Performance benchmarks
python scripts/test_scenarios.py --scenario performance

# All edge cases
python scripts/test_scenarios.py --scenario edge_cases
```

#### Test Report Format

```
📊 Test Report
============================================================
Total Tests: 25
Passed: 23
Failed: 2
Success Rate: 92.0%
Average Execution Time: 1.45s

📋 Results by Category:
  basic: 4/4 (100.0%)
  validation: 5/5 (100.0%)
  intervals: 6/6 (100.0%)
  performance: 3/3 (100.0%)
  edge_cases: 3/4 (75.0%)
  caching: 2/2 (100.0%)

❌ Failed Tests:
  • Weekend Date Range - Expected min 0 data points, got error
```

### Core Test Client (`mcp_test_client.py`)

Low-level MCP client for programmatic testing:

#### Features

- **MCP Protocol Implementation**: Full JSON-RPC 2.0 over stdio
- **Connection Management**: Automatic server startup and cleanup
- **Tool Discovery**: Automatic discovery of available MCP tools
- **Error Handling**: Comprehensive error reporting and logging
- **Performance Monitoring**: Execution time tracking for all requests

#### API Usage

```python
from scripts.mcp_test_client import MCPTestClient

# Initialize client
client = MCPTestClient(
    server_command=["python", "-m", "trading_mcp.server"],
    cwd="/path/to/project"
)

# Use as context manager
async with client:
    # Call specific tool
    result = await client.get_stock_chart_data(
        symbol="RELIANCE",
        start_date="2024-01-01",
        end_date="2024-01-02",
        interval="1h"
    )
    
    # Generic tool call
    result = await client.call_tool("get_stock_chart_data", {
        "symbol": "TCS",
        "start_date": "2024-01-01",
        "end_date": "2024-01-05",
        "interval": "1d"
    })
```

#### Command Line Usage

```bash
# Run all predefined tests
python scripts/mcp_test_client.py --test-all

# Test specific function with parameters
python scripts/mcp_test_client.py \
    --function get_stock_chart_data \
    --symbol RELIANCE \
    --start-date 2024-01-01 \
    --end-date 2024-01-02 \
    --interval 1h

# Get help
python scripts/mcp_test_client.py --help
```

## Development Integration

### VS Code Integration

Add to your VS Code tasks.json for quick testing:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Test MCP Interactive",
            "type": "shell",
            "command": "python",
            "args": ["scripts/interactive_client.py"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "Test MCP All Scenarios",
            "type": "shell",
            "command": "python",
            "args": ["scripts/test_scenarios.py", "--scenario", "all"],
            "group": "test"
        }
    ]
}
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
- name: Run MCP Tests
  run: |
    source venv/bin/activate
    python scripts/test_scenarios.py --scenario all
    python scripts/mcp_test_client.py --test-all
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running MCP tests..."
source venv/bin/activate
python scripts/test_scenarios.py --scenario basic
if [ $? -ne 0 ]; then
    echo "MCP tests failed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

1. **Server Won't Start**
   ```bash
   # Check if trading-mcp package is installed
   pip install -e .
   
   # Verify server can start manually
   python -m trading_mcp.server
   ```

2. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /path/to/trade-mcp
   
   # Activate virtual environment
   source venv/bin/activate
   ```

3. **Dependency Issues**
   ```bash
   # Install dev dependencies
   pip install -e ".[dev]"
   
   # Verify rich and click are installed
   pip list | grep -E "(rich|click)"
   ```

4. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.py
   ```

### Debug Mode

Enable debug logging in any script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export PYTHONPATH="/path/to/trade-mcp/src:$PYTHONPATH"
python scripts/interactive_client.py
```

## Best Practices

### During Development

1. **Use Interactive Client** for exploratory testing
2. **Run Basic Scenarios** before committing changes
3. **Add Custom Scenarios** for new features
4. **Monitor Performance** with benchmark tests

### Before Deployment

1. **Run All Scenarios** to ensure comprehensive coverage
2. **Check Performance** benchmarks meet requirements
3. **Validate Edge Cases** are handled correctly
4. **Test Error Scenarios** for proper error handling

### Continuous Integration

1. **Include in CI Pipeline** for automated testing
2. **Generate Test Reports** for tracking progress
3. **Monitor Performance Trends** over time
4. **Alert on Test Failures** for immediate attention

## Contributing

When adding new test scenarios:

1. **Add to appropriate category** in `test_scenarios.py`
2. **Include expected results** for validation
3. **Add documentation** for complex scenarios
4. **Test both success and failure cases**

### Example New Scenario

```python
{
    "name": "New Feature Test",
    "category": "basic",
    "description": "Test new feature functionality",
    "function": "new_function_name",
    "args": {
        "param1": "value1",
        "param2": "value2"
    },
    "expected_result": {
        "success": True,
        "min_data_points": 1
    }
}
```

## Performance Benchmarks

Current performance targets:

- **Quick Response**: < 3 seconds for small datasets
- **Medium Dataset**: < 5 seconds for week of hourly data
- **Large Dataset**: < 10 seconds for week of minute data
- **Cache Hit**: < 0.5 seconds for cached requests

Use the performance benchmark feature to validate these targets:

```bash
# Interactive performance test
python scripts/interactive_client.py
# Select option 6 for performance benchmark

# Automated performance tests
python scripts/test_scenarios.py --scenario performance
```

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the logs for error details
3. Test with the interactive client for debugging
4. Run individual scenarios to isolate issues