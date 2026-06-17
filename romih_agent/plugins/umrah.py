# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - Umrah & Hajj
========================================
Manages: packages, pilgrims, groups, catering, transport.

The KEY plugin for Saudi market — billions in revenue.
"""
from datetime import datetime, timedelta
from tools.mcp_connectors import SQLConnector, DBConfig


class UmrahPlugin:
    """Enterprise Plugin for Umrah & Hajj operations."""
    
    def __init__(self, db_path: str = "umrah.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        # Umrah packages
        self.db.create_table("packages", {
            "name": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'umrah'",  # umrah, hajj, ziyara
            "duration_days": "INTEGER DEFAULT 7",
            "price": "REAL DEFAULT 0",
            "currency": "TEXT DEFAULT 'SAR'",
            "includes": "TEXT",  # JSON: hotel, transport, meals, visa
            "seats_total": "INTEGER DEFAULT 0",
            "seats_booked": "INTEGER DEFAULT 0",
            "status": "TEXT DEFAULT 'active'",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        # Pilgrims
        self.db.create_table("pilgrims", {
            "name": "TEXT NOT NULL",
            "passport": "TEXT",
            "nationality": "TEXT",
            "phone": "TEXT",
            "dob": "TEXT",
            "gender": "TEXT DEFAULT 'male'",
            "mahram": "TEXT",  # for female pilgrims
            "package_id": "INTEGER REFERENCES packages(id)",
            "group_id": "INTEGER REFERENCES groups(id)",
            "status": "TEXT DEFAULT 'pending'",  # pending, confirmed, arrived, completed
            "visa_number": "TEXT",
            "visa_issued": "TEXT",
            "arrival_date": "TEXT",
            "departure_date": "TEXT",
            "notes": "TEXT",
            "registered_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        # Groups
        self.db.create_table("groups", {
            "name": "TEXT NOT NULL",
            "package_id": "INTEGER REFERENCES packages(id)",
            "leader": "TEXT",
            "size": "INTEGER DEFAULT 0",
            "max_size": "INTEGER DEFAULT 50",
            "status": "TEXT DEFAULT 'forming'",  # forming, confirmed, in_makkah, completed
            "hotel_id": "INTEGER",
            "transport_id": "INTEGER",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        # Catering/Accommodation
        self.db.create_table("accommodation", {
            "name": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'hotel'",  # hotel, apartment, camp
            "location": "TEXT",  # Makkah, Madinah, Mina, Arafat
            "rooms_total": "INTEGER DEFAULT 0",
            "rooms_booked": "INTEGER DEFAULT 0",
            "price_per_night": "REAL DEFAULT 0",
            "contact": "TEXT",
            "notes": "TEXT"
        })
        
        self.db.create_table("meals", {
            "group_id": "INTEGER REFERENCES groups(id)",
            "date": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'lunch'",  # breakfast, lunch, dinner, suhoor, iftar
            "menu": "TEXT",
            "count": "INTEGER DEFAULT 0",
            "served": "INTEGER DEFAULT 0",
            "status": "TEXT DEFAULT 'planned'"
        })
        
        # Transport
        self.db.create_table("transport", {
            "name": "TEXT NOT NULL",
            "type": "TEXT DEFAULT 'bus'",  # bus, van, car
            "plate_number": "TEXT",
            "capacity": "INTEGER DEFAULT 0",
            "driver_name": "TEXT",
            "driver_phone": "TEXT",
            "status": "TEXT DEFAULT 'available'",
            "current_location": "TEXT"
        })
        
        self.db.create_table("trips", {
            "transport_id": "INTEGER REFERENCES transport(id)",
            "group_id": "INTEGER REFERENCES groups(id)",
            "from_location": "TEXT",
            "to_location": "TEXT",
            "departure": "TEXT",
            "estimated_arrival": "TEXT",
            "passenger_count": "INTEGER DEFAULT 0",
            "status": "TEXT DEFAULT 'scheduled'",  # scheduled, in_transit, arrived
            "driver_notes": "TEXT"
        })
    
    # ═══ Packages ═══
    
    def add_package(self, name: str, package_type: str = "umrah",
                    duration: int = 7, price: float = 0, seats: int = 0) -> dict:
        return self.db.insert("packages", {
            "name": name, "type": package_type,
            "duration_days": duration, "price": price, "seats_total": seats
        })
    
    def get_packages(self) -> list:
        return self.db.query("SELECT * FROM packages WHERE status = 'active' ORDER BY name")
    
    def package_stats(self, package_id: int) -> dict:
        pkg = self.db.query("SELECT * FROM packages WHERE id = ?", (package_id,))
        if not pkg:
            return {"error": "Package not found"}
        pkg = pkg[0]
        pilgrims = self.db.query(
            "SELECT COUNT(*) as c FROM pilgrims WHERE package_id = ? AND status != 'cancelled'",
            (package_id,)
        )
        return {
            "package": pkg,
            "pilgrims_registered": pilgrims[0]["c"] if pilgrims else 0,
            "available_seats": pkg["seats_total"] - pkg["seats_booked"],
            "occupancy": round(pkg["seats_booked"] / pkg["seats_total"] * 100, 1) if pkg["seats_total"] else 0
        }
    
    # ═══ Pilgrims ═══
    
    def register_pilgrim(self, name: str, passport: str = "", nationality: str = "",
                         package_id: int = None, phone: str = "",
                         gender: str = "male", mahram: str = "",
                         arrival: str = "", departure: str = "") -> dict:
        return self.db.insert("pilgrims", {
            "name": name, "passport": passport, "nationality": nationality,
            "package_id": package_id, "phone": phone,
            "gender": gender, "mahram": mahram,
            "arrival_date": arrival, "departure_date": departure
        })
    
    def get_pilgrims(self, package_id: int = None, group_id: int = None,
                     status: str = None) -> list:
        conditions = []
        params = []
        if package_id:
            conditions.append("p.package_id = ?")
            params.append(package_id)
        if group_id:
            conditions.append("p.group_id = ?")
            params.append(group_id)
        if status:
            conditions.append("p.status = ?")
            params.append(status)
        
        where = " AND ".join(conditions) if conditions else "1=1"
        return self.db.query(f"""
            SELECT p.*, pk.name as package_name FROM pilgrims p
            LEFT JOIN packages pk ON p.package_id = pk.id
            WHERE {where} ORDER BY p.name LIMIT 200
        """, tuple(params))
    
    def update_pilgrim_status(self, pilgrim_id: int, status: str,
                              visa_number: str = "") -> dict:
        if visa_number:
            self.db.execute(
                "UPDATE pilgrims SET status = ?, visa_number = ?, visa_issued = date('now') WHERE id = ?",
                (status, visa_number, pilgrim_id)
            )
        else:
            self.db.execute("UPDATE pilgrims SET status = ? WHERE id = ?", (status, pilgrim_id))
        return {"ok": True, "pilgrim_id": pilgrim_id, "status": status}
    
    def search_pilgrim(self, query: str) -> list:
        return self.db.query(
            "SELECT * FROM pilgrims WHERE name LIKE ? OR passport LIKE ? OR phone LIKE ? ORDER BY name",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
    
    # ═══ Groups ═══
    
    def create_group(self, name: str, package_id: int = None,
                     leader: str = "", max_size: int = 50) -> dict:
        return self.db.insert("groups", {
            "name": name, "package_id": package_id, "leader": leader, "max_size": max_size
        })
    
    def get_groups(self) -> list:
        return self.db.query("""
            SELECT g.*, pk.name as package_name FROM groups g
            LEFT JOIN packages pk ON g.package_id = pk.id
            ORDER BY g.created_at DESC
        """)
    
    def assign_to_group(self, pilgrim_id: int, group_id: int) -> dict:
        self.db.execute("UPDATE pilgrims SET group_id = ? WHERE id = ?", (group_id, pilgrim_id))
        # Update group size
        count = self.db.query("SELECT COUNT(*) as c FROM pilgrims WHERE group_id = ?", (group_id,))
        self.db.execute("UPDATE groups SET size = ? WHERE id = ?",
                       (count[0]["c"] if count else 0, group_id))
        return {"ok": True, "pilgrim_id": pilgrim_id, "group_id": group_id}
    
    def group_details(self, group_id: int) -> dict:
        group = self.db.query("SELECT * FROM groups WHERE id = ?", (group_id,))
        if not group:
            return {"error": "Group not found"}
        pilgrims = self.get_pilgrims(group_id=group_id)
        trips = self.db.query("""
            SELECT t.*, tr.name as transport_name FROM trips t
            JOIN transport tr ON t.transport_id = tr.id
            WHERE t.group_id = ? ORDER BY t.departure
        """, (group_id,))
        return {
            "group": group[0],
            "pilgrims": len(pilgrims),
            "pilgrim_list": pilgrims[:20],
            "trips": len(trips),
            "trip_list": trips[:10]
        }
    
    # ═══ Meals & Accommodation ═══
    
    def add_meal_plan(self, group_id: int, date: str, meal_type: str,
                      menu: str = "", count: int = 0) -> dict:
        return self.db.insert("meals", {
            "group_id": group_id, "date": date, "type": meal_type,
            "menu": menu, "count": count
        })
    
    def get_meals(self, group_id: int = None, date: str = None) -> list:
        if group_id and date:
            return self.db.query(
                "SELECT * FROM meals WHERE group_id = ? AND date = ? ORDER BY type",
                (group_id, date)
            )
        if group_id:
            return self.db.query(
                "SELECT * FROM meals WHERE group_id = ? ORDER BY date DESC, type",
                (group_id,)
            )
        return self.db.query("SELECT * FROM meals ORDER BY date DESC LIMIT 50")
    
    def add_accommodation(self, name: str, acc_type: str = "hotel",
                          location: str = "Makkah", rooms: int = 0,
                          price: float = 0) -> dict:
        return self.db.insert("accommodation", {
            "name": name, "type": acc_type, "location": location,
            "rooms_total": rooms, "price_per_night": price
        })
    
    def get_accommodations(self) -> list:
        return self.db.query("SELECT * FROM accommodation ORDER BY location, name")
    
    # ═══ Transport ═══
    
    def add_transport(self, name: str, vehicle_type: str = "bus",
                      plate: str = "", capacity: int = 0,
                      driver: str = "", driver_phone: str = "") -> dict:
        return self.db.insert("transport", {
            "name": name, "type": vehicle_type, "plate_number": plate,
            "capacity": capacity, "driver_name": driver, "driver_phone": driver_phone
        })
    
    def get_fleet(self) -> list:
        return self.db.query("SELECT * FROM transport ORDER BY status, name")
    
    def schedule_trip(self, transport_id: int, group_id: int,
                      from_loc: str, to_loc: str,
                      departure: str, count: int = 0) -> dict:
        return self.db.insert("trips", {
            "transport_id": transport_id, "group_id": group_id,
            "from_location": from_loc, "to_location": to_loc,
            "departure": departure, "passenger_count": count
        })
    
    def get_trips(self, date: str = None) -> list:
        if date:
            return self.db.query("""
                SELECT t.*, tr.name as transport_name, tr.driver_name,
                       g.name as group_name
                FROM trips t
                JOIN transport tr ON t.transport_id = tr.id
                JOIN groups g ON t.group_id = g.id
                WHERE date(t.departure) = ? ORDER BY t.departure
            """, (date,))
        return self.db.query("""
            SELECT t.*, tr.name as transport_name, tr.driver_name,
                   g.name as group_name
            FROM trips t
            JOIN transport tr ON t.transport_id = tr.id
            JOIN groups g ON t.group_id = g.id
            ORDER BY t.departure DESC LIMIT 30
        """)
    
    # ═══ Reports ═══
    
    def daily_operations(self) -> dict:
        """Today's Umrah operations overview"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        arrivals = self.db.query(
            "SELECT COUNT(*) as c FROM pilgrims WHERE arrival_date = ?", (today,)
        )
        departures = self.db.query(
            "SELECT COUNT(*) as c FROM pilgrims WHERE departure_date = ?", (today,)
        )
        active_groups = self.db.query(
            "SELECT COUNT(*) as c FROM groups WHERE status = 'in_makkah'"
        )
        trips_today = self.db.query(
            "SELECT COUNT(*) as c FROM trips WHERE date(departure) = ?", (today,)
        )
        meals_today = self.db.query(
            "SELECT COUNT(*) as c FROM meals WHERE date = ?", (today,)
        )
        
        return {
            "date": today,
            "arrivals_today": arrivals[0]["c"] if arrivals else 0,
            "departures_today": departures[0]["c"] if departures else 0,
            "active_groups": active_groups[0]["c"] if active_groups else 0,
            "trips_today": trips_today[0]["c"] if trips_today else 0,
            "meals_today": meals_today[0]["c"] if meals_today else 0
        }
    
    def umrah_report(self) -> dict:
        """Comprehensive Umrah operations report"""
        packages = self.get_packages()
        total_pilgrims = self.db.query("SELECT COUNT(*) as c FROM pilgrims WHERE status != 'cancelled'")
        total_groups = self.db.query("SELECT COUNT(*) as c FROM groups")
        fleet = self.db.query("SELECT COUNT(*) as c FROM transport WHERE status = 'available'")
        active_pilgrims = self.db.query("SELECT COUNT(*) as c FROM pilgrims WHERE status IN ('confirmed','arrived')")
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "packages": len(packages),
            "total_pilgrims": total_pilgrims[0]["c"] if total_pilgrims else 0,
            "active_pilgrims": active_pilgrims[0]["c"] if active_pilgrims else 0,
            "total_groups": total_groups[0]["c"] if total_groups else 0,
            "available_vehicles": fleet[0]["c"] if fleet else 0,
            "package_list": packages[:10]
        }
    
    def close(self):
        self.db.close()
