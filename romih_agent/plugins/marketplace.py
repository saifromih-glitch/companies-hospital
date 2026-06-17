# -*- coding: utf-8 -*-
"""
Romih Plugin Marketplace
=========================
SaaS-style plugin catalog: browse, activate, deactivate.
Integrated with Onboarding for auto-activation.
"""
import json, os
from datetime import datetime
from dataclasses import dataclass, field
from tools.registry import Tool, RiskLevel, ToolParam

MARKET_FILE = "analytics_data/marketplace.json"
os.makedirs("analytics_data", exist_ok=True)


@dataclass
class Plugin:
    """A marketplace plugin listing"""
    id: str
    name_ar: str
    name_en: str
    icon: str
    description_ar: str
    features: list
    tier: str  # basic, professional, enterprise
    category: str
    price_monthly: int = 0  # 0 = included in base
    active: bool = True  # available in marketplace
    auto_with: list = field(default_factory=list)  # industries that auto-activate


# Plugin catalog
CATALOG = [
    Plugin(
        id="workshop", name_ar="إدارة الورش", name_en="Workshop",
        icon="🏭", tier="professional", category="operations",
        description_ar="إدارة كاملة للورشة: عملاء، تصليحات، قطع غيار، فواتير، تقارير يومية",
        features=["إضافة وإدارة العملاء", "تسجيل التصليحات ومتابعتها", "إدارة قطع الغيار والمخزون", "إنشاء الفواتير", "تقرير يومي"],
        auto_with=["workshop"]
    ),
    Plugin(
        id="hotels", name_ar="إدارة الفنادق", name_en="Hotels",
        icon="🏨", tier="enterprise", category="hospitality",
        description_ar="إدارة الفنادق والشقق المفروشة: عقارات، غرف، حجوزات، صيانة، عقود",
        features=["إضافة العقارات والغرف", "إدارة الحجوزات", "متابعة الصيانة", "عقود الإيجار", "تقارير الإشغال والإيرادات"],
        auto_with=["hotel"]
    ),
    Plugin(
        id="umrah", name_ar="العمرة والحج", name_en="Umrah & Hajj",
        icon="🕋", tier="enterprise", category="hospitality",
        description_ar="إدارة رحلات العمرة والحج: باقات، حجاج، مجموعات، إعاشة، نقل",
        features=["إدارة باقات العمرة والحج", "تسجيل الحجاج وإدارة الجوازات", "تنظيم المجموعات", "خدمات الإعاشة", "النقل والمواصلات", "تقارير الرحلات"],
        auto_with=["umrah"]
    ),
    Plugin(
        id="hr", name_ar="الموارد البشرية", name_en="Human Resources",
        icon="👥", tier="professional", category="management",
        description_ar="إدارة الموظفين: حضور، رواتب، إجازات، تقييمات أداء",
        features=["إدارة الموظفين", "كشف الحضور", "إدارة الرواتب", "الإجازات والطلبات", "تقييم الأداء"],
        auto_with=["general", "retail", "construction", "healthcare", "education", "workshop", "hotel", "umrah"]
    ),
    Plugin(
        id="finance", name_ar="المالية", name_en="Finance",
        icon="💰", tier="professional", category="management",
        description_ar="إدارة الحسابات: فواتير، مصروفات، تقارير مالية",
        features=["إنشاء الفواتير", "تسجيل المصروفات", "إدارة الحسابات", "تقارير مالية"],
        auto_with=["general", "retail", "construction", "healthcare", "education", "workshop", "hotel", "umrah"]
    ),
    Plugin(
        id="projects", name_ar="المشاريع", name_en="Projects",
        icon="📋", tier="professional", category="management",
        description_ar="إدارة المشاريع والمهام: إنشاء مشاريع، توزيع مهام، متابعة التقدم",
        features=["إنشاء المشاريع", "توزيع المهام", "متابعة التقدم", "تقارير المشاريع"],
        auto_with=["general", "construction"]
    ),
    Plugin(
        id="onboarding", name_ar="المقابلة التعريفية", name_en="Onboarding",
        icon="🧠", tier="basic", category="system",
        description_ar="مقابلة ذكية لتخصيص Romih حسب مجالك واحتياجاتك",
        features=["تحديد مجال العمل", "تفعيل تلقائي للبلجنز", "ملف تعريفي دائم"],
        auto_with=[]  # always active
    ),
]


