"""
Message formatter for Joker Trading Bot
Formats signal and result messages to match the Joker Trading style.
"""

def format_signal_message(symbol, signal_type, entry_time, duration, wins, losses, pair_wins, pair_losses):
    """
    Format a signal message like the Joker Trading bot.
    
    Example output:
    》 JOKER 15 M 《
    
    🏁 EURUSD
    🟢 CALL
    🕐 05:45
    ⏳ 15 minutos
    
    Win: 4 | Loss: 1 (80%)
    Esse par: 4x1 (80%)
    """
    total = wins + losses
    win_rate = round((wins / total * 100), 0) if total > 0 else 0
    
    pair_total = pair_wins + pair_losses
    pair_win_rate = round((pair_wins / pair_total * 100), 0) if pair_total > 0 else 0
    
    # Signal type emoji
    if signal_type == "CALL":
        type_emoji = "🟢"
    else:
        type_emoji = "🔴"
    
    message = (
        f"》 JOKER 15 M 《\n\n"
        f"🏁 {symbol}\n"
        f"{type_emoji} {signal_type}\n"
        f"🕐 {entry_time}\n"
        f"⏳ {duration} minutos\n\n"
        f"Win: {wins} | Loss: {losses} ({int(win_rate)}%)\n"
        f"Esse par: {pair_wins}x{pair_losses} ({int(pair_win_rate)}%)"
    )
    
    return message

def format_result_message(symbol, entry_time, signal_type, result):
    """
    Format a result message like the Joker Trading bot.
    
    Example output for WIN:
    ✅ → EURUSD 05:45 ⬆️
    
    Example output for LOSS:
    ❌ → EURUSD 05:45 ⬇️
    """
    # Direction emoji based on signal type
    if signal_type == "CALL":
        direction_emoji = "⬆️"
    else:
        direction_emoji = "⬇️"
    
    # Result emoji
    if result == "WIN":
        result_emoji = "✅"
    else:
        result_emoji = "❌"
    
    message = f"{result_emoji} → {symbol} {entry_time} {direction_emoji}"
    
    return message

def format_stats_message(wins, losses, win_rate):
    """Format a standalone stats message."""
    return (
        f"📊 *إحصائيات اليوم*\n\n"
        f"✅ Win: {wins}\n"
        f"❌ Loss: {losses}\n"
        f"📈 Win Rate: {int(win_rate)}%"
    )

def format_startup_message(bot_name):
    """Format a startup message."""
    return (
        f"🤖 *{bot_name}* تم تشغيله بنجاح!\n\n"
        f"✅ نظام الإشارات: نشط\n"
        f"✅ تعقب النتائج: نشط\n"
        f"✅ قاعدة البيانات: متصلة\n\n"
        f"_سيبدأ البوت بإرسال إشارات EUR/USD تلقائياً_"
    )

def format_error_message(error_text):
    """Format an error message."""
    return f"⚠️ *خطأ في النظام*\n\n`{error_text}`"
