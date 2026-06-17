# -*- coding: utf-8 -*-
"""Register HR Plugin as tools in Romih Agent."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.hr import HRPlugin


def register(tools_registry):
    hr = HRPlugin(db_path="hr.db")
    
    # Employee tools
    tools_registry.register(Tool(
        name="hr_add_employee",
        description="Add new employee. Need: name, phone, department, position, salary.",
        category="hr",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Full name", required=True),
        ],
        execute=lambda name, phone="", email="", department="", position="", salary=0, **_: 
            hr.add_employee(name, phone, email, department, position, float(salary))
    ))
    
    tools_registry.register(Tool(
        name="hr_list_employees",
        description="List all employees or filter by department",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="department", type="string", description="Department filter", required=False)],
        execute=lambda department=None, **_: {"employees": hr.get_employees(department)}
    ))
    
    tools_registry.register(Tool(
        name="hr_search_employee",
        description="Search employee by name or phone",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="query", type="string", description="Name or phone", required=True)],
        execute=lambda query, **_: {"results": hr.search_employee(query)}
    ))
    
    tools_registry.register(Tool(
        name="hr_update_employee",
        description="Update employee field (name, phone, email, department, position, salary, status)",
        category="hr",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="employee_id", type="int", description="Employee ID", required=True),
            ToolParam(name="field", type="string", description="Field to update", required=True),
            ToolParam(name="value", type="string", description="New value", required=True),
        ],
        execute=lambda employee_id, field, value, **_: hr.update_employee(int(employee_id), field, value)
    ))
    
    tools_registry.register(Tool(
        name="hr_departments",
        description="Show employee count and salary by department",
        category="hr",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"departments": hr.count_by_department()}
    ))
    
    # Leave tools
    tools_registry.register(Tool(
        name="hr_request_leave",
        description="Submit leave request for an employee",
        category="hr",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="employee_id", type="int", description="Employee ID", required=True),
            ToolParam(name="start_date", type="string", description="Start date YYYY-MM-DD", required=True),
            ToolParam(name="end_date", type="string", description="End date YYYY-MM-DD", required=True),
            ToolParam(name="leave_type", type="string", description="annual/sick/emergency/unpaid", required=False),
        ],
        execute=lambda employee_id, start_date, end_date, leave_type="annual", **_: 
            hr.request_leave(int(employee_id), start_date, end_date, leave_type)
    ))
    
    tools_registry.register(Tool(
        name="hr_list_leaves",
        description="List leave requests (all, pending, or by employee)",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="status", type="string", description="pending/approved/rejected", required=False)],
        execute=lambda status=None, **_: {"leaves": hr.get_leaves(status)}
    ))
    
    tools_registry.register(Tool(
        name="hr_approve_leave",
        description="Approve or reject leave request",
        category="hr",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="leave_id", type="int", description="Leave request ID", required=True),
            ToolParam(name="approved", type="bool", description="True=approve, False=reject", required=True),
        ],
        execute=lambda leave_id, approved, **_: hr.approve_leave(int(leave_id), approved)
    ))
    
    tools_registry.register(Tool(
        name="hr_leave_balance",
        description="Check leave balance for an employee",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="employee_id", type="int", description="Employee ID", required=True)],
        execute=lambda employee_id, **_: hr.leave_balance(int(employee_id))
    ))
    
    # Payroll tools
    tools_registry.register(Tool(
        name="hr_generate_payroll",
        description="Generate payroll for all active employees for current month",
        category="hr",
        risk=RiskLevel.HIGH,
        params=[],
        execute=lambda **_: hr.generate_payroll()
    ))
    
    tools_registry.register(Tool(
        name="hr_list_payroll",
        description="View payroll for a specific month (default: current)",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="month", type="string", description="YYYY-MM format", required=False)],
        execute=lambda month=None, **_: {"payroll": hr.get_payroll(month)}
    ))
    
    tools_registry.register(Tool(
        name="hr_mark_paid",
        description="Mark a payroll entry as paid",
        category="hr",
        risk=RiskLevel.HIGH,
        params=[ToolParam(name="payroll_id", type="int", description="Payroll entry ID", required=True)],
        execute=lambda payroll_id, **_: hr.mark_paid(int(payroll_id))
    ))
    
    tools_registry.register(Tool(
        name="hr_payroll_summary",
        description="Payroll summary for a month (total, paid, pending)",
        category="hr",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: hr.payroll_summary()
    ))
    
    # Evaluation tools
    tools_registry.register(Tool(
        name="hr_add_evaluation",
        description="Add employee performance evaluation (score 0-100)",
        category="hr",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="employee_id", type="int", description="Employee ID", required=True),
            ToolParam(name="period", type="string", description="Period YYYY-Q1", required=True),
            ToolParam(name="score", type="float", description="Score 0-100", required=True),
        ],
        execute=lambda employee_id, period, score, strengths="", **_: 
            hr.add_evaluation(int(employee_id), period, float(score), strengths)
    ))
    
    tools_registry.register(Tool(
        name="hr_list_evaluations",
        description="View employee evaluations",
        category="hr",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="employee_id", type="int", description="Employee ID (optional)", required=False)],
        execute=lambda employee_id=None, **_: {"evaluations": hr.get_evaluations(int(employee_id) if employee_id else None)}
    ))
    
    tools_registry.register(Tool(
        name="hr_top_performers",
        description="Show top performing employees by evaluation scores",
        category="hr",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"top_performers": hr.top_performers()}
    ))
    
    # Report
    tools_registry.register(Tool(
        name="hr_report",
        description="Generate comprehensive HR report: employees, payroll, leaves, departments",
        category="hr",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: hr.hr_report()
    ))
    
    print("HR: 16 tools registered (employees=5, leaves=4, payroll=4, evaluations=3)")
