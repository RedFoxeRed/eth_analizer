"""
Генератор торговых сигналов
"""
from typing import Dict, Optional


class SignalGenerator:
    """Класс для генерации сигналов на основе индикаторов"""
    
    @staticmethod
    def get_signal(candle_close: float, ema_50: float, ema_200: float) -> Optional[str]:
        """
        Определение направления тренда
        
        Args:
            candle_close: Цена закрытия последней свечи
            ema_50: Значение EMA50
            ema_200: Значение EMA200
            
        Returns:
            'LONG', 'SHORT' или None (нет сигнала)
        """
        # ЛОНГ тренд
        if ema_50 > ema_200 and candle_close > ema_50:
            return 'LONG'
        
        # ШОРТ тренд
        if ema_50 < ema_200 and candle_close < ema_50:
            return 'SHORT'
        
        # Нет сигнала
        return None
