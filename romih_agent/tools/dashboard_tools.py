# -*- coding: utf-8 -*-
"""Custom Dashboard Tools — user can verbally customize their dashboard"""

from tools.custom_dashboard import (
    add_card, remove_card, reset_dashboard, 
    get_available_cards, customize_dashboard, CARD_CATALOG
)


def register(tools_registry):
    """Register dashboard customization tools"""
    from tools.registry import Tool, RiskLevel
    
    def _add_dashboard_card(user_id: str = "", card: str = "", industry: str = "general") -> str:
        if not card:
            available = get_available_cards(industry)
            lines = ["**اختر كارت لإضافته:**"]
            for cat, cards in available.items():
                cat_name = {"workshop": "🏭 ورشة", "hotel": "🏨 فندق", "umrah": "🕋 عمرة", "mgmt": "📋 إدارة"}.get(cat, cat)
                lines.append(f"\n{cat_name}:")
                for c in cards:
                    lines.append(f"  • `{c['key']}` — {c['icon']} {c['title']}")
            return "\n".join(lines)
        uid = user_id or "anonymous"
        return add_card(uid, card.strip())
    
    def _remove_dashboard_card(user_id: str = "", card: str = "") -> str:
        if not card:
            return "🔍 اكتب اسم الكارت اللي عايز تشيله، مثلاً: `workshop_customers`"
        uid = user_id or "anonymous"
        return remove_card(uid, card.strip())
    
    def _reset_dashboard(user_id: str = "", industry: str = "general") -> str:
        uid = user_id or "anonymous"
        return reset_dashboard(uid, industry)
    
    def _list_available_cards(industry: str = "general") -> str:
        available = get_available_cards(industry)
        lines = ["📊 **الكروت المتاحة:**"]
        for cat, cards in available.items():
            cat_name = {"workshop": "🏭 ورشة", "hotel": "🏨 فندق", "umrah": "🕋 عمرة", "mgmt": "📋 إدارة"}.get(cat, cat)
            lines.append(f"\n{cat_name}:")
            for c in cards:
                lines.append(f"  • `{c['key']}` — {c['icon']} {c['title']}")
        return "\n".join(lines)
    
    tools_registry.register(Tool(
        name="dash_add",
        description="أضف كارت للداشبورد (workshop_customers, hotel_bookings, umrah_pilgrims, mgmt_revenue...)",
        category="dashboard",
        risk=RiskLevel.LOW,
        execute=_add_dashboard_card
    ))
    
    tools_registry.register(Tool(
        name="dash_remove",
        description="شيل كارت من الداشبورد",
        category="dashboard",
        risk=RiskLevel.LOW,
        execute=_remove_dashboard_card
    ))
    
    tools_registry.register(Tool(
        name="dash_list",
        description="اعرض الكروت المتاحة للداشبورد",
        category="dashboard",
        risk=RiskLevel.LOW,
        execute=_list_available_cards
    ))
    
    tools_registry.register(Tool(
        name="dash_reset",
        description="أرجع الداشبورد للوضع الافتراضي",
        category="dashboard",
        risk=RiskLevel.LOW,
        execute=_reset_dashboard
    ))
    
    return 4
