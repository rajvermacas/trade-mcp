# Product Requirements Document: Trading MCP for Indian Stock Market

## Executive Summary

This document outlines the requirements for developing a Model Context Protocol (MCP) server specifically designed for trading operations in the Indian stock market. The MCP will enable Large Language Models (LLMs) to access real-time stock data, technical indicators, and market news through a standardized interface, facilitating intelligent conversations about market analysis, pattern recognition, and trading decisions.

## Problem Statement

LLMs currently lack direct access to real-time Indian stock market data, limiting their ability to provide informed trading insights and analysis. There is a need for a structured interface that can:
- Provide accurate, real-time stock market data for Indian securities
- Calculate technical indicators on demand
- Deliver relevant market news
- Present data in a format optimized for LLM consumption

## Objectives and Success Metrics

### Primary Objectives
1. Create an MCP server that provides real-time Indian stock market data
2. Support multiple time intervals for chart data (intraday to monthly)
3. Enable technical indicator calculations with customizable parameters
4. Integrate market news from multiple sources
5. Implement efficient caching to optimize performance

### Success Metrics
- Response time < 2 seconds for stock data queries
- 99% uptime for the MCP server
- Support for 100+ NSE-listed stocks
- Accurate data matching Yahoo Finance sources
- Successful integration with Claude Desktop and other MCP clients

## User Stories and Use Cases

### User Stories
1. **As an LLM user**, I want to get real-time stock prices and historical data for Indian stocks so that I can analyze market trends
2. **As an LLM user**, I want to calculate technical indicators with custom parameters so that I can perform technical analysis
3. **As an LLM user**, I want to access relevant market news so that I can understand market sentiment and events
4. **As a developer**, I want clear error messages so that I can debug issues quickly

### Use Cases
1. **Market Analysis**: User asks LLM to analyze RELIANCE stock performance over the last month
2. **Technical Analysis**: User requests RSI and MACD indicators for TCS stock
3. **News Context**: User asks about recent news affecting INFY stock price
4. **Pattern Recognition**: LLM identifies chart patterns using coordinate data

## Functional Requirements

### Core Functions

#### 1. get_stock_chart_data
**Purpose**: Retrieve OHLC (Open, High, Low, Close) data with volume for specified stocks

**Input Parameters**:
- `symbol` (string, required): NSE stock symbol (supports both "RELIANCE" and "RELIANCE.NS" formats)
- `start_date` (string, required): Start date in ISO format (YYYY-MM-DD)
- `end_date` (string, required): End date in ISO format (YYYY-MM-DD)
- `interval` (string, optional): Time interval - "1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo" (default: "1h")

**Output Format**:
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01T10:00:00+05:30",
      "open": 2450.50,
      "high": 2465.75,
      "low": 2445.00,
      "close": 2460.25,
      "volume": 1250000
    }
  ],
  "metadata": {
    "symbol": "RELIANCE.NS",
    "interval": "1h",
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "data_points": 100
  }
}
```

#### 2. calculate_technical_indicator
**Purpose**: Calculate technical indicators for specified stocks

**Input Parameters**:
- `symbol` (string, required): NSE stock symbol
- `indicator` (string, required): Indicator name (see Appendix A for full list)
- `start_date` (string, required): Start date in ISO format
- `end_date` (string, required): End date in ISO format
- `interval` (string, optional): Time interval (default: "1d")
- `params` (object, optional): Indicator-specific parameters (see Appendix A for each indicator's parameters)

**Output Format**:
```json
{
  "success": true,
  "data": {
    "indicator": "RSI",
    "values": [
      {
        "timestamp": "2024-01-01T00:00:00+05:30",
        "value": 65.5
      }
    ],
    "parameters": {
      "period": 14
    }
  },
  "metadata": {
    "symbol": "RELIANCE.NS",
    "interval": "1d",
    "data_points": 50
  }
}
```

#### 3. get_market_news
**Purpose**: Retrieve relevant market news

**Input Parameters**:
- `query_type` (string, required): "company", "market", or "sector"
- `query` (string, optional): Company symbol, sector name, or search keywords
- `start_date` (string, optional): Filter news from this date
- `limit` (number, optional): Maximum number of articles (default: 10)

**Output Format**:
```json
{
  "success": true,
  "articles": [
    {
      "title": "Reliance Industries Q3 Results Beat Estimates",
      "summary": "Reliance Industries reported better-than-expected Q3 results...",
      "source": "Economic Times",
      "published_date": "2024-01-15T14:30:00+05:30",
      "url": "https://example.com/article",
      "sentiment": "positive",
      "relevance_score": 0.95,
      "category": "company",
      "tags": ["earnings", "oil-gas", "reliance"]
    }
  ],
  "metadata": {
    "total_results": 25,
    "query_type": "company",
    "time_range": "last_7_days"
  }
}
```

### Error Handling
All functions should return structured errors:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "The symbol 'INVALID' is not a valid NSE stock symbol",
    "details": {
      "provided_symbol": "INVALID",
      "suggestion": "Did you mean 'INFY'?"
    }
  }
}
```

