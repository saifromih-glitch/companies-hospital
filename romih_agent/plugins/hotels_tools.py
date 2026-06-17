# -*- coding: utf-8 -*-
"""Register Hotels Plugin as tools."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.hotels import HotelsPlugin


def register(tools_registry):
    h = HotelsPlugin(db_path="hotels.db")
    
    # Property tools
    tools_registry.register(Tool(
        name="hotel_add_property",
        description="Add hotel/apartment/villa with rooms and location",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="name", type="string", description="Property name", required=True),
                ToolParam(name="type", type="string", description="hotel/apartment/villa/camp", required=False),
                ToolParam(name="location", type="string", description="Makkah/Madinah/etc", required=False)],
        execute=lambda name, type="hotel", location="Makkah", rooms=0, **_: 
            h.add_property(name, type, location, int(rooms))
    ))
    
    tools_registry.register(Tool(
        name="hotel_list_properties",
        description="List all properties",
        category="hotels", risk=RiskLevel.LOW, params=[],
        execute=lambda **_: {"properties": h.get_properties()}
    ))
    
    # Room tools
    tools_registry.register(Tool(
        name="hotel_add_room",
        description="Add room to a property with type and price",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="property_id", type="int", description="Property ID", required=True),
                ToolParam(name="number", type="string", description="Room number", required=True),
                ToolParam(name="type", type="string", description="standard/deluxe/suite/vip", required=False),
                ToolParam(name="price", type="float", description="Price per night", required=False)],
        execute=lambda property_id, number, type="standard", price=0, **_: 
            h.add_room(int(property_id), number, type, float(price))
    ))
    
    tools_registry.register(Tool(
        name="hotel_availability",
        description="Check available rooms for dates",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="property_id", type="int", description="Property ID", required=True),
                ToolParam(name="check_in", type="string", description="Check-in YYYY-MM-DD", required=True),
                ToolParam(name="check_out", type="string", description="Check-out YYYY-MM-DD", required=True)],
        execute=lambda property_id, check_in, check_out, **_: h.check_availability(int(property_id), check_in, check_out)
    ))
    
    # Booking tools
    tools_registry.register(Tool(
        name="hotel_book_room",
        description="Book a room for a guest",
        category="hotels",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="room_id", type="int", description="Room ID", required=True),
                ToolParam(name="guest_name", type="string", description="Guest name", required=True),
                ToolParam(name="check_in", type="string", description="Check-in YYYY-MM-DD", required=True),
                ToolParam(name="check_out", type="string", description="Check-out YYYY-MM-DD", required=True)],
        execute=lambda room_id, guest_name, check_in, check_out, **_: 
            h.book_room(int(room_id), guest_name, check_in, check_out)
    ))
    
    tools_registry.register(Tool(
        name="hotel_list_bookings",
        description="List bookings by status or date",
        category="hotels", risk=RiskLevel.LOW, params=[],
        execute=lambda **_: {"bookings": h.get_bookings()}
    ))
    
    tools_registry.register(Tool(
        name="hotel_check_in",
        description="Check in a guest",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="booking_id", type="int", description="Booking ID", required=True)],
        execute=lambda booking_id, **_: h.check_in(int(booking_id))
    ))
    
    tools_registry.register(Tool(
        name="hotel_check_out",
        description="Check out a guest",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="booking_id", type="int", description="Booking ID", required=True)],
        execute=lambda booking_id, **_: h.check_out(int(booking_id))
    ))
    
    # Maintenance
    tools_registry.register(Tool(
        name="hotel_report_issue",
        description="Report maintenance issue",
        category="hotels",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="issue", type="string", description="Issue description", required=True),
                ToolParam(name="room_id", type="int", description="Room ID (optional)", required=False)],
        execute=lambda issue, room_id=None, **_: h.report_issue(issue, int(room_id) if room_id else None)
    ))
    
    # Contracts
    tools_registry.register(Tool(
        name="hotel_add_contract",
        description="Add rental contract (annual/monthly/seasonal)",
        category="hotels",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="property_id", type="int", description="Property ID", required=True),
                ToolParam(name="tenant", type="string", description="Tenant name", required=True),
                ToolParam(name="start_date", type="string", description="Start YYYY-MM-DD", required=True),
                ToolParam(name="rent", type="float", description="Monthly rent", required=False)],
        execute=lambda property_id, tenant, start_date, rent=0, **_: 
            h.add_contract(int(property_id), tenant, start_date, float(rent))
    ))
    
    # Reports
    tools_registry.register(Tool(
        name="hotel_occupancy",
        description="Occupancy rate report",
        category="hotels", risk=RiskLevel.LOW, params=[],
        execute=lambda **_: h.occupancy_report()
    ))
    
    tools_registry.register(Tool(
        name="hotel_revenue",
        description="Revenue report for hotels",
        category="hotels", risk=RiskLevel.LOW, params=[],
        execute=lambda **_: h.revenue_report()
    ))
    
    tools_registry.register(Tool(
        name="hotel_report",
        description="Comprehensive hotels report",
        category="hotels", risk=RiskLevel.LOW, params=[],
        execute=lambda **_: h.hotels_report()
    ))
    
    print("Hotels: 13 tools registered (properties=2, rooms=2, bookings=4, maintenance=1, contracts=1, reports=3)")
