"""
Configuration file for Joker Trading Bot
Edit this file to configure your bot settings.
"""

# ============================================================
# TELEGRAM SETTINGS - REQUIRED
# ============================================================
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "8547784958:AAEJPryv_lKK3W9wvL4gfPjFAbkEmB3Bewc"

# Your Telegram Channel or Chat ID where signals will be sent
# For a channel: use @channel_username or numeric ID (e.g., -1001234567890)
# For a group: use numeric ID (e.g., -1001234567890)
# For a private chat: use your numeric user ID
TELEGRAM_CHAT_ID = "-1003815910109"

# ============================================================
# TRADING SETTINGS
# ============================================================
# Trading pair symbol for yfinance (Yahoo Finance format)
SYMBOL_YFINANCE = "EURUSD=X"

# Display name for the symbol in messages
SYMBOL_DISPLAY = "EURUSD"

# Timeframe for signal generation
TIMEFRAME = "5m"

# Trade duration in minutes
TRADE_DURATION = 15

# Timezone for displaying times (e.g., "UTC", "America/New_York", "Europe/London", "Asia/Riyadh")
TIMEZONE = "UTC"

# ============================================================
# INDICATOR SETTINGS
# ============================================================
# RSI Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# EMA Settings
EMA_PERIOD = 100

# Bollinger Bands Settings
BB_PERIOD = 20
BB_STD = 2.0

# ============================================================
# BOT BEHAVIOR SETTINGS
# ============================================================
# How often to check for new signals (in seconds)
SIGNAL_CHECK_INTERVAL = 60  # Check every 60 seconds

# How often to check for pending results (in seconds)
RESULT_CHECK_INTERVAL = 60  # Check every 60 seconds

# Minimum time between signals (in minutes) to avoid spam
MIN_SIGNAL_INTERVAL = 15

# ============================================================
# TRADING HOURS (UTC)
# ============================================================
# Set to True to enable trading hours restriction
ENABLE_TRADING_HOURS = True

# Trading hours in UTC (24-hour format)
TRADING_START_HOUR = 7   # 7:00 UTC (9:00 Cairo / 10:00 Riyadh)
TRADING_END_HOUR = 20    # 20:00 UTC (22:00 Cairo / 23:00 Riyadh)

# ============================================================
# BOT NAME (displayed in messages)
# ============================================================
BOT_NAME = "JOKER 15 M"
