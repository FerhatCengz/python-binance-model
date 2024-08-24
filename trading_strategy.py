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

    # 50 ve 200 periyotluk basit hareketli ortalamalar (SMA) hesaplama
    data['sma_50'] = ta.sma(data['close'], length=50)
    data['sma_200'] = ta.sma(data['close'], length=200)
    
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

    # ADX hesaplama
    data['adx'] = ta.adx(data['high'], data['low'], data['close'], length=14)['ADX_14']
    
    # Hacim Hareketli Ortalaması (Volume Moving Average)
    data['volume_ma'] = ta.sma(data['volume'], length=20)
    
    # On-Balance Volume (OBV)
    data['obv'] = ta.obv(data['close'], data['volume'])

    return data

def evaluate_trading_signal(data: pd.DataFrame, symbol: str, model=None):
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

    if data['sma_50'].isnull().all():
        raise ValueError("sma_50 sütunu boş veya eksik veri içeriyor.")
    
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

    # Trend Tespiti
    sma_50 = data['sma_50'].iloc[-1]
    sma_200 = data['sma_200'].iloc[-1]
    adx = data['adx'].iloc[-1]

    trend = "unknown"
    if sma_50 > sma_200 and adx > 25:
        trend = "uptrend"
    elif sma_50 < sma_200 and adx > 25:
        trend = "downtrend"
    
    # Hacim Analizi
    volume_ma = data['volume_ma'].iloc[-1]
    current_volume = data['volume'].iloc[-1]
    obv = data['obv'].iloc[-1]

    volume_signal = "normal"
    if current_volume > volume_ma * 1.5:
        volume_signal = "high"
    elif current_volume < volume_ma * 0.5:
        volume_signal = "low"

    signal = {
        "symbol": symbol,
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
        'take_profit': take_profit,  # Take-Profit seviyesini ekliyoruz
        'trend': trend,  # Trend yönünü ekliyoruz
        'current_volume': current_volume,  # Mevcut hacmi ekliyoruz
        'volume_ma': volume_ma,  # Hacim hareketli ortalaması
        'volume_signal': volume_signal,  # Hacim sinyali (high, low, normal)
        'obv': obv  # OBV (On-Balance Volume)
    }

    last_row = data.iloc[-1]

    # Bollinger Bantları ve ATR ile Alım-Satım sinyalleri
    if current_price < bb_lower and last_row['rsi'] < 30 and atr > atr_threshold and trend == "uptrend":
        signal['buy'] = True
    elif current_price > bb_upper and last_row['rsi'] > 70 and atr > atr_threshold and trend == "downtrend":
        signal['sell'] = True
    
    # Destek ve Direnç Seviyelerine dayalı alım-satım sinyalleri
    if current_price < support1 or current_price < previous_low:
        signal['buy'] = True
    elif current_price > resistance1 or current_price > previous_high:
        signal['sell'] = True

    return signal
