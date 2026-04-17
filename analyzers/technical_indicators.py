"""
Технические индикаторы для анализа
"""
import pandas as pd
from typing import List, Dict


class TechnicalIndicators:
    """Класс для расчета технических индикаторов"""
    
    @staticmethod
    def calculate_indicators(candles: List[Dict]) -> Dict:
        """
        Расчет всех индикаторов на основе свечей
        
        Args:
            candles: Список свечей от DataFetcher
            
        Returns:
            Словарь с рассчитанными индикаторами
        """
        df = pd.DataFrame(candles)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        indicators = {
            'rsi_14': TechnicalIndicators._calculate_rsi(df, period=14),
            'ema_50': TechnicalIndicators._calculate_ema(df, period=50),
            'ema_200': TechnicalIndicators._calculate_ema(df, period=200),
            'atr_14': TechnicalIndicators._calculate_atr(df, period=14),
            'avg_volume_20': TechnicalIndicators._calculate_avg_volume(df, period=20),
        }
        
        return indicators
    
    @staticmethod
    def _calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
        """
        Расчет RSI (Relative Strength Index)
        
        Returns:
            Последнее значение RSI
        """
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi.iloc[-1], 2)
    
    @staticmethod
    def _calculate_ema(df: pd.DataFrame, period: int) -> float:
        """
        Расчет EMA (Exponential Moving Average)
        
        Returns:
            Последнее значение EMA
        """
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return round(ema.iloc[-1], 2)
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """
        Расчет ATR (Average True Range)
        
        Returns:
            Последнее значение ATR
        """
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return round(atr.iloc[-1], 2)
    
    @staticmethod
    def _calculate_avg_volume(df: pd.DataFrame, period: int = 20) -> float:
        """
        Расчет среднего объема
        
        Returns:
            Средний объем за период
        """
        avg_volume = df['volume'].rolling(window=period).mean()
        return round(avg_volume.iloc[-1], 2)
