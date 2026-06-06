import os
import sys
import requests
from flask import Flask, request, jsonify

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
from model import get_stock_info, get_stock_prediction, get_stock_history_data, get_stock_name

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
YAHOO_SEARCH_URL = 'https://query2.finance.yahoo.com/v1/finance/search'

COMMON_STOCKS = {
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'tesla': 'TSLA',
    'amazon': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'netflix': 'NFLX',
    'nvidia': 'NVDA',
    'prudential': 'PRU',
    'dow': '^DJI',
    'nasdaq': '^IXIC',
    'sp500': '^GSPC',
    'bobs': 'BOBS',
}

ALL_STOCKS = [
    ('AAPL', 'Apple'),
    ('MSFT', 'Microsoft'),
    ('GOOGL', 'Google'),
    ('GOOG', 'Google'),
    ('AMZN', 'Amazon'),
    ('TSLA', 'Tesla'),
    ('META', 'Meta'),
    ('NFLX', 'Netflix'),
    ('NVDA', 'NVIDIA'),
    ('JPM', 'JPMorgan Chase'),
    ('JNJ', 'Johnson & Johnson'),
    ('V', 'Visa'),
    ('WMT', 'Walmart'),
    ('PG', 'Procter & Gamble'),
    ('UNH', 'UnitedHealth'),
    ('HD', 'Home Depot'),
    ('MA', 'Mastercard'),
    ('DIS', 'Disney'),
    ('BA', 'Boeing'),
    ('KO', 'Coca-Cola'),
    ('INTC', 'Intel'),
    ('AMD', 'Advanced Micro Devices'),
    ('CSCO', 'Cisco'),
    ('CRM', 'Salesforce'),
    ('IBM', 'IBM'),
    ('ORCL', 'Oracle'),
    ('SAP', 'SAP'),
    ('ADBE', 'Adobe'),
    ('PYPL', 'PayPal'),
    ('SQ', 'Block'),
    ('UBER', 'Uber'),
    ('LYFT', 'Lyft'),
    ('SNAP', 'Snap'),
    ('PINS', 'Pinterest'),
    ('TWTR', 'Twitter/X'),
    ('SPOT', 'Spotify'),
    ('ROKU', 'Roku'),
    ('PLTR', 'Palantir'),
    ('COIN', 'Coinbase'),
    ('GME', 'GameStop'),
    ('AMC', 'AMC Entertainment'),
    ('NIO', 'NIO'),
    ('XPEV', 'XPeng'),
    ('F', 'Ford'),
    ('GM', 'General Motors'),
    ('T', 'AT&T'),
    ('VZ', 'Verizon'),
    ('PEP', 'PepsiCo'),
    ('MCD', 'McDonald\'s'),
    ('SBUX', 'Starbucks'),
    ('PRU', 'Prudential Financial'),
    ('AXP', 'American Express'),
    ('GS', 'Goldman Sachs'),
    ('MS', 'Morgan Stanley'),
    ('BLK', 'BlackRock'),
    ('BRK.B', 'Berkshire Hathaway'),
    ('C', 'Citigroup'),
    ('BAC', 'Bank of America'),
    ('WFC', 'Wells Fargo'),
    ('USB', 'US Bancorp'),
    ('^DJI', 'Dow Jones Industrial'),
    ('^IXIC', 'NASDAQ Composite'),
    ('^GSPC', 'S&P 500'),
    ('QCOM', 'Qualcomm'),
    ('AVGO', 'Broadcom'),
    ('ASML', 'ASML'),
    ('MRNA', 'Moderna'),
    ('AZN', 'AstraZeneca'),
    ('ZM', 'Zoom'),
    ('MSTR', 'MicroStrategy'),
    ('BOB', 'Berkshire Hathaway Inc'),
    ('LCAP', 'Large Cap'),
    ('LMT', 'Lockheed Martin'),
    ('RTX', 'Raytheon Technologies'),
    ('NOC', 'Northrop Grumman'),
    ('CAT', 'Caterpillar'),
    ('DE', 'Deere & Company'),
    ('MMM', '3M Company'),
    ('HON', 'Honeywell International'),
    ('GE', 'General Electric'),
    ('BOBS', 'Bob\'s Discount Furniture, Inc.'),
    ('SO', 'Southern Company'),
    ('NEE', 'NextEra Energy'),
    ('DUK', 'Duke Energy'),
    ('EXC', 'Exelon Corporation'),
    ('XOM', 'Exxon Mobil'),
    ('CVX', 'Chevron'),
    ('COP', 'ConocoPhillips'),
    ('SLB', 'Schlumberger'),
    ('MPC', 'Marathon Petroleum'),
]

