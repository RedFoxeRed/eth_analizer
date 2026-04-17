"""
Модуль для получения свечей с Bybit
Возвращает последние 200 свечей с полным набором данных
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from pybit.unified_trading import HTTP
from dotenv import load_dotenv

load_dotenv()


class DataFetcher:
    """Класс для получения рыночных данных с Bybit"""
    
    def __init__(self, testnet: Optional[bool] = None, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None):
        """
        Инициализация подключения к Bybit
        
        Args:
            testnet: Использовать тестовую сеть (True) или основную (False)
            api_key: API ключ (если None - берется из .env)
            api_secret: API секрет (если None - берется из .env)
        """
        if testnet is None:
            testnet = os.getenv('BYBIT_TESTNET', 'True').lower() == 'true'
        
        if api_key is None:
            api_key = os.getenv('BYBIT_API_KEY', '')
        
        if api_secret is None:
            api_secret = os.getenv('BYBIT_API_SECRET', '')
        
        # Основная сеть (не тестнет)
        self.session = HTTP(
            testnet=False,
            api_key=api_key if api_key else None,
            api_secret=api_secret if api_secret else None,
            recv_window=10000,
        )
        self.symbol = 'ETHUSDT'
        self.timeframe = '5'
        self.limit = 200
    
    def get_candles(self, symbol: Optional[str] = None, timeframe: Optional[str] = None, 
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Получение свечей с Bybit
        
        Args:
            symbol: Торговая пара (по умолчанию ETHUSDT)
            timeframe: Таймфрейм (по умолчанию 15 минут)
            limit: Количество свечей (по умолчанию 200)
            
        Returns:
            Список словарей с данными свечей
        """
        sym = symbol or self.symbol
        tf = timeframe or self.timeframe
        lim = limit or self.limit
        
        try:
            response = self.session.get_kline(
                category="linear",
                symbol=sym,
                interval=tf,
                limit=lim
            )
            
            if response['retCode'] == 0:
                candles = response['result']['list']
                return [self._parse_candle(candle) for candle in candles]
            else:
                print(f"Ошибка получения данных: {response['retMsg']}")
                return []
                
        except Exception as e:
            print(f"Ошибка при получении свечей: {e}")
            return []
    
    def _parse_candle(self, candle: list) -> Dict:
        """
        Парсинг данных свечи
        
        Args:
            candle: Список данных свечи от Bybit
            
        Returns:
            Словарь с распарсенными данными свечи
        """
        return {
            'timestamp': int(candle[0]),  # Время начала свечи (ms)
            'datetime': datetime.fromtimestamp(int(candle[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'open': float(candle[1]),      # Цена открытия
            'high': float(candle[2]),      # Максимальная цена
            'low': float(candle[3]),       # Минимальная цена
            'close': float(candle[4]),     # Цена закрытия
            'volume': float(candle[5]),    # Объем в контрактах
            'turnover': float(candle[6])   # Объем в USDT
        }
    
    def get_latest_candles(self) -> List[Dict]:
        """
        Получение последних 200 свечей (удобный метод)
        
        Returns:
            Список из 200 последних свечей
        """
        return self.get_candles()
    
    def get_wallet_balance(self, coin: str = 'USDT') -> Optional[Dict]:
        """
        Получение баланса кошелька
        
        Args:
            coin: Валюта (по умолчанию USDT)
            
        Returns:
            Словарь с данными баланса или None
        """
        try:
            response = self.session.get_wallet_balance(
                accountType="UNIFIED",
                coin=coin
            )
            
            if response['retCode'] == 0:
                result = response['result']
                balance_info = result['list'][0]
                coin_info = balance_info['coin'][0]  # Информация по конкретной монете
                
                return {
                    'total_equity': float(balance_info.get('totalEquity', 0)),
                    'wallet_balance': float(balance_info.get('totalWalletBalance', 0)),
                    'available_balance': float(coin_info.get('walletBalance', 0)),
                    'unrealised_pnl': float(coin_info.get('unrealisedPnl', 0)),
                    'coin': coin
                }
            else:
                print(f"Ошибка получения баланса: {response['retMsg']}")
                return None
                
        except Exception as e:
            print(f"Ошибка при получении баланса: {e}")
            return None


# Пример использования
if __name__ == '__main__':
    fetcher = DataFetcher(testnet=True)
    
    # Тест свечей
    candles = fetcher.get_latest_candles()
    print(f"Получено свечей: {len(candles)}")
    
    # Тест баланса
    print("\nПроверка баланса...")
    balance = fetcher.get_wallet_balance('USDT')
    if balance:
        print(f"  Общий капитал: {balance['total_equity']} USDT")
        print(f"  Доступно: {balance['available_balance']} USDT")
        print(f"  Нerealized PnL: {balance['unrealised_pnl']} USDT")
