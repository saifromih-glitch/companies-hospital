# -*- coding: utf-8 -*-
"""Register Onboarding as tools and integrate with chat flow."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.onboarding import OnboardingInterview


def register(tools_registry):
    onboard = OnboardingInterview()
    
    tools_registry.register(Tool(
        name="onboarding_start",
        description="Start or restart the onboarding interview to customize Romih for your business",
        category="system",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: onboard.get_welcome()
    ))
    
    tools_registry.register(Tool(
        name="onboarding_answer",
        description="Answer the current onboarding question",
        category="system",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="answer", type="string", description="Your answer to the question", required=True)],
        execute=lambda answer, **_: onboard.ask(answer)[0]
    ))
    
    tools_registry.register(Tool(
        name="onboarding_reset",
        description="Reset and restart the onboarding interview",
        category="system",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: ["Resetting...", onboard.get_welcome()][1] if onboard.reset() == "reset" else onboard.get_welcome()
    ))
    
    tools_registry.register(Tool(
        name="onboarding_profile",
        description="View your saved business profile",
        category="system",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"profile": onboard.profile.__dict__} if onboard.is_complete() else {"message": "Onboarding not complete yet"}
    ))
    
    print("Onboarding: 4 tools registered (start, answer, reset, profile)")
