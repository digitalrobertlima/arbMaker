import requests
import time
from datetime import datetime

BASE_URL = 'https://api.bitpreco.com'

def get_orderbook():
    try:
        response = requests.get(f"{BASE_URL}/btc-brl/orderbook")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter o livro de ordens: {e}")
        return None

def simulate_order(amount, price, side):
    print(f"Simulando ordem de {'compra' if side == 'buy' else 'venda'}:")
    print(f"Quantidade: {amount:.4f} BTC")
    print(f"Preço: R${price:.2f}")
    print("Ordem simulada com sucesso!")
    return {'success': True, 'amount': amount, 'price': price, 'side': side}

def print_orderbook(bids, asks, bot_order=None):
    print("\nLivro de Ordens Dinâmico")
    print("Tipo       Preço       Quantidade")
    print("-----------------------------")
    print("Top 5 Ordens de Compra:")
    for bid in bids[:5]:
        print(f"Compra     R${bid['price']:.2f}   {bid['amount']:.4f} BTC")
    print("Top 5 Ordens de Venda:")
    for ask in asks[:5]:
        print(f"Venda      R${ask['price']:.2f}   {ask['amount']:.4f} BTC")
    if bot_order:
        side = 'Compra' if bot_order['side'] == 'buy' else 'Venda'
        print(f"Ordem Simulada: {side} R${bot_order['price']:.2f} {bot_order['amount']:.4f} BTC")

def monitor_order_completion(side, target_price, bot_order):
    print_orderbook([], [], bot_order)
    while True:
        orderbook = get_orderbook()
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            print("Livro de ordens não disponível ou malformado. Atualizando...")
            time.sleep(10)
            continue

        bids = orderbook['bids']
        asks = orderbook['asks']

        if side == 'buy':
            if any(ask['price'] <= target_price for ask in asks):
                print(f"Ordem de compra a R${target_price:.2f} concluída.")
                log_transaction(side, target_price, bot_order)
                return True
        else:
            if any(bid['price'] >= target_price for bid in bids):
                print(f"Ordem de venda a R${target_price:.2f} concluída.")
                log_transaction(side, target_price, bot_order)
                return True

        print_orderbook(bids, asks, bot_order)
        print("Ordem ainda não concluída. Atualizando...")
        time.sleep(10)
