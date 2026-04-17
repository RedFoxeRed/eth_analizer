"""
Расчет точки входа, SL, TP и проверка сделки
"""
from typing import Dict, Optional, List


class TradeSetup:
    """Класс для расчета параметров сделки"""
    
    @staticmethod
    def calculate_long_setup(candles: List[Dict], indicators: Dict) -> Optional[Dict]:
        """
        Расчет параметров для LONG сделки
        
        Args:
            candles: Список свечей (последние 3+)
            indicators: Рассчитанные индикаторы
            
        Returns:
            Словарь с параметрами сделки или None если не прошла проверку
        """
        if len(candles) < 3:
            return None
        
        entry = candles[0]['close']
        atr_14 = indicators['atr_14']
        
        # SL = min(low последних 3 свечей) - буфер
        recent_lows = [candles[i]['low'] for i in range(3)]
        sl = min(recent_lows) - (0.1 * atr_14)
        
        # TP = Entry + (1.4 × ATR)
        tp = entry + (1.4 * atr_14)
        
        # Проверка RR
        risk = entry - sl
        reward = tp - entry
        rr = reward / risk if risk > 0 else 0
        
        if rr < 1.2:
            return {
                'valid': False,
                'reason': f'RR слишком низкий: {rr:.2f} < 1.2',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        # Проверка размера SL (не более 2% от цены)
        sl_percent = (risk / entry) * 100
        if sl_percent > 2.0:
            return {
                'valid': False,
                'reason': f'SL слишком большой: {sl_percent:.2f}% > 2%',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        # Проверка TP (не менее 0.4% от цены)
        tp_percent = (reward / entry) * 100
        if tp_percent < 0.4:
            return {
                'valid': False,
                'reason': f'TP слишком близкий: {tp_percent:.2f}% < 0.4%',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        return {
            'valid': True,
            'entry': round(entry, 2),
            'sl': round(sl, 2),
            'tp': round(tp, 2),
            'rr': round(rr, 2),
            'sl_percent': round(sl_percent, 2),
            'tp_percent': round(tp_percent, 2)
        }
    
    @staticmethod
    def calculate_short_setup(candles: List[Dict], indicators: Dict) -> Optional[Dict]:
        """
        Расчет параметров для SHORT сделки (зеркально)
        
        Args:
            candles: Список свечей (последние 3+)
            indicators: Рассчитанные индикаторы
            
        Returns:
            Словарь с параметрами сделки или None если не прошла проверку
        """
        if len(candles) < 3:
            return None
        
        entry = candles[0]['close']
        atr_14 = indicators['atr_14']
        
        # SL = Entry + (1 × ATR)
        sl = entry + atr_14
        
        # TP = Entry - (1.4 × ATR)
        tp = entry - (1.4 * atr_14)
        
        # Проверка RR
        risk = sl - entry
        reward = entry - tp
        rr = reward / risk if risk > 0 else 0
        
        if rr < 1.2:
            return {
                'valid': False,
                'reason': f'RR слишком низкий: {rr:.2f} < 1.2',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        # Проверка размера SL (не более 2% от цены)
        sl_percent = (risk / entry) * 100
        if sl_percent > 2.0:
            return {
                'valid': False,
                'reason': f'SL слишком большой: {sl_percent:.2f}% > 2%',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        # Проверка TP (не менее 0.4% от цены)
        tp_percent = (reward / entry) * 100
        if tp_percent < 0.4:
            return {
                'valid': False,
                'reason': f'TP слишком близкий: {tp_percent:.2f}% < 0.4%',
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'rr': round(rr, 2)
            }
        
        return {
            'valid': True,
            'entry': round(entry, 2),
            'sl': round(sl, 2),
            'tp': round(tp, 2),
            'rr': round(rr, 2),
            'sl_percent': round(sl_percent, 2),
            'tp_percent': round(tp_percent, 2)
        }
