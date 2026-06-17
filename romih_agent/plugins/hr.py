# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - HR & Payroll
========================================
Manages: employees, leaves, payroll, performance.

Second institutional plugin — high demand in Saudi market.
"""
from datetime import datetime, timedelta
from tools.mcp_connectors import SQLConnector, DBConfig


class HRPlugin:
    """
    Enterprise Plugin for HR management.
    
    Tables:
        employees     - staff records
        leaves        - leave requests
        payroll       - salary payments
        evaluations   - performance reviews
    """
    
    def __init__(self, db_path: str = "hr.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("employees", {
            "name": "TEXT NOT NULL",
            "phone": "TEXT",
            "email": "TEXT",
            "department": "TEXT",
            "position": "TEXT",
            "salary": "REAL DEFAULT 0",
            "hire_date": "TEXT DEFAULT (date('now'))",
            "status": "TEXT DEFAULT 'active'",  # active, inactive, terminated
            "id_number": "TEXT",
            "bank_account": "TEXT"
        })
        
        self.db.create_table("leaves", {
            "employee_id": "INTEGER REFERENCES employees(id)",
            "type": "TEXT DEFAULT 'annual'",  # annual, sick, emergency, unpaid
            "start_date": "TEXT NOT NULL",
            "end_date": "TEXT NOT NULL",
            "reason": "TEXT",
            "status": "TEXT DEFAULT 'pending'",  # pending, approved, rejected
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("payroll", {
            "employee_id": "INTEGER REFERENCES employees(id)",
            "month": "TEXT NOT NULL",  # YYYY-MM
            "basic_salary": "REAL DEFAULT 0",
            "overtime": "REAL DEFAULT 0",
            "bonus": "REAL DEFAULT 0",
            "deductions": "REAL DEFAULT 0",
            "net_salary": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'pending'",  # pending, paid
            "paid_at": "TEXT"
        })
        
        self.db.create_table("evaluations", {
            "employee_id": "INTEGER REFERENCES employees(id)",
            "period": "TEXT NOT NULL",  # YYYY-Q1, YYYY-Q2, etc.
            "score": "REAL DEFAULT 0",  # 0-100
            "strengths": "TEXT",
            "improvements": "TEXT",
            "reviewer": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
    
    # ═══ Employees ═══
    
    def add_employee(self, name: str, phone: str = "", email: str = "",
                     department: str = "", position: str = "", salary: float = 0,
                     id_number: str = "", bank_account: str = "") -> dict:
        return self.db.insert("employees", {
            "name": name, "phone": phone, "email": email,
            "department": department, "position": position,
            "salary": salary, "id_number": id_number, "bank_account": bank_account
        })
    
    def get_employees(self, department: str = None, status: str = "active") -> list:
        if department:
            return self.db.query(
                "SELECT * FROM employees WHERE department = ? AND status = ? ORDER BY name",
                (department, status)
            )
        return self.db.query(
            "SELECT * FROM employees WHERE status = ? ORDER BY name",
            (status,)
        )
    
    def search_employee(self, query: str) -> list:
        return self.db.query(
            "SELECT * FROM employees WHERE name LIKE ? OR phone LIKE ? OR department LIKE ? ORDER BY name",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
    
    def update_employee(self, emp_id: int, field: str, value) -> dict:
        valid = ["name", "phone", "email", "department", "position", "salary", "status"]
        if field not in valid:
            return {"error": f"Invalid field: {field}"}
        self.db.execute(f"UPDATE employees SET {field} = ? WHERE id = ?", (value, emp_id))
        return {"ok": True, "employee_id": emp_id, field: value}
    
    def count_by_department(self) -> list:
        return self.db.query(
            "SELECT department, COUNT(*) as count, SUM(salary) as total_salary FROM employees WHERE status='active' GROUP BY department"
        )
    
    # ═══ Leaves ═══
    
    def request_leave(self, employee_id: int, start_date: str, end_date: str,
                      leave_type: str = "annual", reason: str = "") -> dict:
        return self.db.insert("leaves", {
            "employee_id": employee_id, "type": leave_type,
            "start_date": start_date, "end_date": end_date, "reason": reason
        })
    
    def get_leaves(self, status: str = None, employee_id: int = None) -> list:
        if employee_id:
            return self.db.query("""
                SELECT l.*, e.name as employee_name FROM leaves l
                JOIN employees e ON l.employee_id = e.id
                WHERE l.employee_id = ? ORDER BY l.created_at DESC LIMIT 50
            """, (employee_id,))
        if status:
            return self.db.query("""
                SELECT l.*, e.name as employee_name FROM leaves l
                JOIN employees e ON l.employee_id = e.id
                WHERE l.status = ? ORDER BY l.created_at DESC LIMIT 50
            """, (status,))
        return self.db.query("""
            SELECT l.*, e.name as employee_name FROM leaves l
            JOIN employees e ON l.employee_id = e.id
            ORDER BY l.created_at DESC LIMIT 50
        """)
    
    def approve_leave(self, leave_id: int, approved: bool = True) -> dict:
        status = "approved" if approved else "rejected"
        self.db.execute("UPDATE leaves SET status = ? WHERE id = ?", (status, leave_id))
        return {"ok": True, "leave_id": leave_id, "status": status}
    
    def leave_balance(self, employee_id: int) -> dict:
        # Count used annual leave days this year
        year = datetime.now().year
        used = self.db.query("""
            SELECT COALESCE(SUM(julianday(end_date) - julianday(start_date) + 1), 0) as days
            FROM leaves WHERE employee_id = ? AND type = 'annual' AND status = 'approved'
            AND start_date >= ?
        """, (employee_id, f"{year}-01-01"))
        days_used = int(used[0]["days"]) if used else 0
        return {
            "employee_id": employee_id,
            "annual_allowance": 21,
            "used": days_used,
            "remaining": 21 - days_used
        }
    
    # ═══ Payroll ═══
    
    def generate_payroll(self, month: str = None) -> dict:
        """Generate payroll for all active employees for a given month"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        employees = self.get_employees(status="active")
        total = 0
        processed = 0
        
        for emp in employees:
            # Check if already processed
            existing = self.db.query(
                "SELECT id FROM payroll WHERE employee_id = ? AND month = ?",
                (emp["id"], month)
            )
            if existing:
                continue
            
            # Calculate
            basic = emp["salary"]
            net = basic  # Simplified: no overtime/bonus/deductions
            
            self.db.insert("payroll", {
                "employee_id": emp["id"], "month": month,
                "basic_salary": basic, "net_salary": net, "status": "pending"
            })
            total += net
            processed += 1
        
        return {
            "month": month,
            "employees_processed": processed,
            "total_payroll": total,
            "average_salary": round(total / processed, 2) if processed else 0
        }
    
    def get_payroll(self, month: str = None) -> list:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        return self.db.query("""
            SELECT p.*, e.name as employee_name, e.department
            FROM payroll p JOIN employees e ON p.employee_id = e.id
            WHERE p.month = ? ORDER BY e.department, e.name
        """, (month,))
    
    def mark_paid(self, payroll_id: int) -> dict:
        self.db.execute(
            "UPDATE payroll SET status = 'paid', paid_at = datetime('now') WHERE id = ?",
            (payroll_id,)
        )
        return {"ok": True, "payroll_id": payroll_id, "status": "paid"}
    
    def payroll_summary(self, month: str = None) -> dict:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        result = self.db.query("""
            SELECT COUNT(*) as count, SUM(net_salary) as total, 
                   SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) as paid_count
            FROM payroll WHERE month = ?
        """, (month,))
        r = result[0] if result else {"count": 0, "total": 0, "paid_count": 0}
        return {
            "month": month,
            "total_employees": r["count"],
            "total_payroll": r["total"] or 0,
            "paid": r["paid_count"],
            "pending": (r["count"] or 0) - (r["paid_count"] or 0)
        }
    
    # ═══ Evaluations ═══
    
    def add_evaluation(self, employee_id: int, period: str, score: float,
                       strengths: str = "", improvements: str = "", reviewer: str = "") -> dict:
        return self.db.insert("evaluations", {
            "employee_id": employee_id, "period": period, "score": score,
            "strengths": strengths, "improvements": improvements, "reviewer": reviewer
        })
    
    def get_evaluations(self, employee_id: int = None) -> list:
        if employee_id:
            return self.db.query("""
                SELECT ev.*, e.name as employee_name FROM evaluations ev
                JOIN employees e ON ev.employee_id = e.id
                WHERE ev.employee_id = ? ORDER BY ev.created_at DESC
            """, (employee_id,))
        return self.db.query("""
            SELECT ev.*, e.name as employee_name FROM evaluations ev
            JOIN employees e ON ev.employee_id = e.id
            ORDER BY ev.created_at DESC LIMIT 50
        """)
    
    def top_performers(self, limit: int = 5) -> list:
        return self.db.query("""
            SELECT e.name, e.department, e.position, AVG(ev.score) as avg_score
            FROM evaluations ev JOIN employees e ON ev.employee_id = e.id
            WHERE e.status = 'active'
            GROUP BY ev.employee_id
            ORDER BY avg_score DESC LIMIT ?
        """, (limit,))
    
    # ═══ Reports ═══
    
    def hr_report(self) -> dict:
        """Comprehensive HR report"""
        active = self.get_employees(status="active")
        departments = self.count_by_department()
        total_salary = sum(e["salary"] for e in active)
        
        # This month payroll
        month = datetime.now().strftime("%Y-%m")
        payroll = self.payroll_summary(month)
        
        # Pending leaves
        pending_leaves = self.get_leaves(status="pending")
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_employees": len(active),
            "departments": len(departments),
            "total_monthly_salary": total_salary,
            "avg_salary": round(total_salary / len(active), 2) if active else 0,
            "department_breakdown": departments,
            "payroll": payroll,
            "pending_leaves": len(pending_leaves),
            "pending_leave_details": pending_leaves[:5]
        }
    
    def close(self):
        self.db.close()