class Marketplace:
    """Plugin marketplace with per-user activation"""
    
    def __init__(self):
        self.catalog = CATALOG
        self.activations = {}  # {user_id: [plugin_ids]}
        self._load()
    
    def _load(self):
        if os.path.exists(MARKET_FILE):
            try:
                with open(MARKET_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.activations = data.get("activations", {})
            except:
                pass
    
    def _save(self):
        with open(MARKET_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "activations": self.activations,
                "last_updated": datetime.now().isoformat(),
                "total_plugins": len(self.catalog)
            }, f, ensure_ascii=False, indent=2)
    
    def list_plugins(self, tier: str = "", user_id: str = "") -> dict:
        """List available plugins with activation status"""
        plugins = []
        user_plugins = self.activations.get(user_id, [])
        
        for p in self.catalog:
            if not p.active:
                continue
            if tier and p.tier != tier:
                continue
            
            plugins.append({
                "id": p.id,
                "name": p.name_ar,
                "icon": p.icon,
                "description": p.description_ar,
                "features": p.features[:5],
                "tier": p.tier,
                "category": p.category,
                "price": f"${p.price_monthly}/month" if p.price_monthly else "مضمن",
                "activated": p.id in user_plugins
            })
        
        return {
            "total": len(plugins),
            "user_activated": len(user_plugins),
            "plugins": plugins
        }
    
    def activate(self, plugin_id: str, user_id: str) -> dict:
        """Activate a plugin for a user"""
        # Check plugin exists
        plugin = next((p for p in self.catalog if p.id == plugin_id), None)
        if not plugin:
            return {"ok": False, "error": f"Plugin '{plugin_id}' not found"}
        
        if user_id not in self.activations:
            self.activations[user_id] = []
        
        if plugin_id in self.activations[user_id]:
            return {"ok": True, "message": f"Plugin {plugin.icon} {plugin.name_ar} already activated"}
        
        self.activations[user_id].append(plugin_id)
        self._save()
        return {"ok": True, "message": f"Activated {plugin.icon} {plugin.name_ar}"}
    
    def deactivate(self, plugin_id: str, user_id: str) -> dict:
        """Deactivate a plugin for a user"""
        if user_id not in self.activations:
            return {"ok": False, "error": "No plugins activated"}
        
        if plugin_id not in self.activations[user_id]:
            return {"ok": False, "error": f"Plugin '{plugin_id}' not active"}
        
        # Prevent deactivating system plugins
        if plugin_id == "onboarding":
            return {"ok": False, "error": "Cannot deactivate system plugin"}
        
        self.activations[user_id].remove(plugin_id)
        self._save()
        plugin = next((p for p in self.catalog if p.id == plugin_id), None)
        return {"ok": True, "message": f"Deactivated {plugin.icon} {plugin_id}"}
    
    def auto_activate(self, industries: list, user_id: str) -> list:
        """Auto-activate plugins based on industry (called from Onboarding)"""
        if user_id not in self.activations:
            self.activations[user_id] = []
        
        activated = []
        for plugin in self.catalog:
            if not plugin.active:
                continue
            for industry in industries:
                if industry in plugin.auto_with and plugin.id not in self.activations[user_id]:
                    self.activations[user_id].append(plugin.id)
                    activated.append(plugin.name_ar)
                    break
        
        self._save()
        return activated
    
    def user_status(self, user_id: str) -> dict:
        """Get a user's marketplace status"""
        user_plugins = self.activations.get(user_id, [])
        active_details = []
        for pid in user_plugins:
            p = next((p for p in self.catalog if p.id == pid), None)
            if p:
                active_details.append({"id": p.id, "name": p.name_ar, "icon": p.icon, "tier": p.tier})
        
        return {
            "activated_count": len(user_plugins),
            "available_count": len([p for p in self.catalog if p.active]),
            "active_plugins": active_details
        }


# ═══════════════════════════════════════
# 🔌 Registration
# ═══════════════════════════════════════

_market = Marketplace()


def register(tools_registry):
    tools_registry.register(Tool(
        name="marketplace_list",
        description="Browse available plugins in the marketplace",
        category="marketplace",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="user_id", type="string", description="Your user ID", required=False),
            ToolParam(name="tier", type="string", description="Filter: basic, professional, enterprise", required=False)
        ],
        execute=lambda user_id="", tier="", **_: _market.list_plugins(tier, user_id)
    ))
    
    tools_registry.register(Tool(
        name="marketplace_activate",
        description="Activate a plugin from the marketplace",
        category="marketplace",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="plugin_id", type="string", description="Plugin ID to activate", required=True),
            ToolParam(name="user_id", type="string", description="Your user ID", required=True)
        ],
        execute=lambda plugin_id, user_id, **_: _market.activate(plugin_id, user_id)
    ))
    
    tools_registry.register(Tool(
        name="marketplace_deactivate",
        description="Deactivate a plugin",
        category="marketplace",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="plugin_id", type="string", description="Plugin ID to deactivate", required=True),
            ToolParam(name="user_id", type="string", description="Your user ID", required=True)
        ],
        execute=lambda plugin_id, user_id, **_: _market.deactivate(plugin_id, user_id)
    ))
    
    tools_registry.register(Tool(
        name="marketplace_status",
        description="Show your current marketplace status",
        category="marketplace",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="user_id", type="string", description="Your user ID", required=True)],
        execute=lambda user_id, **_: _market.user_status(user_id)
    ))
    
    print("Marketplace: 4 tools registered (list, activate, deactivate, status)")
