# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - Finance & Accounting
================================================
Manages: invoices, expenses, accounts, financial reports.

Third institutional plugin — essential for any business.
"""
from datetime import datetime
from tools.mcp_connectors import SQLConnector, DBConfig


class FinancePlugin:
    """
    Enterprise Plugin for financial management.
    
    Tables:
        invoices     - income invoices
        expenses     - outgoing expenses
        accounts     - chart of accounts
        transactions - ledger entries
    """
    
    def __init__(self, db_path: str = "finance.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("invoices", {
            "number": "TEXT NOT NULL",  # INV-001
            "client_name": "TEXT NOT NULL",
            "amount": "REAL DEFAULT 0",
            "tax": "REAL DEFAULT 0",  # VAT 15%
            "total": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'unpaid'",  # unpaid, partial, paid, cancelled
            "due_date": "TEXT",
            "notes": "TEXT",
            "issued_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("expenses", {
            "category": "TEXT NOT NULL",  # rent, utilities, supplies, salary, marketing, other
            "description": "TEXT NOT NULL",
            "amount": "REAL DEFAULT 0",
            "vendor": "TEXT",
            "payment_method": "TEXT DEFAULT 'cash'",  # cash, bank, card
            "receipt_number": "TEXT",
            "date": "TEXT DEFAULT (date('now'))",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("accounts", {
            "name": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'expense'",  # asset, liability, income, expense
            "balance": "REAL DEFAULT 0",
            "currency": "TEXT DEFAULT 'SAR'",
            "bank_name": "TEXT",
            "account_number": "TEXT",
            "notes": "TEXT"
        })
        
        self.db.create_table("transactions", {
            "account_id": "INTEGER REFERENCES accounts(id)",
            "type": "TEXT DEFAULT 'debit'",  # debit, credit
            "amount": "REAL DEFAULT 0",
            "description": "TEXT",
            "reference": "TEXT",  # invoice or expense ID
            "date": "TEXT DEFAULT (date('now'))",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
    
    # ═══ Invoices ═══
    
    def _next_invoice_number(self) -> str:
        result = self.db.query("SELECT COUNT(*) as c FROM invoices")
        count = (result[0]["c"] if result else 0) + 1
        return f"INV-{count:04d}"
    
    def create_invoice(self, client_name: str, amount: float, tax_rate: float = 15,
                       due_date: str = "", notes: str = "") -> dict:
        tax = round(amount * tax_rate / 100, 2)
        total = round(amount + tax, 2)
        number = self._next_invoice_number()
        return self.db.insert("invoices", {
            "number": number, "client_name": client_name,
            "amount": amount, "tax": tax, "total": total,
            "due_date": due_date, "notes": notes
        })
    
    def get_invoices(self, status: str = None) -> list:
        if status:
            return self.db.query(
                "SELECT * FROM invoices WHERE status = ? ORDER BY issued_at DESC LIMIT 50",
                (status,)
            )
        return self.db.query("SELECT * FROM invoices ORDER BY issued_at DESC LIMIT 50")
    
    def record_payment(self, invoice_id: int, amount: float) -> dict:
        inv = self.db.query("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        if not inv:
            return {"error": "Invoice not found"}
        inv = inv[0]
        # In a full system we'd track partial payments separately
        new_status = "paid" if amount >= inv["total"] else "partial"
        self.db.execute("UPDATE invoices SET status = ? WHERE id = ?", (new_status, invoice_id))
        return {"ok": True, "invoice_id": invoice_id, "paid": amount, "status": new_status}
    
    def outstanding_invoices(self) -> list:
        return self.db.query(
            "SELECT * FROM invoices WHERE status IN ('unpaid', 'partial') ORDER BY due_date"
        )
    
    # ═══ Expenses ═══
    
    def add_expense(self, category: str, description: str, amount: float,
                    vendor: str = "", payment_method: str = "cash") -> dict:
        return self.db.insert("expenses", {
            "category": category, "description": description,
            "amount": amount, "vendor": vendor, "payment_method": payment_method
        })
    
    def get_expenses(self, category: str = None, days: int = 30) -> list:
        if category:
            return self.db.query(
                "SELECT * FROM expenses WHERE category = ? AND date >= date('now', ?) ORDER BY date DESC",
                (category, f"-{days} days")
            )
        return self.db.query(
            "SELECT * FROM expenses WHERE date >= date('now', ?) ORDER BY date DESC LIMIT 50",
            (f"-{days} days",)
        )
    
    def expenses_by_category(self, days: int = 30) -> list:
        return self.db.query("""
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM expenses WHERE date >= date('now', ?)
            GROUP BY category ORDER BY total DESC
        """, (f"-{days} days",))
    
    # ═══ Accounts ═══
    
    def add_account(self, name: str, account_type: str = "expense",
                    balance: float = 0, bank_name: str = "") -> dict:
        return self.db.insert("accounts", {
            "name": name, "type": account_type, "balance": balance, "bank_name": bank_name
        })
    
    def get_accounts(self) -> list:
        return self.db.query("SELECT * FROM accounts ORDER BY name")
    
    def add_transaction(self, account_id: int, trans_type: str, amount: float,
                        description: str = "") -> dict:
        self.db.insert("transactions", {
            "account_id": account_id, "type": trans_type,
            "amount": amount, "description": description
        })
        # Update account balance
        delta = amount if trans_type == "credit" else -amount
        self.db.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (delta, account_id)
        )
        return {"ok": True, "account_id": account_id, "new_balance": "updated"}
    
    # ═══ Reports ═══
    
    def income_statement(self, days: int = 30) -> dict:
        """Profit & Loss summary"""
        # Revenue
        rev = self.db.query("""
            SELECT COALESCE(SUM(amount), 0) as total FROM invoices
            WHERE status != 'cancelled' AND date(issued_at) >= date('now', ?)
        """, (f"-{days} days",))
        revenue = rev[0]["total"] if rev else 0
        
        # Expenses
        exp = self.db.query("""
            SELECT COALESCE(SUM(amount), 0) as total FROM expenses
            WHERE date >= date('now', ?)
        """, (f"-{days} days",))
        expenses = exp[0]["total"] if exp else 0
        
        profit = revenue - expenses
        
        return {
            "period": f"Last {days} days",
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit,
            "margin": round((profit / revenue * 100), 1) if revenue > 0 else 0
        }
    
    def cash_flow(self) -> dict:
        """Current cash position"""
        # Unpaid invoices (money to receive)
        unpaid = self.db.query(
            "SELECT COALESCE(SUM(total), 0) as total FROM invoices WHERE status IN ('unpaid', 'partial')"
        )
        receivables = unpaid[0]["total"] if unpaid else 0
        
        # Available cash (bank accounts)
        bank = self.db.query(
            "SELECT COALESCE(SUM(balance), 0) as total FROM accounts"
        )
        cash = bank[0]["total"] if bank else 0
        
        return {
            "cash_available": cash,
            "receivables": receivables,
            "total": cash + receivables
        }
    
    def finance_report(self) -> dict:
        """Comprehensive financial report"""
        pnl = self.income_statement()
        cf = self.cash_flow()
        outstanding = self.outstanding_invoices()
        top_expenses = self.expenses_by_category()
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "income_statement": pnl,
            "cash_flow": cf,
            "outstanding_invoices": len(outstanding),
            "outstanding_amount": sum(inv["total"] for inv in outstanding),
            "top_expense_categories": top_expenses[:5]
        }
    
    def close(self):
        self.db.close()
