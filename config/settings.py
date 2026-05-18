import os

class Config:
    # OANDA Connection
    OANDA_API_KEY = os.getenv("OANDA_API_KEY")
    OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
    OANDA_ENV = os.getenv("OANDA_ENV", "practice")
    INSTRUMENT = "XAU_USD"
    
    # Strategy Parameters
    EMA_FAST = 50      # Period for fast EMA (H1)
    EMA_SLOW = 200     # Period for slow EMA (H1)
    EMA_SIGNAL = 20    # Period for entry signal EMA (M5)
    RISK_PER_TRADE = 0.01  # 1% risk per trade
    
    # Risk Management
    MAX_DAILY_LOSS = 0.03  # 3% max daily drawdown
    MAX_POSITION_SIZE = 10000 # Units
    ATR_PERIOD = 14
    
    # Infrastructure
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    DB_CONNECTION = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/gold_trader")