Error codes:
- `INVALID_SYMBOL`: Invalid stock symbol
- `INVALID_DATE_RANGE`: Invalid date range provided
- `DATA_UNAVAILABLE`: Data not available for the requested period
- `MARKET_CLOSED`: Request made during market holidays
- `API_ERROR`: External API failure
- `RATE_LIMIT`: API rate limit exceeded
- `INVALID_INDICATOR`: Unknown technical indicator
- `INVALID_PARAMETERS`: Invalid indicator parameters

## Non-Functional Requirements

### Performance Requirements
- Response time: < 2 seconds for all queries
- Concurrent request handling: Support 50+ simultaneous requests
- Cache hit ratio: > 80% for frequently accessed data

### Security Requirements
- Secure API key management for Yahoo Finance
- Input validation for all parameters
- Rate limiting to prevent abuse
- No storage of sensitive user data

### Reliability Requirements
- 99% uptime during market hours
- Graceful degradation when external APIs fail
- Automatic retry with exponential backoff
- Comprehensive error logging

### Scalability Requirements
- Modular architecture to add new indicators easily
- Support for additional exchanges (BSE) in future
- Extensible news source integration

## Technical Constraints

### Technology Stack
- **Language**: Python 3.9+
- **MCP Framework**: Official MCP Python SDK
- **Data Source**: Yahoo Finance API (yfinance)
- **Technical Indicators**: TA-Lib or pandas-ta
- **Caching**: In-memory cache with TTL
- **Logging**: Python logging module with structured logs

### API Limitations
- Yahoo Finance rate limits
- Market data availability during trading hours only
- Historical data limitations for free tier

### Development Constraints
- Maximum 800 lines per file
- Test-driven development approach
- Comprehensive logging for all operations
- Follow project structure guidelines

## Dependencies

### External Dependencies
- Yahoo Finance API for stock data
- News aggregation APIs (to be determined)
- Python libraries: yfinance, pandas, numpy, ta-lib/pandas-ta

### Internal Dependencies
- MCP SDK for server implementation
- Caching layer
- Logging infrastructure

## Timeline and Milestones

### Phase 1: Foundation (Week 1)
- Project setup with pyproject.toml
- Basic MCP server implementation
- Stock data fetching functionality

### Phase 2: Core Features (Week 2)
- Technical indicator calculations
- Caching implementation
- Comprehensive error handling

### Phase 3: Advanced Features (Week 3)
- News integration
- Performance optimization
- Testing and documentation

### Phase 4: Polish (Week 4)
- Integration testing with Claude Desktop
- Performance tuning
- Final documentation

## Risk Assessment

### Technical Risks
1. **API Rate Limiting**: Mitigation - Implement intelligent caching
2. **Data Accuracy**: Mitigation - Data validation and multiple source verification
3. **Performance Issues**: Mitigation - Optimize data structures and queries

### Business Risks
1. **API Cost Overruns**: Mitigation - Monitor usage and implement quotas
2. **Regulatory Compliance**: Mitigation - Ensure data usage complies with exchange rules
3. **Market Data Licensing**: Mitigation - Use only freely available data sources

### Mitigation Strategies
- Implement comprehensive monitoring
- Create fallback data sources
- Regular testing during market hours
- Clear documentation for troubleshooting

## Appendices

### A. Supported Technical Indicators

