from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
LOCAL_DB = BASE_DIR / "database" / "classroom.db"


def _postgres_enabled() -> bool:
    return bool(os.getenv("DATABASE_URL"))


class Database:
    def backend_name(self) -> str:
        return "postgresql" if _postgres_enabled() else "sqlite-local"

    def _sqlite(self):
        LOCAL_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(LOCAL_DB)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """CREATE TABLE IF NOT EXISTS attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                classroom TEXT NOT NULL,
                students INTEGER NOT NULL,
                attendance REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()
        return conn

    def save_attendance(self, classroom: str, students: int, attendance: float) -> None:
        if _postgres_enabled():
            import psycopg
            with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO attendance (classroom, students, attendance) VALUES (%s, %s, %s)",
                        (classroom, students, attendance),
                    )
                conn.commit()
            return

        with self._sqlite() as conn:
            conn.execute(
                "INSERT INTO attendance (classroom, students, attendance) VALUES (?, ?, ?)",
                (classroom, students, attendance),
            )
            conn.commit()

    def recent_attendance(self, limit: int = 50) -> list[dict[str, Any]]:
        if _postgres_enabled():
            import psycopg
            with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT classroom, students, attendance, created_at FROM attendance ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                    rows = cur.fetchall()
                    return [
                        {"classroom": r[0], "students": r[1], "attendance": r[2], "created_at": str(r[3])}
                        for r in rows
                    ]

        with self._sqlite() as conn:
            rows = conn.execute(
                "SELECT classroom, students, attendance, created_at FROM attendance ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]


db = Database()
