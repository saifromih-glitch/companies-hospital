# -*- coding: utf-8 -*-
"""Personalized Dashboard API — industry-specific data per user"""
import os, sys, json

_AGENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "romih_agent")
sys.path.insert(0, _AGENT_DIR)


def get_user_dashboard(user_id: str = "", industry: str = "", user_name: str = "") -> dict:
    """
    Return personalized dashboard data based on user's industry.
    Called from romih_router.py
    """
    # Determine name and industry from user profile
    if not user_name or not industry:
        try:
            from plugins.onboarding import OnboardingInterview
            onboard = OnboardingInterview("onboarding_profile.json")
            if onboard.is_complete():
                if not user_name and onboard.profile.name:
                    user_name = onboard.profile.name
                if not industry and onboard.profile.industry:
                    industry = ",".join(onboard.profile.industry)
        except:
            pass
    
    if not industry:
        industry = "general"
    
    result = {
        "user_id": user_id,
        "user_name": user_name or "",
        "industry": industry,
        "personalized": True,
        "greeting": _greeting(industry, user_name),
        "cards": [],
        "quick_actions": [],
        "stats": {}
    }
    
    # Build industry-specific dashboard
    industries = industry.split(",")
    
    if "workshop" in industries:
        result["cards"].extend(_workshop_cards(user_id))
        result["quick_actions"].extend([
            {"label": "+ عميل جديد", "action": "/romih/goal", "icon": "👤"},
            {"label": "+ تصليح", "action": "/romih/goal", "icon": "🔧"},
            {"label": "+ فاتورة", "action": "/romih/goal", "icon": "📄"},
        ])
        result["stats"]["workshop"] = _workshop_stats(user_id)
    
    if "hotel" in industries:
        result["cards"].extend(_hotel_cards(user_id))
        result["quick_actions"].extend([
            {"label": "+ حجز جديد", "action": "/romih/goal", "icon": "🏨"},
            {"label": "+ نزيل", "action": "/romih/goal", "icon": "👤"},
        ])
        result["stats"]["hotels"] = _hotel_stats(user_id)
    
    if "umrah" in industries:
        result["cards"].extend(_umrah_cards(user_id))
        result["quick_actions"].extend([
            {"label": "+ حاج جديد", "action": "/romih/goal", "icon": "🕋"},
            {"label": "+ باقة", "action": "/romih/goal", "icon": "📦"},
            {"label": "+ مجموعة", "action": "/romih/goal", "icon": "👥"},
        ])
        result["stats"]["umrah"] = _umrah_stats(user_id)
    
    # Always include management cards
    result["cards"].extend(_management_cards(user_id))
    result["quick_actions"].extend([
        {"label": "تقرير اليوم", "action": "/romih/goal", "icon": "📊"},
    ])
    result["stats"]["management"] = _management_stats(user_id)
    
    # System info
    result["system"] = {
        "tools": 174,
        "plugins_active": len([c for c in result.get("cards", [])]),
        "uptime": "24/7",
    }
    
    return result


def _greeting(industry: str, user_name: str = "") -> str:
    name_part = f" {user_name}" if user_name else " بك"
    greetings = {
        "workshop": f"👋 أهلاً{name_part}! هذه لوحة تحكم ورشتك",
        "hotel": f"👋 أهلاً{name_part}! هذه لوحة تحكم فندقك",
        "umrah": f"👋 أهلاً{name_part}! هذه لوحة تحكم شركة العمرة",
        "general": f"👋 أهلاً{name_part}! هذه لوحة تحكم أعمالك",
    }
    for key, msg in greetings.items():
        if key in industry:
            return msg
    return greetings["general"]