#### Trend Indicators
- **SMA** (Simple Moving Average) - `{"period": 20}`
- **EMA** (Exponential Moving Average) - `{"period": 20}`
- **WMA** (Weighted Moving Average) - `{"period": 20}`
- **DEMA** (Double Exponential Moving Average) - `{"period": 20}`
- **TEMA** (Triple Exponential Moving Average) - `{"period": 20}`
- **TRIMA** (Triangular Moving Average) - `{"period": 20}`
- **KAMA** (Kaufman Adaptive Moving Average) - `{"period": 20}`
- **MAMA** (MESA Adaptive Moving Average) - `{"fastlimit": 0.5, "slowlimit": 0.05}`
- **T3** (Triple Exponential Moving Average T3) - `{"period": 20, "vfactor": 0.7}`
- **MACD** (Moving Average Convergence Divergence) - `{"fast": 12, "slow": 26, "signal": 9}`
- **MACDEXT** (MACD Extended) - `{"fast": 12, "slow": 26, "signal": 9, "matype": 0}`
- **ADX** (Average Directional Index) - `{"period": 14}`
- **ADXR** (Average Directional Index Rating) - `{"period": 14}`
- **APO** (Absolute Price Oscillator) - `{"fast": 12, "slow": 26, "matype": 0}`
- **AROON** (Aroon Indicator) - `{"period": 14}`
- **AROONOSC** (Aroon Oscillator) - `{"period": 14}`
- **BOP** (Balance of Power) - No parameters
- **CCI** (Commodity Channel Index) - `{"period": 20}`
- **CMO** (Chande Momentum Oscillator) - `{"period": 14}`
- **DX** (Directional Movement Index) - `{"period": 14}`
- **MINUS_DI** (Minus Directional Indicator) - `{"period": 14}`
- **PLUS_DI** (Plus Directional Indicator) - `{"period": 14}`
- **MINUS_DM** (Minus Directional Movement) - `{"period": 14}`
- **PLUS_DM** (Plus Directional Movement) - `{"period": 14}`
- **PPO** (Percentage Price Oscillator) - `{"fast": 12, "slow": 26, "matype": 0}`

#### Momentum Indicators
- **RSI** (Relative Strength Index) - `{"period": 14}`
- **STOCH** (Stochastic) - `{"fastk": 14, "slowk": 3, "slowd": 3}`
- **STOCHF** (Stochastic Fast) - `{"fastk": 14, "fastd": 3}`
- **STOCHRSI** (Stochastic RSI) - `{"period": 14, "fastk": 14, "fastd": 3}`
- **WILLR** (Williams %R) - `{"period": 14}`
- **MFI** (Money Flow Index) - `{"period": 14}`
- **TRIX** (Triple Exponential Average) - `{"period": 30}`
- **ULTOSC** (Ultimate Oscillator) - `{"period1": 7, "period2": 14, "period3": 28}`
- **ROC** (Rate of Change) - `{"period": 10}`
- **ROCP** (Rate of Change Percentage) - `{"period": 10}`
- **ROCR** (Rate of Change Ratio) - `{"period": 10}`
- **ROCR100** (Rate of Change Ratio 100) - `{"period": 10}`
- **MOM** (Momentum) - `{"period": 10}`

#### Volatility Indicators
- **BBANDS** (Bollinger Bands) - `{"period": 20, "nbdevup": 2, "nbdevdn": 2, "matype": 0}`
- **ATR** (Average True Range) - `{"period": 14}`
- **NATR** (Normalized Average True Range) - `{"period": 14}`
- **TRANGE** (True Range) - No parameters
- **STDDEV** (Standard Deviation) - `{"period": 20, "nbdev": 1}`
- **VAR** (Variance) - `{"period": 20, "nbdev": 1}`

#### Volume Indicators
- **AD** (Accumulation/Distribution Line) - No parameters
- **ADOSC** (Chaikin Accumulation/Distribution Oscillator) - `{"fast": 3, "slow": 10}`
- **OBV** (On Balance Volume) - No parameters
- **VWAP** (Volume Weighted Average Price) - `{"period": 14}`
- **PVT** (Price Volume Trend) - No parameters
- **NVI** (Negative Volume Index) - No parameters
- **PVI** (Positive Volume Index) - No parameters
- **EMV** (Ease of Movement) - `{"period": 14}`
- **FI** (Force Index) - `{"period": 13}`
- **VPT** (Volume Price Trend) - No parameters
- **VWMA** (Volume Weighted Moving Average) - `{"period": 20}`

#### Overlap Studies
- **SAR** (Parabolic SAR) - `{"acceleration": 0.02, "maximum": 0.2}`
- **SAREXT** (Parabolic SAR Extended) - `{"startvalue": 0, "offsetonreverse": 0, "accelerationinitlong": 0.02, "accelerationlong": 0.02, "accelerationmaxlong": 0.2, "accelerationinitshort": 0.02, "accelerationshort": 0.02, "accelerationmaxshort": 0.2}`
- **HT_TRENDLINE** (Hilbert Transform - Instantaneous Trendline) - No parameters
- **MIDPOINT** (Midpoint over period) - `{"period": 14}`
- **MIDPRICE** (Midpoint Price over period) - `{"period": 14}`

