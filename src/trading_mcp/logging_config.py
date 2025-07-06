"""
Centralized logging configuration for Trading MCP Server.

Provides structured logging with file rotation, multiple formats, and
environment-based configuration for debugging production issues.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra context data if present
        if hasattr(record, 'mcp_request_id'):
            log_entry["mcp_request_id"] = record.mcp_request_id
        if hasattr(record, 'tool_name'):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, 'symbol'):
            log_entry["symbol"] = record.symbol
        if hasattr(record, 'response_time'):
            log_entry["response_time_ms"] = record.response_time
        if hasattr(record, 'cache_hit'):
            log_entry["cache_hit"] = record.cache_hit
        
        return json.dumps(log_entry)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "resources/logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable structured JSON logging
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured root logger
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler for general logs
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / "trading_mcp.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Structured JSON handler for analysis
    if enable_json:
        json_handler = logging.handlers.RotatingFileHandler(
            log_path / "trading_mcp_structured.jsonl",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        json_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(json_handler)
    
    # Error-specific handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "trading_mcp_errors.log",
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s\n"
        "%(pathname)s:%(lineno)d in %(funcName)s()\n",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    return root_logger


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Get a logger with optional context.
    
    Args:
        name: Logger name (typically __name__)
        context: Optional context to add to all log records
        
    Returns:
        Configured logger with context
    """
    logger = logging.getLogger(name)
    
    if context:
        context_filter = ContextFilter(context)
        logger.addFilter(context_filter)
    
    return logger


def log_mcp_request(logger: logging.Logger, method: str, params: Dict[str, Any], request_id: str = None):
    """Log MCP request with structured data."""
    logger.info(
        f"MCP Request: {method}",
        extra={
            "mcp_request_id": request_id,
            "method": method,
            "params": params
        }
    )


def log_mcp_response(logger: logging.Logger, method: str, response_time: float, success: bool, request_id: str = None):
    """Log MCP response with performance metrics."""
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"MCP Response: {method} ({'success' if success else 'error'}) in {response_time:.2f}ms",
        extra={
            "mcp_request_id": request_id,
            "method": method,
            "response_time": response_time,
            "success": success
        }
    )


def log_tool_call(logger: logging.Logger, tool_name: str, symbol: str, params: Dict[str, Any], request_id: str = None):
    """Log tool call with context."""
    logger.info(
        f"Tool Call: {tool_name} for {symbol}",
        extra={
            "mcp_request_id": request_id,
            "tool_name": tool_name,
            "symbol": symbol,
            "params": params
        }
    )


def log_cache_event(logger: logging.Logger, cache_key: str, hit: bool, request_id: str = None):
    """Log cache hit/miss events."""
    logger.debug(
        f"Cache {'HIT' if hit else 'MISS'}: {cache_key}",
        extra={
            "mcp_request_id": request_id,
            "cache_key": cache_key,
            "cache_hit": hit
        }
    )


def log_api_call(logger: logging.Logger, provider: str, symbol: str, response_time: float, success: bool, request_id: str = None):
    """Log external API calls."""
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"API Call: {provider} for {symbol} in {response_time:.2f}ms ({'success' if success else 'failed'})",
        extra={
            "mcp_request_id": request_id,
            "api_provider": provider,
            "symbol": symbol,
            "response_time": response_time,
            "api_success": success
        }
    )


# Environment-based configuration
def configure_from_env():
    """Configure logging from environment variables."""
    log_level = os.getenv("TRADING_MCP_LOG_LEVEL", "INFO")
    log_dir = os.getenv("TRADING_MCP_LOG_DIR", "resources/logs")
    enable_console = os.getenv("TRADING_MCP_LOG_CONSOLE", "true").lower() == "true"
    enable_file = os.getenv("TRADING_MCP_LOG_FILE", "true").lower() == "true"
    enable_json = os.getenv("TRADING_MCP_LOG_JSON", "true").lower() == "true"
    
    return setup_logging(
        log_level=log_level,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_json=enable_json
    )


# Initialize logging on import
if not logging.getLogger().handlers:
    configure_from_env()