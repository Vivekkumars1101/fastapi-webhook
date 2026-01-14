import sqlite3
from datetime import datetime
from .config import settings

def get_db():
    path = settings.DATABASE_URL.replace("sqlite:////", "/")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn TEXT NOT NULL,
            ts TEXT NOT NULL,
            text TEXT,
            created_at TEXT NOT NULL
        )
    """) # [cite: 190]
    conn.commit()
    conn.close()

def save_message(m_id, from_m, to_m, ts, text):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO messages (message_id, from_msisdn, to_msisdn, ts, text, created_at) VALUES (?,?,?,?,?,?)",
            (m_id, from_m, to_m, ts, text, datetime.utcnow().isoformat() + "Z")
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate" # Graceful idempotency handling [cite: 58, 176]
    finally:
        conn.close()

def get_messages(limit: int, offset: int, from_msisdn: str = None, since: str = None, query: str = None):
    conn = get_db()
    base_sql = "FROM messages WHERE 1=1"
    params = []

    if from_msisdn:
        base_sql += " AND from_msisdn = ?"
        params.append(from_msisdn)
    if since:
        base_sql += " AND ts >= ?"
        params.append(since)
    if query:
        base_sql += " AND text LIKE ?"
        params.append(f"%{query}%")

    # Get total count for metadata
    total = conn.execute(f"SELECT COUNT(*) {base_sql}", params).fetchone()[0]

    # Get paginated results
    data_sql = f"SELECT message_id, from_msisdn as 'from', to_msisdn as 'to', ts, text {base_sql} ORDER BY ts ASC, message_id ASC LIMIT ? OFFSET ?"
    rows = conn.execute(data_sql, params + [limit, offset]).fetchall()
    conn.close()
    
    return [dict(r) for r in rows], total

def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders = conn.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages").fetchone()[0]
    
    per_sender = conn.execute("""
        SELECT from_msisdn as 'from', COUNT(*) as count 
        FROM messages GROUP BY from_msisdn 
        ORDER BY count DESC LIMIT 10
    """).fetchall()

    ts_range = conn.execute("SELECT MIN(ts), MAX(ts) FROM messages").fetchone()
    conn.close()

    return {
        "total_messages": total,
        "senders_count": senders,
        "messages_per_sender": [dict(r) for r in per_sender],
        "first_message_ts": ts_range[0] if ts_range else None,
        "last_message_ts": ts_range[1] if ts_range else None
    }
