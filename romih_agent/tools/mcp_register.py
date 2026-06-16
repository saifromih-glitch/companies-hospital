# -*- coding: utf-8 -*-
"""
Register MCP Connector tools in Romih Agent's Tool Registry.
"""
from tools.registry import Tool, RiskLevel, ToolParam
from tools.mcp_connectors import SQLConnector, FileConnector, DBConfig


def register(tools_registry):
    """Register MCP connectors as tools"""
    sql = SQLConnector(DBConfig(db_type="sqlite", database="romih.db"))
    files = FileConnector(".")
    
    tools_registry.register(Tool(
        name="db_query",
        description="Execute SQL SELECT on database to look up customers, repairs, parts",
        category="data",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="sql", type="string", description="SQL SELECT query", required=True)],
        execute=lambda sql, **_: {"result": sql.query(sql)}
    ))
    
    tools_registry.register(Tool(
        name="db_execute", 
        description="Execute SQL INSERT/UPDATE/DELETE on database",
        category="data",
        risk=RiskLevel.HIGH,
        params=[ToolParam(name="sql", type="string", description="SQL query", required=True)],
        execute=lambda sql, **_: sql.execute(sql)
    ))
    
    tools_registry.register(Tool(
        name="db_tables",
        description="List all database tables",
        category="data",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"tables": sql.list_tables()}
    ))
    
    tools_registry.register(Tool(
        name="file_read",
        description="Read file from workspace — check logs, configs, documents",
        category="file",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="path", type="string", description="Relative file path", required=True)],
        execute=lambda path, **_: files.read(path)
    ))
    
    tools_registry.register(Tool(
        name="file_write",
        description="Write content to file in workspace",
        category="file",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="path", type="string", description="Relative file path", required=True),
            ToolParam(name="content", type="string", description="File content to write", required=True)
        ],
        execute=lambda path, content, **_: files.write(path, content)
    ))
    
    tools_registry.register(Tool(
        name="file_list",
        description="List files in directory",
        category="file",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="path", type="string", description="Directory path", required=False)],
        execute=lambda path=".", **_: {"files": files.list(path)}
    ))
    
    print("MCP: 6 connectors registered (sql=3, files=3)")
