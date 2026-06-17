# -*- coding: utf-8 -*-
"""Customizable Dashboard — user can add/remove/reorder cards via /goal"""

import json, os, sys
from datetime import datetime

_AGENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, _AGENT_DIR)

PREF_DIR = os.path.join(os.path.dirname(__file__), '..', 'analytics_data')
os.makedirs(PREF_DIR, exist_ok=True)

# All available card types with their defaults
CARD_CATALOG = {
    # Workshop
    "workshop_customers": {"id": "customers", "title": "العملاء", "icon": "👥", "color": "#3B82F6"},
    "workshop_repairs": {"id": "repairs", "title": "تصليحات جارية", "icon": "🔧", "color": "#F59E0B"},
    "workshop_parts": {"id": "parts", "title": "قطع الغيار", "icon": "⚙️", "color": "#10B981"},
    "workshop_invoices": {"id": "invoices", "title": "فواتير غير مدفوعة", "icon": "📄", "color": "#EF4444"},
    # Hotel
    "hotel_properties": {"id": "properties", "title": "العقارات", "icon": "🏨", "color": "#3B82F6"},
    "hotel_bookings": {"id": "bookings", "title": "حجوزات نشطة", "icon": "📅", "color": "#10B981"},
    "hotel_rooms": {"id": "rooms", "title": "غرف متاحة", "icon": "🚪", "color": "#F59E0B"},
    "hotel_occupancy": {"id": "occupancy", "title": "نسبة الإشغال", "icon": "📊", "color": "#8B5CF6"},
    # Umrah
    "umrah_pilgrims": {"id": "pilgrims", "title": "الحجاج", "icon": "🕋", "color": "#3B82F6"},
    "umrah_packages": {"id": "packages", "title": "الباقات", "icon": "📦", "color": "#10B981"},
    "umrah_groups": {"id": "groups", "title": "المجموعات", "icon": "👥", "color": "#F59E0B"},
    "umrah_visas": {"id": "visas", "title": "تأشيرات معلقة", "icon": "📋", "color": "#EF4444"},
    # Management (always available)
    "mgmt_employees": {"id": "employees", "title": "الموظفين", "icon": "👥", "color": "#6366F1"},
    "mgmt_revenue": {"id": "revenue", "title": "إيرادات الشهر", "icon": "💰", "color": "#10B981"},
    "mgmt_projects": {"id": "projects", "title": "المشاريع", "icon": "📊", "color": "#8B5CF6"},
    "mgmt_tasks": {"id": "tasks", "title": "المهام اليوم", "icon": "✅", "color": "#F59E0B"},
    "mgmt_attendance": {"id": "attendance", "title": "الحضور اليوم", "icon": "🕐", "color": "#3B82F6"},
}


def get_saved_prefs(user_id: str) -> dict:
    """Load user's saved dashboard preferences"""
    fpath = os.path.join(PREF_DIR, f'dashboard_prefs_{user_id}.json')
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"cards": [], "hidden": [], "layout": "grid"}


def save_prefs(user_id: str, prefs: dict):
    """Save user's dashboard preferences"""
    fpath = os.path.join(PREF_DIR, f'dashboard_prefs_{user_id}.json')
    prefs['updated_at'] = datetime.now().isoformat()
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def add_card(user_id: str, card_key: str) -> str:
    """Add a card to user's dashboard"""
    prefs = get_saved_prefs(user_id)
    if card_key in prefs['hidden']:
        prefs['hidden'].remove(card_key)
    if card_key not in prefs['cards']:
        prefs['cards'].append(card_key)
    save_prefs(user_id, prefs)
    card = CARD_CATALOG.get(card_key, {})
    return f"""✅ تمت إضافة كارت **{card.get('title', card_key)}** {card.get('icon', '📊')} إلى الداشبورد

الآن عندك {len(prefs['cards'])} كارت في الداشبورد"""


def remove_card(user_id: str, card_key: str) -> str:
    """Remove a card from user's dashboard"""
    prefs = get_saved_prefs(user_id)
    if card_key in prefs['cards']:
        prefs['cards'].remove(card_key)
    if card_key not in prefs['hidden']:
        prefs['hidden'].append(card_key)
    save_prefs(user_id, prefs)
    card = CARD_CATALOG.get(card_key, {})
    return f"""🗑️ تمت إزالة كارت **{card.get('title', card_key)}** {card.get('icon', '📊')} من الداشبورد"""


def reset_dashboard(user_id: str, industry: str = "general") -> str:
    """Reset dashboard to default for user's industry"""
    defaults = []
    if "workshop" in industry:
        defaults.extend(["workshop_customers", "workshop_repairs", "workshop_parts", "workshop_invoices"])
    if "hotel" in industry:
        defaults.extend(["hotel_properties", "hotel_bookings", "hotel_rooms", "hotel_occupancy"])
    if "umrah" in industry:
        defaults.extend(["umrah_pilgrims", "umrah_packages", "umrah_groups", "umrah_visas"])
    if not defaults:
        defaults = ["mgmt_employees", "mgmt_revenue", "mgmt_tasks"]
    defaults.extend(["mgmt_employees", "mgmt_revenue"])
    
    prefs = {"cards": list(set(defaults)), "hidden": [], "layout": "grid"}
    save_prefs(user_id, prefs)
    return "🔄 تم إعادة الداشبورد للوضع الافتراضي"


def get_available_cards(industry: str = "general") -> list:
    """List all cards the user can add"""
    by_cat = {}
    for key, card in CARD_CATALOG.items():
        cat = key.split('_')[0]
        if cat == "mgmt" or cat in industry:
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append({"key": key, **card})
    return by_cat


def customize_dashboard(user_id: str, industry: str = "general") -> dict:
    """Return full customizable dashboard data"""
    prefs = get_saved_prefs(user_id)
    
    # If no preferences, use defaults
    if not prefs['cards']:
        if "workshop" in industry:
            prefs['cards'] = ["workshop_customers", "workshop_repairs", "workshop_parts", "workshop_invoices"]
        elif "hotel" in industry:
            prefs['cards'] = ["hotel_properties", "hotel_bookings", "hotel_rooms", "hotel_occupancy"]
        elif "umrah" in industry:
            prefs['cards'] = ["umrah_pilgrims", "umrah_packages", "umrah_groups", "umrah_visas"]
        prefs['cards'].extend(["mgmt_employees", "mgmt_revenue"])
    
    # Build visible cards
    visible_cards = []
    for key in prefs['cards']:
        if key not in prefs.get('hidden', []):
            card = CARD_CATALOG.get(key, {})
            visible_cards.append({
                **card,
                "key": key,
                "value": 0,  # real count from DB
                "link": "/romih/goal"
            })
    
    # Available to add
    available = get_available_cards(industry)
    
    return {
        "cards": visible_cards,
        "hidden_cards": prefs.get('hidden', []),
        "available_to_add": available,
        "layout": prefs.get('layout', 'grid'),
        "customizable": True
    }
