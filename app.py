from flask import Flask, request, jsonify
from data_fetcher import fetch_binance_data
from trading_strategy import evaluate_trading_signal

app = Flask(__name__)

VALID_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

@app.route('/trade_signal', methods=['POST'])
def trade_signal():
    data = request.get_json()
    symbol = data.get('symbol')
    interval = data.get('interval', '15m')

    if interval not in VALID_INTERVALS:
        return jsonify({'error': 'Invalid interval'}), 400

    try:
        # Binance'ten verileri çek
        market_data = fetch_binance_data(symbol, interval)

        # Alım-satım sinyali oluştur (model parametresi olmadan)
        signal = evaluate_trading_signal(market_data, symbol)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(
        signal=signal,
        interval=interval
    )

if __name__ == '__main__':
    app.run(port=8080)