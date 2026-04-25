from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


BACKEND_DIR = Path(__file__).resolve().parent
APP_DIR = BACKEND_DIR.parent
DATA_DIR = APP_DIR / "data"
DB_PATH = DATA_DIR / "utos.sqlite"
SCHEMA_PATH = BACKEND_DIR / "schema.sql"


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        from .seed import seed_database

        seed_database(conn)


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
