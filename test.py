from data_fetcher import fetch_binance_data

# fetch_binance_data fonksiyonunu test edin
market_data = fetch_binance_data('BTCUSDT', '30m')
print(market_data)