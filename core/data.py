import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments.candles as candles
import pandas as pd
import redis
from config.settings import Config

class OANDADataHandler:
    def __init__(self):
        self.api = oandapyV20.API(access_token=Config.OANDA_API_KEY,
                                  environment=Config.OANDA_ENV)
        self.redis_client = redis.Redis(host=Config.REDIS_HOST, port=6379, db=0)

    def stream_prices(self):
        """Stream real-time bid/ask prices for XAUUSD"""
        params = {"instruments": Config.INSTRUMENT}
        stream = pricing.PricingStream(accountID=Config.OANDA_ACCOUNT_ID, params=params)
        
        try:
            for tick in self.api.request(stream):
                if tick["type"] == "PRICE":
                    bid = float(tick["bids"][0]["price"])
                    ask = float(tick["asks"][0]["price"])
                    # Cache latest price in Redis with 5-second expiry
                    self.redis_client.setex("latest_price", 5, f"{bid},{ask}")
                    yield {"bid": bid, "ask": ask, "time": tick["time"]}
        except Exception as e:
            print(f"Streaming error: {e}")

    def get_historical_candles(self, granularity="H1", count=500):
        """Fetch historical candlestick data"""
        params = {
            "granularity": granularity,
            "count": count,
            "price": "M"  # Midpoint candles
        }
        r = candles.Candles(instrument=Config.INSTRUMENT, params=params)
        self.api.request(r)
        
        # Convert to DataFrame
        data = []
        for candle in r.response['candles']:
            if candle['complete']:
                data.append({
                    'time': pd.Timestamp(candle['time']),
                    'open': float(candle['mid']['o']),
                    'high': float(candle['mid']['h']),
                    'low': float(candle['mid']['l']),
                    'close': float(candle['mid']['c']),
                    'volume': candle['volume']
                })
        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        return df
