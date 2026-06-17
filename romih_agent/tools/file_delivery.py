# -*- coding: utf-8 -*-
"""File generation and delivery tools — CSV, Excel, PDF for Telegram"""
from tools.registry import Tool, RiskLevel, ToolParam


def register(tools_registry):
    tools_registry.register(Tool(
        name="file_csv",
        description="Create a CSV file and return its content. Can be sent via Telegram if chat_id provided.",
        category="files",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="headers", type="string", description="Comma-separated column names", required=True),
            ToolParam(name="data", type="string", description="Optional: rows of data, one per line, comma-separated", required=False),
            ToolParam(name="chat_id", type="number", description="Telegram chat ID (sends directly if set)", required=False),
        ],
        execute=_create_csv
    ))


def _create_csv(headers="", data="", chat_id=0, **kwargs):
    lines = [headers]
    if data:
        lines.extend(data.strip().split('\n'))
    csv_content = '\n'.join(lines)
    
    return {
        "ok": True,
        "csv": csv_content[:5000],
        "filename": "romih_data.csv",
        "message": "CSV created. Content returned inline."
    }
