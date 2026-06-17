# -*- coding: utf-8 -*-
"""Register Finance Plugin as tools in Romih Agent."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.finance import FinancePlugin


def register(tools_registry):
    fin = FinancePlugin(db_path="finance.db")
    
    # Invoice tools
    tools_registry.register(Tool(
        name="fin_create_invoice",
        description="Create a new invoice with automatic VAT calculation (15%)",
        category="finance",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="client_name", type="string", description="Client name", required=True),
            ToolParam(name="amount", type="float", description="Amount before tax", required=True),
        ],
        execute=lambda client_name, amount, **_: fin.create_invoice(client_name, float(amount))
    ))
    
    tools_registry.register(Tool(
        name="fin_list_invoices",
        description="List invoices (all or filter: unpaid/partial/paid/cancelled)",
        category="finance",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="status", type="string", description="Filter status", required=False)],
        execute=lambda status=None, **_: {"invoices": fin.get_invoices(status)}
    ))
    
    tools_registry.register(Tool(
        name="fin_record_payment",
        description="Record payment on an invoice",
        category="finance",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="invoice_id", type="int", description="Invoice ID", required=True),
            ToolParam(name="amount", type="float", description="Amount paid", required=True),
        ],
        execute=lambda invoice_id, amount, **_: fin.record_payment(int(invoice_id), float(amount))
    ))
    
    tools_registry.register(Tool(
        name="fin_outstanding",
        description="Show all outstanding (unpaid) invoices",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"outstanding": fin.outstanding_invoices()}
    ))
    
    # Expense tools
    tools_registry.register(Tool(
        name="fin_add_expense",
        description="Record a new expense (rent, utilities, supplies, salary, marketing, other)",
        category="finance",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="category", type="string", description="rent/utilities/supplies/salary/marketing/other", required=True),
            ToolParam(name="description", type="string", description="What was spent", required=True),
            ToolParam(name="amount", type="float", description="Amount spent", required=True),
        ],
        execute=lambda category, description, amount, **_: fin.add_expense(category, description, float(amount))
    ))
    
    tools_registry.register(Tool(
        name="fin_list_expenses",
        description="List recent expenses (default: last 30 days)",
        category="finance",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="category", type="string", description="Filter by category", required=False)],
        execute=lambda category=None, **_: {"expenses": fin.get_expenses(category)}
    ))
    
    tools_registry.register(Tool(
        name="fin_expenses_by_category",
        description="Show expenses grouped by category with totals",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"categories": fin.expenses_by_category()}
    ))
    
    # Account tools
    tools_registry.register(Tool(
        name="fin_add_account",
        description="Add a bank/cash account",
        category="finance",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Account name", required=True),
            ToolParam(name="balance", type="float", description="Current balance", required=False),
        ],
        execute=lambda name, balance=0, account_type="asset", **_: fin.add_account(name, account_type, float(balance))
    ))
    
    tools_registry.register(Tool(
        name="fin_list_accounts",
        description="List all financial accounts",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"accounts": fin.get_accounts()}
    ))
    
    # Report tools
    tools_registry.register(Tool(
        name="fin_income_statement",
        description="Profit & Loss statement (last 30 days)",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: fin.income_statement()
    ))
    
    tools_registry.register(Tool(
        name="fin_cash_flow",
        description="Cash position: available cash + receivables",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: fin.cash_flow()
    ))
    
    tools_registry.register(Tool(
        name="fin_report",
        description="Comprehensive financial report: P&L, cash flow, outstanding, expenses",
        category="finance",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: fin.finance_report()
    ))
    
    print("Finance: 12 tools registered (invoices=4, expenses=3, accounts=2, reports=3)")
