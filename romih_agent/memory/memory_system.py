"""
Romih Agent - Memory System
============================
ذاكرة ثلاثية المستويات: قصيرة + جلسة + طويلة المدى
"""
import json
import os
import time
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MemoryItem:
    content: str
    category: str  # fact, decision, lesson, preference
    timestamp: float = field(default_factory=time.time)
    importance: int = 1  # 1-5
    tags: list[str] = field(default_factory=list)


class ShortTermMemory:
    """ذاكرة قصيرة المدى - المحادثة الحالية"""

    def __init__(self, max_items: int = 50):
        self.items: list[MemoryItem] = []
        self.max_items = max_items

    def add(self, item: MemoryItem):
        self.items.append(item)
        if len(self.items) > self.max_items:
            self._compress()

    def _compress(self):
        """ضغط الذاكرة: الاحتفاظ بالأهم"""
        # نحتفظ بـ 80% الأحدث + 20% الأهم
        recent = self.items[-int(self.max_items * 0.8):]
        important = sorted(self.items[:-int(self.max_items * 0.8)],
                          key=lambda x: x.importance, reverse=True)
        self.items = important[:int(self.max_items * 0.2)] + recent

    def get_context(self, n: int = 20) -> list[MemoryItem]:
        return self.items[-n:]

    def clear(self):
        self.items = []


class SessionMemory:
    """ذاكرة الجلسة - حقائق وتفضيلات"""

    def __init__(self, session_id: str = ""):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.facts: dict[str, str] = {}
        self.preferences: dict[str, str] = {}
        self.decisions: list[dict] = []

    def remember_fact(self, key: str, value: str):
        self.facts[key] = value

    def set_preference(self, key: str, value: str):
        self.preferences[key] = value

    def record_decision(self, context: str, decision: str):
        self.decisions.append({
            "time": datetime.now().isoformat(),
            "context": context,
            "decision": decision
        })

    def get_facts(self) -> dict:
        return self.facts

    def get_preferences(self) -> dict:
        return self.preferences

    def get_summary(self) -> str:
        """ملخص الجلسة الحالية"""
        lines = []
        if self.facts:
            lines.append("حقائق:")
            for k, v in self.facts.items():
                lines.append(f"  • {k}: {v}")
        if self.preferences:
            lines.append("تفضيلات:")
            for k, v in self.preferences.items():
                lines.append(f"  • {k}: {v}")
        if self.decisions:
            lines.append("قرارات:")
            for d in self.decisions[-5:]:
                lines.append(f"  • [{d['time']}] {d['decision']}")
        return "\n".join(lines) if lines else "لا توجد ذاكرة للجلسة"


class LongTermMemory:
    """ذاكرة طويلة المدى - معرفة تراكمية"""

    def __init__(self, storage_path: str = "memory/long_term.json"):
        self.storage_path = storage_path
        self.knowledge: list[MemoryItem] = []
        self._load()

    def _load(self):
        """تحميل الذاكرة من القرص"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge = [MemoryItem(**item) for item in data]

    def _save(self):
        """حفظ الذاكرة للقرص"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump([{
                "content": item.content,
                "category": item.category,
                "timestamp": item.timestamp,
                "importance": item.importance,
                "tags": item.tags
            } for item in self.knowledge], f, ensure_ascii=False, indent=2)

    def add(self, item: MemoryItem):
        """إضافة معرفة جديدة"""
        self.knowledge.append(item)
        self._save()

    def search(self, query: str, limit: int = 5) -> list[MemoryItem]:
        """بحث بسيط في الذاكرة (نصي - لسه هنضيف Vector DB)"""
        results = []
        query_lower = query.lower()
        for item in self.knowledge:
            score = 0
            if query_lower in item.content.lower():
                score += 3
            for tag in item.tags:
                if query_lower in tag.lower():
                    score += 2
            if item.category.lower() in query_lower:
                score += 1
            if score > 0:
                results.append((score, item))
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:limit]]

    def get_recent(self, n: int = 5) -> list[MemoryItem]:
        """آخر المعرفة المضافة"""
        return sorted(self.knowledge,
                     key=lambda x: x.timestamp, reverse=True)[:n]

    def get_lessons(self) -> list[MemoryItem]:
        """الدروس المستفادة"""
        return [item for item in self.knowledge
                if item.category == "lesson"]

    def get_stats(self) -> dict:
        """إحصائيات الذاكرة"""
        categories = {}
        for item in self.knowledge:
            categories[item.category] = categories.get(item.category, 0) + 1
        return {
            "total": len(self.knowledge),
            "categories": categories,
            "last_updated": datetime.fromtimestamp(
                max((i.timestamp for i in self.knowledge), default=0)
            ).isoformat() if self.knowledge else "فارغة"
        }


class MemorySystem:
    """نظام الذاكرة الموحد"""

    def __init__(self, storage_path: str = "memory"):
        self.short_term = ShortTermMemory()
        self.session = SessionMemory()
        self.long_term = LongTermMemory(
            os.path.join(storage_path, "long_term.json")
        )

    def remember(self, content: str, category: str = "fact",
                 importance: int = 3, tags: list[str] = []):
        """تذكر معلومة - تضاف لكل المستويات"""
        item = MemoryItem(
            content=content,
            category=category,
            importance=importance,
            tags=tags
        )
        self.short_term.add(item)
        self.long_term.add(item)

    def learn_lesson(self, problem: str, solution: str):
        """تعلم درس جديد"""
        lesson = f"المشكلة: {problem}\nالحل: {solution}"
        self.remember(lesson, category="lesson", importance=5,
                     tags=["lesson", "repair-notebook"])

    def recall(self, query: str) -> list[MemoryItem]:
        """استدعاء ذاكرة"""
        return self.long_term.search(query)

    def get_daily_summary(self) -> str:
        """ملخص يومي"""
        parts = []
        parts.append("📊 ملخص الجلسة:")
        parts.append(self.session.get_summary())
        parts.append(f"\n📚 الذاكرة طويلة المدى: {self.long_term.get_stats()['total']} عنصر")
        lessons = self.long_term.get_lessons()
        if lessons:
            parts.append(f"\n📝 آخر ٣ دروس:")
            for lesson in lessons[-3:]:
                parts.append(f"  • {lesson.content[:100]}...")
        return "\n".join(parts)
