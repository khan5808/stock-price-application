from flask import Flask, request, jsonify
from data import get_stock_data
from model import train_model, predict_next_price
from db import init_db, save_prediction
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize DB
init_db()

@app.route("/")
def home():
    return {"message": "Stock Prediction API Running"}

# Get historical stock data
@app.route("/stock/<ticker>", methods=["GET"])
def stock_data(ticker):
    try:
        df = get_stock_data(ticker)
        data = df.tail(30).to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Predict next price
@app.route("/predict/<ticker>", methods=["GET"])
def predict(ticker):
    try:
        df = get_stock_data(ticker)

        model, processed_df = train_model(df)
        prediction = predict_next_price(model, processed_df)

        # Save to DB
        save_prediction(ticker, prediction)

        return jsonify({
            "ticker": ticker.upper(),
            "predicted_price": prediction
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get past predictions
@app.route("/predictions", methods=["GET"])
def get_predictions():
    import sqlite3
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
    rows = cursor.fetchall()

    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)

