"""
Исполнитель торговых решений
"""
from core.order_manager import OrderManager


class TradingExecutor:
    """Класс для исполнения торговых операций"""
    
    @staticmethod
    def execute(signal: str, trade_setup: dict, order_manager: OrderManager, balance: float):
        """
        Исполнение торгового сигнала
        
        Args:
            signal: 'LONG' или 'SHORT'
            trade_setup: Параметры сделки (entry, sl, tp, rr)
            order_manager: Менеджер ордеров
            balance: Доступный баланс
        """
        print(f"\n[TradingExecutor] Исполнение сигнала: {signal}")
        print(f"  Entry: {trade_setup['entry']}")
        print(f"  SL: {trade_setup['sl']}")
        print(f"  TP: {trade_setup['tp']}")
        print(f"  RR: {trade_setup['rr']}")
        
        # Установка плеча
        order_manager.set_leverage(100)
        
        # Расчет размера позиции (1% от баланса)
        qty = order_manager.calculate_position_size(
            balance=balance,
            entry=trade_setup['entry'],
            leverage=100,
            risk_percent=1.0
        )
        
        print(f"  Balance: {balance} USDT")
        print(f"  Risk: 1% = {balance * 0.01:.2f} USDT (маржа)")
        print(f"  Position size: {qty} ETH")
        print(f"  Leverage: 100x")
        
        # Определение стороны
        side = 'Buy' if signal == 'LONG' else 'Sell'
        
        # Размещение ордера
        print(f"\n⚠️  РАЗМЕЩЕНИЕ ОРДЕРА...")
        order_result = order_manager.place_limit_order(
            side=side,
            entry=trade_setup['entry'],
            qty=qty,
            sl=trade_setup['sl'],
            tp=trade_setup['tp']
        )
        
        if order_result:
            print(f"\n✅ СДЕЛКА ОТКРЫТА! Жду закрытия вручную.")
        else:
            print(f"\n❌ ОШИБКА ОТКРЫТИЯ СДЕЛКИ!")
