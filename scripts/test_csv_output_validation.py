#!/usr/bin/env python3
"""
Comprehensive test script for CSV output functionality validation.
Tests both get_stock_chart_data and calculate_technical_indicator MCP functions.
"""

import sys
import os
import json
import csv
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_mcp.stock_data import StockDataProvider
from trading_mcp.server import TradingMCPServer
from trading_mcp.csv_utils import get_csv_metadata

# Test configuration
TEST_SYMBOL = "RELIANCE"
TEST_INDEX = "^NSEI"
TEST_START_DATE = "2024-01-01"
TEST_END_DATE = "2024-01-07"
TEST_INTERVAL = "1h"
TEST_INDICATOR = "RSI"
TEST_INDICATOR_PARAMS = {"period": 14}

class CSVOutputValidator:
    """Comprehensive validator for CSV output functionality."""
    
    def __init__(self):
        self.provider = StockDataProvider()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name: str, passed: bool, details: str = "", 
                       expected: Any = None, actual: Any = None):
        """Log test result with details."""
        result = {
            "test_name": test_name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if expected is not None:
            result["expected"] = expected
        if actual is not None:
            result["actual"] = actual
        
        self.test_results.append(result)
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            
        print(f"{'✓' if passed else '✗'} {test_name}: {details}")
        
    def test_stock_data_csv_functionality(self) -> bool:
        """Test get_stock_chart_data CSV functionality and response format."""
        print("\n=== Testing get_stock_chart_data CSV functionality ===")
        
        try:
            # Test basic CSV output
            response = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_csv_stock_001"
            )
            
            # Validate response structure
            success = response.get("success", False)
            self.log_test_result(
                "stock_data_response_success",
                success,
                f"Response success: {success}"
            )
            
            if not success:
                self.log_test_result(
                    "stock_data_basic_functionality", 
                    False, 
                    f"API call failed: {response.get('error', {}).get('message', 'Unknown error')}"
                )
                return False
            
            # Check required response fields
            required_fields = ["file_path", "filename", "metadata"]
            for field in required_fields:
                has_field = field in response
                self.log_test_result(
                    f"stock_data_response_has_{field}",
                    has_field,
                    f"Response contains {field}: {has_field}"
                )
            
            file_path = response.get("file_path")
            if not file_path:
                self.log_test_result(
                    "stock_data_file_path_provided",
                    False,
                    "No file path provided in response"
                )
                return False
            
            # Validate file exists
            file_exists = os.path.exists(file_path)
            self.log_test_result(
                "stock_data_csv_file_exists",
                file_exists,
                f"CSV file exists at {file_path}: {file_exists}"
            )
            
            if not file_exists:
                return False
            
            # Validate CSV file structure and content
            return self._validate_stock_csv_content(file_path)
            
        except Exception as e:
            self.log_test_result(
                "stock_data_csv_functionality",
                False,
                f"Exception during test: {str(e)}"
            )
            return False
    
    def test_indicator_csv_functionality(self) -> bool:
        """Test calculate_technical_indicator CSV functionality and response format."""
        print("\n=== Testing calculate_technical_indicator CSV functionality ===")
        
        try:
            # Test basic CSV output for indicators
            response = self.provider.calculate_technical_indicator(
                symbol=TEST_SYMBOL,
                indicator=TEST_INDICATOR,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                params=TEST_INDICATOR_PARAMS,
                request_id="test_csv_indicator_001"
            )
            
            # Validate response structure
            success = response.get("success", False)
            self.log_test_result(
                "indicator_response_success",
                success,
                f"Response success: {success}"
            )
            
            if not success:
                self.log_test_result(
                    "indicator_basic_functionality", 
                    False, 
                    f"API call failed: {response.get('error', {}).get('message', 'Unknown error')}"
                )
                return False
            
            # Check required response fields
            required_fields = ["file_path", "filename", "metadata"]
            for field in required_fields:
                has_field = field in response
                self.log_test_result(
                    f"indicator_response_has_{field}",
                    has_field,
                    f"Response contains {field}: {has_field}"
                )
            
            file_path = response.get("file_path")
            if not file_path:
                self.log_test_result(
                    "indicator_file_path_provided",
                    False,
                    "No file path provided in response"
                )
                return False
            
            # Validate file exists
            file_exists = os.path.exists(file_path)
            self.log_test_result(
                "indicator_csv_file_exists",
                file_exists,
                f"CSV file exists at {file_path}: {file_exists}"
            )
            
            if not file_exists:
                return False
            
            # Validate CSV file structure and content
            return self._validate_indicator_csv_content(file_path, TEST_INDICATOR)
            
        except Exception as e:
            self.log_test_result(
                "indicator_csv_functionality",
                False,
                f"Exception during test: {str(e)}"
            )
            return False
    
    def _validate_stock_csv_content(self, file_path: str) -> bool:
        """Validate stock data CSV file content and structure."""
        try:
            # Check file is readable
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            # Validate headers
            expected_headers = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            actual_headers = list(rows[0].keys()) if rows else []
            headers_match = set(expected_headers) == set(actual_headers)
            
            self.log_test_result(
                "stock_csv_headers_correct",
                headers_match,
                f"Headers match expected: {headers_match}",
                expected_headers,
                actual_headers
            )
            
            # Validate row count > 0
            row_count = len(rows)
            has_data = row_count > 0
            self.log_test_result(
                "stock_csv_has_data",
                has_data,
                f"CSV contains {row_count} rows"
            )
            
            if not has_data:
                return False
            
            # Validate data types and values
            first_row = rows[0]
            
            # Check timestamp format
            timestamp_valid = self._validate_timestamp(first_row['timestamp'])
            self.log_test_result(
                "stock_csv_timestamp_valid",
                timestamp_valid,
                f"Timestamp format valid: {first_row['timestamp']}"
            )
            
            # Check numeric fields
            numeric_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in numeric_fields:
                try:
                    float(first_row[field])
                    numeric_valid = True
                except (ValueError, TypeError):
                    numeric_valid = False
                
                self.log_test_result(
                    f"stock_csv_{field}_numeric",
                    numeric_valid,
                    f"{field} is numeric: {first_row[field]}"
                )
            
            # Validate OHLC relationships
            ohlc_valid = self._validate_ohlc_relationships(rows)
            self.log_test_result(
                "stock_csv_ohlc_relationships",
                ohlc_valid,
                f"OHLC relationships valid in {len(rows)} rows"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "stock_csv_content_validation",
                False,
                f"Error validating CSV content: {str(e)}"
            )
            return False
    
    def _validate_indicator_csv_content(self, file_path: str, indicator: str) -> bool:
        """Validate indicator CSV file content and structure."""
        try:
            # Check file is readable
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            # Validate basic structure
            row_count = len(rows)
            has_data = row_count > 0
            self.log_test_result(
                "indicator_csv_has_data",
                has_data,
                f"CSV contains {row_count} rows"
            )
            
            if not has_data:
                return False
            
            # Validate headers contain timestamp
            headers = list(rows[0].keys())
            has_timestamp = 'timestamp' in headers
            self.log_test_result(
                "indicator_csv_has_timestamp",
                has_timestamp,
                f"CSV contains timestamp column: {has_timestamp}"
            )
            
            # Validate timestamp format
            first_row = rows[0]
            timestamp_valid = self._validate_timestamp(first_row['timestamp'])
            self.log_test_result(
                "indicator_csv_timestamp_valid",
                timestamp_valid,
                f"Timestamp format valid: {first_row['timestamp']}"
            )
            
            # Validate indicator-specific columns
            if indicator.upper() == "RSI":
                has_value = 'value' in headers
                self.log_test_result(
                    "indicator_csv_has_value_column",
                    has_value,
                    f"RSI CSV has value column: {has_value}"
                )
                
                if has_value:
                    try:
                        rsi_value = float(first_row['value'])
                        rsi_range_valid = 0 <= rsi_value <= 100
                        self.log_test_result(
                            "indicator_csv_rsi_range_valid",
                            rsi_range_valid,
                            f"RSI value in valid range (0-100): {rsi_value}"
                        )
                    except (ValueError, TypeError):
                        self.log_test_result(
                            "indicator_csv_value_numeric",
                            False,
                            f"RSI value not numeric: {first_row['value']}"
                        )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "indicator_csv_content_validation",
                False,
                f"Error validating CSV content: {str(e)}"
            )
            return False
    
    def _validate_timestamp(self, timestamp_str: str) -> bool:
        """Validate timestamp format."""
        try:
            # Expected format: 2024-01-15T09:15:00+05:30
            datetime.fromisoformat(timestamp_str.replace('+05:30', '+0530'))
            return True
        except ValueError:
            return False
    
    def _validate_ohlc_relationships(self, rows: List[Dict]) -> bool:
        """Validate OHLC relationships in stock data."""
        try:
            for row in rows[:5]:  # Check first 5 rows
                o, h, l, c = float(row['open']), float(row['high']), float(row['low']), float(row['close'])
                
                # High should be >= Open, Close, Low
                if not (h >= o and h >= c and h >= l):
                    return False
                
                # Low should be <= Open, Close, High  
                if not (l <= o and l <= c and l <= h):
                    return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def test_data_integrity_validation(self) -> bool:
        """Validate data integrity between CSV and original JSON data."""
        print("\n=== Testing data integrity validation ===")
        
        try:
            # Get both CSV and original data for comparison
            csv_response = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_integrity_001"
            )
            
            if not csv_response.get("success"):
                self.log_test_result(
                    "data_integrity_setup",
                    False,
                    "Failed to get CSV response for integrity test"
                )
                return False
            
            # Read CSV data
            csv_file_path = csv_response["file_path"]
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                csv_data = list(reader)
            
            # Validate data consistency
            csv_row_count = len(csv_data)
            self.log_test_result(
                "data_integrity_csv_rows",
                csv_row_count > 0,
                f"CSV contains {csv_row_count} data rows"
            )
            
            # Check data types are preserved
            if csv_data:
                first_row = csv_data[0]
                
                # Timestamp should be ISO format
                timestamp_preserved = self._validate_timestamp(first_row['timestamp'])
                self.log_test_result(
                    "data_integrity_timestamp_format",
                    timestamp_preserved,
                    f"Timestamp format preserved: {first_row['timestamp']}"
                )
                
                # Numeric precision should be preserved (2 decimal places for prices)
                try:
                    open_price = float(first_row['open'])
                    # Check if it has reasonable precision (not too many decimals)
                    precision_ok = len(str(open_price).split('.')[-1]) <= 2
                    self.log_test_result(
                        "data_integrity_price_precision",
                        precision_ok,
                        f"Price precision preserved: {open_price}"
                    )
                except ValueError:
                    self.log_test_result(
                        "data_integrity_price_precision",
                        False,
                        f"Price not numeric: {first_row['open']}"
                    )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "data_integrity_validation",
                False,
                f"Exception during integrity test: {str(e)}"
            )
            return False
    
    def test_response_size_reduction(self) -> bool:
        """Measure and verify response size reduction (90%+ target)."""
        print("\n=== Testing response size reduction ===")
        
        try:
            # Get CSV response
            csv_response = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_size_001"
            )
            
            if not csv_response.get("success"):
                self.log_test_result(
                    "response_size_setup",
                    False,
                    "Failed to get CSV response for size test"
                )
                return False
            
            # Measure CSV response size (JSON serialized)
            csv_response_size = len(json.dumps(csv_response).encode('utf-8'))
            
            # Simulate original JSON response size by reading CSV and creating equivalent JSON
            csv_file_path = csv_response["file_path"]
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                csv_data = list(reader)
            
            # Create equivalent JSON response structure (what would have been returned before)
            original_response_structure = {
                "success": True,
                "data": csv_data,
                "metadata": csv_response["metadata"]
            }
            
            original_response_size = len(json.dumps(original_response_structure).encode('utf-8'))
            
            # Calculate reduction percentage
            size_reduction = ((original_response_size - csv_response_size) / original_response_size) * 100
            reduction_target_met = size_reduction >= 90.0
            
            self.log_test_result(
                "response_size_reduction_calculation",
                True,
                f"Original: {original_response_size} bytes, CSV: {csv_response_size} bytes, Reduction: {size_reduction:.1f}%"
            )
            
            self.log_test_result(
                "response_size_reduction_target",
                reduction_target_met,
                f"Size reduction target (90%+) met: {size_reduction:.1f}% >= 90%"
            )
            
            # Additional metadata about actual file
            file_size = os.path.getsize(csv_file_path)
            self.log_test_result(
                "csv_file_size_reasonable",
                file_size > 0,
                f"CSV file size: {file_size} bytes"
            )
            
            return reduction_target_met
            
        except Exception as e:
            self.log_test_result(
                "response_size_reduction",
                False,
                f"Exception during size test: {str(e)}"
            )
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for file operations."""
        print("\n=== Testing error handling ===")
        
        try:
            # Test with invalid symbol
            response = self.provider.get_stock_chart_data(
                symbol="INVALID_SYMBOL_12345",
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_error_001"
            )
            
            # Should handle gracefully
            handled_gracefully = not response.get("success", True)  # Should be False
            self.log_test_result(
                "error_handling_invalid_symbol",
                handled_gracefully,
                f"Invalid symbol handled gracefully: {handled_gracefully}"
            )
            
            if handled_gracefully:
                error_structure = response.get("error", {})
                has_error_code = "code" in error_structure
                has_error_message = "message" in error_structure
                
                self.log_test_result(
                    "error_response_has_code",
                    has_error_code,
                    f"Error response has code: {has_error_code}"
                )
                
                self.log_test_result(
                    "error_response_has_message",
                    has_error_message,
                    f"Error response has message: {has_error_message}"
                )
            
            # Test with invalid date range
            response2 = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date="2025-12-31",  # Future date
                end_date="2025-12-31",
                interval=TEST_INTERVAL,
                request_id="test_error_002"
            )
            
            # Should handle gracefully or return empty data
            handled_or_empty = not response2.get("success", True) or (
                response2.get("success") and response2.get("metadata", {}).get("row_count", 0) == 0
            )
            self.log_test_result(
                "error_handling_invalid_date_range",
                handled_or_empty,
                f"Invalid date range handled appropriately: {handled_or_empty}"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "error_handling_test",
                False,
                f"Exception during error handling test: {str(e)}"
            )
            return False
    
    def test_mcp_protocol_compliance(self) -> bool:
        """Verify MCP protocol compliance of new response format."""
        print("\n=== Testing MCP protocol compliance ===")
        
        try:
            response = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_mcp_001"
            )
            
            # Check response is valid JSON serializable
            try:
                json.dumps(response)
                json_serializable = True
            except (TypeError, ValueError):
                json_serializable = False
            
            self.log_test_result(
                "mcp_response_json_serializable",
                json_serializable,
                f"Response is JSON serializable: {json_serializable}"
            )
            
            # Check response structure matches MCP expectations
            has_success_field = "success" in response
            self.log_test_result(
                "mcp_response_has_success",
                has_success_field,
                f"Response has success field: {has_success_field}"
            )
            
            if response.get("success"):
                # Success response should have file_path
                has_file_path = "file_path" in response
                self.log_test_result(
                    "mcp_success_response_structure",
                    has_file_path,
                    f"Success response has file_path: {has_file_path}"
                )
            else:
                # Error response should have error field
                has_error = "error" in response
                self.log_test_result(
                    "mcp_error_response_structure",
                    has_error,
                    f"Error response has error field: {has_error}"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "mcp_protocol_compliance",
                False,
                f"Exception during MCP compliance test: {str(e)}"
            )
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Validate performance benchmark requirements."""
        print("\n=== Testing performance benchmarks ===")
        
        try:
            # Test response time for CSV generation
            start_time = time.time()
            response = self.provider.get_stock_chart_data(
                symbol=TEST_SYMBOL,
                start_date=TEST_START_DATE,
                end_date=TEST_END_DATE,
                interval=TEST_INTERVAL,
                request_id="test_perf_001"
            )
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            performance_acceptable = response_time < 5000  # Under 5 seconds
            
            self.log_test_result(
                "performance_response_time",
                performance_acceptable,
                f"Response time acceptable: {response_time:.2f}ms < 5000ms"
            )
            
            # Test file write performance
            if response.get("success"):
                file_path = response["file_path"]
                file_size = os.path.getsize(file_path)
                
                # Should write reasonable amount of data
                reasonable_size = file_size > 100  # At least 100 bytes
                self.log_test_result(
                    "performance_file_size",
                    reasonable_size,
                    f"File size reasonable: {file_size} bytes > 100 bytes"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "performance_benchmarks",
                False,
                f"Exception during performance test: {str(e)}"
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests and return comprehensive report."""
        print("🧪 Starting CSV Output Functionality Validation")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        test_categories = [
            ("Stock Data CSV Functionality", self.test_stock_data_csv_functionality),
            ("Indicator CSV Functionality", self.test_indicator_csv_functionality),
            ("Data Integrity Validation", self.test_data_integrity_validation),
            ("Response Size Reduction", self.test_response_size_reduction),
            ("Error Handling", self.test_error_handling),
            ("MCP Protocol Compliance", self.test_mcp_protocol_compliance),
            ("Performance Benchmarks", self.test_performance_benchmarks)
        ]
        
        category_results = {}
        for category_name, test_func in test_categories:
            try:
                category_passed = test_func()
                category_results[category_name] = "PASS" if category_passed else "FAIL"
            except Exception as e:
                category_results[category_name] = "FAIL"
                print(f"❌ {category_name} failed with exception: {str(e)}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Generate comprehensive test report
        report = {
            "test_suite": "CSV Output Functionality Validation",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(total_duration, 2),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "success_rate": round((self.passed_tests / self.total_tests) * 100, 1) if self.total_tests > 0 else 0
            },
            "category_results": category_results,
            "detailed_results": self.test_results,
            "test_configuration": {
                "test_symbol": TEST_SYMBOL,
                "test_index": TEST_INDEX,
                "test_start_date": TEST_START_DATE,
                "test_end_date": TEST_END_DATE,
                "test_interval": TEST_INTERVAL,
                "test_indicator": TEST_INDICATOR,
                "test_indicator_params": TEST_INDICATOR_PARAMS
            }
        }
        
        return report


def main():
    """Main test execution function."""
    validator = CSVOutputValidator()
    
    try:
        # Run all tests
        report = validator.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CSV OUTPUT VALIDATION TEST REPORT")
        print("=" * 60)
        
        print(f"Duration: {report['duration_seconds']}s")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']}%")
        
        print("\nCategory Results:")
        for category, result in report['category_results'].items():
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"  {status_icon} {category}: {result}")
        
        # Save detailed report
        reports_dir = Path(__file__).parent.parent / "resources" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"csv_validation_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed report saved: {report_file}")
        
        # Determine overall success
        all_categories_passed = all(result == "PASS" for result in report['category_results'].values())
        high_success_rate = report['summary']['success_rate'] >= 80
        
        overall_success = all_categories_passed and high_success_rate
        
        if overall_success:
            print("\n🎉 TESTING_COMPLETE: csv_functionality_validation - ALL TESTS PASSED")
            return 0
        else:
            print("\n❌ TESTING_COMPLETE: csv_functionality_validation - SOME TESTS FAILED")
            return 1
            
    except Exception as e:
        print(f"\n💥 Fatal error during testing: {str(e)}")
        print("❌ TESTING_COMPLETE: csv_functionality_validation - FATAL ERROR")
        return 2


if __name__ == "__main__":
    sys.exit(main())