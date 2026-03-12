import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta, timezone
import pytz

class SignalGenerator:
    def __init__(self, symbol="EURUSD=X", timeframe="5m", rsi_period=14, ema_period=100, bb_period=20, bb_std=2):
        self.symbol = symbol
        self.timeframe = timeframe
        self.rsi_period = rsi_period
        self.ema_period = ema_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        
    def get_data(self):
        """Fetch historical data from yfinance and ensure 1D format."""
        try:
            # Fetch last 2 days of data
            data = yf.download(self.symbol, period="2d", interval=self.timeframe, progress=False)
            
            if data.empty:
                return None
            
            # Critical Fix: In newer yfinance versions, data might be a MultiIndex DataFrame
            # if multiple tickers were requested or just by default.
            # We flatten it to ensure we have simple 'Close', 'Open', etc. columns.
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Ensure we are working with a clean copy to avoid SettingWithCopy warnings
            df = data.copy()
            
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def calculate_indicators(self, df):
        """Calculate technical indicators ensuring inputs are 1D series."""
        try:
            # Ensure 'Close' is a 1D Series even if yfinance returns it differently
            close_series = df['Close'].squeeze()
            high_series = df['High'].squeeze()
            low_series = df['Low'].squeeze()

            # Calculate EMA 100
            df['EMA_100'] = ta.trend.ema_indicator(close_series, window=self.ema_period)
            
            # Calculate RSI
            df['RSI'] = ta.momentum.rsi(close_series, window=self.rsi_period)
            
            # Calculate Bollinger Bands
            bb = ta.volatility.BollingerBands(close=close_series, window=self.bb_period, window_dev=self.bb_std)
            df['BB_High'] = bb.bollinger_hband()
            df['BB_Low'] = bb.bollinger_lband()
            
            return df
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return df

    def check_signals(self):
        """Check for entry signals on the latest completed candle."""
        df = self.get_data()
        if df is None or len(df) < self.ema_period + 5:
            return None
            
        df = self.calculate_indicators(df)
        
        # Get the latest completed candle (the one before the current live candle)
        # Squeeze to ensure we get a Series, then access by index
        current = df.iloc[-2]
        
        # Use scalar values for comparison to avoid dimension errors
        close_val = float(current['Close'])
        low_val = float(current['Low'])
        high_val = float(current['High'])
        ema_val = float(current['EMA_100'])
        bb_low_val = float(current['BB_Low'])
        bb_high_val = float(current['BB_High'])
        rsi_val = float(current['RSI'])
        
        signal = None
        
        # Call Signal (Buy) Condition:
        # Price below EMA 100 (Downtrend), Price touches/crosses BB Lower Band, RSI < 30 (Oversold)
        if close_val < ema_val and low_val <= bb_low_val and rsi_val < 30:
            signal = "CALL"
            
        # Put Signal (Sell) Condition:
        # Price above EMA 100 (Uptrend), Price touches/crosses BB Upper Band, RSI > 70 (Overbought)
        elif close_val > ema_val and high_val >= bb_high_val and rsi_val > 70:
            signal = "PUT"
            
        if signal:
            now = datetime.now(timezone.utc)
            # Round up to next 5 minutes for entry time display
            minutes = (now.minute // 5 + 1) * 5
            entry_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)
            
            return {
                "symbol": "EURUSD",
                "type": signal,
                "entry_time": entry_time.strftime("%H:%M"),
                "duration": "15",
                "entry_datetime": entry_time
            }
            
        return None

if __name__ == "__main__":
    generator = SignalGenerator()
    print(generator.check_signals())
