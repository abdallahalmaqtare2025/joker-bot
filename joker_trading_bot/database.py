import sqlite3
import os
from datetime import datetime, date
import pytz

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "signals.db")

def init_db():
    """Initialize the SQLite database and create tables if not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table to store signals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            entry_time TEXT NOT NULL,
            entry_datetime TEXT NOT NULL,
            expiry_datetime TEXT NOT NULL,
            entry_price REAL,
            close_price REAL,
            result TEXT DEFAULT 'PENDING',
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Table to store daily stats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            symbol TEXT NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0.0,
            updated_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at: {DB_PATH}")

def save_signal(symbol, signal_type, entry_time, entry_datetime, expiry_datetime, entry_price):
    """Save a new signal to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO signals (symbol, signal_type, entry_time, entry_datetime, expiry_datetime, entry_price, result, date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
    """, (symbol, signal_type, entry_time, entry_datetime.isoformat(), expiry_datetime.isoformat(), entry_price, today, now))
    
    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return signal_id

def update_signal_result(signal_id, close_price, result):
    """Update the result of a signal after expiry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE signals
        SET close_price = ?, result = ?
        WHERE id = ?
    """, (close_price, result, signal_id))
    
    conn.commit()
    conn.close()

def get_pending_signals():
    """Get all signals with PENDING result."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, symbol, signal_type, entry_time, entry_datetime, expiry_datetime, entry_price
        FROM signals
        WHERE result = 'PENDING'
        ORDER BY created_at ASC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    signals = []
    for row in rows:
        signals.append({
            "id": row[0],
            "symbol": row[1],
            "signal_type": row[2],
            "entry_time": row[3],
            "entry_datetime": row[4],
            "expiry_datetime": row[5],
            "entry_price": row[6]
        })
    return signals

def update_daily_stats(symbol, date_str=None):
    """Recalculate and update daily stats for a symbol."""
    if date_str is None:
        date_str = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count wins and losses for today
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses
        FROM signals
        WHERE date = ? AND symbol = ? AND result != 'PENDING'
    """, (date_str, symbol))
    
    row = cursor.fetchone()
    wins = row[0] or 0
    losses = row[1] or 0
    total = wins + losses
    win_rate = round((wins / total * 100), 0) if total > 0 else 0.0
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO daily_stats (date, symbol, wins, losses, win_rate, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            wins = excluded.wins,
            losses = excluded.losses,
            win_rate = excluded.win_rate,
            updated_at = excluded.updated_at
    """, (date_str, symbol, wins, losses, win_rate, now))
    
    conn.commit()
    conn.close()
    
    return {"wins": wins, "losses": losses, "win_rate": win_rate}

def get_daily_stats(symbol, date_str=None):
    """Get daily stats for a symbol."""
    if date_str is None:
        date_str = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT wins, losses, win_rate
        FROM daily_stats
        WHERE date = ? AND symbol = ?
    """, (date_str, symbol))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"wins": row[0], "losses": row[1], "win_rate": row[2]}
    return {"wins": 0, "losses": 0, "win_rate": 0.0}

def get_pair_stats(symbol, date_str=None):
    """Get per-pair stats (e.g., 'Esse par: 4x1 (80%)')."""
    if date_str is None:
        date_str = date.today().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses
        FROM signals
        WHERE date = ? AND symbol = ? AND result != 'PENDING'
    """, (date_str, symbol))
    
    row = cursor.fetchone()
    conn.close()
    
    wins = row[0] or 0
    losses = row[1] or 0
    total = wins + losses
    win_rate = round((wins / total * 100), 0) if total > 0 else 0.0
    
    return {"wins": wins, "losses": losses, "win_rate": win_rate}

if __name__ == "__main__":
    init_db()
    print("[DB] Tables created successfully.")
