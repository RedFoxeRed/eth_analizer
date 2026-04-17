"""
Тестовый скрипт для размещения ордера
"""
from core.data_fetcher import DataFetcher
from core.order_manager import OrderManager


def test_order():
    """Тест размещения лимитного ордера"""
    
    # Инициализация
    fetcher = DataFetcher()
    order_manager = OrderManager(fetcher.session)
    
    # Получаем баланс
    balance_info = fetcher.get_wallet_balance('USDT')
    if not balance_info:
        print("❌ Не удалось получить баланс")
        return
    
    balance = balance_info['available_balance']
    print(f"💰 Доступный баланс: {balance} USDT")
    
    # Параметры сделки (тестовые)
    entry = 3000.0  # Точка входа
    tp = 2950.0     # Stop-loss
    sl = 3070.0     # Take-profit
    side = 'Sell'    # LONG
    
    print(f"\n📊 Параметры сделки:")
    print(f"  Side: {side} (LONG)")
    print(f"  Entry: {entry}")
    print(f"  SL: {sl}")
    print(f"  TP: {tp}")
    
    # Установка плеча
    order_manager.set_leverage(100)
    
    # Расчет размера позиции (1% от баланса)
    qty = order_manager.calculate_position_size(
        balance=balance,
        entry=entry,
        leverage=100,
        risk_percent=1.0
    )
    
    print(f"\n📐 Расчет:")
    print(f"  Маржа: {balance * 0.01:.2f} USDT (1%)")
    print(f"  Позиция: {qty} ETH")
    print(f"  Плечо: 100x")
    
    # Размещение ордера
    print(f"\n⚠️  РАЗМЕЩЕНИЕ ОРДЕРА...")
    order_result = order_manager.place_limit_order(
        side=side,
        entry=entry,
        qty=qty,
        sl=sl,
        tp=tp
    )
    
    if order_result:
        print(f"\n✅ СДЕЛКА ОТКРЫТА!")
        print(f"  Закрой вручную через терминал Bybit")
    else:
        print(f"\n❌ ОШИБКА ОТКРЫТИЯ СДЕЛКИ")


if __name__ == '__main__':
    test_order()
