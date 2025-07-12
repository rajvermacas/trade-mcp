"""
Technical Indicator Registry for Trading MCP Server

This module provides a comprehensive registry of technical indicators mapping
PRD Appendix A specifications to pandas_ta and custom implementations.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
import pandas as pd
import pandas_ta as ta
import numpy as np
from .enhanced_supertrend import EnhancedSupertrendIndicator


class IndicatorRegistry:
    """Registry for all supported technical indicators."""
    
    def __init__(self):
        """Initialize the indicator registry with all supported indicators."""
        self._registry = {}
        self._setup_registry()
    
    def _setup_registry(self):
        """Setup the complete indicator registry mapping PRD indicators to implementations."""
        
        # Trend Indicators
        self._registry.update({
            # Moving Averages
            "SMA": {
                "category": "trend",
                "description": "Simple Moving Average",
                "function": self._sma,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "EMA": {
                "category": "trend", 
                "description": "Exponential Moving Average",
                "function": self._ema,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "WMA": {
                "category": "trend",
                "description": "Weighted Moving Average", 
                "function": self._wma,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "DEMA": {
                "category": "trend",
                "description": "Double Exponential Moving Average",
                "function": self._dema,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "TEMA": {
                "category": "trend",
                "description": "Triple Exponential Moving Average",
                "function": self._tema,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            
            # Oscillators and Trend Indicators
            "MACD": {
                "category": "trend",
                "description": "Moving Average Convergence Divergence",
                "function": self._macd,
                "default_params": {"fast": 12, "slow": 26, "signal": 9},
                "required_params": ["fast", "slow", "signal"],
                "data_requirements": ["Close"]
            },
            "ADX": {
                "category": "trend",
                "description": "Average Directional Index",
                "function": self._adx,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "APO": {
                "category": "trend",
                "description": "Absolute Price Oscillator",
                "function": self._apo,
                "default_params": {"fast": 12, "slow": 26},
                "required_params": ["fast", "slow"],
                "data_requirements": ["Close"]
            },
            "AROON": {
                "category": "trend",
                "description": "Aroon Indicator",
                "function": self._aroon,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low"]
            },
            "AROONOSC": {
                "category": "trend",
                "description": "Aroon Oscillator",
                "function": self._aroon_osc,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low"]
            },
            "CCI": {
                "category": "trend",
                "description": "Commodity Channel Index",
                "function": self._cci,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "CMO": {
                "category": "trend",
                "description": "Chande Momentum Oscillator",
                "function": self._cmo,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "DX": {
                "category": "trend",
                "description": "Directional Movement Index",
                "function": self._dx,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "MINUS_DI": {
                "category": "trend",
                "description": "Minus Directional Indicator",
                "function": self._minus_di,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "PLUS_DI": {
                "category": "trend",
                "description": "Plus Directional Indicator",
                "function": self._plus_di,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "PPO": {
                "category": "trend",
                "description": "Percentage Price Oscillator",
                "function": self._ppo,
                "default_params": {"fast": 12, "slow": 26},
                "required_params": ["fast", "slow"],
                "data_requirements": ["Close"]
            },
        })
        
        # Momentum Indicators
        self._registry.update({
            "RSI": {
                "category": "momentum",
                "description": "Relative Strength Index",
                "function": self._rsi,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "STOCH": {
                "category": "momentum",
                "description": "Stochastic Oscillator",
                "function": self._stoch,
                "default_params": {"fastk": 14, "slowk": 3, "slowd": 3},
                "required_params": ["fastk", "slowk", "slowd"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "WILLR": {
                "category": "momentum",
                "description": "Williams %R",
                "function": self._willr,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "MFI": {
                "category": "momentum",
                "description": "Money Flow Index",
                "function": self._mfi,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close", "Volume"]
            },
            "TRIX": {
                "category": "momentum",
                "description": "Triple Exponential Average",
                "function": self._trix,
                "default_params": {"period": 30},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "ULTOSC": {
                "category": "momentum",
                "description": "Ultimate Oscillator",
                "function": self._ultosc,
                "default_params": {"period1": 7, "period2": 14, "period3": 28},
                "required_params": ["period1", "period2", "period3"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "ROC": {
                "category": "momentum",
                "description": "Rate of Change",
                "function": self._roc,
                "default_params": {"period": 10},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
            "MOM": {
                "category": "momentum",
                "description": "Momentum",
                "function": self._mom,
                "default_params": {"period": 10},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
        })
        
        # Volatility Indicators
        self._registry.update({
            "BBANDS": {
                "category": "volatility",
                "description": "Bollinger Bands",
                "function": self._bbands,
                "default_params": {"period": 20, "std": 2},
                "required_params": ["period", "std"],
                "data_requirements": ["Close"]
            },
            "ATR": {
                "category": "volatility",
                "description": "Average True Range",
                "function": self._atr,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "NATR": {
                "category": "volatility",
                "description": "Normalized Average True Range",
                "function": self._natr,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "TRANGE": {
                "category": "volatility",
                "description": "True Range",
                "function": self._trange,
                "default_params": {},
                "required_params": [],
                "data_requirements": ["High", "Low", "Close"]
            },
            "STDDEV": {
                "category": "volatility",
                "description": "Standard Deviation",
                "function": self._stddev,
                "default_params": {"period": 20},
                "required_params": ["period"],
                "data_requirements": ["Close"]
            },
        })
        
        # Volume Indicators
        self._registry.update({
            "AD": {
                "category": "volume",
                "description": "Accumulation/Distribution Line",
                "function": self._ad,
                "default_params": {},
                "required_params": [],
                "data_requirements": ["High", "Low", "Close", "Volume"]
            },
            "ADOSC": {
                "category": "volume",
                "description": "Chaikin Accumulation/Distribution Oscillator",
                "function": self._adosc,
                "default_params": {"fast": 3, "slow": 10},
                "required_params": ["fast", "slow"],
                "data_requirements": ["High", "Low", "Close", "Volume"]
            },
            "OBV": {
                "category": "volume",
                "description": "On Balance Volume",
                "function": self._obv,
                "default_params": {},
                "required_params": [],
                "data_requirements": ["Close", "Volume"]
            },
            "VWAP": {
                "category": "volume",
                "description": "Volume Weighted Average Price",
                "function": self._vwap,
                "default_params": {},
                "required_params": [],
                "data_requirements": ["High", "Low", "Close", "Volume"]
            },
            "EMV": {
                "category": "volume",
                "description": "Ease of Movement",
                "function": self._emv,
                "default_params": {"period": 14},
                "required_params": ["period"],
                "data_requirements": ["High", "Low", "Volume"]
            },
            "FI": {
                "category": "volume",
                "description": "Force Index",
                "function": self._fi,
                "default_params": {"period": 13},
                "required_params": ["period"],
                "data_requirements": ["Close", "Volume"]
            },
        })
        
        # Custom Indicators
        self._registry.update({
            "ENHANCED_SUPERTREND": {
                "category": "custom",
                "description": "Enhanced Supertrend with ML Signal Scoring",
                "function": self._enhanced_supertrend,
                "default_params": {
                    "atr_period": 10,
                    "st_multiplier": 3.0,
                    "rsi_period": 14,
                    "volume_period": 20,
                    "volume_threshold": 1.5
                },
                "required_params": ["atr_period", "st_multiplier"],
                "data_requirements": ["High", "Low", "Close", "Volume"]
            },
            "SUPERTREND": {
                "category": "custom",
                "description": "Traditional Supertrend",
                "function": self._supertrend,
                "default_params": {"period": 10, "multiplier": 3},
                "required_params": ["period", "multiplier"],
                "data_requirements": ["High", "Low", "Close"]
            },
            "ICHIMOKU": {
                "category": "custom",
                "description": "Ichimoku Cloud",
                "function": self._ichimoku,
                "default_params": {"conversion": 9, "base": 26, "span": 52},
                "required_params": ["conversion", "base", "span"],
                "data_requirements": ["High", "Low", "Close"]
            },
        })
    
    def get_supported_indicators(self) -> List[str]:
        """Get list of all supported indicator names."""
        return list(self._registry.keys())
    
    def get_indicator_info(self, indicator: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific indicator."""
        return self._registry.get(indicator.upper())
    
    def calculate_indicator(self, df: pd.DataFrame, indicator: str, params: Dict[str, Any]) -> Optional[pd.Series]:
        """Calculate the specified technical indicator."""
        indicator = indicator.upper()
        
        if indicator not in self._registry:
            return None
        
        indicator_config = self._registry[indicator]
        
        # Merge default parameters with provided parameters
        final_params = indicator_config["default_params"].copy()
        final_params.update(params)
        
        # Convert string parameters to appropriate types
        for key, value in final_params.items():
            if isinstance(value, str):
                try:
                    # Try to convert to int first
                    if value.isdigit():
                        final_params[key] = int(value)
                    else:
                        # Try to convert to float
                        final_params[key] = float(value)
                except ValueError:
                    # Keep as string if conversion fails
                    pass
        
        # Validate data requirements
        missing_columns = []
        for required_col in indicator_config["data_requirements"]:
            if required_col not in df.columns:
                missing_columns.append(required_col)
        
        if missing_columns:
            raise ValueError(f"Missing required columns for {indicator}: {missing_columns}")
        
        # Call the indicator function
        try:
            return indicator_config["function"](df, **final_params)
        except Exception as e:
            # Pass through the original error message for more specific error handling
            error_msg = str(e)
            if "insufficient data" in error_msg.lower():
                raise Exception(error_msg)
            else:
                raise Exception(f"Error calculating {indicator}: {error_msg}")
    
    # Trend Indicator Implementations
    def _sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Simple Moving Average."""
        return ta.sma(df['Close'], length=period)
    
    def _ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Exponential Moving Average."""
        return ta.ema(df['Close'], length=period)
    
    def _wma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Weighted Moving Average."""
        return ta.wma(df['Close'], length=period)
    
    def _dema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Double Exponential Moving Average."""
        return ta.dema(df['Close'], length=period)
    
    def _tema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Triple Exponential Moving Average."""
        return ta.tema(df['Close'], length=period)
    
    def _macd(self, df: pd.DataFrame, fast: int, slow: int, signal: int) -> pd.Series:
        """Moving Average Convergence Divergence."""
        macd_result = ta.macd(df['Close'], fast=fast, slow=slow, signal=signal)
        return macd_result[f'MACD_{fast}_{slow}_{signal}']
    
    def _adx(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Average Directional Index."""
        return ta.adx(df['High'], df['Low'], df['Close'], length=period)[f'ADX_{period}']
    
    def _apo(self, df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
        """Absolute Price Oscillator."""
        return ta.apo(df['Close'], fast=fast, slow=slow)
    
    def _aroon(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Aroon Indicator (returns both Up and Down)."""
        return ta.aroon(df['High'], df['Low'], length=period)
    
    def _aroon_osc(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Aroon Oscillator."""
        aroon_result = ta.aroon(df['High'], df['Low'], length=period)
        return aroon_result[f'AROONU_{period}'] - aroon_result[f'AROOND_{period}']
    
    def _cci(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Commodity Channel Index."""
        return ta.cci(df['High'], df['Low'], df['Close'], length=period)
    
    def _cmo(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Chande Momentum Oscillator."""
        return ta.cmo(df['Close'], length=period)
    
    def _dx(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Directional Movement Index."""
        adx_result = ta.adx(df['High'], df['Low'], df['Close'], length=period)
        return adx_result[f'DX_{period}']
    
    def _minus_di(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Minus Directional Indicator."""
        adx_result = ta.adx(df['High'], df['Low'], df['Close'], length=period)
        return adx_result[f'DMN_{period}']
    
    def _plus_di(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Plus Directional Indicator."""
        adx_result = ta.adx(df['High'], df['Low'], df['Close'], length=period)
        return adx_result[f'DMP_{period}']
    
    def _ppo(self, df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
        """Percentage Price Oscillator."""
        return ta.ppo(df['Close'], fast=fast, slow=slow)
    
    # Momentum Indicator Implementations
    def _rsi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Relative Strength Index."""
        return ta.rsi(df['Close'], length=period)
    
    def _stoch(self, df: pd.DataFrame, fastk: int, slowk: int, slowd: int) -> pd.DataFrame:
        """Stochastic Oscillator."""
        return ta.stoch(df['High'], df['Low'], df['Close'], k=fastk, d=slowk, smooth_k=slowd)
    
    def _willr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Williams %R."""
        return ta.willr(df['High'], df['Low'], df['Close'], length=period)
    
    def _mfi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Money Flow Index."""
        return ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=period)
    
    def _trix(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Triple Exponential Average."""
        return ta.trix(df['Close'], length=period)
    
    def _ultosc(self, df: pd.DataFrame, period1: int, period2: int, period3: int) -> pd.Series:
        """Ultimate Oscillator."""
        return ta.uo(df['High'], df['Low'], df['Close'], fast=period1, medium=period2, slow=period3)
    
    def _roc(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Rate of Change."""
        return ta.roc(df['Close'], length=period)
    
    def _mom(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Momentum."""
        return ta.mom(df['Close'], length=period)
    
    # Volatility Indicator Implementations
    def _bbands(self, df: pd.DataFrame, period: int, std: float) -> pd.DataFrame:
        """Bollinger Bands."""
        return ta.bbands(df['Close'], length=period, std=std)
    
    def _atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Average True Range."""
        return ta.atr(df['High'], df['Low'], df['Close'], length=period)
    
    def _natr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Normalized Average True Range."""
        return ta.natr(df['High'], df['Low'], df['Close'], length=period)
    
    def _trange(self, df: pd.DataFrame) -> pd.Series:
        """True Range."""
        return ta.true_range(df['High'], df['Low'], df['Close'])
    
    def _stddev(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Standard Deviation."""
        return ta.stdev(df['Close'], length=period)
    
    # Volume Indicator Implementations
    def _ad(self, df: pd.DataFrame) -> pd.Series:
        """Accumulation/Distribution Line."""
        return ta.ad(df['High'], df['Low'], df['Close'], df['Volume'])
    
    def _adosc(self, df: pd.DataFrame, fast: int, slow: int) -> pd.Series:
        """Chaikin Accumulation/Distribution Oscillator."""
        return ta.adosc(df['High'], df['Low'], df['Close'], df['Volume'], fast=fast, slow=slow)
    
    def _obv(self, df: pd.DataFrame) -> pd.Series:
        """On Balance Volume."""
        return ta.obv(df['Close'], df['Volume'])
    
    def _vwap(self, df: pd.DataFrame) -> pd.Series:
        """Volume Weighted Average Price."""
        return ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    def _emv(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Ease of Movement."""
        return ta.eom(df['High'], df['Low'], df['Close'], df['Volume'], length=period)
    
    def _fi(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Force Index."""
        return ta.efi(df['Close'], df['Volume'], length=period)
    
    # Custom Indicator Implementations
    def _enhanced_supertrend(self, df: pd.DataFrame, **params) -> pd.DataFrame:
        """Enhanced Supertrend with ML Signal Scoring."""
        indicator = EnhancedSupertrendIndicator()
        return indicator.calculate(df, params)
    
    def _supertrend(self, df: pd.DataFrame, period: int, multiplier: float) -> pd.DataFrame:
        """Traditional Supertrend."""
        return ta.supertrend(df['High'], df['Low'], df['Close'], length=period, multiplier=multiplier)
    
    def _ichimoku(self, df: pd.DataFrame, conversion: int, base: int, span: int) -> pd.DataFrame:
        """Ichimoku Cloud."""
        return ta.ichimoku(df['High'], df['Low'], df['Close'], 
                          tenkan=conversion, kijun=base, senkou=span)