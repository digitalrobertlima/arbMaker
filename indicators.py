import pandas as pd

def calculate_rsi(data, period=14):
    df = pd.DataFrame(data)
    df['price'] = pd.to_numeric(df['price'])
    df['delta'] = df['price'].diff()
    df['gain'] = df['delta'].where(df['delta'] > 0, 0)
    df['loss'] = -df['delta'].where(df['delta'] < 0, 0)
    avg_gain = df['gain'].rolling(window=period, min_periods=1).mean()
    avg_loss = df['loss'].rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_williams(data, period=14):
    df = pd.DataFrame(data)
    df['price'] = pd.to_numeric(df['price'])
    df['high'] = df['price'].rolling(window=period, min_periods=1).max()
    df['low'] = df['price'].rolling(window=period, min_periods=1).min()
    df['williams'] = ((df['high'] - df['price']) / (df['high'] - df['low'])) * -100
    return df['williams'].iloc[-1]

def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    df = pd.DataFrame(data)
    df['price'] = pd.to_numeric(df['price'])
    df['short_ema'] = df['price'].ewm(span=short_period, adjust=False).mean()
    df['long_ema'] = df['price'].ewm(span=long_period, adjust=False).mean()
    df['macd'] = df['short_ema'] - df['long_ema']
    df['signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
    df['histogram'] = df['macd'] - df['signal']
    return df['macd'].iloc[-1], df['signal'].iloc[-1], df['histogram'].iloc[-1]
