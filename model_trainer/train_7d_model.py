import pandas as pd
from fetcher.stock_data_manager import get_stock_data
from fetcher.news_fetcher import get_combined_news
from utils.sentiment_analyzer import analyze_sentiment
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def train_and_predict_7d(symbol, key):
    # Fetch price data
    df = get_stock_data(symbol, key)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    
    # News sentiment
    news = get_combined_news(symbol)
    compounds = [analyze_sentiment(x)["compound"] for x in news]
    avg_sent = sum(compounds)/len(compounds) if compounds else 0.0
    df["news_sentiment"] = avg_sent

    features = ["close", "news_sentiment"]
    data = df[features].values

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    # Prepare sequences
    X, y = [], []
    n_input = 60
    for i in range(n_input, len(scaled)):
        X.append(scaled[i-n_input:i])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)

    # Build model
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=5, batch_size=32, verbose=1)

    # Predict next 7 days
    input_seq = scaled[-n_input:]
    preds = []
    for _ in range(7):
        pred = model.predict(input_seq.reshape(1, n_input, X.shape[2]))[0][0]
        preds.append(pred)
        input_seq = np.vstack([input_seq[1:], [[pred, avg_sent]]])

    # Inverse scale
    preds = scaler.inverse_transform([[p, avg_sent] for p in preds])[:, 0]
    return preds
