import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import logging
from database import get_pending_signals, update_signal_result, update_daily_stats

logger = logging.getLogger(__name__)

class ResultTracker:
    def __init__(self, symbol="EURUSD=X"):
        self.symbol = symbol
        
    def get_price_at_time(self, target_datetime_str):
        """Fetch the closing price at or near a specific datetime."""
        try:
            target_dt = datetime.fromisoformat(target_datetime_str)
            
            # Use UTC if not specified
            if target_dt.tzinfo is None:
                target_dt = target_dt.replace(tzinfo=timezone.utc)
            
            # Fetch 1m data around the target time
            start = target_dt - timedelta(minutes=5)
            end = target_dt + timedelta(minutes=10)
            
            data = yf.download(
                self.symbol,
                start=start.strftime("%Y-%m-%d %H:%M:%S"),
                end=end.strftime("%Y-%m-%d %H:%M:%S"),
                interval="1m",
                progress=False
            )
            
            if data.empty:
                return None
            
            # Flatten MultiIndex if necessary
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data.index = pd.to_datetime(data.index)
            # Find the candle closest to the target time
            after_target = data[data.index >= target_dt]
            
            if not after_target.empty:
                return float(after_target.iloc[0]['Close'])
            else:
                return float(data.iloc[-1]['Close'])
                
        except Exception as e:
            logger.error(f"Error fetching price at {target_datetime_str}: {e}")
            return None
    
    def get_current_price(self):
        """Get the current price of the symbol."""
        try:
            data = yf.download(self.symbol, period="1d", interval="1m", progress=False)
            if data.empty:
                return None
            
            # Flatten MultiIndex if necessary
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            return float(data.iloc[-1]['Close'])
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return None
    
    def check_and_resolve_pending(self):
        """Check all pending signals and resolve them if expired."""
        pending = get_pending_signals()
        resolved = []
        
        now = datetime.now(timezone.utc)
        
        for signal in pending:
            expiry_dt = datetime.fromisoformat(signal['expiry_datetime'])
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            
            # Check if the signal has expired (with 1 minute buffer)
            if now >= expiry_dt + timedelta(minutes=1):
                close_price = self.get_price_at_time(signal['expiry_datetime'])
                
                if close_price is None:
                    close_price = self.get_current_price()
                
                if close_price is None:
                    continue
                
                entry_price = float(signal['entry_price'])
                signal_type = signal['signal_type']
                
                # Determine result
                if signal_type == "CALL":
                    result = "WIN" if close_price > entry_price else "LOSS"
                else:
                    result = "WIN" if close_price < entry_price else "LOSS"
                
                update_signal_result(signal['id'], close_price, result)
                stats = update_daily_stats(signal['symbol'])
                
                resolved.append({
                    "id": signal['id'],
                    "symbol": signal['symbol'],
                    "signal_type": signal_type,
                    "entry_time": signal['entry_time'],
                    "entry_price": entry_price,
                    "close_price": close_price,
                    "result": result,
                    "stats": stats
                })
        
        return resolved

if __name__ == "__main__":
    tracker = ResultTracker()
    print(f"Current price: {tracker.get_current_price()}")
