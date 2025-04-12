
# Conceptual Diagram for Bitcoin Trading Strategy
![Conceptual Diagram](https://github.com/faryzafarizal/UMHackathon-Wonder-Girls/blob/00d5db2ba8f46e918a92309858a4050be966fc03/prototype/updated_diagram.png)

### Data Acquisition:
- Fetches data from CryptoQuant via CyboTrade API.
- Sources include exchange netflow, miner-to-exchange flows, exchange reserves, and price OHLCV data.

### Data Preprocessing:
- Cleans and handles missing values.
- Converts timestamps into a usable format.  

### Feature Engineering:
- Calculates returns from price data.
- Computes 20-day rolling volatility.
- Calculates VWAP (Volume-Weighted Average Price).
- Calculates Miner Sell Ratio.  

### Refer to [Preprocessing Data and Feature Engineering](https://github.com/faryzafarizal/UMHackathon-Wonder-Girls/tree/336d81f9a94ac7a6784e87e5e0c190d274ccae35/codes)

### Model Training:
- Uses a Gaussian Hidden Markov Model (HMM).
- Trains the model on the engineered features: returns, volatility, VWAP, and Miner Sell Ratio.

### Trading Signals:
- Predicts hidden states using the trained HMM.
- Maps hidden states to trading signals (Buy, Sell, Hold).

### Backtesting:
- Simulates trading based on the generated signals.
- Incorporates a trading fee of 0.06% per trade.
- Tracks portfolio value over time.

### Performance Metrics:
- Calculates Sharpe Ratio and Maximum Drawdown to assess strategy performance.

### Visualization:
- Plots the portfolio value over time for visual analysis.
