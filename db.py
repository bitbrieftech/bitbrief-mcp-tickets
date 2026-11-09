"""The ticket store: the system our MCP server puts in front of a model.

A demo store, built in memory from seed.sql each time the server starts.
Swap these functions for your real database or API; the server does not care.
"""

import sqlite3
import threading
from pathlib import Path

SEED = Path(__file__).parent / "seed.sql"

# Tools run on worker threads, so one connection is shared behind a lock.
_conn = sqlite3.connect(":memory:", check_same_thread=False)
_conn.row_factory = sqlite3.Row
_conn.executescript(SEED.read_text())
_lock = threading.Lock()


def search(query: str, status: str | None = None, limit: int = 10) -> list[dict]:
    """Tickets whose subject or body contains `query`, oldest first."""
    # Parameters, never string formatting: the query comes from a model.
    sql = "SELECT id, subject, status, priority, created_at FROM tickets WHERE (subject LIKE ? OR body LIKE ?)"
    params: list = [f"%{query}%", f"%{query}%"]
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY created_at LIMIT ?"
    params.append(limit)
    with _lock:
        return [dict(row) for row in _conn.execute(sql, params)]