def _workshop_cards(user_id: str) -> list:
    return [
        {"id": "customers", "title": "العملاء", "icon": "👥", "value": _count("workshop_customers", user_id), "color": "#3B82F6", "link": "/romih/goal"},
        {"id": "repairs", "title": "تصليحات جارية", "icon": "🔧", "value": _count("workshop_repairs", user_id, "status='pending' OR status='in_progress'"), "color": "#F59E0B", "link": "/romih/goal"},
        {"id": "parts", "title": "قطع الغيار", "icon": "⚙️", "value": _count("workshop_parts", user_id), "color": "#10B981", "link": "/romih/goal"},
        {"id": "invoices", "title": "فواتير غير مدفوعة", "icon": "📄", "value": _count("workshop_invoices", user_id, "status='unpaid'"), "color": "#EF4444", "link": "/romih/goal"},
    ]


def _hotel_cards(user_id: str) -> list:
    return [
        {"id": "properties", "title": "العقارات", "icon": "🏨", "value": _count("hotel_properties", user_id), "color": "#3B82F6", "link": "/romih/goal"},
        {"id": "bookings", "title": "حجوزات نشطة", "icon": "📅", "value": _count("hotel_bookings", user_id, "status='confirmed'"), "color": "#10B981", "link": "/romih/goal"},
        {"id": "rooms", "title": "غرف متاحة", "icon": "🚪", "value": _count("hotel_rooms", user_id, "status='available'"), "color": "#F59E0B", "link": "/romih/goal"},
        {"id": "occupancy", "title": "نسبة الإشغال", "icon": "📊", "value": "—", "color": "#8B5CF6", "link": "/romih/goal"},
    ]


def _umrah_cards(user_id: str) -> list:
    return [
        {"id": "pilgrims", "title": "الحجاج", "icon": "🕋", "value": _count("umrah_pilgrims", user_id), "color": "#3B82F6", "link": "/romih/goal"},
        {"id": "packages", "title": "الباقات", "icon": "📦", "value": _count("umrah_packages", user_id), "color": "#10B981", "link": "/romih/goal"},
        {"id": "groups", "title": "المجموعات", "icon": "👥", "value": _count("umrah_groups", user_id), "color": "#F59E0B", "link": "/romih/goal"},
        {"id": "visas", "title": "تأشيرات معلقة", "icon": "📋", "value": _count("umrah_pilgrims", user_id, "status='visa_pending'"), "color": "#EF4444", "link": "/romih/goal"},
    ]


def _management_cards(user_id: str) -> list:
    return [
        {"id": "employees", "title": "الموظفين", "icon": "👥", "value": _count("hr_employees", user_id), "color": "#6366F1", "link": "/romih/goal"},
        {"id": "revenue", "title": "إيرادات الشهر", "icon": "💰", "value": "—", "color": "#10B981", "link": "/romih/goal"},
    ]


def _count(table: str, user_id: str, where: str = "") -> int:
    try:
        from tools.multi_tenant_db import MultiTenantDB
        db = MultiTenantDB(table.split('_')[0])
        return db.count(table, user_id if user_id else "anonymous")
    except:
        return 0


def _workshop_stats(user_id: str) -> dict:
    return {
        "total_customers": _count("workshop_customers", user_id),
        "active_repairs": _count("workshop_repairs", user_id, "status='in_progress'"),
        "unpaid_invoices": _count("workshop_invoices", user_id, "status='unpaid'"),
    }

def _hotel_stats(user_id: str) -> dict:
    return {
        "total_properties": _count("hotel_properties", user_id),
        "active_bookings": _count("hotel_bookings", user_id, "status='confirmed'"),
        "available_rooms": _count("hotel_rooms", user_id, "status='available'"),
    }

def _umrah_stats(user_id: str) -> dict:
    return {
        "total_pilgrims": _count("umrah_pilgrims", user_id),
        "total_packages": _count("umrah_packages", user_id),
        "total_groups": _count("umrah_groups", user_id),
    }

def _management_stats(user_id: str) -> dict:
    return {
        "employees": _count("hr_employees", user_id),
        "pending_leaves": _count("hr_leaves", user_id, "status='pending'"),
    }
