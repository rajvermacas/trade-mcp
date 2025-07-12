"""
Enhanced Supertrend indicator implementation.

This module contains the Enhanced Supertrend strategy logic adapted for the Trading MCP server.
Based on the original strategy that combines multiple filters for improved performance.
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import time
from typing import Dict, Any


class EnhancedSupertrendIndicator:
    """
    Enhanced Supertrend indicator with multiple filters for signal confirmation.
    
    Features:
    - Traditional Supertrend calculation with ATR
    - Volume surge confirmation filter
    - RSI momentum filter  
    - ML-based signal strength scoring
    - Buy/sell signal generation
    """
    
    def calculate(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Calculate Enhanced Supertrend indicator with multiple filters.
        
        Args:
            df: OHLCV DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
            params: Parameters dictionary with optional keys:
                - atr_period: ATR calculation period (default: 10)
                - st_multiplier: Supertrend multiplier (default: 3.0)
                - rsi_period: RSI calculation period (default: 14)
                - volume_period: Volume moving average period (default: 20)
                - volume_threshold: Volume surge threshold multiplier (default: 1.5)
        
        Returns:
            DataFrame with columns:
            - supertrend: Supertrend line value
            - trend: 1 for uptrend, -1 for downtrend  
            - signal_strength: ML-based signal strength score (0-8)
            - volume_surge: Boolean indicating volume surge
            - rsi: RSI value
            - buy_signal: Boolean buy signal
            - sell_signal: Boolean sell signal
            - atr: Average True Range value
        """
        # Get parameters with defaults
        atr_period = params.get("atr_period", 10)
        st_multiplier = params.get("st_multiplier", 3.0)
        rsi_period = params.get("rsi_period", 14)
        volume_period = params.get("volume_period", 20)
        volume_threshold = params.get("volume_threshold", 1.5)
        
        # Ensure we have enough data
        min_periods = max(atr_period, rsi_period, volume_period) + 10
        if len(df) < min_periods:
            raise ValueError(f"Insufficient data: need at least {min_periods} periods, got {len(df)}")
        
        # Calculate ATR using pandas_ta
        atr = ta.atr(df['High'], df['Low'], df['Close'], length=atr_period)
        
        # Calculate Supertrend
        supertrend, trend = self._calculate_supertrend(df, atr, st_multiplier)
        
        # Calculate RSI using pandas_ta
        rsi = ta.rsi(df['Close'], length=rsi_period)
        
        # Calculate volume filter
        volume_surge = self._calculate_volume_filter(df, volume_period, volume_threshold)
        
        # RSI conditions for entry
        rsi_buy_condition = (rsi >= 40) & (rsi <= 80)
        rsi_sell_condition = (rsi >= 20) & (rsi <= 60)
        
        # Generate entry signals
        buy_signal = (
            (trend == 1) &  # Uptrend
            (trend.shift(1) == -1) &  # Previous bar was downtrend (signal)
            volume_surge &  # Volume confirmation
            rsi_buy_condition  # RSI not overbought
        )
        
        sell_signal = (
            (trend == -1) &  # Downtrend  
            (trend.shift(1) == 1) &  # Previous bar was uptrend (signal)
            volume_surge &  # Volume confirmation
            rsi_sell_condition  # RSI not oversold
        )
        
        # Calculate signal strength (ML scoring)
        signal_strength = self._calculate_signal_strength(df, rsi, atr, volume_period, volume_threshold)
        
        # Create result DataFrame
        result = pd.DataFrame(index=df.index)
        result['supertrend'] = supertrend
        result['trend'] = trend.astype('Int64')  # Use nullable integer type to handle NaN
        result['signal_strength'] = signal_strength
        result['volume_surge'] = volume_surge
        result['rsi'] = rsi
        result['buy_signal'] = buy_signal
        result['sell_signal'] = sell_signal
        result['atr'] = atr
        
        # Drop rows where essential indicators are NaN
        # Keep rows where at least supertrend, trend, and atr are valid
        essential_cols = ['supertrend', 'trend', 'atr']
        result = result.dropna(subset=essential_cols)
        
        return result
    
    def _calculate_supertrend(self, df: pd.DataFrame, atr: pd.Series, multiplier: float) -> tuple:
        """Calculate Supertrend indicator and trend direction."""
        high = df['High']
        low = df['Low'] 
        close = df['Close']
        
        # Calculate basic upper and lower bands
        hl2 = (high + low) / 2
        basic_upper = hl2 + (multiplier * atr)
        basic_lower = hl2 - (multiplier * atr)
        
        # Calculate final upper and lower bands
        final_upper = basic_upper.copy()
        final_lower = basic_lower.copy()
        
        # Find first valid ATR index
        first_valid_idx = atr.first_valid_index()
        if first_valid_idx is None:
            # All ATR values are NaN, return empty series
            return pd.Series(index=df.index, dtype=float), pd.Series(index=df.index, dtype=int)
        
        first_valid_pos = df.index.get_loc(first_valid_idx)
        
        for i in range(first_valid_pos + 1, len(df)):
            # Skip if current or previous ATR is NaN
            if pd.isna(basic_upper.iloc[i]) or pd.isna(final_upper.iloc[i-1]):
                continue
                
            # Final Upper Band
            if basic_upper.iloc[i] < final_upper.iloc[i-1] or close.iloc[i-1] > final_upper.iloc[i-1]:
                final_upper.iloc[i] = basic_upper.iloc[i]
            else:
                final_upper.iloc[i] = final_upper.iloc[i-1]
                
            # Final Lower Band    
            if basic_lower.iloc[i] > final_lower.iloc[i-1] or close.iloc[i-1] < final_lower.iloc[i-1]:
                final_lower.iloc[i] = basic_lower.iloc[i]
            else:
                final_lower.iloc[i] = final_lower.iloc[i-1]
        
        # Calculate Supertrend and trend
        supertrend = pd.Series(index=df.index, dtype=float)
        trend = pd.Series(index=df.index, dtype=int)
        
        # Start from first valid ATR index
        if pd.notna(final_lower.iloc[first_valid_pos]):
            supertrend.iloc[first_valid_pos] = final_lower.iloc[first_valid_pos]
            trend.iloc[first_valid_pos] = 1
        
        for i in range(first_valid_pos + 1, len(df)):
            # Skip if essential values are NaN
            if pd.isna(final_lower.iloc[i]) or pd.isna(final_upper.iloc[i]):
                continue
                
            if close.iloc[i] <= final_lower.iloc[i]:
                supertrend.iloc[i] = final_lower.iloc[i]
                trend.iloc[i] = 1
            elif close.iloc[i] >= final_upper.iloc[i]:
                supertrend.iloc[i] = final_upper.iloc[i]
                trend.iloc[i] = -1
            else:
                if pd.notna(supertrend.iloc[i-1]) and pd.notna(trend.iloc[i-1]):
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    trend.iloc[i] = trend.iloc[i-1]
        
        return supertrend, trend
    
    def _calculate_volume_filter(self, df: pd.DataFrame, period: int, threshold: float) -> pd.Series:
        """Calculate volume confirmation filter."""
        volume_avg = df['Volume'].rolling(window=period).mean()
        volume_surge = df['Volume'] > (volume_avg * threshold)
        return volume_surge
    
    def _calculate_signal_strength(self, df: pd.DataFrame, rsi: pd.Series, atr: pd.Series, 
                                 volume_period: int, volume_threshold: float) -> pd.Series:
        """Calculate ML-based signal strength scoring (0-8 points)."""
        signal_strength = pd.Series(0, index=df.index, dtype=float)
        
        # Volume surge intensity (0-3 points)
        volume_avg = df['Volume'].rolling(window=volume_period).mean()
        volume_intensity = df['Volume'] / volume_avg
        signal_strength += np.where(volume_intensity > 2.0, 3,
                                   np.where(volume_intensity > 1.8, 2,
                                           np.where(volume_intensity > 1.5, 1, 0)))
        
        # RSI momentum (0-2 points)
        signal_strength += np.where((rsi > 50) & (rsi < 70), 2,
                                   np.where((rsi > 30) & (rsi < 80), 1, 0))
        
        # Volatility factor (0-2 points) - stable market conditions preferred
        atr_avg = atr.rolling(20).mean()
        signal_strength += np.where(atr < atr_avg * 1.2, 2,
                                   np.where(atr < atr_avg * 1.5, 1, 0))
        
        # Time of day factor (0-1 points) - morning hours preferred
        # Note: In practice, this would use actual timestamps, here we approximate
        signal_strength += 1  # Simplified for now
        
        return signal_strength