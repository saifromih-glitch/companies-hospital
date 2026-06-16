# -*- coding: utf-8 -*-
"""
Register Workshop Plugin as tools in Romih Agent.
Romih can now manage: customers, repairs, parts, invoices.
"""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.workshop import WorkshopPlugin


def register(tools_registry):
    ws = WorkshopPlugin(db_path="workshop.db")
    
    # Customer tools
    tools_registry.register(Tool(
        name="workshop_add_customer",
        description="Add new customer to workshop. Need: name, phone, vehicle.",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Customer name", required=True),
            ToolParam(name="phone", type="string", description="Phone number", required=False),
            ToolParam(name="vehicle", type="string", description="Vehicle model", required=False),
        ],
        execute=lambda name, phone="", vehicle="", **_: ws.add_customer(name, phone, vehicle)
    ))
    
    tools_registry.register(Tool(
        name="workshop_list_customers",
        description="List all workshop customers",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"customers": ws.get_customers()}
    ))
    
    tools_registry.register(Tool(
        name="workshop_search_customer",
        description="Search customer by name or phone",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="query", type="string", description="Name or phone to search", required=True)],
        execute=lambda query, **_: {"results": ws.search_customer(query)}
    ))
    
    # Repair tools
    tools_registry.register(Tool(
        name="workshop_add_repair",
        description="Start a new repair job for a customer",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="customer_id", type="int", description="Customer ID", required=True),
            ToolParam(name="description", type="string", description="What to repair", required=True),
            ToolParam(name="repair_type", type="string", description="hydraulic/mechanical/electrical", required=False),
            ToolParam(name="cost", type="float", description="Estimated cost", required=False),
        ],
        execute=lambda customer_id, description, repair_type="mechanical", cost=0.0, **_: 
            ws.add_repair(int(customer_id), description, repair_type, float(cost))
    ))
    
    tools_registry.register(Tool(
        name="workshop_list_repairs",
        description="List repairs (all or filter by status: pending/in_progress/done/delivered)",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="status", type="string", description="Filter by status", required=False)],
        execute=lambda status=None, **_: {"repairs": ws.get_repairs(status) if status else ws.get_repairs()}
    ))
    
    tools_registry.register(Tool(
        name="workshop_update_status",
        description="Update repair status to: pending, in_progress, done, delivered",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="repair_id", type="int", description="Repair ID", required=True),
            ToolParam(name="status", type="string", description="New status", required=True),
        ],
        execute=lambda repair_id, status, **_: ws.update_repair_status(int(repair_id), status)
    ))
    
    # Parts/inventory tools
    tools_registry.register(Tool(
        name="workshop_add_part",
        description="Add spare part to inventory",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Part name", required=True),
            ToolParam(name="quantity", type="int", description="Quantity", required=False),
            ToolParam(name="cost", type="float", description="Cost per unit", required=False),
            ToolParam(name="supplier", type="string", description="Supplier name", required=False),
        ],
        execute=lambda name, quantity=1, cost=0.0, supplier="", **_: 
            ws.add_part(name, int(quantity), float(cost), supplier)
    ))
    
    tools_registry.register(Tool(
        name="workshop_inventory",
        description="List all parts in inventory",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"inventory": ws.get_inventory()}
    ))
    
    tools_registry.register(Tool(
        name="workshop_low_stock",
        description="Check parts below minimum stock level",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"low_stock": ws.check_low_stock()}
    ))
    
    # Invoice tools
    tools_registry.register(Tool(
        name="workshop_create_invoice",
        description="Create invoice for a repair",
        category="workshop",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="customer_id", type="int", description="Customer ID", required=True),
            ToolParam(name="repair_id", type="int", description="Repair ID", required=True),
            ToolParam(name="total", type="float", description="Total amount", required=True),
        ],
        execute=lambda customer_id, repair_id, total, **_: 
            ws.create_invoice(int(customer_id), int(repair_id), float(total))
    ))
    
    tools_registry.register(Tool(
        name="workshop_list_invoices",
        description="List invoices (all or filter: unpaid/partial/paid)",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="status", type="string", description="Filter by status", required=False)],
        execute=lambda status=None, **_: {"invoices": ws.get_invoices(status)}
    ))
    
    tools_registry.register(Tool(
        name="workshop_daily_report",
        description="Generate today's workshop summary report",
        category="workshop",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: ws.daily_report()
    ))
    
    print("Workshop: 12 tools registered (customers=3, repairs=3, parts=3, invoices=2, report=1)")
