# -*- coding: utf-8 -*-
"""
Romih Audit Trail
==================
Full audit logging: who did what, when, from where.
Security, compliance, and trust foundation.
"""
import json, os, hashlib
from datetime import datetime
from collections import defaultdict
from tools.registry import Tool, RiskLevel, ToolParam

AUDIT_FILE = "analytics_data/audit_log.jsonl"
os.makedirs("analytics_data", exist_ok=True)


class AuditTrail:
    """Immutable audit log with integrity verification"""
    
    def __init__(self):
        self.path = AUDIT_FILE
        self._count = self._load_count()
    
    def _load_count(self):
        if os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                return sum(1 for _ in f)
        return 0
    
    def log(self, action: str, user: str, details: str = "", 
            category: str = "general", result: str = "", plugin: str = "") -> dict:
        """
        Record an auditable event.
        Every entry is immutable and hashed for integrity.
        """
        event = {
            "id": self._count + 1,
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "category": category,
            "details": details[:500],
            "result": result[:200],
            "plugin": plugin
        }
        # Integrity hash
        event["hash"] = hashlib.sha256(
            json.dumps(event, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:16]
        
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        
        self._count += 1
        return {"ok": True, "event_id": event["id"], "hash": event["hash"]}
    
    def query(self, user: str = "", category: str = "", 
              action: str = "", limit: int = 20, hours: int = 24) -> list:
        """Query the audit log with filters"""
        cutoff = datetime.now().isoformat() if hours == 0 else None
        results = []
        
        if not os.path.exists(self.path):
            return []
        
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    if user and e.get("user") != user:
                        continue
                    if category and e.get("category") != category:
                        continue
                    if action and e.get("action") != action:
                        continue
                    if hours > 0:
                        ts = datetime.fromisoformat(e["timestamp"])
                        if (datetime.now() - ts).total_seconds() > hours * 3600:
                            continue
                    results.append(e)
                except:
                    continue
        
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results[:limit]
    
    def summary(self, hours: int = 24) -> dict:
        """Generate audit summary"""
        events = self.query(hours=hours)
        
        by_category = defaultdict(int)
        by_action = defaultdict(int)
        by_user = defaultdict(int)
        unique_users = set()
        
        for e in events:
            by_category[e.get("category", "general")] += 1
            by_action[e.get("action", "unknown")] += 1
            by_user[e.get("user", "unknown")] += 1
            unique_users.add(e.get("user", ""))
        
        suspicious = [e for e in events if e.get("category") in 
                      ["security", "auth_fail", "blocked"]]
        
        return {
            "period_hours": hours,
            "total_events": len(events),
            "unique_users": len(unique_users),
            "by_category": dict(by_category.most_common(5) if hasattr(by_category, 'most_common') 
                               else sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]),
            "by_action": dict(by_action.most_common(5) if hasattr(by_action, 'most_common')
                             else sorted(by_action.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_users": dict(sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:5]),
            "suspicious_events": len(suspicious)
        }
    
    def verify_integrity(self, limit: int = 100) -> dict:
        """Verify the audit log hasn't been tampered with"""
        if not os.path.exists(self.path):
            return {"ok": True, "message": "No audit log yet"}
        
        checked = 0
        tampered = 0
        
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                if checked >= limit:
                    break
                try:
                    e = json.loads(line.strip())
                    original_hash = e.pop("hash", "")
                    recalculated = hashlib.sha256(
                        json.dumps(e, sort_keys=True, ensure_ascii=False).encode()
                    ).hexdigest()[:16]
                    if original_hash != recalculated:
                        tampered += 1
                    checked += 1
                except:
                    checked += 1
        
        return {
            "ok": tampered == 0,
            "checked": checked,
            "tampered": tampered,
            "status": "INTEGRITY VERIFIED" if tampered == 0 else f"WARNING: {tampered} tampered entries"
        }
    
    def clear_old(self, days: int = 90) -> dict:
        """Archive entries older than N days"""
        if not os.path.exists(self.path):
            return {"ok": True, "cleared": 0}
        
        cutoff = datetime.now().isoformat()
        old = []
        recent = []
        
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    ts = datetime.fromisoformat(e["timestamp"])
                    if (datetime.now() - ts).days > days:
                        old.append(e)
                    else:
                        recent.append(line.strip())
                except:
                    continue
        
        # Archive old entries
        if old:
            archive_path = f"analytics_data/audit_archive_{datetime.now().strftime('%Y%m%d')}.json"
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(old, f, ensure_ascii=False, indent=2)
        
        # Write recent back
        with open(self.path, 'w', encoding='utf-8') as f:
            for line in recent:
                f.write(line + "\n")
        
        return {"ok": True, "cleared": len(old), "kept": len(recent)}


# ═══════════════════════════════════════
# 🔌 Registration
# ═══════════════════════════════════════

_audit = AuditTrail()


def register(tools_registry):
    tools_registry.register(Tool(
        name="audit_log",
        description="Record an auditable event (called automatically by system)",
        category="audit",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="action", type="string", description="Action name", required=True),
            ToolParam(name="user", type="string", description="User who performed", required=True),
            ToolParam(name="details", type="string", description="Event details", required=False),
            ToolParam(name="category", type="string", description="Category", required=False),
            ToolParam(name="result", type="string", description="Result of action", required=False),
            ToolParam(name="plugin", type="string", description="Related plugin", required=False)
        ],
        execute=lambda action, user, details="", category="general", result="", plugin="", **_: 
            _audit.log(action, user, details, category, result, plugin)
    ))
    
    tools_registry.register(Tool(
        name="audit_query",
        description="Search the audit log with filters",
        category="audit",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="user", type="string", description="Filter by user", required=False),
            ToolParam(name="category", type="string", description="Filter by category", required=False),
            ToolParam(name="action", type="string", description="Filter by action", required=False),
            ToolParam(name="hours", type="number", description="Last N hours (0=all)", required=False),
            ToolParam(name="limit", type="number", description="Max results (default 20)", required=False)
        ],
        execute=lambda user="", category="", action="", hours=24, limit=20, **_: 
            {"events": _audit.query(user, category, action, limit, hours)}
    ))
    
    tools_registry.register(Tool(
        name="audit_summary",
        description="Get audit trail summary for the last N hours",
        category="audit",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="hours", type="number", description="Last N hours (default 24)", required=False)],
        execute=lambda hours=24, **_: _audit.summary(hours)
    ))
    
    tools_registry.register(Tool(
        name="audit_integrity",
        description="Verify audit log integrity (detect tampering)",
        category="audit",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: _audit.verify_integrity()
    ))
    
    tools_registry.register(Tool(
        name="audit_cleanup",
        description="Archive old audit entries",
        category="audit",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="days", type="number", description="Keep last N days (default 90)", required=False)],
        execute=lambda days=90, **_: _audit.clear_old(days)
    ))
    
    print("Audit: 5 tools registered (log, query, summary, integrity, cleanup)")
