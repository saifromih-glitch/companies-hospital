# -*- coding: utf-8 -*-
"""
Multi-Tenant Database Layer
PostgreSQL on Railway with automatic user isolation.
"""
import os
from datetime import datetime

DB_URL = os.environ.get("DATABASE_URL", "")


def get_db():
    if DB_URL and "postgres" in DB_URL:
        import psycopg2
        conn = psycopg2.connect(DB_URL)
        return conn, "postgres"
    else:
        import sqlite3
        conn = sqlite3.connect("romih_data.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"


# Table definitions (id_type and ts_type filled dynamically)
TABLE_DEFS = {
    "workshop": [
        "workshop_customers(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, phone TEXT, car_model TEXT, car_plate TEXT, notes TEXT, created_at {ts_type})",
        "workshop_repairs(id {id_type}, user_id TEXT NOT NULL, customer_id INTEGER, description TEXT NOT NULL, status TEXT DEFAULT 'pending', cost REAL DEFAULT 0, created_at {ts_type})",
        "workshop_parts(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, quantity INTEGER DEFAULT 0, price REAL DEFAULT 0, created_at {ts_type})",
        "workshop_invoices(id {id_type}, user_id TEXT NOT NULL, customer_id INTEGER, total REAL DEFAULT 0, status TEXT DEFAULT 'unpaid', created_at {ts_type})",
    ],
    "hr": [
        "hr_employees(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, position TEXT, salary REAL DEFAULT 0, phone TEXT, joined_at DATE DEFAULT CURRENT_DATE)",
        "hr_leaves(id {id_type}, user_id TEXT NOT NULL, employee_id INTEGER, type TEXT DEFAULT 'annual', start_date DATE, end_date DATE, status TEXT DEFAULT 'pending')",
        "hr_payroll(id {id_type}, user_id TEXT NOT NULL, employee_id INTEGER, month TEXT, amount REAL, paid BOOLEAN DEFAULT FALSE)",
    ],
    "finance": [
        "finance_invoices(id {id_type}, user_id TEXT NOT NULL, number TEXT, client TEXT, amount REAL DEFAULT 0, status TEXT DEFAULT 'unpaid', created_at {ts_type})",
        "finance_expenses(id {id_type}, user_id TEXT NOT NULL, category TEXT, amount REAL, description TEXT, created_at {ts_type})",
    ],
    "projects": [
        "projects_list(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, description TEXT, status TEXT DEFAULT 'active', created_at {ts_type})",
        "project_tasks(id {id_type}, user_id TEXT NOT NULL, project_id INTEGER, title TEXT NOT NULL, status TEXT DEFAULT 'todo', assigned_to TEXT, created_at {ts_type})",
    ],
    "umrah": [
        "umrah_pilgrims(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, passport TEXT, nationality TEXT, package_id INTEGER, group_id INTEGER, status TEXT DEFAULT 'registered', created_at {ts_type})",
        "umrah_packages(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, type TEXT DEFAULT 'umrah', price REAL, duration_days INTEGER, available_seats INTEGER DEFAULT 50)",
        "umrah_groups(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, leader TEXT, pilgrim_count INTEGER DEFAULT 0, departure_date DATE)",
    ],
    "hotels": [
        "hotel_properties(id {id_type}, user_id TEXT NOT NULL, name TEXT NOT NULL, city TEXT, type TEXT DEFAULT 'hotel', total_rooms INTEGER DEFAULT 0, created_at {ts_type})",
        "hotel_rooms(id {id_type}, user_id TEXT NOT NULL, property_id INTEGER, number TEXT NOT NULL, type TEXT DEFAULT 'standard', price_per_night REAL, status TEXT DEFAULT 'available')",
        "hotel_bookings(id {id_type}, user_id TEXT NOT NULL, room_id INTEGER, guest_name TEXT, check_in DATE, check_out DATE, status TEXT DEFAULT 'confirmed', created_at {ts_type})",
    ],
}


class MultiTenantDB:
    def __init__(self, plugin_name: str):
        self.plugin = plugin_name
        self.conn, self.db_type = get_db()
        self.ph = "%s" if self.db_type == "postgres" else "?"
        self._init_tables()
    
    def _init_tables(self):
        cur = self.conn.cursor()
        id_type = "SERIAL PRIMARY KEY" if self.db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        ts_type = "TIMESTAMP DEFAULT NOW()" if self.db_type == "postgres" else "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        
        if self.plugin in TABLE_DEFS:
            for table_def in TABLE_DEFS[self.plugin]:
                sql = f"CREATE TABLE IF NOT EXISTS {table_def.format(id_type=id_type, ts_type=ts_type)}"
                try:
                    cur.execute(sql)
                except Exception as e:
                    pass
        self.conn.commit()
    
    def insert(self, table: str, data: dict) -> dict:
        data["user_id"] = data.get("user_id", "anonymous")
        cols = ", ".join(data.keys())
        placeholders = ", ".join([self.ph] * len(data))
        vals = list(data.values())
        cur = self.conn.cursor()
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        if self.db_type == "postgres":
            sql += " RETURNING id"
            cur.execute(sql, vals)
            row_id = cur.fetchone()[0]
        else:
            cur.execute(sql, vals)
            row_id = cur.lastrowid
        self.conn.commit()
        return {"ok": True, "id": row_id}
    
    def select(self, table: str, user_id: str, where: str = "",
               params: list = None, limit: int = 50) -> list:
        cur = self.conn.cursor()
        sql = f"SELECT * FROM {table} WHERE user_id = {self.ph}"
        vals = [user_id]
        if where:
            sql += f" AND {where}"
            if params:
                vals.extend(params)
        sql += f" ORDER BY id DESC LIMIT {limit}"
        cur.execute(sql, vals)
        if self.db_type == "postgres":
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            for k, v in r.items():
                if isinstance(v, datetime):
                    r[k] = v.isoformat()
        return rows
    
    def update(self, table: str, row_id: int, user_id: str, data: dict) -> dict:
        sets = ", ".join([f"{k} = {self.ph}" for k in data.keys()])
        vals = list(data.values()) + [row_id, user_id]
        cur = self.conn.cursor()
        cur.execute(f"UPDATE {table} SET {sets} WHERE id = {self.ph} AND user_id = {self.ph}", vals)
        self.conn.commit()
        return {"ok": True, "affected": cur.rowcount}
    
    def delete(self, table: str, row_id: int, user_id: str) -> dict:
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id = {self.ph} AND user_id = {self.ph}", [row_id, user_id])
        self.conn.commit()
        return {"ok": True, "affected": cur.rowcount}
    
    def count(self, table: str, user_id: str) -> int:
        cur = self.conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = {self.ph}", [user_id])
        return cur.fetchone()[0]
    
    def summary(self, user_id: str) -> dict:
        tables_data = {}
        if self.plugin in TABLE_DEFS:
            for table_def in TABLE_DEFS[self.plugin]:
                table_name = table_def.split('(')[0].strip()
                try:
                    tables_data[table_name] = self.count(table_name, user_id)
                except:
                    tables_data[table_name] = 0
        return {"plugin": self.plugin, "db_type": self.db_type, "tables": tables_data}
