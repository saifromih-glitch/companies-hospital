# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - Workshop
====================================
Manages: customers, repairs, spare parts, invoices.

The first institutional plugin built for Mohammed's workshop.
"""
import json
from datetime import datetime
from tools.mcp_connectors import SQLConnector, DBConfig


class WorkshopPlugin:
    """
    Enterprise Plugin for mechanical workshops.
    
    Tables:
        customers   - client information
        repairs     - repair jobs
        parts       - spare parts inventory
        invoices    - billing
    """
    
    def __init__(self, db_path: str = "workshop.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        """Create all tables if they don't exist"""
        self.db.create_table("customers", {
            "name": "TEXT NOT NULL",
            "phone": "TEXT",
            "vehicle": "TEXT",
            "notes": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("repairs", {
            "customer_id": "INTEGER REFERENCES customers(id)",
            "description": "TEXT NOT NULL",
            "type": "TEXT",  # hydraulic, mechanical, electrical
            "cost": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'pending'",  # pending, in_progress, done, delivered
            "started_at": "TEXT DEFAULT (datetime('now'))",
            "finished_at": "TEXT"
        })
        
        self.db.create_table("parts", {
            "name": "TEXT NOT NULL",
            "quantity": "INTEGER DEFAULT 1",
            "unit": "TEXT DEFAULT 'piece'",
            "cost_per_unit": "REAL DEFAULT 0",
            "supplier": "TEXT",
            "min_quantity": "INTEGER DEFAULT 5"
        })
        
        self.db.create_table("invoices", {
            "customer_id": "INTEGER REFERENCES customers(id)",
            "repair_id": "INTEGER REFERENCES repairs(id)",
            "total": "REAL DEFAULT 0",
            "paid": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'unpaid'",  # unpaid, partial, paid
            "notes": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
    
    # ═══ Customers ═══
    
    def add_customer(self, name: str, phone: str = "", vehicle: str = "", notes: str = "") -> dict:
        """Add a new customer"""
        return self.db.insert("customers", {
            "name": name, "phone": phone, "vehicle": vehicle, "notes": notes
        })
    
    def get_customers(self) -> list:
        """List all customers"""
        return self.db.query("SELECT * FROM customers ORDER BY id DESC LIMIT 50")
    
    def search_customer(self, query: str) -> list:
        """Search customers by name or phone"""
        return self.db.query(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY id DESC",
            (f"%{query}%", f"%{query}%")
        )
    
    # ═══ Repairs ═══
    
    def add_repair(self, customer_id: int, description: str, repair_type: str = "mechanical", cost: float = 0) -> dict:
        """Start a new repair job"""
        return self.db.insert("repairs", {
            "customer_id": customer_id, "description": description,
            "type": repair_type, "cost": cost
        })
    
    def get_repairs(self, status: str = None) -> list:
        """List repairs, optionally filtered by status"""
        if status:
            return self.db.query("""
                SELECT r.*, c.name as customer_name 
                FROM repairs r 
                JOIN customers c ON r.customer_id = c.id 
                WHERE r.status = ? 
                ORDER BY r.id DESC LIMIT 50
            """, (status,))
        return self.db.query("""
            SELECT r.*, c.name as customer_name 
            FROM repairs r 
            JOIN customers c ON r.customer_id = c.id 
            ORDER BY r.id DESC LIMIT 50
        """)
    
    def update_repair_status(self, repair_id: int, status: str) -> dict:
        """Update repair status (pending, in_progress, done, delivered)"""
        if status == "done":
            self.db.execute(
                "UPDATE repairs SET status = ?, finished_at = datetime('now') WHERE id = ?",
                (status, repair_id)
            )
        else:
            self.db.execute("UPDATE repairs SET status = ? WHERE id = ?", (status, repair_id))
        return {"ok": True, "repair_id": repair_id, "status": status}
    
    # ═══ Parts Inventory ═══
    
    def add_part(self, name: str, quantity: int = 1, cost: float = 0, supplier: str = "", min_qty: int = 5) -> dict:
        """Add spare part to inventory"""
        return self.db.insert("parts", {
            "name": name, "quantity": quantity, "cost_per_unit": cost,
            "supplier": supplier, "min_quantity": min_qty
        })
    
    def get_inventory(self) -> list:
        """List all parts in inventory"""
        return self.db.query("SELECT * FROM parts ORDER BY name")
    
    def check_low_stock(self) -> list:
        """Find parts below minimum quantity"""
        return self.db.query(
            "SELECT * FROM parts WHERE quantity <= min_quantity ORDER BY quantity ASC"
        )
    
    def update_stock(self, part_id: int, delta: int) -> dict:
        """Add or remove stock (delta can be negative)"""
        part = self.db.query("SELECT quantity FROM parts WHERE id = ?", (part_id,))
        if not part:
            return {"error": "Part not found"}
        new_qty = part[0]["quantity"] + delta
        self.db.execute("UPDATE parts SET quantity = ? WHERE id = ?", (new_qty, part_id))
        return {"ok": True, "part_id": part_id, "new_quantity": new_qty}
    
    # ═══ Invoices ═══
    
    def create_invoice(self, customer_id: int, repair_id: int, total: float, notes: str = "") -> dict:
        """Create a new invoice"""
        return self.db.insert("invoices", {
            "customer_id": customer_id, "repair_id": repair_id,
            "total": total, "notes": notes
        })
    
    def get_invoices(self, status: str = None) -> list:
        """List invoices"""
        if status:
            return self.db.query("""
                SELECT i.*, c.name as customer_name 
                FROM invoices i 
                JOIN customers c ON i.customer_id = c.id 
                WHERE i.status = ? 
                ORDER BY i.id DESC LIMIT 50
            """, (status,))
        return self.db.query("""
            SELECT i.*, c.name as customer_name 
            FROM invoices i 
            JOIN customers c ON i.customer_id = c.id 
            ORDER BY i.id DESC LIMIT 50
        """)
    
    def record_payment(self, invoice_id: int, amount: float) -> dict:
        """Record a payment on an invoice"""
        inv = self.db.query("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        if not inv:
            return {"error": "Invoice not found"}
        inv = inv[0]
        new_paid = inv["paid"] + amount
        new_status = "paid" if new_paid >= inv["total"] else "partial"
        self.db.execute(
            "UPDATE invoices SET paid = ?, status = ? WHERE id = ?",
            (new_paid, new_status, invoice_id)
        )
        return {"ok": True, "invoice_id": invoice_id, "paid": new_paid, "remaining": inv["total"] - new_paid}
    
    # ═══ Reports ═══
    
    def daily_report(self) -> dict:
        """Generate today's workshop report"""
        today = datetime.now().strftime("%Y-%m-%d")
        active_repairs = self.db.query("SELECT COUNT(*) as c FROM repairs WHERE status IN ('pending','in_progress')")
        completed_today = self.db.query(
            "SELECT COUNT(*) as c FROM repairs WHERE status = 'done' AND date(finished_at) = ?", (today,)
        )
        revenue_today = self.db.query("""
            SELECT COALESCE(SUM(total), 0) as total FROM invoices 
            WHERE date(created_at) = ?
        """, (today,))
        paid_today = self.db.query("""
            SELECT COALESCE(SUM(paid), 0) as total FROM invoices 
            WHERE date(created_at) = ?
        """, (today,))
        low_stock = self.check_low_stock()
        
        return {
            "date": today,
            "active_repairs": active_repairs[0]["c"] if active_repairs else 0,
            "completed_today": completed_today[0]["c"] if completed_today else 0,
            "revenue_today": revenue_today[0]["total"] if revenue_today else 0,
            "paid_today": paid_today[0]["total"] if paid_today else 0,
            "low_stock_items": len(low_stock),
            "low_stock_details": low_stock
        }
    
    def close(self):
        self.db.close()
