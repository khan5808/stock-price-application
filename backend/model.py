import yfinance as yf
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
from datetime import datetime

class StockPriceModel:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, features, target):
        self.model.fit(features, target)

    def predict(self, features):
        return self.model.predict(features)

PERIOD_CONFIG = {
    '24h': {'count': 24, 'interval': '1h', 'period': '1d'},
    '7d': {'count': 7, 'interval': '1d', 'period': '8d'},
    '1m': {'count': 30, 'interval': '1d', 'period': '1mo'},
}

class InvalidPeriodError(ValueError):
    pass


def get_stock_name(stock_symbol):
    try:
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        return info.get('shortName') or info.get('longName') or stock_symbol.upper()
    except Exception:
        return stock_symbol.upper()


def _format_labels(index, period):
    labels = []
    for timestamp in index:
        if period == '24h':
            labels.append(timestamp.strftime('%I %p').lstrip('0'))
        elif period == '7d':
            labels.append(timestamp.strftime('%a'))
        else:
            labels.append(timestamp.strftime('%b %d'))
    return labels


def _normalize_history(df, count, period):
    if df is None or df.empty:
        return [], []

    df = df.copy()
    df.index = df.index.tz_localize(None) if df.index.tzinfo else df.index
    
    # Drop rows with NaN close prices
    df = df.dropna(subset=['Close'])
    
    # If all data was NaN, return empty
    if df.empty:
        return [], []

    if period == '24h':
        # For 24h chart, create continuous hourly data for the past 24 hours
        now = datetime.now()
        hourly_labels = []
        hourly_prices = []

        # Generate labels for the past 24 hours (most recent first)
        for i in range(24):
            hour_time = now - pd.to_timedelta(i, unit='h')
            hourly_labels.append(hour_time.strftime('%I %p').lstrip('0'))
            # Find the closest price data for this hour
            closest_price = None
            min_diff = float('inf')

            for idx, row in df.iterrows():
                time_diff = abs((idx - hour_time).total_seconds() / 3600)  # difference in hours
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_price = row['Close']

            if closest_price is not None and not pd.isna(closest_price) and min_diff <= 2:  # within 2 hours
                hourly_prices.append(round(float(closest_price), 2))
            else:
                # Use last known price or previous price for gaps
                if hourly_prices:
                    hourly_prices.append(hourly_prices[-1])
                else:
                    # If no data available, use the first available price
                    if not df.empty and not pd.isna(df['Close'].iloc[0]):
                        hourly_prices.append(round(float(df['Close'].iloc[0]), 2))

        # Reverse to show chronological order (oldest to newest)
        return hourly_labels[::-1], hourly_prices[::-1]

    if period == '1m':
        # For 1m chart, create continuous daily data for the past 30 days
        now = datetime.now()
        daily_labels = []
        daily_prices = []

        # Generate labels for the past 30 days (most recent first)
        for i in range(30):
            day_time = now - pd.to_timedelta(i, unit='d')
            daily_labels.append(day_time.strftime('%b %d'))
            # Find the closest price data for this day
            closest_price = None
            min_diff = float('inf')

            for idx, row in df.iterrows():
                time_diff = abs((idx - day_time).total_seconds() / 86400)  # difference in days
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_price = row['Close']

            if closest_price is not None and not pd.isna(closest_price) and min_diff <= 3:  # within 3 days (handles weekends)
                daily_prices.append(round(float(closest_price), 2))
            else:
                # Use last known price for weekends/holidays
                if daily_prices:
                    daily_prices.append(daily_prices[-1])
                else:
                    # If no data available, use the first available price
                    if not df.empty and not pd.isna(df['Close'].iloc[0]):
                        daily_prices.append(round(float(df['Close'].iloc[0]), 2))

        # Reverse to show chronological order (oldest to newest)
        return daily_labels[::-1], daily_prices[::-1]

    if period == '7d':
        # For 7d chart, create continuous daily data for the past 7 days
        now = datetime.now()
        daily_labels = []
        daily_prices = []

        # Generate labels for the past 7 days (most recent first)
        for i in range(7):
            day_time = now - pd.to_timedelta(i, unit='d')
            daily_labels.append(day_time.strftime('%a'))
            # Find the closest price data for this day
            closest_price = None
            min_diff = float('inf')

            for idx, row in df.iterrows():
                time_diff = abs((idx - day_time).total_seconds() / 86400)  # difference in days
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_price = row['Close']

            if closest_price is not None and not pd.isna(closest_price) and min_diff <= 1:  # within 1 day (for 7d chart)
                daily_prices.append(round(float(closest_price), 2))
            else:
                # Use last known price for weekends
                if daily_prices:
                    daily_prices.append(daily_prices[-1])
                else:
                    # If no data available, use the first available price
                    if not df.empty and not pd.isna(df['Close'].iloc[0]):
                        daily_prices.append(round(float(df['Close'].iloc[0]), 2))

        # Reverse to show chronological order (oldest to newest)
        return daily_labels[::-1], daily_prices[::-1]

    # For other periods, use existing logic
    if len(df) > count:
        df = df.tail(count)

    prices = df['Close'].round(2).astype(float).tolist()
    labels = _format_labels(df.index, period)

    return labels, prices


