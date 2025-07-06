#!/usr/bin/env python3
"""
Test Scenarios for Trading MCP Server

This module contains comprehensive test scenarios for validating the Trading MCP server
functionality. It includes positive tests, negative tests, edge cases, and performance
benchmarks.

Usage:
    python scripts/test_scenarios.py
    python scripts/test_scenarios.py --scenario basic
    python scripts/test_scenarios.py --scenario performance
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_test_client import MCPTestClient


class TradingMCPTestScenarios:
    """Comprehensive test scenarios for Trading MCP server"""
    
    @staticmethod
    def get_basic_scenarios() -> List[Dict[str, Any]]:
        """Basic functionality test scenarios"""
        return [
            {
                "name": "Valid Symbol - RELIANCE Hourly",
                "category": "basic",
                "description": "Test basic stock data retrieval for RELIANCE with hourly interval",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "Valid Symbol - TCS Daily",
                "category": "basic",
                "description": "Test daily data retrieval for TCS stock",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-05",
                    "interval": "1d"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "Valid Symbol - INFY with .NS suffix",
                "category": "basic",
                "description": "Test symbol with explicit .NS suffix",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INFY.NS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "Default Interval Test",
                "category": "basic",
                "description": "Test default interval (should be 1h)",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "HDFC",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            }
        ]
    
    @staticmethod
    def get_validation_scenarios() -> List[Dict[str, Any]]:
        """Input validation test scenarios"""
        return [
            {
                "name": "Invalid Symbol",
                "category": "validation",
                "description": "Test with invalid stock symbol",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INVALID_SYMBOL_123",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": False,
                    "error_type": "INVALID_SYMBOL"
                }
            },
            {
                "name": "Invalid Date Range - Start after End",
                "category": "validation",
                "description": "Test with start date after end date",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-05",
                    "end_date": "2024-01-01",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": False,
                    "error_type": "INVALID_DATE_RANGE"
                }
            },
            {
                "name": "Invalid Date Format",
                "category": "validation",
                "description": "Test with invalid date format",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024/01/01",
                    "end_date": "2024/01/02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": False,
                    "error_type": "INVALID_DATE_FORMAT"
                }
            },
            {
                "name": "Invalid Interval",
                "category": "validation",
                "description": "Test with invalid interval",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "invalid_interval"
                },
                "expected_result": {
                    "success": False,
                    "error_type": "INVALID_INTERVAL"
                }
            },
            {
                "name": "Empty Symbol",
                "category": "validation",
                "description": "Test with empty symbol",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": False,
                    "error_type": "INVALID_SYMBOL"
                }
            }
        ]
    
    @staticmethod
    def get_interval_scenarios() -> List[Dict[str, Any]]:
        """Test different time intervals"""
        return [
            {
                "name": "1-minute Interval",
                "category": "intervals",
                "description": "Test 1-minute interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "1m"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "5-minute Interval",
                "category": "intervals",
                "description": "Test 5-minute interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "5m"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "15-minute Interval",
                "category": "intervals",
                "description": "Test 15-minute interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INFY",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "15m"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "30-minute Interval",
                "category": "intervals",
                "description": "Test 30-minute interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "HDFC",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "30m"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "Weekly Interval",
                "category": "intervals",
                "description": "Test weekly interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "interval": "1wk"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            },
            {
                "name": "Monthly Interval",
                "category": "intervals",
                "description": "Test monthly interval data",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-06-01",
                    "interval": "1mo"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 1
                }
            }
        ]
    
    @staticmethod
    def get_performance_scenarios() -> List[Dict[str, Any]]:
        """Performance testing scenarios"""
        return [
            {
                "name": "Quick Response Test",
                "category": "performance",
                "description": "Test response time for small dataset",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "max_execution_time": 3.0  # seconds
                }
            },
            {
                "name": "Medium Dataset Test",
                "category": "performance",
                "description": "Test response time for medium dataset",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "max_execution_time": 5.0  # seconds
                }
            },
            {
                "name": "Large Dataset Test",
                "category": "performance",
                "description": "Test response time for large dataset",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "INFY",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07",
                    "interval": "1m"
                },
                "expected_result": {
                    "success": True,
                    "max_execution_time": 10.0  # seconds
                }
            }
        ]
    
    @staticmethod
    def get_edge_case_scenarios() -> List[Dict[str, Any]]:
        """Edge case testing scenarios"""
        return [
            {
                "name": "Weekend Date Range",
                "category": "edge_cases",
                "description": "Test with weekend dates (no trading)",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-06",  # Saturday
                    "end_date": "2024-01-07",   # Sunday
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 0  # May have no data
                }
            },
            {
                "name": "Holiday Date Range",
                "category": "edge_cases",
                "description": "Test with holiday dates",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-26",  # Republic Day
                    "end_date": "2024-01-26",
                    "interval": "1d"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 0  # Holiday - no trading
                }
            },
            {
                "name": "Very Short Time Range",
                "category": "edge_cases",
                "description": "Test with very short time range",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-01",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 0
                }
            },
            {
                "name": "Future Date Range",
                "category": "edge_cases",
                "description": "Test with future dates",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2025-12-01",
                    "end_date": "2025-12-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "min_data_points": 0  # Future dates - no data
                }
            }
        ]
    
    @staticmethod
    def get_caching_scenarios() -> List[Dict[str, Any]]:
        """Caching functionality test scenarios"""
        return [
            {
                "name": "Cache Hit Test - Same Request",
                "category": "caching",
                "description": "Test cache hit with identical request",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "RELIANCE",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "cache_performance": True  # Second call should be faster
                }
            },
            {
                "name": "Cache Miss Test - Different Symbol",
                "category": "caching",
                "description": "Test cache miss with different symbol",
                "function": "get_stock_chart_data",
                "args": {
                    "symbol": "TCS",
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-02",
                    "interval": "1h"
                },
                "expected_result": {
                    "success": True,
                    "cache_performance": False  # New request - no cache benefit
                }
            }
        ]
    
    @staticmethod
    def get_all_scenarios() -> List[Dict[str, Any]]:
        """Get all test scenarios"""
        all_scenarios = []
        all_scenarios.extend(TradingMCPTestScenarios.get_basic_scenarios())
        all_scenarios.extend(TradingMCPTestScenarios.get_validation_scenarios())
        all_scenarios.extend(TradingMCPTestScenarios.get_interval_scenarios())
        all_scenarios.extend(TradingMCPTestScenarios.get_performance_scenarios())
        all_scenarios.extend(TradingMCPTestScenarios.get_edge_case_scenarios())
        all_scenarios.extend(TradingMCPTestScenarios.get_caching_scenarios())
        return all_scenarios
    
    @staticmethod
    def get_scenarios_by_category(category: str) -> List[Dict[str, Any]]:
        """Get scenarios by category"""
        category_map = {
            "basic": TradingMCPTestScenarios.get_basic_scenarios,
            "validation": TradingMCPTestScenarios.get_validation_scenarios,
            "intervals": TradingMCPTestScenarios.get_interval_scenarios,
            "performance": TradingMCPTestScenarios.get_performance_scenarios,
            "edge_cases": TradingMCPTestScenarios.get_edge_case_scenarios,
            "caching": TradingMCPTestScenarios.get_caching_scenarios
        }
        
        if category in category_map:
            return category_map[category]()
        else:
            return []


class ScenarioRunner:
    """Test scenario execution and reporting"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.client: Optional[MCPTestClient] = None
        
    async def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        print(f"🧪 Running: {scenario['name']}")
        print(f"   Category: {scenario['category']}")
        print(f"   Description: {scenario['description']}")
        
        start_time = time.time()
        
        try:
            # Execute the test
            result = await self.client.call_tool(scenario['function'], scenario['args'])
            execution_time = time.time() - start_time
            
            # Parse result
            success = self._parse_result(result)
            
            # Validate against expected result
            validation_result = self._validate_result(success, scenario.get('expected_result', {}))
            
            print(f"   Result: {'✅ PASS' if validation_result['passed'] else '❌ FAIL'}")
            if not validation_result['passed']:
                print(f"   Reason: {validation_result['reason']}")
            print(f"   Execution time: {execution_time:.2f}s")
            
            return {
                "scenario": scenario['name'],
                "category": scenario['category'],
                "passed": validation_result['passed'],
                "execution_time": execution_time,
                "result": success,
                "validation": validation_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   Result: ❌ ERROR - {e}")
            
            return {
                "scenario": scenario['name'],
                "category": scenario['category'],
                "passed": False,
                "execution_time": execution_time,
                "error": str(e),
                "validation": {"passed": False, "reason": f"Exception: {e}"}
            }
    
    def _parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MCP tool result"""
        content = result.get('content', [])
        if not content:
            return {"success": False, "error": "No content in response"}
        
        text_content = content[0].get('text', '{}')
        try:
            if isinstance(text_content, str):
                return json.loads(text_content)
            else:
                return text_content
        except json.JSONDecodeError:
            return {"success": False, "error": "Failed to parse response"}
    
    def _validate_result(self, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate result against expected outcome"""
        if not expected:
            return {"passed": True, "reason": "No validation criteria"}
        
        # Check success flag
        if 'success' in expected:
            if result.get('success') != expected['success']:
                return {
                    "passed": False,
                    "reason": f"Expected success={expected['success']}, got {result.get('success')}"
                }
        
        # Check minimum data points
        if 'min_data_points' in expected and result.get('success'):
            data_points = len(result.get('data', []))
            if data_points < expected['min_data_points']:
                return {
                    "passed": False,
                    "reason": f"Expected min {expected['min_data_points']} data points, got {data_points}"
                }
        
        # Check error type
        if 'error_type' in expected and not result.get('success'):
            error_code = result.get('error_code', '')
            if error_code != expected['error_type']:
                return {
                    "passed": False,
                    "reason": f"Expected error type {expected['error_type']}, got {error_code}"
                }
        
        return {"passed": True, "reason": "All validations passed"}
    
    async def run_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run multiple scenarios and generate report"""
        if not scenarios:
            return {"error": "No scenarios provided"}
        
        print(f"🚀 Running {len(scenarios)} test scenarios")
        print("=" * 60)
        
        # Start MCP client
        server_command = ["python", "-m", "trading_mcp.server"]
        self.client = MCPTestClient(server_command, str(self.project_root))
        
        try:
            if not await self.client.start():
                return {"error": "Failed to start MCP client"}
            
            results = []
            for scenario in scenarios:
                result = await self.run_scenario(scenario)
                results.append(result)
                print()  # Add spacing between tests
                
                # Add delay between tests
                await asyncio.sleep(0.5)
            
            # Generate report
            report = self._generate_report(results)
            return report
            
        finally:
            if self.client:
                await self.client.close()
    
    def _generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        # Group by category
        categories = {}
        for result in results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'failed': 0}
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        # Calculate average execution time
        avg_execution_time = sum(r['execution_time'] for r in results) / len(results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "avg_execution_time": avg_execution_time
            },
            "categories": categories,
            "results": results
        }
        
        self._print_report(report)
        return report
    
    def _print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted test report"""
        print("\n📊 Test Report")
        print("=" * 60)
        
        summary = report['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Average Execution Time: {summary['avg_execution_time']:.2f}s")
        
        print(f"\n📋 Results by Category:")
        for category, stats in report['categories'].items():
            success_rate = (stats['passed'] / stats['total']) * 100
            print(f"  {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in report['results'] if not r['passed']]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['scenario']} - {test['validation']['reason']}")


async def main():
    """Main entry point for test scenario runner"""
    parser = argparse.ArgumentParser(description="Trading MCP Test Scenarios")
    parser.add_argument("--scenario", 
                       choices=["basic", "validation", "intervals", "performance", "edge_cases", "caching", "all"],
                       default="all",
                       help="Test scenario category to run")
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available Test Scenarios:")
        print("=" * 60)
        
        categories = {
            "basic": "Basic functionality tests",
            "validation": "Input validation tests",
            "intervals": "Time interval tests",
            "performance": "Performance benchmarks",
            "edge_cases": "Edge case handling",
            "caching": "Caching functionality"
        }
        
        for category, description in categories.items():
            scenarios = TradingMCPTestScenarios.get_scenarios_by_category(category)
            print(f"\n{category.upper()} ({len(scenarios)} tests): {description}")
            for scenario in scenarios:
                print(f"  • {scenario['name']}")
        
        return
    
    # Get scenarios to run
    if args.scenario == "all":
        scenarios = TradingMCPTestScenarios.get_all_scenarios()
    else:
        scenarios = TradingMCPTestScenarios.get_scenarios_by_category(args.scenario)
    
    if not scenarios:
        print(f"No scenarios found for category: {args.scenario}")
        return
    
    # Run scenarios
    project_root = Path(__file__).parent.parent
    runner = ScenarioRunner(project_root)
    
    await runner.run_scenarios(scenarios)


if __name__ == "__main__":
    asyncio.run(main())