#### Pattern Recognition
- **CDL2CROWS** (Two Crows) - No parameters
- **CDL3BLACKCROWS** (Three Black Crows) - No parameters
- **CDL3INSIDE** (Three Inside Up/Down) - No parameters
- **CDL3LINESTRIKE** (Three-Line Strike) - No parameters
- **CDL3OUTSIDE** (Three Outside Up/Down) - No parameters
- **CDL3STARSINSOUTH** (Three Stars In The South) - No parameters
- **CDL3WHITESOLDIERS** (Three Advancing White Soldiers) - No parameters
- **CDLABANDONEDBABY** (Abandoned Baby) - `{"penetration": 0.3}`
- **CDLADVANCEBLOCK** (Advance Block) - No parameters
- **CDLBELTHOLD** (Belt-hold) - No parameters
- **CDLBREAKAWAY** (Breakaway) - No parameters
- **CDLCLOSINGMARUBOZU** (Closing Marubozu) - No parameters
- **CDLCONCEALBABYSWALL** (Concealing Baby Swallow) - No parameters
- **CDLCOUNTERATTACK** (Counterattack) - No parameters
- **CDLDARKCLOUDCOVER** (Dark Cloud Cover) - `{"penetration": 0.5}`
- **CDLDOJI** (Doji) - No parameters
- **CDLDOJISTAR** (Doji Star) - No parameters
- **CDLDRAGONFLYDOJI** (Dragonfly Doji) - No parameters
- **CDLENGULFING** (Engulfing Pattern) - No parameters
- **CDLEVENINGDOJISTAR** (Evening Doji Star) - `{"penetration": 0.3}`
- **CDLEVENINGSTAR** (Evening Star) - `{"penetration": 0.3}`
- **CDLGAPSIDESIDEWHITE** (Up/Down-gap side-by-side white lines) - No parameters
- **CDLGRAVESTONEDOJI** (Gravestone Doji) - No parameters
- **CDLHAMMER** (Hammer) - No parameters
- **CDLHANGINGMAN** (Hanging Man) - No parameters
- **CDLHARAMI** (Harami Pattern) - No parameters
- **CDLHARAMICROSS** (Harami Cross Pattern) - No parameters
- **CDLHIGHWAVE** (High-Wave Candle) - No parameters
- **CDLHIKKAKE** (Hikkake Pattern) - No parameters
- **CDLHIKKAKEMOD** (Modified Hikkake Pattern) - No parameters
- **CDLHOMINGPIGEON** (Homing Pigeon) - No parameters
- **CDLIDENTICAL3CROWS** (Identical Three Crows) - No parameters
- **CDLINNECK** (In-Neck Pattern) - No parameters
- **CDLINVERTEDHAMMER** (Inverted Hammer) - No parameters
- **CDLKICKING** (Kicking) - No parameters
- **CDLKICKINGBYLENGTH** (Kicking by length) - No parameters
- **CDLLADDERBOTTOM** (Ladder Bottom) - No parameters
- **CDLLONGLEGGEDDOJI** (Long Legged Doji) - No parameters
- **CDLLONGLINE** (Long Line Candle) - No parameters
- **CDLMARUBOZU** (Marubozu) - No parameters
- **CDLMATCHINGLOW** (Matching Low) - No parameters
- **CDLMATHOLD** (Mat Hold) - `{"penetration": 0.5}`
- **CDLMORNINGDOJISTAR** (Morning Doji Star) - `{"penetration": 0.3}`
- **CDLMORNINGSTAR** (Morning Star) - `{"penetration": 0.3}`
- **CDLONNECK** (On-Neck Pattern) - No parameters
- **CDLPIERCING** (Piercing Pattern) - No parameters
- **CDLRICKSHAWMAN** (Rickshaw Man) - No parameters
- **CDLRISEFALL3METHODS** (Rising/Falling Three Methods) - No parameters
- **CDLSEPARATINGLINES** (Separating Lines) - No parameters
- **CDLSHOOTINGSTAR** (Shooting Star) - No parameters
- **CDLSHORTLINE** (Short Line Candle) - No parameters
- **CDLSPINNINGTOP** (Spinning Top) - No parameters
- **CDLSTALLEDPATTERN** (Stalled Pattern) - No parameters
- **CDLSTICKSANDWICH** (Stick Sandwich) - No parameters
- **CDLTAKURI** (Takuri) - No parameters
- **CDLTASUKIGAP** (Tasuki Gap) - No parameters
- **CDLTHRUSTING** (Thrusting Pattern) - No parameters
- **CDLTRISTAR** (Tristar Pattern) - No parameters
- **CDLUNIQUE3RIVER** (Unique 3 River) - No parameters
- **CDLUPSIDEGAP2CROWS** (Upside Gap Two Crows) - No parameters
- **CDLXSIDEGAP3METHODS** (Upside/Downside Gap Three Methods) - No parameters

