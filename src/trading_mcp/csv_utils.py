"""
CSV utility functions for writing stock data and technical indicators to CSV files.
"""

import os
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from .logging_config import get_logger

logger = get_logger(__name__)


def ensure_reports_directory() -> str:
    """
    Ensure the resources/reports directory exists.
    
    Returns:
        Absolute path to the reports directory
    """
    project_root = Path(__file__).parent.parent.parent
    reports_dir = project_root / "resources" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return str(reports_dir.absolute())


def generate_filename(symbol: str, data_type: str, indicator: str = None) -> str:
    """
    Generate a timestamped filename for CSV output.
    
    Args:
        symbol: Stock symbol
        data_type: Type of data ('stock_data' or 'indicator')
        indicator: Indicator name (for technical indicators)
        
    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    symbol_clean = symbol.replace("^", "").replace(".NS", "")
    
    if data_type == "stock_data":
        return f"{symbol_clean}_stock_data_{timestamp}.csv"
    elif data_type == "indicator" and indicator:
        indicator_clean = indicator.upper().replace(" ", "_")
        return f"{symbol_clean}_{indicator_clean}_{timestamp}.csv"
    else:
        return f"{symbol_clean}_{data_type}_{timestamp}.csv"


def write_stock_data_to_csv(
    data_points: List[Dict[str, Any]], 
    symbol: str, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Write stock chart data to CSV file.
    
    Args:
        data_points: List of OHLC data points
        symbol: Stock symbol
        metadata: Metadata about the data
        
    Returns:
        Dictionary with file path and metadata
    """
    try:
        reports_dir = ensure_reports_directory()
        filename = generate_filename(symbol, "stock_data")
        file_path = os.path.join(reports_dir, filename)
        
        if not data_points:
            raise ValueError("No data points to write")
        
        # Write CSV with headers
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for point in data_points:
                writer.writerow(point)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        logger.info(
            f"Successfully wrote stock data to CSV: {filename}",
            extra={
                "symbol": symbol,
                "file_path": file_path,
                "row_count": len(data_points),
                "file_size_bytes": file_size
            }
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": filename,
            "metadata": {
                "rows": len(data_points),
                "size": file_size,
                "symbol": metadata.get("symbol", ""),
                "format": "CSV"
            }
        }
        
    except Exception as e:
        logger.error(
            f"Error writing stock data to CSV: {str(e)}",
            extra={
                "symbol": symbol,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        return {
            "success": False,
            "error": {
                "code": "CSV_WRITE_ERROR",
                "message": f"Failed to write stock data to CSV: {str(e)}",
                "details": {
                    "symbol": symbol,
                    "error_type": type(e).__name__
                }
            }
        }


def write_indicator_data_to_csv(
    indicator_data: Dict[str, Any], 
    symbol: str, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Write technical indicator data to CSV file.
    
    Args:
        indicator_data: Indicator data with 'indicator', 'values', and 'parameters'
        symbol: Stock symbol
        metadata: Metadata about the data
        
    Returns:
        Dictionary with file path and metadata
    """
    try:
        reports_dir = ensure_reports_directory()
        indicator_name = indicator_data.get("indicator", "unknown")
        filename = generate_filename(symbol, "indicator", indicator_name)
        file_path = os.path.join(reports_dir, filename)
        
        values = indicator_data.get("values", [])
        if not values:
            raise ValueError("No indicator values to write")
        
        # Determine CSV columns from the first value
        first_value = values[0]
        if isinstance(first_value, dict):
            fieldnames = list(first_value.keys())
        else:
            fieldnames = ['timestamp', 'value']
        
        # Write CSV with headers
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for value in values:
                if isinstance(value, dict):
                    # Handle complex indicator data (e.g., Enhanced Supertrend)
                    writer.writerow(value)
                else:
                    # Handle simple value data
                    writer.writerow({
                        'timestamp': value.get('timestamp', ''),
                        'value': value.get('value', '')
                    })
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        logger.info(
            f"Successfully wrote indicator data to CSV: {filename}",
            extra={
                "symbol": symbol,
                "indicator": indicator_name,
                "file_path": file_path,
                "row_count": len(values),
                "file_size_bytes": file_size
            }
        )
        
        return {
            "success": True,
            "file_path": file_path,
            "filename": filename,
            "metadata": {
                "rows": len(values),
                "size": file_size,
                "indicator": indicator_name,
                "symbol": metadata.get("symbol", ""),
                "format": "CSV"
            }
        }
        
    except Exception as e:
        logger.error(
            f"Error writing indicator data to CSV: {str(e)}",
            extra={
                "symbol": symbol,
                "indicator": indicator_data.get("indicator", "unknown"),
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        return {
            "success": False,
            "error": {
                "code": "CSV_WRITE_ERROR",
                "message": f"Failed to write indicator data to CSV: {str(e)}",
                "details": {
                    "symbol": symbol,
                    "indicator": indicator_data.get("indicator", "unknown"),
                    "error_type": type(e).__name__
                }
            }
        }


def get_csv_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata about a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with file metadata
    """
    try:
        if not os.path.exists(file_path):
            return {"exists": False}
        
        file_size = os.path.getsize(file_path)
        mod_time = os.path.getmtime(file_path)
        
        # Count rows (excluding header)
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            row_count = sum(1 for row in reader) - 1  # Subtract header row
        
        return {
            "exists": True,
            "file_size_bytes": file_size,
            "row_count": row_count,
            "last_modified": datetime.fromtimestamp(mod_time).isoformat(),
            "absolute_path": os.path.abspath(file_path)
        }
        
    except Exception as e:
        logger.error(
            f"Error getting CSV metadata: {str(e)}",
            extra={
                "file_path": file_path,
                "error": str(e)
            }
        )
        return {
            "exists": False,
            "error": str(e)
        }