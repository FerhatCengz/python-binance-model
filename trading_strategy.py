import pandas as pd
import pandas_ta as ta
from sklearn.preprocessing import MinMaxScaler

def calculate_technical_indicators(data: pd.DataFrame):
    # RSI hesaplama
    data['rsi'] = ta.rsi(data['close'], length=14)

    # MACD hesaplama
    macd = ta.macd(data['close'])
    data['macd'] = macd['MACD_12_26_9']
    data['macd_signal'] = macd['MACDs_12_26_9']

    # 50 periyotluk basit hareketli ortalama (SMA) hesaplama
    data['sma_50'] = ta.sma(data['close'], length=50)
    
    return data

def evaluate_trading_signal(data: pd.DataFrame, model=None):
    data = calculate_technical_indicators(data)
    
    # Mevcut fiyat (son kapanış fiyatı)
    current_price = data['close'].iloc[-1]
    
    # Model ile tahmin yap, model None değilse
    if model is not None:
        model_input = data['close'].values[-60:]
        model_input = model_input.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        model_input = scaler.fit_transform(model_input)
        model_input = np.reshape(model_input, (1, model_input.shape[0], 1))

        predicted_price = model.predict(model_input)
        predicted_price = scaler.inverse_transform(predicted_price)
    else:
        predicted_price = None  # Model yoksa tahmin edilen fiyat None olacak

    # Alım ve satım için önerilen fiyatlar (50 günlük SMA'ya dayalı olarak)
    buy_price = data['sma_50'].iloc[-1] * 0.98  # %2 altında bir fiyat
    sell_price = data['sma_50'].iloc[-1] * 1.02  # %2 üstünde bir fiyat

    signal = {
        'buy': False,
        'sell': False,
        'current_price': current_price,  # Mevcut fiyatı ekliyoruz
        'predicted_price': predicted_price if model else None,
        'rsi': data.iloc[-1]['rsi'],
        'macd': data.iloc[-1]['macd'],
        'macd_signal': data.iloc[-1]['macd_signal'],
        'buy_price': buy_price,
        'sell_price': sell_price
    }

    last_row = data.iloc[-1]

    if last_row['rsi'] < 30 and last_row['macd'] > last_row['macd_signal'] and (model is None or last_row['close'] < predicted_price):
        signal['buy'] = True
    elif last_row['rsi'] > 70 and last_row['macd'] < last_row['macd_signal'] and (model is None or last_row['close'] > predicted_price):
        signal['sell'] = True

    return signal
