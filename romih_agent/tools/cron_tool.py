# -*- coding: utf-8 -*-
"""Cron/Scheduler for Romih Agent — reminders and recurring tasks."""
import json, os, asyncio, threading
from datetime import datetime, timedelta
from tools.registry import Tool, RiskLevel, ToolParam

CRON_FILE = "cron_jobs.json"


class CronScheduler:
    """Simple in-memory scheduler with persistent storage"""
    
    def __init__(self, filepath: str = CRON_FILE):
        self.filepath = filepath
        self.jobs = []  # [{id, task, time, interval, chat_id, created_at}]
        self.running = False
        self._thread = None
        self._load()
    
    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.jobs = json.load(f)
            except:
                self.jobs = []
    
    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, ensure_ascii=False, indent=2)
    
    def add(self, task: str, when: str, chat_id: int = 0, recurring: str = "") -> dict:
        """
        Add a cron job.
        when: "in 30min", "at 15:00", "every day 08:00", "every monday 09:00"
        """
        job_id = str(len(self.jobs) + 1)
        job = {
            "id": job_id,
            "task": task,
            "when": when,
            "recurring": recurring,
            "chat_id": chat_id,
            "created_at": datetime.now().isoformat(),
            "enabled": True,
            "last_run": None
        }
        self.jobs.append(job)
        self._save()
        return {"ok": True, "message": f"\u2705 \u062A\u0645 \u062C\u062F\u0648\u0644\u0629 \u0627\u0644\u062A\u0630\u0643\u064A\u0631: {task} ({when})", "job_id": job_id}
    
    def list(self, chat_id: int = 0) -> list:
        active = [j for j in self.jobs if j.get("enabled", True)]
        if chat_id:
            active = [j for j in active if j["chat_id"] == chat_id]
        return active
    
    def remove(self, job_id: str) -> dict:
        for j in self.jobs:
            if j["id"] == job_id:
                j["enabled"] = False
                self._save()
                return {"ok": True, "message": f"\u274C \u062A\u0645 \u0625\u0644\u063A\u0627\u0621 \u0627\u0644\u062A\u0630\u0643\u064A\u0631"}
        return {"ok": False, "error": "\u0627\u0644\u062A\u0630\u0643\u064A\u0631 \u063A\u064A\u0631 \u0645\u0648\u062C\u0648\u062F"}
    
    def clear(self, chat_id: int = 0):
        before = len(self.jobs)
        self.jobs = [j for j in self.jobs if j["chat_id"] != chat_id]
        self._save()
        return {"ok": True, "message": f"\u062A\u0645 \u062D\u0630\u0641 {before - len(self.jobs)} \u062A\u0630\u0643\u064A\u0631"}

_scheduler = CronScheduler()


def register(tools_registry):
    tools_registry.register(Tool(
        name="cron_add",
        description="Schedule a reminder or recurring task. When can be: 'in Xmin', 'at HH:MM', 'every day HH:MM', 'every monday HH:MM'",
        category="system",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="task", type="string", description="What to remind about", required=True),
            ToolParam(name="when", type="string", description="When: 'in 30min', 'at 15:00', 'every day 08:00', 'every monday 09:00'", required=True),
            ToolParam(name="chat_id", type="number", description="Telegram chat ID", required=False)
        ],
        execute=lambda task, when, chat_id=0, **_: _scheduler.add(task, when, chat_id)
    ))
    
    tools_registry.register(Tool(
        name="cron_list",
        description="List all active reminders",
        category="system",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="chat_id", type="number", description="Telegram chat ID", required=False)],
        execute=lambda chat_id=0, **_: {"ok": True, "jobs": _scheduler.list(chat_id)}
    ))
    
    tools_registry.register(Tool(
        name="cron_remove",
        description="Cancel a reminder by ID",
        category="system",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="job_id", type="string", description="Reminder ID (from cron_list)", required=True)],
        execute=lambda job_id, **_: _scheduler.remove(job_id)
    ))
    
    tools_registry.register(Tool(
        name="cron_clear",
        description="Clear all reminders for a chat",
        category="system",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="chat_id", type="number", description="Telegram chat ID", required=True)],
        execute=lambda chat_id, **_: _scheduler.clear(chat_id)
    ))
    
    print("Cron: 4 tools registered (add, list, remove, clear)")
