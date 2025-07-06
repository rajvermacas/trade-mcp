# Debugging Trading MCP Server with Claude Desktop

## Overview

When your Trading MCP Server is integrated with Claude Desktop, debugging can be challenging because you don't see the server's console output. This guide explains the comprehensive logging system implemented to help you debug issues in production.

## Logging System Architecture

### Log Files Location
All logs are written to `resources/logs/`:

- **`trading_mcp.log`** - General application logs (human-readable)
- **`trading_mcp_structured.jsonl`** - Structured JSON logs for analysis
- **`trading_mcp_errors.log`** - Error-specific logs with stack traces

### Log Levels
- **DEBUG**: Detailed information for development debugging
- **INFO**: General information about normal operations
- **WARNING**: Warning conditions that may need attention
- **ERROR**: Error conditions that prevent normal operation
- **CRITICAL**: Critical conditions that may cause the application to stop

## Configuration

### Environment Variables
Create a `.env` file in your project root to configure logging:

```bash
# Copy from .env.example
cp .env.example .env

# Edit the configuration
TRADING_MCP_LOG_LEVEL=DEBUG          # For detailed debugging
TRADING_MCP_LOG_DIR=resources/logs   # Log directory
TRADING_MCP_LOG_CONSOLE=true         # Console output (for development)
TRADING_MCP_LOG_FILE=true            # File logging
TRADING_MCP_LOG_JSON=true            # Structured JSON logs
```

### Claude Desktop Integration
When running with Claude Desktop, set environment variables in your MCP configuration:

```json
{
  "mcpServers": {
    "trading-mcp": {
      "command": "python",
      "args": ["-m", "trading_mcp.server"],
      "cwd": "/path/to/trade-mcp",
      "env": {
        "TRADING_MCP_LOG_LEVEL": "INFO",
        "TRADING_MCP_LOG_DIR": "/path/to/trade-mcp/resources/logs"
      }
    }
  }
}
```

## Common Debugging Scenarios

### 1. Server Won't Start
**Symptoms**: Claude Desktop can't connect to MCP server

**Check**:
```bash
# Look for startup errors
tail -f resources/logs/trading_mcp_errors.log

# Check general logs
tail -f resources/logs/trading_mcp.log
```

**Look for**:
- Import errors
- Permission issues
- Port conflicts
- Missing dependencies

### 2. Tool Calls Fail
**Symptoms**: Claude gets errors when calling `get_stock_chart_data`

**Check**:
```bash
# Watch real-time logs during tool calls
tail -f resources/logs/trading_mcp.log

# Check for specific errors
grep "Tool call failed" resources/logs/trading_mcp.log
```

**Look for**:
- Invalid symbols
- Network errors
- Yahoo Finance API issues
- Validation failures

### 3. Poor Performance
**Symptoms**: Slow responses from MCP server

**Check**:
```bash
# Analyze response times in structured logs
grep "response_time" resources/logs/trading_mcp_structured.jsonl | jq .

# Check cache performance
grep "cache_hit" resources/logs/trading_mcp_structured.jsonl | jq .
```

**Look for**:
- High response times (>3000ms)
- Low cache hit rates
- API call patterns

### 4. Data Quality Issues
**Symptoms**: Wrong or missing stock data

**Check**:
```bash
# Track specific symbol requests
grep "RELIANCE" resources/logs/trading_mcp.log

# Check API responses
grep "yahoo_finance" resources/logs/trading_mcp_structured.jsonl | jq .
```

## Structured Log Analysis

### Using jq for JSON Log Analysis
```bash
# Get all requests for a specific symbol
cat resources/logs/trading_mcp_structured.jsonl | \
  jq 'select(.symbol == "RELIANCE.NS")'

# Analyze response times
cat resources/logs/trading_mcp_structured.jsonl | \
  jq 'select(.response_time) | {symbol, response_time, cache_hit}'

# Find errors
cat resources/logs/trading_mcp_structured.jsonl | \
  jq 'select(.level == "ERROR")'

# Cache performance
cat resources/logs/trading_mcp_structured.jsonl | \
  jq 'select(.cache_hit != null) | {cache_hit, symbol, response_time}'
```

### Request Tracking
Each request gets a unique `mcp_request_id` that you can track:

```bash
# Follow a specific request through the system
grep "550e8400-e29b-41d4-a716-446655440000" resources/logs/trading_mcp_structured.jsonl
```

## Log Rotation

Logs automatically rotate when they reach 10MB:
- Keeps 5 backup files
- Old logs are compressed
- Prevents disk space issues

## Troubleshooting Commands

### Quick Health Check
```bash
# Check if server is logging
ls -la resources/logs/

# Check latest activity
tail -20 resources/logs/trading_mcp.log

# Check for recent errors
tail -20 resources/logs/trading_mcp_errors.log
```

### Real-time Monitoring
```bash
# Watch all logs in real-time
tail -f resources/logs/trading_mcp.log resources/logs/trading_mcp_errors.log

# Monitor specific operations
tail -f resources/logs/trading_mcp.log | grep "get_stock_chart_data"
```

### Log Analysis Scripts
```bash
# Count requests by symbol (requires jq)
cat resources/logs/trading_mcp_structured.jsonl | \
  jq -r 'select(.symbol) | .symbol' | \
  sort | uniq -c | sort -nr

# Average response times
cat resources/logs/trading_mcp_structured.jsonl | \
  jq 'select(.response_time) | .response_time' | \
  awk '{sum+=$1; count++} END {print "Average response time:", sum/count, "ms"}'
```

## Development vs Production

### Development Mode
```bash
export TRADING_MCP_LOG_LEVEL=DEBUG
export TRADING_MCP_LOG_CONSOLE=true
python -m trading_mcp.server
```

### Production Mode
```bash
export TRADING_MCP_LOG_LEVEL=INFO
export TRADING_MCP_LOG_CONSOLE=false
python -m trading_mcp.server
```

## Performance Monitoring

Key metrics to monitor:
- **Response Time**: < 3000ms for all requests
- **Cache Hit Rate**: > 60% for optimal performance
- **Error Rate**: < 1% of all requests
- **API Success Rate**: > 99% for Yahoo Finance calls

## Emergency Debugging

If the server is completely unresponsive:

1. **Check if process is running**:
   ```bash
   ps aux | grep trading_mcp
   ```

2. **Check recent errors**:
   ```bash
   tail -50 resources/logs/trading_mcp_errors.log
   ```

3. **Restart with debug logging**:
   ```bash
   TRADING_MCP_LOG_LEVEL=DEBUG python -m trading_mcp.server
   ```

4. **Test independently**:
   ```bash
   python scripts/mcp_test_client.py --function get_stock_chart_data --symbol RELIANCE
   ```

## Contact and Support

When reporting issues, include:
- Relevant log snippets from `trading_mcp_errors.log`
- The specific request that failed
- Environment configuration
- Steps to reproduce

This comprehensive logging system ensures you can debug any issues that arise when the MCP server is running with Claude Desktop.