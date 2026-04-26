import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


def train_and_predict(prices):
    values = np.array(prices).reshape(-1,1)
    if len(values) < 80:
        return float(values[-1][0]) if len(values) else 0.0

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    lookback = 60
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i])
        y.append(scaled[i])

    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1],1)))
    model.add(Dropout(0.2))
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    last_seq = scaled[-lookback:].reshape(1,lookback,1)
    pred = model.predict(last_seq, verbose=0)
    return float(scaler.inverse_transform(pred)[0][0])
