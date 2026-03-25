import numpy as np
from sklearn.linear_model import LinearRegression

def train_model(df):
    df = df[['Close']]

    # Create lag features (previous 5 days)
    for i in range(1, 6):
        df[f'lag_{i}'] = df['Close'].shift(i)

    df.dropna(inplace=True)

    X = df.drop('Close', axis=1)
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    return model, df

def predict_next_price(model, df):
    last_row = df.iloc[-1]
    features = last_row.drop('Close').values.reshape(1, -1)

    prediction = model.predict(features)[0]
    return float(prediction)

