# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - Hotels & Real Estate
================================================
Manages: properties, rooms, bookings, maintenance, contracts.

For hotels, serviced apartments, and real estate in Saudi Arabia.
"""
from datetime import datetime, timedelta
from tools.mcp_connectors import SQLConnector, DBConfig


class HotelsPlugin:
    
    def __init__(self, db_path: str = "hotels.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("properties", {
            "name": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'hotel'",  # hotel, apartment, villa, camp
            "location": "TEXT",  # Makkah, Madinah, Jeddah, Riyadh
            "address": "TEXT",
            "total_rooms": "INTEGER DEFAULT 0",
            "stars": "INTEGER DEFAULT 3",
            "contact": "TEXT",
            "notes": "TEXT"
        })
        
        self.db.create_table("rooms", {
            "property_id": "INTEGER REFERENCES properties(id)",
            "number": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'standard'",  # standard, deluxe, suite, vip
            "floor": "INTEGER DEFAULT 0",
            "beds": "INTEGER DEFAULT 2",
            "price_per_night": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'available'",  # available, occupied, maintenance, reserved
            "notes": "TEXT"
        })
        
        self.db.create_table("bookings", {
            "room_id": "INTEGER REFERENCES rooms(id)",
            "guest_name": "TEXT NOT NULL",
            "guest_phone": "TEXT",
            "guest_id_number": "TEXT",
            "check_in": "TEXT NOT NULL",
            "check_out": "TEXT NOT NULL",
            "guests_count": "INTEGER DEFAULT 1",
            "total_price": "REAL DEFAULT 0",
            "paid": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'confirmed'",  # confirmed, checked_in, checked_out, cancelled
            "source": "TEXT DEFAULT 'direct'",  # direct, booking, agoda, umrah_package
            "notes": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("maintenance", {
            "room_id": "INTEGER REFERENCES rooms(id)",
            "property_id": "INTEGER REFERENCES properties(id)",
            "issue": "TEXT NOT NULL",
            "priority": "TEXT DEFAULT 'medium'",
            "status": "TEXT DEFAULT 'reported'",  # reported, in_progress, fixed
            "reported_by": "TEXT",
            "assigned_to": "TEXT",
            "cost": "REAL DEFAULT 0",
            "reported_at": "TEXT DEFAULT (datetime('now'))",
            "fixed_at": "TEXT"
        })
        
        self.db.create_table("contracts", {
            "property_id": "INTEGER REFERENCES properties(id)",
            "tenant_name": "TEXT NOT NULL",
            "tenant_phone": "TEXT",
            "type": "TEXT DEFAULT 'annual'",  # annual, monthly, seasonal
            "start_date": "TEXT NOT NULL",
            "end_date": "TEXT",
            "monthly_rent": "REAL DEFAULT 0",
            "deposit": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'active'",
            "notes": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
    
    # ═══ Properties ═══
    
    def add_property(self, name: str, prop_type: str = "hotel",
                     location: str = "Makkah", rooms: int = 0,
                     stars: int = 3) -> dict:
        return self.db.insert("properties", {
            "name": name, "type": prop_type, "location": location,
            "total_rooms": rooms, "stars": stars
        })
    
    def get_properties(self) -> list:
        return self.db.query("SELECT * FROM properties ORDER BY location, name")
    
    # ═══ Rooms ═══
    
    def add_room(self, property_id: int, number: str, room_type: str = "standard",
                 price: float = 0, beds: int = 2) -> dict:
        return self.db.insert("rooms", {
            "property_id": property_id, "number": number,
            "type": room_type, "price_per_night": price, "beds": beds
        })
    
    def get_rooms(self, property_id: int = None, status: str = None) -> list:
        if property_id and status:
            return self.db.query(
                "SELECT r.*, p.name as property_name FROM rooms r JOIN properties p ON r.property_id = p.id WHERE r.property_id = ? AND r.status = ? ORDER BY r.number",
                (property_id, status)
            )
        if property_id:
            return self.db.query(
                "SELECT r.*, p.name as property_name FROM rooms r JOIN properties p ON r.property_id = p.id WHERE r.property_id = ? ORDER BY r.number",
                (property_id,)
            )
        return self.db.query("""
            SELECT r.*, p.name as property_name FROM rooms r 
            JOIN properties p ON r.property_id = p.id ORDER BY p.name, r.number
        """)
    
    def check_availability(self, property_id: int, check_in: str, check_out: str) -> list:
        """Find available rooms for a date range"""
        return self.db.query("""
            SELECT r.*, p.name as property_name FROM rooms r
            JOIN properties p ON r.property_id = p.id
            WHERE r.property_id = ? 
            AND r.status = 'available'
            AND r.id NOT IN (
                SELECT room_id FROM bookings 
                WHERE status NOT IN ('cancelled', 'checked_out')
                AND check_in < ? AND check_out > ?
            )
            ORDER BY r.type, r.price_per_night
        """, (property_id, check_out, check_in))
    
    # ═══ Bookings ═══
    
    def book_room(self, room_id: int, guest_name: str, check_in: str, check_out: str,
                  guests: int = 1, phone: str = "", total: float = 0) -> dict:
        result = self.db.insert("bookings", {
            "room_id": room_id, "guest_name": guest_name,
            "check_in": check_in, "check_out": check_out,
            "guests_count": guests, "guest_phone": phone, "total_price": total
        })
        # Mark room as occupied
        if result.get("ok"):
            self.db.execute("UPDATE rooms SET status = 'reserved' WHERE id = ?", (room_id,))
        return result
    
    def get_bookings(self, status: str = None, date: str = None) -> list:
        if date:
            return self.db.query("""
                SELECT b.*, r.number as room_number, p.name as property_name
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN properties p ON r.property_id = p.id
                WHERE b.check_in <= ? AND b.check_out > ?
                ORDER BY b.check_in
            """, (date, date))
        if status:
            return self.db.query("""
                SELECT b.*, r.number as room_number, p.name as property_name
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN properties p ON r.property_id = p.id
                WHERE b.status = ? ORDER BY b.check_in DESC LIMIT 50
            """, (status,))
        return self.db.query("""
            SELECT b.*, r.number as room_number, p.name as property_name
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            JOIN properties p ON r.property_id = p.id
            ORDER BY b.check_in DESC LIMIT 50
        """)
    
    def check_in(self, booking_id: int) -> dict:
        bk = self.db.query("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        if not bk:
            return {"error": "Booking not found"}
        self.db.execute("UPDATE bookings SET status = 'checked_in' WHERE id = ?", (booking_id,))
        self.db.execute("UPDATE rooms SET status = 'occupied' WHERE id = ?", (bk[0]["room_id"],))
        return {"ok": True, "booking_id": booking_id}
    
    def check_out(self, booking_id: int) -> dict:
        bk = self.db.query("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        if not bk:
            return {"error": "Booking not found"}
        self.db.execute("UPDATE bookings SET status = 'checked_out' WHERE id = ?", (booking_id,))
        self.db.execute("UPDATE rooms SET status = 'available' WHERE id = ?", (bk[0]["room_id"],))
        return {"ok": True, "booking_id": booking_id}
    
    # ═══ Maintenance ═══
    
    def report_issue(self, issue: str, room_id: int = None,
                     property_id: int = None, priority: str = "medium") -> dict:
        return self.db.insert("maintenance", {
            "room_id": room_id, "property_id": property_id,
            "issue": issue, "priority": priority
        })
    
    def get_maintenance(self, status: str = None) -> list:
        if status:
            return self.db.query("""
                SELECT m.*, r.number as room_number, p.name as property_name
                FROM maintenance m
                LEFT JOIN rooms r ON m.room_id = r.id
                LEFT JOIN properties p ON m.property_id = p.id
                WHERE m.status = ? ORDER BY m.priority DESC, m.reported_at DESC
            """, (status,))
        return self.db.query("""
            SELECT m.*, r.number as room_number, p.name as property_name
            FROM maintenance m
            LEFT JOIN rooms r ON m.room_id = r.id
            LEFT JOIN properties p ON m.property_id = p.id
            ORDER BY m.status, m.priority DESC LIMIT 30
        """)
    
    def fix_issue(self, issue_id: int) -> dict:
        self.db.execute(
            "UPDATE maintenance SET status = 'fixed', fixed_at = datetime('now') WHERE id = ?",
            (issue_id,)
        )
        return {"ok": True, "issue_id": issue_id, "status": "fixed"}
    
    # ═══ Contracts ═══
    
    def add_contract(self, property_id: int, tenant: str, start_date: str,
                     rent: float = 0, contract_type: str = "annual",
                     phone: str = "", deposit: float = 0) -> dict:
        return self.db.insert("contracts", {
            "property_id": property_id, "tenant_name": tenant,
            "start_date": start_date, "type": contract_type,
            "monthly_rent": rent, "tenant_phone": phone, "deposit": deposit
        })
    
    def get_contracts(self, status: str = "active") -> list:
        return self.db.query("""
            SELECT c.*, p.name as property_name FROM contracts c
            JOIN properties p ON c.property_id = p.id
            WHERE c.status = ? ORDER BY c.start_date DESC
        """, (status,))
    
    # ═══ Reports ═══
    
    def occupancy_report(self) -> dict:
        total = self.db.query("SELECT COUNT(*) as c FROM rooms")
        occupied = self.db.query("SELECT COUNT(*) as c FROM rooms WHERE status IN ('occupied', 'reserved')")
        total_r = total[0]["c"] if total else 0
        occ_r = occupied[0]["c"] if occupied else 0
        
        return {
            "total_rooms": total_r,
            "occupied": occ_r,
            "available": total_r - occ_r,
            "occupancy_rate": round(occ_r / total_r * 100, 1) if total_r else 0
        }
    
    def revenue_report(self, days: int = 30) -> dict:
        rev = self.db.query("""
            SELECT COALESCE(SUM(total_price), 0) as total FROM bookings
            WHERE check_in >= date('now', ?) AND status NOT IN ('cancelled')
        """, (f"-{days} days",))
        paid = self.db.query("""
            SELECT COALESCE(SUM(paid), 0) as total FROM bookings
            WHERE check_in >= date('now', ?)
        """, (f"-{days} days",))
        return {
            "period": f"Last {days} days",
            "revenue": rev[0]["total"] if rev else 0,
            "collected": paid[0]["total"] if paid else 0,
            "outstanding": (rev[0]["total"] if rev else 0) - (paid[0]["total"] if paid else 0)
        }
    
    def hotels_report(self) -> dict:
        props = self.get_properties()
        occ = self.occupancy_report()
        rev = self.revenue_report()
        maint = self.get_maintenance(status="reported")
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "properties": len(props),
            "occupancy": occ,
            "revenue": rev,
            "open_maintenance": len(maint)
        }
    
    def close(self):
        self.db.close()
