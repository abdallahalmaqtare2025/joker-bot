# 🤖 Joker Trading Bot - 15M Signals (Webhook Ready)

نظام تداول آلي متكامل لزوج EUR/USD يحاكي نظام بوت "Joker Trading". يقوم النظام بتوليد الإشارات تلقائياً، أو استقبالها من **TradingView** عبر Webhook، مع تتبع النتائج تلقائياً وتحديث الإحصائيات.

## 🌟 المميزات الأساسية

1. **نظام توليد الإشارات (Signal Generation)**:
   - **تلقائي**: يعتمد على استراتيجية (BB + RSI + EMA) عبر مكتبة `yfinance`.
   - **عبر TradingView**: يستقبل تنبيهات فورية من أي استراتيجية تختارها عبر Webhook.
   
2. **نظام تعقب النتائج (Auto-Result Tracking)**:
   - تتبع تلقائي للسعر بعد 15 دقيقة من كل إشارة.
   - مقارنة سعر الدخول بسعر الإغلاق وتحديد النتيجة (WIN ✅ أو LOSS ❌).
   
3. **قاعدة البيانات والإحصائيات**:
   - تخزين كامل في SQLite مع تحديث يومي لنسبة النجاح (Win Rate).

## 🛠️ متطلبات التشغيل

- Python 3.10+
- المكتبات: `python-telegram-bot`, `yfinance`, `fastapi`, `uvicorn`, `ta`, `pytz`.

## 🚀 طريقة التثبيت والتشغيل

1. **تثبيت المكتبات**:
   ```bash
   pip install python-telegram-bot yfinance fastapi uvicorn pytz ta apscheduler
   ```

2. **إعداد البوت**:
   - ضع التوكن الخاص بك ومعرف القناة في `config.py`.

3. **تشغيل البوت**:
   ```bash
   python bot.py
   ```

## 🔗 ربط TradingView (Webhook)

البوت الآن يعمل كخادم ويب على المنفذ **8000**. لربط TradingView:

1. **عنوان Webhook**: استخدم عنوان IP الخاص بجهازك أو الخادم متبوعاً بـ `/webhook`.
   - مثال: `http://YOUR_IP:8000/webhook`
   - (ملاحظة: إذا كنت تعمل محلياً، ستحتاج لاستخدام أداة مثل **ngrok** لفتح المنفذ للإنترنت).

2. **رسالة التنبيه (Alert Message)**: في TradingView، اختر "Webhook URL" وضع الرابط، وفي خانة "Message" ضع الكود التالي:
   ```json
   {
     "symbol": "EURUSD",
     "signal": "CALL",
     "duration": "15"
   }
   ```
   *(قم بتغيير CALL إلى PUT حسب نوع التنبيه)*.

---
*تم تطوير هذا النظام بواسطة Manus AI*
