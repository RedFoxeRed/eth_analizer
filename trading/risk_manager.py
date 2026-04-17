"""
Фильтры входа для торговых сигналов
"""
from typing import Dict


class EntryFilters:
    """Класс для проверки условий входа в сделку"""
    
    @staticmethod
    def check_long_entry(candle: Dict, indicators: Dict) -> str:
        """
        Проверка условий для входа в LONG
        
        Args:
            candle: Данные последней свечи
            indicators: Рассчитанные индикаторы
            
        Returns:
            'Вход разрешен' или 'Вход запрещен: причина'
        """
        volume = candle['volume']
        avg_volume = indicators['avg_volume_20']
        close = candle['close']
        open_price = candle['open']
        ema_50 = indicators['ema_50']
        atr_14 = indicators['atr_14']
        
        # 1. Проверка объема (относительная)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio < 0.5:
            return f'Вход запрещен: объем слишком низкий (ratio: {volume_ratio:.2f})'
        
        if volume_ratio < 0.8:
            return f'Вход запрещен: объем недостаточный (ratio: {volume_ratio:.2f})'
        
        # 2. Проверка последней свечи (не большая красная)
        candle_size = abs(close - open_price)
        is_red = close < open_price
        is_large = candle_size > 1.5 * atr_14
        
        if is_red and is_large:
            return 'Вход запрещен: большая красная свеча'
        
        # 3. Подтверждение разворота (текущая свеча закрылась выше открытия)
        if close <= open_price:
            return 'Вход запрещен: нет подтверждения разворота (свеча не зелёная)'
        
        # 4. Положение цены (расстояние от EMA50 ≤ 1 × ATR)
        distance_from_ema = abs(close - ema_50)
        if distance_from_ema > atr_14:
            return f'Вход запрещен: цена далеко от EMA50 (расстояние: {distance_from_ema:.2f}, ATR: {atr_14:.2f})'
        
        return 'Вход разрешен'
    
    @staticmethod
    def check_short_entry(candle: Dict, indicators: Dict) -> str:
        """
        Проверка условий для входа в SHORT
        
        Args:
            candle: Данные последней свечи
            indicators: Рассчитанные индикаторы
            
        Returns:
            'Вход разрешен' или 'Вход запрещен: причина'
        """
        volume = candle['volume']
        avg_volume = indicators['avg_volume_20']
        close = candle['close']
        open_price = candle['open']
        ema_50 = indicators['ema_50']
        atr_14 = indicators['atr_14']
        
        # 1. Проверка объема (относительная)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio < 0.5:
            return f'Вход запрещен: объем слишком низкий (ratio: {volume_ratio:.2f})'
        
        if volume_ratio < 0.8:
            return f'Вход запрещен: объем недостаточный (ratio: {volume_ratio:.2f})'
        
        # 2. Проверка последней свечи (не большая зелёная)
        candle_size = abs(close - open_price)
        is_green = close > open_price
        is_large = candle_size > 1.5 * atr_14
        
        if is_green and is_large:
            return 'Вход запрещен: большая зелёная свеча'
        
        # 3. Подтверждение (текущая свеча закрылась вниз)
        if close >= open_price:
            return 'Вход запрещен: нет подтверждения (свеча не закрылась вниз)'
        
        # 4. Положение цены (расстояние от EMA50 ≤ 1 × ATR)
        distance_from_ema = abs(close - ema_50)
        if distance_from_ema > atr_14:
            return f'Вход запрещен: цена далеко от EMA50 (расстояние: {distance_from_ema:.2f}, ATR: {atr_14:.2f})'
        
        return 'Вход разрешен'
