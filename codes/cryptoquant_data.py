# For fetching data source and cleaning data

import cybotrade
import asyncio
import pandas as pd
import numpy as np
import os
import json
import matplotlib.pyplot as plt
from hmmlearn.hmm import GaussianHMM
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from cybotrade.strategy import Strategy
from cybotrade.models import OrderSide, Exchange, RuntimeConfig, RuntimeMode
from datetime import datetime, timezone
from cybotrade.permutation import Permutation
import cybotrade_datasource
import nest_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY =  "" # Insert your API Key
os.environ["API_KEY"] = API_KEY

# Verify the API key
print(f"API Key set: {API_KEY[:8]}...")

# Define data sources configuration
data_sources = {
    'exchange_netflow': {
        'topic': 'cryptoquant|btc/exchange-flows/netflow',
        'params': {
            'window': 'hour',
            'exchange': 'all_exchange'
        }
    },
    'miner_to_exchange': {
        'topic': 'cryptoquant|btc/inter-entity-flows/miner-to-exchange',
        'params': {
            'window': 'hour',
            'from_miner': 'all_miner',
            'to_exchange': 'all_exchange'
        }
    },
    'exchange_reserve': {
        'topic': 'cryptoquant|btc/exchange-flows/reserve',
        'params': {
            'window': 'hour',
            'exchange': 'all_exchange'
        }
    },
    'price_ohlcv': {
        'topic': 'cryptoquant|btc/market-data/price-ohlcv',
        'params': {
            'window': 'hour',
            'market': 'spot',
            'exchange': 'all_exchange',
            'symbol': 'btc_usd'
        }
    }
}

async def fetch_data(api_key, topic, params, start_time, end_time):
    """Helper function to fetch data from CyboTrade"""
    full_topic = f"{topic}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
    try:
        data = await cybotrade_datasource.query_paginated(
            api_key=api_key,
            topic=full_topic,
            start_time=start_time,
            end_time=end_time
        )
        return pd.DataFrame(data) if isinstance(data, list) else None
    except Exception as e:
        print(f"Error fetching {topic}: {str(e)}")
        return None

async def main():
    try:
        if not API_KEY:
            raise ValueError("API key is not set")

        start_time = datetime(year=2023, month=1, day=1, tzinfo=timezone.utc)
        end_time = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc)
      
        # Dictionary to store all fetched dataframes
        dfs = {}

        # Fetch all data sources
        for source_name, config in data_sources.items():
            print(f"Fetching {source_name}...")
            # Skip mvrv since it doesn't support hourly data
            if source_name == 'mvrv':
                continue

            df = await fetch_data(
                API_KEY,
                config['topic'],
                config['params'],
                start_time,
                end_time
            )
            if df is not None:
                dfs[source_name] = df
                print(f"Successfully fetched {source_name} data: {len(df)} rows")
                display(df.head())
            print("-" * 100)

        return dfs

    except Exception as e:
        print(f"Error details: {str(e)}")
        return None

# Run the async function and store the result
nest_asyncio.apply()
dfs = await main()

for key, df in dfs.items():
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], utc=True)
        df.set_index('time', inplace=True)
    elif 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df.set_index('timestamp', inplace=True)
    dfs[key] = df.sort_index()

# Check for data validity (null)
df = dfs['price_ohlcv']
print(df.isnull().sum())
df = dfs['exchange_netflow']
print(df.isnull().sum())
df = dfs['exchange_reserve']
print(df.isnull().sum())
df = dfs['miner_to_exchange']
print(df.isnull().sum())

price_ohlcv = dfs['price_ohlcv']
exchange_netflow = dfs['exchange_netflow']
exchange_reserve = dfs['exchange_reserve']
miner_to_exchange = dfs['miner_to_exchange']

# Merging data in one table
# Remove flow_mean, transactions_count_flow, and reserve features
merged_df = price_ohlcv.merge(
    exchange_netflow[['datetime', 'netflow_total']],
    on='datetime',
    how='left'
)
merged_df = merged_df.merge(
    exchange_reserve[['datetime', 'reserve_usd']],
    on='datetime',
    how='left'
)
merged_df = merged_df.merge(
    miner_to_exchange[['datetime', 'flow_total']],
    on='datetime',
    how='left'
)

# Add new features into merged_df
# Add returns feature (percentange change)
df = dfs['price_ohlcv']
returns = dfs['price_ohlcv']['close'].pct_change()
merged_df['returns'] = returns

# Add 20-day rolling volatility
merged_df['volatility_20d'] = merged_df['returns'].rolling(20).std() * np.sqrt(252)
dfs['merged_df'] = merged_df

# Add Volume Weighted average price; vwap
merged_df['vwap'] = (merged_df['volume'] * merged_df['close']).cumsum() / merged_df['volume'].cumsum()
dfs['merged_df'] = merged_d

# Add miner sell pressure ratio
merged_df['miner_sell_ratio'] = (merged_df['flow_total'] / merged_df['volume'])
dfs['merged_df'] = merged_df

# Drop rows with missing value (NaN)
df = merged_df
df.dropna(inplace=True)
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Print final dataframe
print(merged_df.head())
