# Concept diagram for Alpha Strategies using HMM




### Data Sources: CryptoQuant
*   exchange_netflow
*   miner_to_exchange
*   exchange_reserve
*   price_ohlcv

### Data Fetching & Prep:
1.  Fetches data from CyboTrade API for each data source.
2.  Combines data from all sources using datetime as the key.
3.  Calculates returns, volatility, VWAP and a miner_sell_ratio
4.  Cleans data (remove NaNs and infinite values).

### Model Training & Signals:
1.  Uses Gaussian Hidden Markov Model (HMM) with the prepared data
2.  Predicts hidden states (market regimes).
3.  Assigns trading signals (Buy, Sell, Hold) based on these hidden states.

### Backtesting & Eval:
1.  Simulates trades based on generated signals.
2.  Evaluates the strategy's performance (Final Portfolio Value).