POPULAR_STOCKS = [
    {'symbol': 'AAPL', 'name': 'Apple'},
    {'symbol': 'MSFT', 'name': 'Microsoft'},
    {'symbol': 'GOOGL', 'name': 'Google'},
    {'symbol': 'AMZN', 'name': 'Amazon'},
    {'symbol': 'TSLA', 'name': 'Tesla'},
]

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/search', methods=['GET'])
def search_stock():
    query = request.args.get('query', '').strip()
    
    # Return popular stocks if no query
    if not query:
        return jsonify(POPULAR_STOCKS)

    query_lower = query.lower()
    
    # Check common stocks first (exact name match)
    if query_lower in COMMON_STOCKS:
        return jsonify([{
            'symbol': COMMON_STOCKS[query_lower],
            'name': query.title()
        }])

    # For short queries, search local stock list first
    local_results = []
    if len(query) <= 5:
        # Search by symbol (case-insensitive)
        for symbol, name in ALL_STOCKS:
            if symbol.lower().startswith(query_lower):
                local_results.append({'symbol': symbol, 'name': name})
        
        # If symbol search didn't find enough, search by name
        if len(local_results) < 5:
            for symbol, name in ALL_STOCKS:
                if name.lower().startswith(query_lower) and {'symbol': symbol, 'name': name} not in local_results:
                    local_results.append({'symbol': symbol, 'name': name})
        
        if local_results:
            return jsonify(local_results[:5])

    # Fall back to Yahoo Finance API for longer queries
    params = {
        'q': query,
        'quotesCount': 10,
        'newsCount': 0,
        'region': 'US',
        'lang': 'en-US',
    }
    try:
        response = requests.get(YAHOO_SEARCH_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get('quotes', []):
            symbol = item.get('symbol')
            name = item.get('shortname') or item.get('longname') or ''
            if symbol:
                results.append({
                    'symbol': symbol,
                    'name': name,
                })
        if results:
            return jsonify(results[:5])
    except Exception:
        pass

    # Fallback: if query looks like a symbol, return it
    if query.isupper() and len(query) <= 5:
        return jsonify([{'symbol': query, 'name': ''}])
    
    return jsonify([])

@app.route('/api/stock_data', methods=['GET'])
def get_stock_data():
    stock_symbol = request.args.get('symbol', '').upper().strip()
    if not stock_symbol:
        return jsonify({'error': 'Missing stock symbol'}), 400

    stock_name = get_stock_name(stock_symbol)
    stock_info = get_stock_info(stock_symbol)
    if stock_info is None:
        return jsonify({'error': 'Unknown stock symbol or no data available'}), 404

    prediction = get_stock_prediction(stock_symbol)
    history = get_stock_history_data(stock_symbol)

    response = {
        'symbol': stock_symbol,
        'name': stock_name,
        'currentPrice': stock_info['currentPrice'],
        'change': stock_info['change'],
        'changePercent': stock_info['changePercent'],
        'keyStats': stock_info.get('keyStats'),
        'prediction': prediction,
        'history': history,
    }
    return jsonify(response)

@app.route('/api/predict/<string:stock_symbol>', methods=['GET'])
def predict_stock(stock_symbol):
    stock_symbol = stock_symbol.upper().strip()
    if not stock_symbol:
        return jsonify({'error': 'Missing stock symbol'}), 400

    prediction = get_stock_prediction(stock_symbol)
    if prediction is None:
        return jsonify({'error': 'Unknown stock symbol or no prediction available'}), 404
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(debug=True)
