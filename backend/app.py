from flask import Flask, request, jsonify

try:
    from .data import get_stock_data, get_current_price
    from .model import train_model, predict_next_price
    from .db import init_db, save_prediction
except ImportError:
    from data import get_stock_data, get_current_price
    from model import train_model, predict_next_price
    from db import init_db, save_prediction

app = Flask(__name__)

# Initialize DB
init_db()

@app.route("/")
def home():
    return {"message": "Stock Prediction API Running"}

# Get historical stock data
@app.route("/stock/<ticker>", methods=["GET"])
def stock_data(ticker):
    try:
        period = request.args.get("period", "1mo")
        interval = request.args.get("interval", "1d")

        df = get_stock_data(ticker, period, interval)
        data = df.tail(30).to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/current/<ticker>")
def current_price(ticker):
    price = get_current_price(ticker)
    return {"ticker": ticker.upper(), "price": price}

@app.route("/leaderboard")
def leaderboard():
    stocks = ["AAPL", "TSLA", "MSFT", "NVDA"]
    results = []

    for s in stocks:
        price = get_current_price(s)
        results.append({"ticker": s, "price": price})

    results.sort(key=lambda x: x["price"], reverse=True)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)




