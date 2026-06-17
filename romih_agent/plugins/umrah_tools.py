# -*- coding: utf-8 -*-
"""Register Umrah Plugin as tools in Romih."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.umrah import UmrahPlugin


def register(tools_registry):
    u = UmrahPlugin(db_path="umrah.db")
    
    # Package tools
    tools_registry.register(Tool(
        name="umrah_add_package",
        description="Add Umrah/Hajj package with price and seats",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Package name", required=True),
            ToolParam(name="type", type="string", description="umrah/hajj/ziyara", required=False),
            ToolParam(name="price", type="float", description="Price in SAR", required=False),
            ToolParam(name="seats", type="int", description="Total seats", required=False),
        ],
        execute=lambda name, type="umrah", price=0, seats=0, **_: 
            u.add_package(name, type, 7, float(price), int(seats))
    ))
    
    tools_registry.register(Tool(
        name="umrah_list_packages",
        description="List all active Umrah packages with stats",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"packages": u.get_packages()}
    ))
    
    # Pilgrim tools
    tools_registry.register(Tool(
        name="umrah_register_pilgrim",
        description="Register a new pilgrim with passport, nationality, package",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Full name", required=True),
            ToolParam(name="passport", type="string", description="Passport number", required=False),
            ToolParam(name="nationality", type="string", description="Nationality", required=False),
        ],
        execute=lambda name, passport="", nationality="", package_id=None, arrival="", **_: 
            u.register_pilgrim(name, passport, nationality, None if not package_id else int(package_id), arrival=arrival)
    ))
    
    tools_registry.register(Tool(
        name="umrah_list_pilgrims",
        description="List pilgrims by package, group, or status",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="status", type="string", description="pending/confirmed/arrived/completed", required=False)],
        execute=lambda status=None, **_: {"pilgrims": u.get_pilgrims(status=status)}
    ))
    
    tools_registry.register(Tool(
        name="umrah_search_pilgrim",
        description="Search pilgrim by name, passport, or phone",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="query", type="string", description="Name/passport/phone", required=True)],
        execute=lambda query, **_: {"results": u.search_pilgrim(query)}
    ))
    
    tools_registry.register(Tool(
        name="umrah_issue_visa",
        description="Issue visa and update pilgrim status",
        category="umrah",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="pilgrim_id", type="int", description="Pilgrim ID", required=True),
            ToolParam(name="visa_number", type="string", description="Visa number", required=True),
        ],
        execute=lambda pilgrim_id, visa_number, **_: u.update_pilgrim_status(int(pilgrim_id), "confirmed", visa_number)
    ))
    
    # Group tools
    tools_registry.register(Tool(
        name="umrah_create_group",
        description="Create pilgrim group with leader and max size",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Group name", required=True),
            ToolParam(name="leader", type="string", description="Group leader", required=False),
            ToolParam(name="max_size", type="int", description="Max pilgrims", required=False),
        ],
        execute=lambda name, leader="", max_size=50, **_: u.create_group(name, leader=leader, max_size=int(max_size))
    ))
    
    tools_registry.register(Tool(
        name="umrah_list_groups",
        description="List all pilgrim groups",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"groups": u.get_groups()}
    ))
    
    tools_registry.register(Tool(
        name="umrah_assign_to_group",
        description="Assign pilgrim to a group",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="pilgrim_id", type="int", description="Pilgrim ID", required=True),
            ToolParam(name="group_id", type="int", description="Group ID", required=True),
        ],
        execute=lambda pilgrim_id, group_id, **_: u.assign_to_group(int(pilgrim_id), int(group_id))
    ))
    
    tools_registry.register(Tool(
        name="umrah_group_details",
        description="View group details: pilgrims, trips, meals",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="group_id", type="int", description="Group ID", required=True)],
        execute=lambda group_id, **_: u.group_details(int(group_id))
    ))
    
    # Catering
    tools_registry.register(Tool(
        name="umrah_add_meal",
        description="Plan meal for a group (breakfast/lunch/dinner/suhoor/iftar)",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="group_id", type="int", description="Group ID", required=True),
            ToolParam(name="date", type="string", description="Date YYYY-MM-DD", required=True),
            ToolParam(name="type", type="string", description="Meal type", required=True),
            ToolParam(name="count", type="int", description="Number of meals", required=False),
        ],
        execute=lambda group_id, date, type, count=0, **_: 
            u.add_meal_plan(int(group_id), date, type, count=int(count))
    ))
    
    # Transport
    tools_registry.register(Tool(
        name="umrah_add_vehicle",
        description="Add vehicle to fleet (bus/van/car) with driver info",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Vehicle name", required=True),
            ToolParam(name="type", type="string", description="bus/van/car", required=False),
            ToolParam(name="capacity", type="int", description="Passenger capacity", required=False),
            ToolParam(name="driver", type="string", description="Driver name", required=False),
        ],
        execute=lambda name, type="bus", capacity=0, driver="", **_: 
            u.add_transport(name, type, capacity=int(capacity), driver=driver)
    ))
    
    tools_registry.register(Tool(
        name="umrah_schedule_trip",
        description="Schedule a trip for a group",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="transport_id", type="int", description="Vehicle ID", required=True),
            ToolParam(name="group_id", type="int", description="Group ID", required=True),
            ToolParam(name="from_loc", type="string", description="From location", required=True),
            ToolParam(name="to_loc", type="string", description="To location", required=True),
            ToolParam(name="departure", type="string", description="Departure datetime", required=True),
        ],
        execute=lambda transport_id, group_id, from_loc, to_loc, departure, **_: 
            u.schedule_trip(int(transport_id), int(group_id), from_loc, to_loc, departure)
    ))
    
    # Reports
    tools_registry.register(Tool(
        name="umrah_daily_ops",
        description="Today's operations: arrivals, departures, trips, meals",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: u.daily_operations()
    ))
    
    tools_registry.register(Tool(
        name="umrah_report",
        description="Comprehensive Umrah report: packages, pilgrims, groups, fleet",
        category="umrah",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: u.umrah_report()
    ))
    
    print("Umrah: 16 tools registered (packages=2, pilgrims=4, groups=4, meals=1, transport=2, reports=3)")
