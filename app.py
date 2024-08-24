from flask import Flask, request, jsonify
from data_fetcher import fetch_binance_data
from trading_strategy import evaluate_trading_signal

app = Flask(__name__)

@app.route('/trade_signal', methods=['POST'])
def trade_signal():
    data = request.get_json()
    symbol = data.get('symbol')
    interval = data.get('interval', '15m')

    # Binance'ten verileri çek
    market_data = fetch_binance_data(symbol, interval)

    # Alım-satım sinyali oluştur (model parametresi olmadan)
    signal = evaluate_trading_signal(market_data)

    return jsonify(signal)

if __name__ == '__main__':
    app.run(port=8080)
