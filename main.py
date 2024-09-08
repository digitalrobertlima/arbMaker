from orderbook import get_orderbook, monitor_order_completion, simulate_order
from trades import get_trades, calculate_rsi, calculate_williams, calculate_macd
from utils import log_transaction
import time
import signal
import sys

def signal_handler(sig, frame):
    print("Interrupção recebida. Encerrando o programa...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    transaction_fee = 0.001
    min_profit = 0.005
    amount = 0.01
    risk_limit = 0.01

    previous_buy_price = None
    previous_sell_price = None

    while True:
        orderbook = get_orderbook()
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            print("Livro de ordens não disponível. Aguardando...")
            time.sleep(10)
            continue

        bids = orderbook['bids']
        asks = orderbook['asks']

        if not bids or not asks:
            print("Livro de ordens vazio. Aguardando...")
            time.sleep(10)
            continue

        best_bid = bids[0]
        best_ask = asks[0]

        buy_price = sum(bid['price'] * bid['amount'] for bid in bids[:5]) / sum(bid['amount'] for bid in bids[:5])
        sell_price = sum(ask['price'] * ask['amount'] for ask in asks[:5]) / sum(ask['amount'] for ask in asks[:5])

        trades = get_trades()
        if trades:
            rsi = calculate_rsi(trades)
            williams = calculate_williams(trades)
            macd, signal, histogram = calculate_macd(trades)

            print(f"RSI: {rsi:.2f}")
            print(f"Williams %R: {williams:.2f}")
            print(f"MACD: {macd:.2f}, Signal: {signal:.2f}, Histogram: {histogram:.2f}")

            if previous_buy_price and previous_sell_price:
                if abs(buy_price - previous_buy_price) > risk_limit or abs(sell_price - previous_sell_price) > risk_limit:
                    print("Movimento de mercado significativo detectado. Ajustando o risco.")
                    previous_buy_price = buy_price
                    previous_sell_price = sell_price
                    time.sleep(15)
                    continue

            print(f"Melhor preço de compra: R${buy_price:.2f}")
            print(f"Melhor preço de venda: R${sell_price:.2f}")

            if (sell_price - buy_price) > (min_profit + transaction_fee):
                if rsi < 30 and williams < -80 and histogram > 0:
                    print(f"Arbitragem identificada: Compra a R${buy_price:.2f} e venda a R${sell_price:.2f}")

                    print("Simulando ordem de compra...")
                    buy_response = simulate_order(amount, buy_price, 'buy')
                    print(f"Resposta da compra: {buy_response}")

                    if buy_response['success']:
                        if monitor_order_completion('buy', buy_price, buy_response):
                            print("Compra simulada concluída com sucesso!")

                            print("Simulando ordem de venda...")
                            sell_response = simulate_order(amount, sell_price, 'sell')
                            print(f"Resposta da venda: {sell_response}")

                            if sell_response['success']:
                                if monitor_order_completion('sell', sell_price, sell_response):
                                    print("Venda simulada concluída com sucesso!")
                                else:
                                    print("Falha na conclusão da venda.")
                            else:
                                print("Falha na simulação da venda.")
                        else:
                            print("Falha na conclusão da compra.")
                    else:
                        print("Falha na simulação da compra.")
                else:
                    print("Condições de mercado não atendidas para arbitragem.")
            else:
                print("Sem oportunidade de arbitragem com margem de lucro mínima.")

            previous_buy_price = buy_price
            previous_sell_price = sell_price
        else:
            print("Não foi possível obter dados de trades. Aguardando...")
        
        time.sleep(15)

if __name__ == "__main__":
    main()