def get_stock_history_data(stock_symbol):
    symbol = stock_symbol.upper()
    ticker = yf.Ticker(symbol)
    history = {}

    for period, config in PERIOD_CONFIG.items():
        try:
            df = ticker.history(period=config['period'], interval=config['interval'], actions=False)
            
            # For indices, sometimes yfinance returns data with different structure
            if df is not None and not df.empty:
                # Ensure Close column exists
                if 'Close' not in df.columns:
                    df = pd.DataFrame()
        except Exception as e:
            print(f"Error fetching {symbol} for {period}: {e}")
            df = pd.DataFrame()

        labels, prices = _normalize_history(df, config['count'], period)
        history[period] = {
            'labels': labels,
            'prices': prices,
        }

    return history


def create_features_and_target(data):
    data = data.copy().reset_index(drop=True)
    features = np.arange(len(data)).reshape(-1, 1)
    target = data['price'].values
    return features, target


def predict_stock_price(stock_symbol):
    history = get_stock_history_data(stock_symbol)
    prices = history.get('1m', {}).get('prices', [])
    if len(prices) < 2:
        return None

    df = pd.DataFrame({'price': prices})
    features, target = create_features_and_target(df)

    model = StockPriceModel()
    model.train(features, target)

    next_index = np.array([[len(prices)]], dtype=float)
    predicted_value = model.predict(next_index)[0]
    return float(round(predicted_value, 2))


def get_stock_info(stock_symbol):
    symbol = stock_symbol.upper()
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return {
            'currentPrice': None,
            'change': 0,
            'changePercent': 0,
            'keyStats': {},
        }

    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    previous_close = info.get('previousClose')
    
    # For indices, try to get the regular market price
    if current_price is None:
        current_price = info.get('currentPrice')
    if previous_close is None:
        previous_close = info.get('regularMarketPreviousClose')
    
    if current_price is None or previous_close is None:
        # Try fetching history data as fallback
        try:
            history = ticker.history(period='5d')
            if not history.empty:
                current_price = history['Close'].iloc[-1]
                previous_close = history['Close'].iloc[0] if len(history) > 1 else current_price
        except Exception:
            pass
    
    change = current_price - previous_close if current_price and previous_close else 0
    change_percent = (change / previous_close * 100) if previous_close else 0

    # Fetch 1y history for 52 week dates and 10 day avg volume
    try:
        history_1y = ticker.history(period='1y')
        if not history_1y.empty:
            high_date = history_1y['High'].idxmax().strftime('%Y-%m-%d')
            low_date = history_1y['Low'].idxmin().strftime('%Y-%m-%d')
            avg_volume_10d = history_1y.tail(10)['Volume'].mean() if len(history_1y) >= 10 else history_1y['Volume'].mean()
        else:
            high_date = low_date = None
            avg_volume_10d = None
    except Exception:
        high_date = low_date = None
        avg_volume_10d = None

    key_stats = {
        'open': info.get('open'),
        'dayHigh': info.get('dayHigh') or info.get('regularMarketDayHigh'),
        'dayLow': info.get('dayLow') or info.get('regularMarketDayLow'),
        'prevClose': previous_close,
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
        'fiftyTwoWeekHighDate': high_date,
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
        'fiftyTwoWeekLowDate': low_date,
        'marketCap': info.get('marketCap'),
        'sharesOut': info.get('sharesOutstanding'),
        'avgVolume10d': avg_volume_10d,
        'dividend': info.get('dividendRate'),
        'dividendYield': info.get('dividendYield'),
        'beta': info.get('beta'),
    }

    return {
        'currentPrice': current_price,
        'change': change,
        'changePercent': change_percent,
        'keyStats': key_stats,
    }


def get_stock_prediction(stock_symbol):
    current_price_info = get_stock_info(stock_symbol)
    if current_price_info is None:
        return None

    predicted_price = predict_stock_price(stock_symbol)
    if predicted_price is None:
        return None

    trend = 'up' if predicted_price >= current_price_info['currentPrice'] else 'down'
    return {
        'symbol': stock_symbol.upper(),
        'predictedPrice': predicted_price,
        'trend': trend,
    }
