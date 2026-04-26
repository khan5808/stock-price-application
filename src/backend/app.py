from flask import Flask, render_template, jsonify, request
from models.lstm_model import train_and_predict
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

WATCHLIST = ['AAPL','MSFT','NVDA','TSLA','AMZN','GOOGL']


def get_info(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    hist = t.history(period='6mo', interval='1d').reset_index()
    return t, info, hist


def calc_signal(hist):
    close = hist['Close']
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else sma20
    price = close.iloc[-1]
    if price > sma20 > sma50:
        return 'BUY'
    elif price < sma20 < sma50:
        return 'SELL'
    return 'HOLD'


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    leaders = []
    for s in WATCHLIST:
        try:
            _, info, _ = get_info(s)
            leaders.append({
                'ticker': s,
                'price': round(info.get('currentPrice',0),2),
                'name': info.get('shortName',s)
            })
        except:
            pass
    leaders = sorted(leaders, key=lambda x: x['price'], reverse=True)
    return render_template('dashboard.html', leaders=leaders)


@app.route('/stock/<ticker>')
def stock(ticker):
    ticker = ticker.upper()
    t, info, hist = get_info(ticker)
    signal = calc_signal(hist)
    news = info.get('longBusinessSummary','No summary available.')
    return render_template('stock.html',
        ticker=ticker,
        name=info.get('shortName',ticker),
        price=round(info.get('currentPrice',0),2),
        market_cap=info.get('marketCap','N/A'),
        pe=info.get('trailingPE','N/A'),
        volume=info.get('volume','N/A'),
        high52=info.get('fiftyTwoWeekHigh','N/A'),
        low52=info.get('fiftyTwoWeekLow','N/A'),
        signal=signal,
        summary=news
    )
    
@app.route('/api/chart/<ticker>')
def api_chart(ticker):
    period = request.args.get('period','6mo')
    interval = request.args.get('interval','1d')
    hist = yf.Ticker(ticker).history(period=period, interval=interval).reset_index()
    data = []
    for _, r in hist.iterrows():
        dt = str(r['Date'])[:10] if 'Date' in hist.columns else str(r['Datetime'])
        data.append({
            'time': dt,
            'open': float(r['Open']),
            'high': float(r['High']),
            'low': float(r['Low']),
            'close': float(r['Close'])
        })
    return jsonify(data)


@app.route('/api/predict/<ticker>')
def predict(ticker):
    hist = yf.Ticker(ticker).history(period='1y')['Close'].dropna()
    pred = train_and_predict(hist.tolist())
    last = float(hist.iloc[-1]) if len(hist) else 0
    signal = 'BUY' if pred > last * 1.01 else ('SELL' if pred < last * 0.99 else 'HOLD')
    return jsonify({'prediction': round(pred,2), 'last_price': round(last,2), 'signal': signal})


@app.route('/api/news/<ticker>')
def api_news(ticker):
    return jsonify([
        {'title': f'{ticker.upper()} rallies after analyst upgrade'},
        {'title': f'{ticker.upper()} earnings expected next month'},
        {'title': f'Institutions increase {ticker.upper()} holdings'}
    ])


@app.route('/api/earnings/<ticker>')
def api_earnings(ticker):
    return jsonify({'next_earnings':'2026-07-28'})


@app.route('/api/insiders/<ticker>')
def api_insiders(ticker):
    return jsonify([
        {'name':'Executive A','type':'Buy','shares':15000},
        {'name':'Director B','type':'Sell','shares':5000}
    ])

@app.route('/api/watchlist')
def watchlist():
    return jsonify(['AAPL','NVDA','MSFT'])

@app.route('/api/portfolio')
def portfolio():
    return jsonify({'cash':100000,'positions':[{'ticker':'AAPL','shares':10}]})

@app.route('/api/sim/buy/<ticker>')
def sim_buy(ticker):
    return jsonify({'status':'ok','action':'buy','ticker':ticker.upper()})

@app.route('/api/sim/sell/<ticker>')
def sim_sell(ticker):
    return jsonify({'status':'ok','action':'sell','ticker':ticker.upper()})

if __name__ == '__main__':
    app.run(debug=True)

