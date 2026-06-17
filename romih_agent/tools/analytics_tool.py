# -*- coding: utf-8 -*-
"""
Romih Analytics & Compounding Knowledge
========================================
Usage Analytics: track tools, users, time saved
Compounding Knowledge: learn from all users, share insights
"""
import json, os, time
from datetime import datetime, timedelta
from collections import defaultdict
from tools.registry import Tool, RiskLevel, ToolParam

DATA_DIR = "analytics_data"
os.makedirs(DATA_DIR, exist_ok=True)


# ═══════════════════════════════════════
# 📊 Usage Analytics
# ═══════════════════════════════════════

class Analytics:
    """Track and analyze Romih usage"""
    
    def __init__(self):
        self.log_path = os.path.join(DATA_DIR, "usage_log.jsonl")
        self._load()
    
    def _load(self):
        self.events = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.events.append(json.loads(line))
            except:
                pass
    
    def track(self, event_type: str, user_id: str = "", **kwargs):
        """Record an event"""
        event = {
            "type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.events.append(event)
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    def summary(self, user_id: str = "", days: int = 7) -> dict:
        """Generate usage summary"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.events 
                  if datetime.fromisoformat(e["timestamp"]) > cutoff
                  and (not user_id or e.get("user_id") == user_id)]
        
        tools_used = defaultdict(int)
        plugins_used = defaultdict(int)
        total_queries = 0
        total_tasks = 0
        errors = 0
        
        for e in recent:
            if e["type"] == "tool_call":
                tools_used[e.get("tool", "unknown")] += 1
            elif e["type"] == "plugin":
                plugins_used[e.get("plugin", "unknown")] += 1
            elif e["type"] == "query":
                total_queries += 1
            elif e["type"] == "task_complete":
                total_tasks += 1
            elif e["type"] == "error":
                errors += 1
        
        top_tools = sorted(tools_used.items(), key=lambda x: x[1], reverse=True)[:5]
        top_plugins = sorted(plugins_used.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Estimate time saved: ~5 min per tool call
        time_saved_min = total_tasks * 5
        
        return {
            "period": f"{days} days",
            "total_queries": total_queries,
            "total_tasks": total_tasks,
            "errors": errors,
            "accuracy": f"{(1 - errors/max(total_tasks,1))*100:.1f}%",
            "time_saved_hours": round(time_saved_min / 60, 1),
            "top_tools": [{"name": t, "count": c} for t, c in top_tools],
            "top_plugins": [{"name": t, "count": c} for t, c in top_plugins],
            "total_events": len(recent)
        }
    
    def weekly_report(self, user_id: str = "") -> str:
        """Generate a human-readable weekly report in Arabic"""
        s = self.summary(user_id, days=7)
        return f"""📊 **تقرير Romih الأسبوعي**
        
🔄 **النشاط:**
• استفسارات: {s['total_queries']}
• مهام مكتملة: {s['total_tasks']}
• الدقة: {s['accuracy']}

⏱️ **الوقت الموفّر:**
• {s['time_saved_hours']} ساعة هذا الأسبوع

🔧 **الأدوات الأكثر استخداماً:**
{chr(10).join([f'  {i+1}. {t["name"]} ({t["count"]}x)' for i, t in enumerate(s['top_tools'][:3])]) or '  لا يوجد'}

📈 **إجمالي الأحداث:** {s['total_events']}

━━━━━━━━━━━━━━━━━━
Romih Agent — مساعدك الذكي 🌸"""


# ═══════════════════════════════════════
# 🧠 Compounding Knowledge
# ═══════════════════════════════════════

class CompoundingKnowledge:
    """
    Learn from all users. Every successful solution 
    feeds back into the system for future users.
    """
    
    def __init__(self):
        self.path = os.path.join(DATA_DIR, "knowledge_base.json")
        self._load()
    
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.patterns = data.get("patterns", [])
                self.insights = data.get("insights", {})
                self.stats = data.get("stats", {"total_learned": 0, "total_reused": 0})
            except:
                self._reset()
        else:
            self._reset()
    
    def _reset(self):
        self.patterns = []  # [{query_pattern, solution, success_count, plugin, tags}]
        self.insights = {}  # {insight_key: {value, confidence, source}}
        self.stats = {"total_learned": 0, "total_reused": 0}
    
    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump({
                "patterns": self.patterns,
                "insights": self.insights,
                "stats": self.stats,
                "last_updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def learn(self, query: str, solution: str, plugin: str = "", tags: list = None) -> dict:
        """Learn from a successful interaction"""
        # Extract key pattern (first 100 chars of query as template)
        pattern = query[:100].strip()
        
        # Check if similar pattern exists
        for p in self.patterns:
            if p["query_pattern"][:50] == pattern[:50]:
                p["success_count"] += 1
                p["solution"] = solution  # Update with latest
                self.stats["total_learned"] += 1
                self._save()
                return {"ok": True, "message": f"Updated existing pattern (used {p['success_count']}x)"}
        
        # New pattern
        self.patterns.append({
            "query_pattern": pattern,
            "solution": solution[:500],
            "success_count": 1,
            "plugin": plugin,
            "tags": tags or [],
            "created_at": datetime.now().isoformat()
        })
        self.stats["total_learned"] += 1
        self._save()
        return {"ok": True, "message": "New pattern learned"}
    
    def find(self, query: str, limit: int = 3) -> list:
        """Find relevant patterns for a query"""
        query_lower = query.lower()
        matches = []
        
        for p in self.patterns:
            score = 0
            pattern_lower = p["query_pattern"].lower()
            
            # Simple keyword matching
            keywords = query_lower.split()
            for kw in keywords:
                if len(kw) > 2 and kw in pattern_lower:
                    score += 1
            
            # Boost by success count
            score *= (1 + min(p["success_count"] / 10, 1))
            
            if score > 0:
                matches.append((score, p))
        
        matches.sort(key=lambda x: x[0], reverse=True)
        results = [{"pattern": m[1]["query_pattern"], "solution": m[1]["solution"], 
                     "used": m[1]["success_count"], "score": round(m[0], 1)} 
                   for m in matches[:limit]]
        
        if matches:
            self.stats["total_reused"] += 1
            self._save()
        
        return results
    
    def collective_insight(self, key: str, value: str = "", confidence: float = 0.0) -> dict:
        """Store or retrieve a collective insight"""
        if value:
            if key in self.insights:
                old = self.insights[key]
                # Weighted average for confidence
                new_conf = (old["confidence"] * 0.7 + confidence * 0.3)
                self.insights[key] = {"value": value, "confidence": new_conf, "source": "collective"}
            else:
                self.insights[key] = {"value": value, "confidence": confidence, "source": "collective"}
            self._save()
            return {"ok": True, "insight": key, "confidence": self.insights[key]["confidence"]}
        else:
            if key in self.insights:
                return {"ok": True, "insight": self.insights[key]}
            return {"ok": False, "message": "Insight not found"}
    
    def top_patterns(self, limit: int = 10) -> list:
        """Get most successful patterns"""
        sorted_p = sorted(self.patterns, key=lambda x: x["success_count"], reverse=True)
        return [{"pattern": p["query_pattern"][:80], "used": p["success_count"], 
                 "plugin": p["plugin"]} for p in sorted_p[:limit]]


# ═══════════════════════════════════════
# 🔌 Tool Registration
# ═══════════════════════════════════════

_analytics = Analytics()
_knowledge = CompoundingKnowledge()


def register(tools_registry):
    # Analytics tools
    tools_registry.register(Tool(
        name="analytics_summary",
        description="Get usage summary for the past N days",
        category="analytics",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="days", type="number", description="Number of days (default 7)", required=False),
            ToolParam(name="user_id", type="string", description="Specific user ID", required=False)
        ],
        execute=lambda days=7, user_id="", **_: _analytics.summary(user_id, days)
    ))
    
    tools_registry.register(Tool(
        name="analytics_report",
        description="Generate a weekly usage report in Arabic",
        category="analytics",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="user_id", type="string", description="User ID", required=False)],
        execute=lambda user_id="", **_: {"report": _analytics.weekly_report(user_id)}
    ))
    
    # Compounding Knowledge tools
    tools_registry.register(Tool(
        name="knowledge_learn",
        description="Learn from a successful interaction and save the pattern",
        category="knowledge",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="query", type="string", description="The query or problem", required=True),
            ToolParam(name="solution", type="string", description="The solution that worked", required=True),
            ToolParam(name="plugin", type="string", description="Related plugin", required=False),
            ToolParam(name="tags", type="string", description="Comma-separated tags", required=False)
        ],
        execute=lambda query, solution, plugin="", tags="", **_: 
            _knowledge.learn(query, solution, plugin, [t.strip() for t in tags.split(",") if t.strip()] if tags else [])
    ))
    
    tools_registry.register(Tool(
        name="knowledge_find",
        description="Find relevant past solutions for a new query",
        category="knowledge",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="query", type="string", description="Search query", required=True),
            ToolParam(name="limit", type="number", description="Max results (default 3)", required=False)
        ],
        execute=lambda query, limit=3, **_: {"matches": _knowledge.find(query, limit)}
    ))
    
    tools_registry.register(Tool(
        name="knowledge_top",
        description="Show most successful learned patterns",
        category="knowledge",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="limit", type="number", description="Max results (default 10)", required=False)],
        execute=lambda limit=10, **_: {"top_patterns": _knowledge.top_patterns(limit)}
    ))
    
    tools_registry.register(Tool(
        name="knowledge_stats",
        description="Show knowledge base statistics",
        category="knowledge",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: _knowledge.stats
    ))
    
    print("Analytics: 6 tools registered (2 analytics + 4 knowledge)")
