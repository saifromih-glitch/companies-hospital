# -*- coding: utf-8 -*-
"""
Romih Agent - MCP Connectors
=============================
Connect Romih to enterprise data sources:
- SQL databases (Postgres, MySQL, SQLite)
- File systems
- REST APIs

Part of the Enterprise Plugin system.
"""
import os, json, sqlite3
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class DBConfig:
    """Database connection configuration"""
    db_type: str = "sqlite"  # sqlite, postgres, mysql
    host: str = ""
    port: int = 5432
    database: str = "romih.db"
    user: str = ""
    password: str = ""


class SQLConnector:
    """
    Universal SQL database connector.
    Supports SQLite (zero-config), PostgreSQL, MySQL.
    """
    
    def __init__(self, config: Optional[DBConfig] = None):
        self.config = config or DBConfig()
        self._conn = None
    
    def connect(self) -> bool:
        """Connect to the database"""
        try:
            if self.config.db_type == "sqlite":
                db_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "..",
                    self.config.database
                )
                self._conn = sqlite3.connect(db_path)
                self._conn.row_factory = sqlite3.Row
            elif self.config.db_type == "postgres":
                import psycopg2
                self._conn = psycopg2.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.user,
                    password=self.config.password
                )
            return True
        except Exception as e:
            print(f"DB connect error: {e}")
            return False
    
    def query(self, sql: str, params: tuple = ()) -> List[dict]:
        """Execute a SELECT query"""
        if not self._conn:
            if not self.connect():
                return [{"error": "Failed to connect"}]
        try:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    def execute(self, sql: str, params: tuple = ()) -> dict:
        """Execute INSERT/UPDATE/DELETE"""
        if not self._conn:
            if not self.connect():
                return {"error": "Failed to connect"}
        try:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            self._conn.commit()
            return {"ok": True, "affected": cur.rowcount, "last_id": cur.lastrowid}
        except Exception as e:
            return {"error": str(e)}
    
    def create_table(self, name: str, columns: dict) -> dict:
        """Create a table if not exists
        columns = {"name": "TEXT", "age": "INTEGER", "salary": "REAL"}
        """
        cols = ", ".join([f"{k} {v}" for k, v in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols})"
        return self.execute(sql)
    
    def insert(self, table: str, data: dict) -> dict:
        """Insert a row into a table"""
        keys = list(data.keys())
        values = [data[k] for k in keys]
        placeholders = ", ".join(["?" for _ in keys])
        sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES ({placeholders})"
        return self.execute(sql, tuple(values))
    
    def list_tables(self) -> List[str]:
        """List all tables"""
        if self.config.db_type == "sqlite":
            result = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        else:
            result = self.query("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return [list(r.values())[0] for r in result if isinstance(r, dict)]
    
    def close(self):
        if self._conn:
            self._conn.close()


class FileConnector:
    """File system connector - read/write files"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = os.path.abspath(base_path)
    
    def read(self, path: str) -> str:
        """Read file contents"""
        full_path = os.path.join(self.base_path, path)
        if not os.path.exists(full_path):
            return f"ERROR: File not found: {path}"
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()[:5000]
    
    def write(self, path: str, content: str) -> dict:
        """Write to file"""
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"ok": True, "path": path, "size": len(content)}
    
    def list(self, path: str = ".") -> List[str]:
        """List files in directory"""
        full_path = os.path.join(self.base_path, path)
        if not os.path.exists(full_path):
            return [f"ERROR: Directory not found: {path}"]
        return os.listdir(full_path)
    
    def search(self, path: str, pattern: str) -> List[str]:
        """Search for files matching pattern"""
        import glob
        results = []
        for f in glob.glob(os.path.join(self.base_path, path, pattern), recursive=True):
            results.append(os.path.relpath(f, self.base_path))
        return results


class APIConnector:
    """REST API connector"""
    
    def __init__(self, base_url: str = "", headers: dict = None):
        self.base_url = base_url
        self.headers = headers or {}
        import httpx
        self._client = httpx
    
    async def get(self, path: str = "/") -> dict:
        """GET request"""
        url = f"{self.base_url}{path}" if self.base_url else path
        async with self._client.AsyncClient(timeout=30) as c:
            r = await c.get(url, headers=self.headers)
            return {"status": r.status_code, "data": r.text[:2000]}
    
    async def post(self, path: str = "/", data: dict = None) -> dict:
        """POST request"""
        url = f"{self.base_url}{path}" if self.base_url else path
        async with self._client.AsyncClient(timeout=30) as c:
            r = await c.post(url, json=data or {}, headers=self.headers)
            return {"status": r.status_code, "data": r.text[:2000]}
