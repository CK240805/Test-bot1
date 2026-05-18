import numpy as np
from config.settings import Config

class RiskManager:
    def __init__(self, portfolio_manager):
        self.portfolio = portfolio_manager
        
    def calculate_position_size(self, signal, current_price):
        """Dynamic position sizing using ATR"""
        # Get recent H1 data for ATR calculation
        h1_df = self.data.get_historical_candles(granularity="H1", count=20)
        atr = self.calculate_atr(h1_df)
        
        # Get current account balance
        balance = self.portfolio.get_balance()
        
        # Risk per trade (1% of balance)
        risk_amount = balance * Config.RISK_PER_TRADE
        
        # Stop loss distance: 1.5x ATR
        stop_distance = atr * 1.5
        
        # Position size = Risk Amount / Stop Distance
        position_size = int(risk_amount / stop_distance)
        
        # Apply position limits
        max_position = Config.MAX_POSITION_SIZE
        return min(position_size, max_position)
    
    def calculate_atr(self, df):
        """Simple ATR calculation"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(Config.ATR_PERIOD).mean().iloc[-1]
    
    def check_drawdown_limits(self):
        """Check daily loss limits"""
        daily_pnl = self.portfolio.get_daily_pnl()
        balance = self.portfolio.get_balance()
        
        if abs(daily_pnl) / balance >= Config.MAX_DAILY_LOSS:
            print("WARNING: Daily loss limit reached. Halting trading.")
            return False
        return True
