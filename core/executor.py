import oandapyV20
import oandapyV20.endpoints.orders as orders

class OrderExecutor:
    def __init__(self, api):
        self.api = api

    def place_market_order(self, signal, position_size):
        """Place a market order with stop-loss and take-profit"""
        if signal['signal'] == 'BUY':
            stop_loss = signal['price'] - (signal['atr'] * 1.5)
            take_profit = signal['price'] + (signal['atr'] * 3.0)
        else:  # SELL
            stop_loss = signal['price'] + (signal['atr'] * 1.5)
            take_profit = signal['price'] - (signal['atr'] * 3.0)
            
        order_data = {
            "order": {
                "type": "MARKET",
                "instrument": Config.INSTRUMENT,
                "units": str(position_size) if signal['signal'] == 'BUY' else str(-position_size),
                "stopLossOnFill": {
                    "price": str(round(stop_loss, 2))
                },
                "takeProfitOnFill": {
                    "price": str(round(take_profit, 2))
                }
            }
        }
        
        r = orders.OrderCreate(Config.OANDA_ACCOUNT_ID, data=order_data)
        response = self.api.request(r)
        print(f"Order placed: {response}")
        return response