#### Cycle Indicators
- **HT_DCPERIOD** (Hilbert Transform - Dominant Cycle Period) - No parameters
- **HT_DCPHASE** (Hilbert Transform - Dominant Cycle Phase) - No parameters
- **HT_PHASOR** (Hilbert Transform - Phasor Components) - No parameters
- **HT_SINE** (Hilbert Transform - SineWave) - No parameters
- **HT_TRENDMODE** (Hilbert Transform - Trend vs Cycle Mode) - No parameters

#### Price Transform
- **AVGPRICE** (Average Price) - No parameters
- **MEDPRICE** (Median Price) - No parameters
- **TYPPRICE** (Typical Price) - No parameters
- **WCLPRICE** (Weighted Close Price) - No parameters

#### Statistical Functions
- **BETA** (Beta) - `{"period": 20}`
- **CORREL** (Pearson's Correlation Coefficient) - `{"period": 30}`
- **LINEARREG** (Linear Regression) - `{"period": 14}`
- **LINEARREG_ANGLE** (Linear Regression Angle) - `{"period": 14}`
- **LINEARREG_INTERCEPT** (Linear Regression Intercept) - `{"period": 14}`
- **LINEARREG_SLOPE** (Linear Regression Slope) - `{"period": 14}`
- **TSF** (Time Series Forecast) - `{"period": 14}`

#### Math Functions
- **MAX** (Maximum value over period) - `{"period": 30}`
- **MAXINDEX** (Index of maximum value) - `{"period": 30}`
- **MIN** (Minimum value over period) - `{"period": 30}`
- **MININDEX** (Index of minimum value) - `{"period": 30}`
- **SUM** (Summation) - `{"period": 30}`

#### Additional Custom Indicators
- **ICHIMOKU** (Ichimoku Cloud) - `{"conversion": 9, "base": 26, "span": 52, "offset": 26}`
- **SUPERTREND** (SuperTrend) - `{"period": 10, "multiplier": 3}`
- **DONCHIAN** (Donchian Channels) - `{"period": 20}`
- **KC** (Keltner Channels) - `{"period": 20, "multiplier": 2}`
- **ZIGZAG** (ZigZag) - `{"percentage": 5}`
- **PSAR** (Parabolic Stop and Reverse) - `{"af": 0.02, "max_af": 0.2}`
- **VORTEX** (Vortex Indicator) - `{"period": 14}`
- **TSI** (True Strength Index) - `{"fast": 13, "slow": 25}`
- **KST** (Know Sure Thing) - `{"r1": 10, "r2": 15, "r3": 20, "r4": 30, "n1": 10, "n2": 10, "n3": 10, "n4": 15}`
- **DPO** (Detrended Price Oscillator) - `{"period": 20}`
- **CG** (Center of Gravity) - `{"period": 10}`
- **FISHER** (Fisher Transform) - `{"period": 10}`
- **SLOPE** (Slope) - `{"period": 14}`
- **RVI** (Relative Vigor Index) - `{"period": 14}`
- **INERTIA** (Inertia Indicator) - `{"period": 14}`
- **SENTINEL** (Sentiment Indicator) - `{"period": 14}`
- **WOBV** (Weighted On Balance Volume) - No parameters
- **PROJECTION_OSCILLATOR** - `{"period": 14}`
- **PROJECTION_BANDS** - `{"period": 14}`

### B. Cache Strategy
- Intraday data: 1-5 minute TTL
- Daily data: 1 hour TTL
- Historical data: 24 hour TTL
- News data: 30 minute TTL

### C. Example MCP Configuration
```json
{
  "name": "trading-mcp",
  "version": "1.0.0",
  "description": "MCP server for Indian stock market trading data",
  "functions": [
    "get_stock_chart_data",
    "calculate_technical_indicator",
    "get_market_news"
  ]
}
```

---

**Document Version**: 1.0  
**Date**: 2025-01-06  
**Author**: Trading MCP Development Team  
**Status**: Pending Approval