from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .policy import absolute_path, check_no_links


class Journal:
    def __init__(self, path: str | Path):
        path = absolute_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        check_no_links(path)
        self.connection = sqlite3.connect(path)
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                request_json TEXT NOT NULL,
                result_json TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                details_json TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(task_id)
            );
        """)
        self.connection.execute("PRAGMA foreign_keys = ON")

    def create(self, task_id: str, request: dict) -> None:
        with self.connection:
            self.connection.execute("INSERT INTO tasks VALUES (?, ?, ?, NULL)",
                                    (task_id, "RECEIVED", json.dumps(request)))
        self.record(task_id, "RECEIVED", {})

    def record(self, task_id: str, status: str, details: dict) -> None:
        with self.connection:
            self.connection.execute("UPDATE tasks SET status=? WHERE task_id=?", (status, task_id))
            self.connection.execute("INSERT INTO events(task_id,created_at,status,details_json) VALUES(?,?,?,?)",
                                    (task_id, datetime.now(timezone.utc).isoformat(), status, json.dumps(details)))

    def finish(self, task_id: str, result: dict) -> None:
        with self.connection:
            self.connection.execute("UPDATE tasks SET result_json=? WHERE task_id=?", (json.dumps(result), task_id))
        self.record(task_id, "SUCCEEDED", {"report_sha256": result["report_sha256"]})

    def close(self) -> None:
        self.connection.close()
