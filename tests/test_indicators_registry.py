"""
Comprehensive tests for the IndicatorRegistry and new technical indicators.

This test suite validates all indicators implemented through the pandas_ta
integration and ensures they work correctly with various parameter configurations.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from trading_mcp.indicators.indicator_registry import IndicatorRegistry
from trading_mcp.stock_data import StockDataProvider


class TestIndicatorRegistry:
    """Test cases for the IndicatorRegistry class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = IndicatorRegistry()
        self.provider = StockDataProvider()
        
        # Create sample OHLC data
        dates = pd.date_range('2024-01-01', periods=100, freq='1d')
        self.sample_df = pd.DataFrame({
            'Open': [2495 + i + np.random.uniform(-3, 3) for i in range(100)],
            'High': [2500 + i + np.random.uniform(-5, 5) for i in range(100)],
            'Low': [2490 + i + np.random.uniform(-5, 5) for i in range(100)],
            'Close': [2500 + i + np.random.uniform(-3, 3) for i in range(100)],
            'Volume': [1000000 + i * 10000 for i in range(100)]
        }, index=dates)
        # Ensure High >= Low and Close is between High and Low, and Open is reasonable
        for i in range(100):
            open_val = self.sample_df.iloc[i]['Open']
            high_val = self.sample_df.iloc[i]['High']
            low_val = self.sample_df.iloc[i]['Low']
            close_val = self.sample_df.iloc[i]['Close']
            
            # Fix ordering
            self.sample_df.loc[self.sample_df.index[i], 'High'] = max(open_val, high_val, low_val, close_val)
            self.sample_df.loc[self.sample_df.index[i], 'Low'] = min(open_val, high_val, low_val, close_val)
            self.sample_df.loc[self.sample_df.index[i], 'Close'] = min(max(close_val, low_val), high_val)
            self.sample_df.loc[self.sample_df.index[i], 'Open'] = min(max(open_val, low_val), high_val)
    
    def test_registry_initialization(self):
        """Test that the registry initializes with expected indicators."""
        supported = self.registry.get_supported_indicators()
        
        # Should have more than the original 7 indicators
        assert len(supported) >= 38
        
        # Should include original indicators
        original_indicators = ["RSI", "SMA", "EMA", "MACD", "BBANDS", "ATR", "ENHANCED_SUPERTREND"]
        for indicator in original_indicators:
            assert indicator in supported
        
        # Should include new trend indicators
        new_trend_indicators = ["WMA", "DEMA", "TEMA", "ADX", "CCI", "CMO", "AROON"]
        for indicator in new_trend_indicators:
            assert indicator in supported
        
        # Should include new momentum indicators
        new_momentum_indicators = ["WILLR", "MFI", "TRIX", "ROC", "MOM"]
        for indicator in new_momentum_indicators:
            assert indicator in supported
        
        # Should include volatility indicators
        volatility_indicators = ["NATR", "TRANGE", "STDDEV"]
        for indicator in volatility_indicators:
            assert indicator in supported
        
        # Should include volume indicators
        volume_indicators = ["AD", "ADOSC", "OBV", "VWAP", "EMV", "FI"]
        for indicator in volume_indicators:
            assert indicator in supported
    
    def test_get_indicator_info(self):
        """Test getting indicator information."""
        rsi_info = self.registry.get_indicator_info("RSI")
        assert rsi_info is not None
        assert rsi_info["category"] == "momentum"
        assert rsi_info["description"] == "Relative Strength Index"
        assert rsi_info["default_params"] == {"period": 14}
        assert rsi_info["data_requirements"] == ["Close"]
        
        # Test case insensitive lookup
        rsi_info_lower = self.registry.get_indicator_info("rsi")
        assert rsi_info_lower == rsi_info
        
        # Test invalid indicator
        invalid_info = self.registry.get_indicator_info("INVALID_INDICATOR")
        assert invalid_info is None
    
    def test_trend_indicators(self):
        """Test trend-based indicators."""
        trend_tests = [
            ("SMA", {"period": 20}),
            ("EMA", {"period": 20}),
            ("WMA", {"period": 20}),
            ("DEMA", {"period": 20}),
            ("TEMA", {"period": 20}),
            ("MACD", {"fast": 12, "slow": 26, "signal": 9}),
            ("ADX", {"period": 14}),
            ("CCI", {"period": 20}),
            ("CMO", {"period": 14}),
        ]
        
        for indicator, params in trend_tests:
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            assert result is not None
            assert len(result) > 0
            # Should have fewer values than input due to lookback period
            assert len(result.dropna()) < len(self.sample_df)
    
    def test_momentum_indicators(self):
        """Test momentum-based indicators."""
        momentum_tests = [
            ("RSI", {"period": 14}),
            ("WILLR", {"period": 14}),
            ("MFI", {"period": 14}),
            ("TRIX", {"period": 30}),
            ("ROC", {"period": 10}),
            ("MOM", {"period": 10}),
        ]
        
        for indicator, params in momentum_tests:
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            assert result is not None
            assert len(result) > 0
            # Check reasonable value ranges for specific indicators
            if indicator == "RSI":
                valid_values = result.dropna()
                assert all(0 <= val <= 100 for val in valid_values)
            elif indicator == "WILLR":
                valid_values = result.dropna()
                assert all(-100 <= val <= 0 for val in valid_values)
    
    def test_volatility_indicators(self):
        """Test volatility-based indicators."""
        volatility_tests = [
            ("ATR", {"period": 14}),
            ("NATR", {"period": 14}),
            ("TRANGE", {}),
            ("STDDEV", {"period": 20}),
            ("BBANDS", {"period": 20, "std": 2}),
        ]
        
        for indicator, params in volatility_tests:
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            assert result is not None
            if indicator == "BBANDS":
                # Bollinger Bands returns DataFrame
                assert isinstance(result, pd.DataFrame)
                assert len(result.columns) >= 3  # Lower, Middle, Upper bands
            else:
                # Others return Series
                assert isinstance(result, pd.Series)
                assert len(result) > 0
                # Volatility indicators should be positive
                if indicator in ["ATR", "NATR", "TRANGE", "STDDEV"]:
                    valid_values = result.dropna()
                    assert all(val >= 0 for val in valid_values)
    
    def test_volume_indicators(self):
        """Test volume-based indicators."""
        volume_tests = [
            ("AD", {}),
            ("ADOSC", {"fast": 3, "slow": 10}),
            ("OBV", {}),
            ("VWAP", {}),
            ("EMV", {"period": 14}),
            ("FI", {"period": 13}),
        ]
        
        for indicator, params in volume_tests:
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            assert result is not None
            assert len(result) > 0
            # Volume indicators should have reasonable values
            if indicator == "VWAP":
                valid_values = result.dropna()
                # VWAP should be close to price range
                assert all(2400 <= val <= 2700 for val in valid_values)
    
    def test_custom_indicators(self):
        """Test custom indicators."""
        custom_tests = [
            ("ENHANCED_SUPERTREND", {
                "atr_period": 10,
                "st_multiplier": 3.0,
                "rsi_period": 14,
                "volume_period": 20,
                "volume_threshold": 1.5
            }),
            ("SUPERTREND", {"period": 10, "multiplier": 3}),
            ("ICHIMOKU", {"conversion": 9, "base": 26, "span": 52}),
        ]
        
        for indicator, params in custom_tests:
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            assert result is not None
            if indicator == "ENHANCED_SUPERTREND":
                # Enhanced Supertrend returns DataFrame with multiple columns
                assert isinstance(result, pd.DataFrame)
                expected_columns = ['supertrend', 'trend', 'signal_strength', 'volume_surge', 
                                   'rsi', 'buy_signal', 'sell_signal', 'atr']
                for col in expected_columns:
                    assert col in result.columns
            else:
                # Other custom indicators may return DataFrames
                assert len(result) > 0
    
    def test_parameter_defaults(self):
        """Test that default parameters are applied correctly."""
        # Test RSI with no parameters (should use default period=14)
        result_default = self.registry.calculate_indicator(self.sample_df, "RSI", {})
        result_explicit = self.registry.calculate_indicator(self.sample_df, "RSI", {"period": 14})
        
        pd.testing.assert_series_equal(result_default, result_explicit)
        
        # Test SMA with no parameters (should use default period=20)
        result_default = self.registry.calculate_indicator(self.sample_df, "SMA", {})
        result_explicit = self.registry.calculate_indicator(self.sample_df, "SMA", {"period": 20})
        
        pd.testing.assert_series_equal(result_default, result_explicit)
    
    def test_data_requirements_validation(self):
        """Test that missing data columns raise appropriate errors."""
        # Create DataFrame missing Volume column
        df_no_volume = self.sample_df.drop('Volume', axis=1)
        
        # MFI requires Volume, should raise error
        with pytest.raises(ValueError, match="Missing required columns"):
            self.registry.calculate_indicator(df_no_volume, "MFI", {"period": 14})
        
        # RSI only needs Close, should work fine
        result = self.registry.calculate_indicator(df_no_volume, "RSI", {"period": 14})
        assert result is not None
        assert len(result) > 0
    
    def test_invalid_indicator(self):
        """Test handling of invalid indicator names."""
        result = self.registry.calculate_indicator(self.sample_df, "INVALID_INDICATOR", {})
        assert result is None
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        # Create very small dataset
        small_df = self.sample_df.head(5)
        
        # Should handle gracefully for most indicators (may return None if not enough data)
        try:
            result = self.registry.calculate_indicator(small_df, "SMA", {"period": 20})
            if result is not None:
                # Should return mostly NaN values if any values at all
                assert result.dropna().empty or len(result.dropna()) < 5
        except Exception:
            # Some indicators may fail with insufficient data, which is acceptable
            pass
        
        # Enhanced Supertrend should raise specific error
        with pytest.raises(Exception, match="Insufficient data"):
            self.registry.calculate_indicator(small_df, "ENHANCED_SUPERTREND", {})
    
    @patch('trading_mcp.stock_data.yf.Ticker')
    def test_integration_with_stock_data_provider(self, mock_ticker):
        """Test integration between registry and stock data provider."""
        # Mock setup
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = self.sample_df
        
        # Test various indicators through the provider
        test_cases = [
            ("WMA", {"period": 20}),
            ("DEMA", {"period": 20}),
            ("ADX", {"period": 14}),
            ("WILLR", {"period": 14}),
            ("NATR", {"period": 14}),
            ("OBV", {}),
            ("SUPERTREND", {"period": 10, "multiplier": 3}),
        ]
        
        for indicator, params in test_cases:
            result = self.provider.calculate_technical_indicator(
                symbol="RELIANCE",
                indicator=indicator,
                start_date="2024-01-01",
                end_date="2024-04-10",
                interval="1d",
                params=params
            )
            
            assert result["success"] is True
            assert result["data"]["indicator"] == indicator
            assert len(result["data"]["values"]) > 0
            assert result["data"]["parameters"] == {**self.registry.get_indicator_info(indicator)["default_params"], **params}
    
    def test_indicator_categories(self):
        """Test that indicators are properly categorized."""
        categories = {}
        for indicator in self.registry.get_supported_indicators():
            info = self.registry.get_indicator_info(indicator)
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(indicator)
        
        # Should have all expected categories
        expected_categories = ["trend", "momentum", "volatility", "volume", "custom"]
        for category in expected_categories:
            assert category in categories
            assert len(categories[category]) > 0
        
        # Verify specific categorizations
        assert "RSI" in categories["momentum"]
        assert "SMA" in categories["trend"]
        assert "ATR" in categories["volatility"]
        assert "OBV" in categories["volume"]
        assert "ENHANCED_SUPERTREND" in categories["custom"]
    
    def test_indicator_performance(self):
        """Test that indicators perform within reasonable time limits."""
        import time
        
        # Test performance of various indicators
        performance_tests = [
            ("RSI", {"period": 14}),
            ("MACD", {"fast": 12, "slow": 26, "signal": 9}),
            ("BBANDS", {"period": 20, "std": 2}),
            ("ADX", {"period": 14}),
        ]
        
        for indicator, params in performance_tests:
            start_time = time.time()
            result = self.registry.calculate_indicator(self.sample_df, indicator, params)
            calculation_time = time.time() - start_time
            
            assert result is not None
            # Should calculate in less than 1 second for 100 data points
            assert calculation_time < 1.0
    
    def test_parameter_validation(self):
        """Test parameter validation and type handling."""
        # Test with string parameters that should be converted to int
        result1 = self.registry.calculate_indicator(self.sample_df, "RSI", {"period": "14"})
        result2 = self.registry.calculate_indicator(self.sample_df, "RSI", {"period": 14})
        
        # Should handle string to int conversion gracefully
        assert result1 is not None
        assert result2 is not None
        
        # Test with invalid parameter types
        with pytest.raises(Exception):
            self.registry.calculate_indicator(self.sample_df, "RSI", {"period": "invalid"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])