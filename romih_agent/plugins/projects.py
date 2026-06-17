# -*- coding: utf-8 -*-
"""
Romih Enterprise Plugin - Projects & Tasks
============================================
Manages: projects, tasks, milestones, time tracking.

Fourth institutional plugin — universal for all businesses.
"""
from datetime import datetime
from tools.mcp_connectors import SQLConnector, DBConfig


class ProjectsPlugin:
    
    def __init__(self, db_path: str = "projects.db"):
        self.db = SQLConnector(DBConfig(db_type="sqlite", database=db_path))
        self.db.connect()
        self._setup_schema()
    
    def _setup_schema(self):
        self.db.create_table("projects", {
            "name": "TEXT NOT NULL",
            "description": "TEXT",
            "status": "TEXT DEFAULT 'active'",  # active, completed, on_hold, cancelled
            "priority": "TEXT DEFAULT 'medium'",  # low, medium, high, urgent
            "budget": "REAL DEFAULT 0",
            "start_date": "TEXT",
            "deadline": "TEXT",
            "client": "TEXT",
            "manager": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))"
        })
        
        self.db.create_table("tasks", {
            "project_id": "INTEGER REFERENCES projects(id)",
            "title": "TEXT NOT NULL",
            "description": "TEXT",
            "status": "TEXT DEFAULT 'todo'",  # todo, in_progress, review, done
            "priority": "TEXT DEFAULT 'medium'",
            "assigned_to": "TEXT",  # employee name
            "estimated_hours": "REAL DEFAULT 0",
            "actual_hours": "REAL DEFAULT 0",
            "due_date": "TEXT",
            "created_at": "TEXT DEFAULT (datetime('now'))",
            "completed_at": "TEXT"
        })
    
    # ═══ Projects ═══
    
    def create_project(self, name: str, description: str = "", priority: str = "medium",
                       budget: float = 0, deadline: str = "", client: str = "",
                       manager: str = "") -> dict:
        return self.db.insert("projects", {
            "name": name, "description": description, "priority": priority,
            "budget": budget, "deadline": deadline, "client": client,
            "manager": manager, "start_date": datetime.now().strftime("%Y-%m-%d")
        })
    
    def get_projects(self, status: str = "active") -> list:
        return self.db.query(
            "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
    
    def update_project_status(self, project_id: int, status: str) -> dict:
        self.db.execute("UPDATE projects SET status = ? WHERE id = ?", (status, project_id))
        return {"ok": True, "project_id": project_id, "status": status}
    
    def project_summary(self, project_id: int) -> dict:
        proj = self.db.query("SELECT * FROM projects WHERE id = ?", (project_id,))
        if not proj:
            return {"error": "Project not found"}
        proj = proj[0]
        tasks = self.db.query("""
            SELECT status, COUNT(*) as count FROM tasks
            WHERE project_id = ? GROUP BY status
        """, (project_id,))
        return {"project": proj, "tasks_summary": tasks}
    
    # ═══ Tasks ═══
    
    def add_task(self, project_id: int, title: str, description: str = "",
                 priority: str = "medium", assigned_to: str = "",
                 estimated_hours: float = 0, due_date: str = "") -> dict:
        return self.db.insert("tasks", {
            "project_id": project_id, "title": title, "description": description,
            "priority": priority, "assigned_to": assigned_to,
            "estimated_hours": estimated_hours, "due_date": due_date
        })
    
    def get_tasks(self, project_id: int = None, status: str = None,
                  assigned_to: str = None) -> list:
        conditions = []
        params = []
        if project_id:
            conditions.append("t.project_id = ?")
            params.append(project_id)
        if status:
            conditions.append("t.status = ?")
            params.append(status)
        if assigned_to:
            conditions.append("t.assigned_to = ?")
            params.append(assigned_to)
        
        where = " AND ".join(conditions) if conditions else "1=1"
        return self.db.query(f"""
            SELECT t.*, p.name as project_name FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE {where} ORDER BY t.priority DESC, t.due_date ASC LIMIT 50
        """, tuple(params))
    
    def update_task_status(self, task_id: int, status: str) -> dict:
        if status == "done":
            self.db.execute(
                "UPDATE tasks SET status = ?, completed_at = datetime('now') WHERE id = ?",
                (status, task_id)
            )
        else:
            self.db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        return {"ok": True, "task_id": task_id, "status": status}
    
    def assign_task(self, task_id: int, person: str) -> dict:
        self.db.execute("UPDATE tasks SET assigned_to = ? WHERE id = ?", (person, task_id))
        return {"ok": True, "task_id": task_id, "assigned_to": person}
    
    # ═══ Reports ═══
    
    def overdue_tasks(self) -> list:
        return self.db.query("""
            SELECT t.*, p.name as project_name FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE t.status NOT IN ('done') AND t.due_date < date('now')
            ORDER BY t.due_date ASC
        """)
    
    def my_tasks(self, person: str) -> list:
        return self.db.query("""
            SELECT t.*, p.name as project_name FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE t.assigned_to = ? AND t.status != 'done'
            ORDER BY t.priority DESC, t.due_date ASC
        """, (person,))
    
    def dashboard(self) -> dict:
        """Project management dashboard"""
        active_projects = self.db.query(
            "SELECT COUNT(*) as c FROM projects WHERE status = 'active'"
        )
        tasks_by_status = self.db.query("""
            SELECT status, COUNT(*) as count FROM tasks GROUP BY status
        """)
        overdue = self.overdue_tasks()
        today_done = self.db.query("""
            SELECT COUNT(*) as c FROM tasks
            WHERE status = 'done' AND date(completed_at) = date('now')
        """)
        urgent = self.db.query(
            "SELECT COUNT(*) as c FROM tasks WHERE priority = 'urgent' AND status != 'done'"
        )
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "active_projects": active_projects[0]["c"] if active_projects else 0,
            "tasks_by_status": {r["status"]: r["count"] for r in tasks_by_status} if tasks_by_status else {},
            "overdue_tasks": len(overdue),
            "overdue_details": overdue[:5],
            "completed_today": today_done[0]["c"] if today_done else 0,
            "urgent_pending": urgent[0]["c"] if urgent else 0
        }
    
    def close(self):
        self.db.close()
