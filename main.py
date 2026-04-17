"""
Основной скрипт запуска мониторинга ETH/USDT
Запрашивает 200 свечей каждые 15 минут
"""
import schedule
import time
from core.data_fetcher import DataFetcher
from core.order_manager import OrderManager
from analyzers.technical_indicators import TechnicalIndicators
from analyzers.signal_generator import SignalGenerator
from trading.executor import TradingExecutor
from trading.risk_manager import EntryFilters
from trading.position_manager import TradeSetup


def fetch_candles_job(fetcher: DataFetcher, order_manager: OrderManager):
    """Задача получения свечей"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Запрос свечей...")
    
    candles = fetcher.get_latest_candles()
    
    print(f"Получено свечей: {len(candles)}")
    
    if candles:
        latest = candles[0]
        print(f"Последняя свеча: {latest['datetime']}")
        print(f"  Close: {latest['close']} | Volume: {latest['volume']}")
        
        # Расчет индикаторов
        indicators = TechnicalIndicators.calculate_indicators(candles)
        
        print(f"\nИндикаторы:")
        print(f"  RSI(14): {indicators['rsi_14']}")
        print(f"  EMA(50): {indicators['ema_50']}")
        print(f"  EMA(200): {indicators['ema_200']}")
        print(f"  ATR(14): {indicators['atr_14']}")
        print(f"  Avg Volume(20): {indicators['avg_volume_20']}")
        
        # Определение сигнала
        signal = SignalGenerator.get_signal(
            candle_close=latest['close'],
            ema_50=indicators['ema_50'],
            ema_200=indicators['ema_200']
        )
        
        if signal:
            print(f"\n📊 СИГНАЛ: {signal}")
            
            # Проверка фильтров входа
            if signal == 'LONG':
                entry_result = EntryFilters.check_long_entry(latest, indicators)
            else:  # SHORT
                entry_result = EntryFilters.check_short_entry(latest, indicators)
            
            print(f"  → {entry_result}")
            
            # Если вход разрешен - рассчитываем параметры сделки
            if entry_result == 'Вход разрешен':
                if signal == 'LONG':
                    trade_setup = TradeSetup.calculate_long_setup(candles, indicators)
                else:  # SHORT
                    trade_setup = TradeSetup.calculate_short_setup(candles, indicators)
                
                if trade_setup and trade_setup['valid']:
                    print(f"\n✅ СДЕЛКА ОДОБРЕНА:")
                    print(f"  Entry: {trade_setup['entry']}")
                    print(f"  SL: {trade_setup['sl']} ({trade_setup['sl_percent']}%)")
                    print(f"  TP: {trade_setup['tp']} ({trade_setup['tp_percent']}%)")
                    print(f"  RR: {trade_setup['rr']}")
                    
                    # Получаем баланс
                    balance_info = fetcher.get_wallet_balance('USDT')
                    if balance_info:
                        balance = balance_info['available_balance']
                        print(f"\n💰 Баланс: {balance} USDT")
                        
                        # Проверяем наличие открытых позиций/ордеров
                        check_result = order_manager.has_open_position_or_order()
                        
                        if check_result['position']:
                            # Позиция уже открыта - ПРОПУСК
                            print(f"\n⏸️  ПРОПУСК: Уже есть открытая позиция")
                        elif check_result['open_order']:
                            # Ордер висит - ОТМЕНА и создание нового
                            print(f"\n🔄 Ордер висит - отменяем и создаем новый...")
                            order_manager.cancel_open_order(check_result['order_id'])
                            TradingExecutor.execute(signal, trade_setup, order_manager, balance)
                        else:
                            # Ничего нет - открываем сделку
                            TradingExecutor.execute(signal, trade_setup, order_manager, balance)
                    else:
                        print(f"\n❌ Не удалось получить баланс")
                else:
                    reason = trade_setup['reason'] if trade_setup else 'Недостаточно данных'
                    print(f"\n❌ СДЕЛКА ОТКЛОНЕНА: {reason}")
        else:
            print(f"\n❌ Нет сигнала для торговли")


def main():
    """Основная функция"""
    print("=" * 50)
    print("ETH/USDT Monitor")
    print("Интервал: 5 минут")
    print("=" * 50)
    
    # Инициализация
    fetcher = DataFetcher()
    order_manager = OrderManager(fetcher.session)
    
    # Первый запуск сразу
    fetch_candles_job(fetcher, order_manager)
    
    # Планирование каждые 5 минут
    schedule.every(1).minutes.do(fetch_candles_job, fetcher, order_manager)
    
    print("\nМониторинг запущен. Нажмите Ctrl+C для остановки.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nМониторинг остановлен.")


if __name__ == '__main__':
    main()
