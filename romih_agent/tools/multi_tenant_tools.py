# -*- coding: utf-8 -*-
"""Register multi-tenant DB as a tool in Romih"""
from tools.registry import Tool, RiskLevel, ToolParam
from tools.multi_tenant_db import MultiTenantDB

_dbs = {}

def _get_db(plugin: str) -> MultiTenantDB:
    if plugin not in _dbs:
        _dbs[plugin] = MultiTenantDB(plugin)
    return _dbs[plugin]


def register(tools_registry):
    tools_registry.register(Tool(
        name="db_summary",
        description="Get database summary for a user and plugin",
        category="system",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="plugin", type="string", description="Plugin: workshop, hr, finance, projects, umrah, hotels", required=True),
            ToolParam(name="user_id", type="string", description="User ID", required=True)
        ],
        execute=lambda plugin, user_id, **_: _get_db(plugin).summary(user_id)
    ))
    print("MultiTenantDB: 1 tool registered (db_summary)")
