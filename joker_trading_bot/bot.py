#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime, timedelta, timezone
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from database import init_db, save_signal, get_daily_stats, get_pair_stats
from signal_generator import SignalGenerator
from result_tracker import ResultTracker
from message_formatter import (
    format_signal_message,
    format_result_message,
    format_startup_message,
    format_stats_message
)

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "bot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# GLOBAL STATE
# ============================================================
last_signal_time = None
signal_generator = SignalGenerator(
    symbol=config.SYMBOL_YFINANCE,
    timeframe=config.TIMEFRAME,
    rsi_period=config.RSI_PERIOD,
    ema_period=config.EMA_PERIOD,
    bb_period=config.BB_PERIOD,
    bb_std=config.BB_STD
)
result_tracker = ResultTracker(symbol=config.SYMBOL_YFINANCE)
app = FastAPI()
telegram_application = None

# ============================================================
# WEBHOOK ENDPOINT (For TradingView)
# ============================================================

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    """Receive alerts from TradingView and send them to Telegram."""
    try:
        data = await request.json()
        logger.info(f"Received Webhook from TradingView: {data}")
        
        # Data format: {"symbol": "EURUSD", "signal": "CALL", "duration": "15"}
        symbol = data.get("symbol", config.SYMBOL_DISPLAY)
        signal_type = data.get("signal")
        duration = data.get("duration", str(config.TRADE_DURATION))
        
        if signal_type and telegram_application:
            await process_manual_signal(symbol, signal_type, duration)
            return {"status": "success", "message": "Signal processed"}
        
        return {"status": "error", "message": "Invalid signal data"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_manual_signal(symbol, signal_type, duration):
    """Process a signal received via Webhook."""
    try:
        now = datetime.now(timezone.utc)
        entry_time = now.strftime("%H:%M")
        expiry_dt = now + timedelta(minutes=int(duration))
        
        entry_price = result_tracker.get_current_price()
        if entry_price is None:
            logger.error("Could not get entry price for webhook signal.")
            return

        stats = get_daily_stats(symbol)
        pair_stats = get_pair_stats(symbol)
        
        save_signal(symbol, signal_type, entry_time, now, expiry_dt, entry_price)
        
        message = format_signal_message(
            symbol, signal_type, entry_time, duration,
            stats['wins'], stats['losses'], pair_stats['wins'], pair_stats['losses']
        )
        
        await telegram_application.bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as e:
        logger.error(f"Error in manual signal processing: {e}")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_trading_hours():
    if not config.ENABLE_TRADING_HOURS:
        return True
    now_utc = datetime.now(timezone.utc)
    return config.TRADING_START_HOUR <= now_utc.hour < config.TRADING_END_HOUR

async def send_message(bot: Bot, text: str, parse_mode: str = "Markdown"):
    try:
        await bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=text, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

async def check_and_send_signals(context: ContextTypes.DEFAULT_TYPE):
    global last_signal_time
    if not is_trading_hours(): return
    
    if last_signal_time:
        elapsed = (datetime.now(timezone.utc) - last_signal_time).total_seconds() / 60
        if elapsed < config.MIN_SIGNAL_INTERVAL: return
    
    try:
        signal = signal_generator.check_signals()
        if signal:
            entry_price = result_tracker.get_current_price()
            if entry_price is None: return
            
            entry_dt = signal['entry_datetime']
            expiry_dt = entry_dt + timedelta(minutes=config.TRADE_DURATION)
            
            stats = get_daily_stats(config.SYMBOL_DISPLAY)
            pair_stats = get_pair_stats(config.SYMBOL_DISPLAY)
            
            save_signal(config.SYMBOL_DISPLAY, signal['type'], signal['entry_time'], entry_dt, expiry_dt, entry_price)
            
            message = format_signal_message(
                config.SYMBOL_DISPLAY, signal['type'], signal['entry_time'], str(config.TRADE_DURATION),
                stats['wins'], stats['losses'], pair_stats['wins'], pair_stats['losses']
            )
            
            await send_message(context.bot, message, parse_mode=None)
            last_signal_time = datetime.now(timezone.utc)
    except Exception as e:
        logger.error(f"Error in signal check: {e}")

async def check_and_send_results(context: ContextTypes.DEFAULT_TYPE):
    try:
        resolved = result_tracker.check_and_resolve_pending()
        for signal in resolved:
            message = format_result_message(signal['symbol'], signal['entry_time'], signal['signal_type'], signal['result'])
            await send_message(context.bot, message, parse_mode=None)
    except Exception as e:
        logger.error(f"Error in result check: {e}")

# ============================================================
# TELEGRAM COMMAND HANDLERS
# ============================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 *Joker Trading Bot* نشط!")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_daily_stats(config.SYMBOL_DISPLAY)
    await update.message.reply_text(format_stats_message(stats['wins'], stats['losses'], stats['win_rate']), parse_mode="Markdown")

# ============================================================
# MAIN EXECUTION
# ============================================================

def run_fastapi():
    # Use dynamic port from environment variable for hosting platforms like Koyeb
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

async def main():
    global telegram_application
    init_db()
    
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    telegram_application = application
    
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("stats", cmd_stats))
    
    job_queue = application.job_queue
    job_queue.run_repeating(check_and_send_signals, interval=config.SIGNAL_CHECK_INTERVAL, first=10)
    job_queue.run_repeating(check_and_send_results, interval=config.RESULT_CHECK_INTERVAL, first=30)
    
    # Run FastAPI in a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()
    
    logger.info("Bot and Webhook server started!")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep the event loop running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
