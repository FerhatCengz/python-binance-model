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
    
    # Bollinger Bantları hesaplama
    bollinger = ta.bbands(data['close'], length=20, std=2)
    data['bb_upper'] = bollinger['BBU_20_2.0']  # Üst bant
    data['bb_middle'] = bollinger['BBM_20_2.0']  # Orta bant (20 SMA)
    data['bb_lower'] = bollinger['BBL_20_2.0']  # Alt bant

    # ATR hesaplama
    data['atr'] = ta.atr(data['high'], data['low'], data['close'], length=14)

    # Pivot noktalarını hesaplama (Pivot, Destek 1, Direnç 1)
    data['pivot'] = (data['high'] + data['low'] + data['close']) / 3
    data['support1'] = (2 * data['pivot']) - data['high']
    data['resistance1'] = (2 * data['pivot']) - data['low']
    
    # Önceki yüksek ve düşük seviyeleri ekleyelim
    data['previous_high'] = data['high'].shift(1)
    data['previous_low'] = data['low'].shift(1)
    
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

    # Bollinger Bantları kontrolü
    bb_upper = data['bb_upper'].iloc[-1]
    bb_lower = data['bb_lower'].iloc[-1]
    
    # ATR kontrolü
    atr = data['atr'].iloc[-1]
    atr_threshold = 0.05 * current_price  # ATR'nin %5'lik bir eşiği geçip geçmediğini kontrol ediyoruz
    
    # Destek ve Direnç Seviyeleri
    support1 = data['support1'].iloc[-1]
    resistance1 = data['resistance1'].iloc[-1]
    previous_high = data['previous_high'].iloc[-1]
    previous_low = data['previous_low'].iloc[-1]

    # Stop-Loss ve Take-Profit seviyeleri
    stop_loss = current_price - (atr * 1.5)  # ATR'ye dayalı dinamik stop-loss
    take_profit = current_price + (atr * 2)  # ATR'ye dayalı dinamik take-profit

    signal = {
        'buy': False,
        'sell': False,
        'current_price': current_price,  # Mevcut fiyatı ekliyoruz
        'predicted_price': predicted_price if model else None,
        'rsi': data.iloc[-1]['rsi'],
        'macd': data.iloc[-1]['macd'],
        'macd_signal': data.iloc[-1]['macd_signal'],
        'buy_price': buy_price,
        'sell_price': sell_price,
        'bb_upper': bb_upper,
        'bb_lower': bb_lower,
        'atr': atr,
        'atr_threshold': atr_threshold,
        'support1': support1,
        'resistance1': resistance1,
        'previous_high': previous_high,
        'previous_low': previous_low,
        'stop_loss': stop_loss,  # Stop-Loss seviyesini ekliyoruz
        'take_profit': take_profit  # Take-Profit seviyesini ekliyoruz
    }

    last_row = data.iloc[-1]

    # Bollinger Bantları ve ATR ile Alım-Satım sinyalleri
    if current_price < bb_lower and last_row['rsi'] < 30 and atr > atr_threshold:
        signal['buy'] = True
    elif current_price > bb_upper and last_row['rsi'] > 70 and atr > atr_threshold:
        signal['sell'] = True
    
    # Destek ve Direnç Seviyelerine dayalı alım-satım sinyalleri
    if current_price < support1 or current_price < previous_low:
        signal['buy'] = True
    elif current_price > resistance1 or current_price > previous_high:
        signal['sell'] = True

    return signal
