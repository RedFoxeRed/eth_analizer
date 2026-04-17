"""
Управление ордерами на Bybit
"""
from typing import Dict, Optional


class OrderManager:
    """Класс для управления ордерами"""
    
    def __init__(self, session):
        """
        Инициализация
        
        Args:
            session: HTTP сессия Bybit
        """
        self.session = session
        self.symbol = 'ETHUSDT'
        self.category = 'linear'  # USDT фьючерсы
    
    def set_leverage(self, leverage: int = 100) -> bool:
        """
        Установка кредитного плеча
        
        Args:
            leverage: Размер плеча (по умолчанию 100)
            
        Returns:
            True если успешно
        """
        try:
            response = self.session.set_leverage(
                category=self.category,
                symbol=self.symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            if response['retCode'] == 0:
                print(f"[OrderManager] Плечо установлено: {leverage}x")
                return True
            else:
                print(f"[OrderManager] Ошибка установки плеча: {response['retMsg']}")
                return False
                
        except Exception as e:
            print(f"[OrderManager] Исключение при установке плеча: {e}")
            return False
    
    def place_limit_order(self, side: str, entry: float, qty: float, 
                          sl: float, tp: float) -> Optional[Dict]:
        """
        Размещение лимитного ордера с SL/TP
        
        Args:
            side: 'Buy' (LONG) или 'Sell' (SHORT)
            entry: Цена входа
            qty: Количество контрактов
            sl: Stop-loss
            tp: Take-profit
            
        Returns:
            Информация об ордере или None
        """
        try:
            # Размещаем лимитный ордер СРАЗУ с SL/TP
            response = self.session.place_order(
                category=self.category,
                symbol=self.symbol,
                side=side,
                orderType="Limit",
                qty=str(qty),
                price=str(entry),
                timeInForce="GTC",
                tpslMode="Full",
                takeProfit=str(tp),
                stopLoss=str(sl),
                tpTriggerBy="LastPrice",
                slTriggerBy="LastPrice"
            )
            
            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                
                print(f"[OrderManager] ✅ Ордер размещен: {order_id}")
                print(f"  Side: {side}")
                print(f"  Entry: {entry}")
                print(f"  Qty: {qty}")
                print(f"  SL: {sl}")
                print(f"  TP: {tp}")
                
                order_info = {
                    'orderId': order_id,
                    'side': side,
                    'entry': entry,
                    'qty': qty,
                    'sl': sl,
                    'tp': tp
                }
                
                return order_info
            else:
                print(f"[OrderManager] ❌ Ошибка размещения ордера: {response['retMsg']}")
                return None
                
        except Exception as e:
            print(f"[OrderManager] Исключение при размещении ордера: {e}")
            return None
    
    def calculate_position_size(self, balance: float, entry: float, 
                                 leverage: int = 100, risk_percent: float = 1.0) -> float:
        """
        Расчет размера позиции в контрактах
        
        Args:
            balance: Доступный баланс
            entry: Цена входа
            leverage: Кредитное плечо
            risk_percent: Процент риска от баланса
            
        Returns:
            Количество контрактов
        """
        # Маржа = баланс * риск%
        margin = balance * (risk_percent / 100)
        
        # Размер позиции = маржа * плечо / цена входа
        position_value = margin * leverage
        qty = position_value / entry
        
        # Округляем до 3 знаков (ETHUSDT мин. шаг = 0.001)
        qty = round(qty, 3)
        
        # Минимальный размер для ETHUSDT = 0.1
        if qty < 0.1:
            print(f"[OrderManager] ⚠️  Размер позиции увеличен до минимума: 0.1 ETH")
            qty = 0.1
        
        return qty
    
    def has_open_position_or_order(self) -> dict:
        """
        Проверка наличия открытой позиции или активного ордера
        
        Returns:
            dict: {'position': bool, 'open_order': bool, 'order_id': str or None}
        """
        result = {
            'position': False,
            'open_order': False,
            'order_id': None
        }
        
        try:
            # Проверка открытых ордеров
            orders_response = self.session.get_open_orders(
                category=self.category,
                symbol=self.symbol
            )
            
            if orders_response['retCode'] == 0:
                open_orders = orders_response['result']['list']
                if len(open_orders) > 0:
                    result['open_order'] = True
                    result['order_id'] = open_orders[0]['orderId']
                    print(f"[OrderManager] ⚠️  Найден открытый ордер: {open_orders[0]['orderId']}")
            
            # Проверка открытой позиции
            position_response = self.session.get_positions(
                category=self.category,
                symbol=self.symbol
            )
            
            if position_response['retCode'] == 0:
                positions = position_response['result']['list']
                for pos in positions:
                    if float(pos.get('size', 0)) > 0:
                        side = "LONG" if pos['side'] == 'Buy' else "SHORT"
                        result['position'] = True
                        print(f"[OrderManager] ⚠️  Найдена открытая позиция {side}: {pos['size']} ETH")
            
            return result
                
        except Exception as e:
            print(f"[OrderManager] ⚠️  Ошибка проверки позиции: {e}")
            return {'position': True, 'open_order': False, 'order_id': None}  # Безопасность
    
    def cancel_open_order(self, order_id: str) -> bool:
        """
        Отмена открытого ордера
        
        Args:
            order_id: ID ордера для отмены
            
        Returns:
            True если успешно
        """
        try:
            response = self.session.cancel_order(
                category=self.category,
                symbol=self.symbol,
                orderId=order_id
            )
            
            if response['retCode'] == 0:
                print(f"[OrderManager] ✅ Ордер отменен: {order_id}")
                return True
            else:
                print(f"[OrderManager] ❌ Ошибка отмены ордера: {response['retMsg']}")
                return False
                
        except Exception as e:
            print(f"[OrderManager] Исключение при отмене ордера: {e}")
            return False
