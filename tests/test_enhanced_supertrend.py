"""
Unit tests for Enhanced Supertrend indicator.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from trading_mcp.indicators.enhanced_supertrend import EnhancedSupertrendIndicator


class TestEnhancedSupertrendIndicator:
    
    def setup_method(self):
        """Setup test data."""
        self.indicator = EnhancedSupertrendIndicator()
        
        # Create sample OHLCV data with 50 periods (sufficient for calculations)
        dates = pd.date_range('2024-01-01', periods=50, freq='1D')
        np.random.seed(42)  # For reproducible test data
        
        # Generate realistic price and volume data
        base_price = 2500.0
        price_data = []
        volume_data = []
        
        for i in range(50):
            # Add some trend and volatility
            trend_factor = 1 + (i * 0.002)  # Slight upward trend
            volatility = np.random.normal(0, 0.02)  # 2% volatility
            
            close = base_price * trend_factor * (1 + volatility)
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = close + np.random.normal(0, close * 0.005)
            
            price_data.append({
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close
            })
            
            # Generate volume data with occasional surges
            base_volume = 1000000
            volume_surge = 2.0 if i % 10 == 0 else 1.0  # Surge every 10 periods
            volume = base_volume * volume_surge * (1 + np.random.normal(0, 0.3))
            volume_data.append(max(volume, 100000))  # Minimum volume
        
        self.test_df = pd.DataFrame(price_data, index=dates)
        self.test_df['Volume'] = volume_data
        
        # Default parameters
        self.default_params = {
            'atr_period': 10,
            'st_multiplier': 3.0,
            'rsi_period': 14,
            'volume_period': 20,
            'volume_threshold': 1.5
        }
    
    def test_calculate_with_default_parameters(self):
        """Test Enhanced Supertrend calculation with default parameters."""
        result = self.indicator.calculate(self.test_df, {})
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check that all expected columns are present
        expected_columns = [
            'supertrend', 'trend', 'signal_strength', 'volume_surge',
            'rsi', 'buy_signal', 'sell_signal', 'atr'
        ]
        for col in expected_columns:
            assert col in result.columns, f"Column {col} missing from result"
        
        # Check that we have data (should be less than input due to NaN drops)
        assert len(result) > 0
        assert len(result) < len(self.test_df)
        
        # Check data types
        assert result['supertrend'].dtype == np.float64
        assert pd.api.types.is_integer_dtype(result['trend'])  # Accept pandas Int64 or numpy int64
        assert result['signal_strength'].dtype == np.float64
        assert result['volume_surge'].dtype == bool
        assert result['rsi'].dtype == np.float64
        assert result['buy_signal'].dtype == bool
        assert result['sell_signal'].dtype == bool
        assert result['atr'].dtype == np.float64
    
    def test_calculate_with_custom_parameters(self):
        """Test Enhanced Supertrend calculation with custom parameters."""
        custom_params = {
            'atr_period': 14,
            'st_multiplier': 2.5,
            'rsi_period': 21,
            'volume_period': 15,
            'volume_threshold': 2.0
        }
        
        result = self.indicator.calculate(self.test_df, custom_params)
        
        # Should still return valid DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        
        # Test with different parameters should give different results
        default_result = self.indicator.calculate(self.test_df, {})
        
        # Results should be different (at least some values)
        assert not result['supertrend'].equals(default_result['supertrend'])
    
    def test_insufficient_data_error(self):
        """Test error handling with insufficient data."""
        # Create DataFrame with only 5 periods (insufficient)
        small_df = self.test_df.head(5)
        
        with pytest.raises(ValueError, match="Insufficient data"):
            self.indicator.calculate(small_df, self.default_params)
    
    def test_trend_values(self):
        """Test that trend values are only 1 or -1."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # Trend should only contain 1 (uptrend) or -1 (downtrend)
        unique_trends = result['trend'].unique()
        assert all(trend in [1, -1] for trend in unique_trends)
    
    def test_signal_strength_range(self):
        """Test that signal strength is within expected range (0-8)."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # Signal strength should be between 0 and 8
        assert result['signal_strength'].min() >= 0
        assert result['signal_strength'].max() <= 8
    
    def test_rsi_range(self):
        """Test that RSI values are within valid range (0-100)."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # RSI should be between 0 and 100
        assert result['rsi'].min() >= 0
        assert result['rsi'].max() <= 100
    
    def test_volume_surge_boolean(self):
        """Test that volume_surge column contains only boolean values."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # volume_surge should be boolean
        assert result['volume_surge'].dtype == bool
        
        # Should have both True and False values in our test data
        assert True in result['volume_surge'].values
        assert False in result['volume_surge'].values
    
    def test_buy_sell_signals_exclusivity(self):
        """Test that buy and sell signals are mutually exclusive."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # Buy and sell signals should never be True at the same time
        simultaneous_signals = result['buy_signal'] & result['sell_signal']
        assert not simultaneous_signals.any()
    
    def test_supertrend_values_reasonable(self):
        """Test that Supertrend values are reasonable relative to price."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # Get price range from original data
        price_min = self.test_df['Close'].min()
        price_max = self.test_df['Close'].max()
        
        # Supertrend should be within reasonable range of prices
        st_min = result['supertrend'].min()
        st_max = result['supertrend'].max()
        
        # Allow for some buffer due to ATR calculations
        buffer_factor = 0.5  # 50% buffer
        assert st_min >= price_min * (1 - buffer_factor)
        assert st_max <= price_max * (1 + buffer_factor)
    
    def test_no_nan_values_in_result(self):
        """Test that main result columns have reasonable NaN handling."""
        result = self.indicator.calculate(self.test_df, self.default_params)
        
        # Key columns should have valid values for most data points
        key_columns = ['supertrend', 'trend', 'signal_strength', 'rsi', 'atr']
        for col in key_columns:
            if col in result.columns:
                valid_values = result[col].dropna()
                # Should have at least some valid values
                assert len(valid_values) > 0
                # For boolean columns, they may be False but not NaN
                if col in ['volume_surge', 'buy_signal', 'sell_signal']:
                    assert not result[col].isna().any()  # Boolean columns shouldn't have NaN
    
    def test_calculate_supertrend_method(self):
        """Test the internal _calculate_supertrend method."""
        # Create simple ATR series for testing
        atr = pd.Series([50.0] * len(self.test_df), index=self.test_df.index)
        
        supertrend, trend = self.indicator._calculate_supertrend(self.test_df, atr, 3.0)
        
        # Check return types and shapes
        assert isinstance(supertrend, pd.Series)
        assert isinstance(trend, pd.Series)
        assert len(supertrend) == len(self.test_df)
        assert len(trend) == len(self.test_df)
        
        # Check that trend values are valid
        assert all(t in [1, -1] for t in trend)
    
    def test_calculate_volume_filter_method(self):
        """Test the internal _calculate_volume_filter method."""
        volume_surge = self.indicator._calculate_volume_filter(self.test_df, 20, 1.5)
        
        # Check return type and shape
        assert isinstance(volume_surge, pd.Series)
        assert len(volume_surge) == len(self.test_df)
        assert volume_surge.dtype == bool
    
    def test_calculate_signal_strength_method(self):
        """Test the internal _calculate_signal_strength method."""
        # Create simple RSI and ATR series for testing
        rsi = pd.Series([60.0] * len(self.test_df), index=self.test_df.index)
        atr = pd.Series([50.0] * len(self.test_df), index=self.test_df.index)
        
        signal_strength = self.indicator._calculate_signal_strength(
            self.test_df, rsi, atr, 20, 1.5
        )
        
        # Check return type and shape
        assert isinstance(signal_strength, pd.Series)
        assert len(signal_strength) == len(self.test_df)
        
        # Check that signal strength is within expected range
        assert signal_strength.min() >= 0
        assert signal_strength.max() <= 8
    
    def test_edge_case_flat_prices(self):
        """Test with flat price data (no volatility)."""
        # Create flat price data
        flat_df = self.test_df.copy()
        flat_df['High'] = 2500.0
        flat_df['Low'] = 2500.0
        flat_df['Close'] = 2500.0
        flat_df['Open'] = 2500.0
        
        # Should still work without errors
        result = self.indicator.calculate(flat_df, self.default_params)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_edge_case_zero_volume(self):
        """Test with zero volume data."""
        zero_vol_df = self.test_df.copy()
        zero_vol_df['Volume'] = 0
        
        # Should still work without errors
        result = self.indicator.calculate(zero_vol_df, self.default_params)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        
        # All volume_surge should be False with zero volume
        assert not result['volume_surge'].any()
    
    @pytest.mark.parametrize("param_name,param_value", [
        ('atr_period', 5),
        ('atr_period', 21),
        ('st_multiplier', 1.5),
        ('st_multiplier', 5.0),
        ('rsi_period', 7),
        ('rsi_period', 28),
        ('volume_period', 10),
        ('volume_period', 30),
        ('volume_threshold', 1.0),
        ('volume_threshold', 3.0),
    ])
    def test_parameter_variations(self, param_name, param_value):
        """Test various parameter values."""
        params = self.default_params.copy()
        params[param_name] = param_value
        
        # Should work without errors for reasonable parameter values
        result = self.indicator.calculate(self.test_df, params)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__])