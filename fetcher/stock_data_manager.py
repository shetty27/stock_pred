import os
import pandas as pd
from datetime import datetime, timedelta
from firebase_handler import get_access_token
import requests
import pandas_ta as ta

DATA_DIR = "historical_data"

# Make sure historical_data folder exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def fetch_full_historical_data(instrument_key):
    access_token = get_access_token()
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/day/{to_date}/{from_date}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    candles = response.json().get("data", {}).get("candles", [])
    if not candles:
        return pd.DataFrame()
    if len(candles[0]) == 7:
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "is_complete"])
    elif len(candles[0]) == 6:
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["is_complete"] = 1
    else:
        raise ValueError(f"Unexpected candle format with {len(candles[0])} elements")

    df["rsi"] = ta.rsi(df["close"], length=14)
    macd = ta.macd(df["close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"] = macd["MACDh_12_26_9"]
    df.dropna(inplace=True)
    return df

def fetch_last_day_candle(instrument_key):
    access_token = get_access_token()
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"https://api.upstox.com/v2/historical-candle/{instrument_key}/day/{to_date}/{from_date}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    candles = response.json().get("data", {}).get("candles", [])
    if not candles:
        return pd.DataFrame()
    if len(candles[0]) == 7:
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "is_complete"])
    elif len(candles[0]) == 6:
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["is_complete"] = 1
    else:
        raise ValueError(f"Unexpected candle format with {len(candles[0])} elements")

    df["rsi"] = ta.rsi(df["close"], length=14)
    macd = ta.macd(df["close"])
    df["macd"] = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"] = macd["MACDh_12_26_9"]
    df.dropna(inplace=True)
    return df

def get_stock_data(symbol, instrument_key):
    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Daily update
        new_candle = fetch_last_day_candle(instrument_key)
        if not new_candle.empty:
            df = pd.concat([df, new_candle], ignore_index=True)
            df.to_csv(file_path, index=False)
    else:
        df = fetch_full_historical_data(instrument_key)
        if not df.empty:
            df.to_csv(file_path, index=False)
    return df
