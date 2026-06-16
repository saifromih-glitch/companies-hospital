# -*- coding: utf-8 -*-
"""
Register cloud-compatible tool overrides.
Patches tools that don't work on Railway with HTTP-based versions.
"""
from tools.registry import Tool, RiskLevel, ToolParam


def register(tools_registry):
    """Override local-only tools with cloud-compatible versions"""
    
    # Check if we're on Railway (OPENROUTER_KEY exists)
    import os
    is_cloud = bool(os.environ.get("OPENROUTER_KEY"))
    if not is_cloud:
        print("Cloud tools: skipping (local environment)")
        return
    
    from tools.cloud_search import web_search, recognize_image, deep_research
    
    # Override web_search (replaces AutoClaw search)
    tools_registry.register(Tool(
        name="web_search",
        description="Search the web using DuckDuckGo. Use for latest information, news, facts.",
        category="search",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="query", type="string", description="Search query", required=True)],
        execute=lambda query, **_: web_search(query)
    ))
    
    # Override image recognition
    tools_registry.register(Tool(
        name="recognize_image",
        description="Analyze and describe an image in Arabic",
        category="creative",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="url", type="string", description="Image URL to analyze", required=True)],
        execute=lambda url, **_: recognize_image(url)
    ))
    
    # Override deep research
    tools_registry.register(Tool(
        name="deep_research",
        description="Conduct in-depth research on a topic and provide Arabic analysis",
        category="search",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="query", type="string", description="Research topic", required=True)],
        execute=lambda query, **_: deep_research(query)
    ))
    
    print("Cloud tools: 3 overrides registered (search, image, research)")
