import pandas as pd
import ta

class MultiTimeframeStrategy:
    def __init__(self, data_handler):
        self.data = data_handler
        
    def calculate_emas(self, df):
        """Calculate EMAs for a DataFrame"""
        df['EMA_Fast'] = ta.trend.ema_indicator(df['close'], window=Config.EMA_FAST)
        df['EMA_Slow'] = ta.trend.ema_indicator(df['close'], window=Config.EMA_SLOW)
        df['EMA_Signal'] = ta.trend.ema_indicator(df['close'], window=Config.EMA_SIGNAL)
        return df
        
    def get_h4_trend(self):
        """Determine long-term trend from H1 timeframe"""
        h1_df = self.data.get_historical_candles(granularity="H1", count=200)
        h1_df = self.calculate_emas(h1_df)
        
        # Last candle determines current trend
        last_row = h1_df.iloc[-1]
        if last_row['EMA_Fast'] > last_row['EMA_Slow']:
            return 'UPTREND'
        elif last_row['EMA_Fast'] < last_row['EMA_Slow']:
            return 'DOWNTREND'
        else:
            return 'NEUTRAL'
    
    def generate_signal(self):
        """Main signal generation function"""
        trend = self.get_h4_trend()
        
        if trend == 'NEUTRAL':
            return None
            
        # Get M5 data for entry timing
        m5_df = self.data.get_historical_candles(granularity="M5", count=100)
        m5_df = self.calculate_emas(m5_df)
        last_row = m5_df.iloc[-1]
        
        signal = None
        if trend == 'UPTREND':
            # Pullback to EMA20 and bullish close above it
            if (last_row['low'] <= last_row['EMA_Signal'] and 
                last_row['close'] > last_row['EMA_Signal']):
                signal = 'BUY'
                
        elif trend == 'DOWNTREND':
            # Rally to EMA20 and bearish close below it
            if (last_row['high'] >= last_row['EMA_Signal'] and 
                last_row['close'] < last_row['EMA_Signal']):
                signal = 'SELL'
                
        if signal:
            return {
                'signal': signal,
                'price': last_row['close'],
                'trend': trend,
                'timestamp': m5_df.index[-1]
            }
        return None
