# -*- coding: utf-8 -*-
"""Register Projects Plugin as tools."""
from tools.registry import Tool, RiskLevel, ToolParam
from plugins.projects import ProjectsPlugin


def register(tools_registry):
    pj = ProjectsPlugin(db_path="projects.db")
    
    # Project tools
    tools_registry.register(Tool(
        name="pj_create_project",
        description="Create a new project with name, priority, budget, deadline",
        category="projects",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="name", type="string", description="Project name", required=True),
        ],
        execute=lambda name, priority="medium", deadline="", client="", budget=0, **_: 
            pj.create_project(name, priority=priority, deadline=deadline, client=client, budget=float(budget))
    ))
    
    tools_registry.register(Tool(
        name="pj_list_projects",
        description="List all active projects",
        category="projects",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"projects": pj.get_projects()}
    ))
    
    tools_registry.register(Tool(
        name="pj_project_summary",
        description="Get summary of a project including task breakdown",
        category="projects",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="project_id", type="int", description="Project ID", required=True)],
        execute=lambda project_id, **_: pj.project_summary(int(project_id))
    ))
    
    # Task tools
    tools_registry.register(Tool(
        name="pj_add_task",
        description="Add a task to a project. Can assign to person, set priority, due date.",
        category="projects",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="project_id", type="int", description="Project ID", required=True),
            ToolParam(name="title", type="string", description="Task title", required=True),
            ToolParam(name="assigned_to", type="string", description="Who is responsible", required=False),
            ToolParam(name="due_date", type="string", description="Deadline YYYY-MM-DD", required=False),
        ],
        execute=lambda project_id, title, assigned_to="", priority="medium", due_date="", **_: 
            pj.add_task(int(project_id), title, assigned_to=assigned_to, priority=priority, due_date=due_date)
    ))
    
    tools_registry.register(Tool(
        name="pj_list_tasks",
        description="List tasks by project, status, or person",
        category="projects",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="project_id", type="int", description="Project ID (optional)", required=False),
            ToolParam(name="status", type="string", description="todo/in_progress/review/done", required=False),
        ],
        execute=lambda project_id=None, status=None, **_: 
            {"tasks": pj.get_tasks(int(project_id) if project_id else None, status)}
    ))
    
    tools_registry.register(Tool(
        name="pj_update_task",
        description="Update task status: todo, in_progress, review, done",
        category="projects",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="task_id", type="int", description="Task ID", required=True),
            ToolParam(name="status", type="string", description="New status", required=True),
        ],
        execute=lambda task_id, status, **_: pj.update_task_status(int(task_id), status)
    ))
    
    tools_registry.register(Tool(
        name="pj_assign_task",
        description="Assign a task to someone",
        category="projects",
        risk=RiskLevel.LOW,
        params=[
            ToolParam(name="task_id", type="int", description="Task ID", required=True),
            ToolParam(name="person", type="string", description="Person name", required=True),
        ],
        execute=lambda task_id, person, **_: pj.assign_task(int(task_id), person)
    ))
    
    tools_registry.register(Tool(
        name="pj_my_tasks",
        description="Show my pending tasks (tasks assigned to me)",
        category="projects",
        risk=RiskLevel.LOW,
        params=[ToolParam(name="person", type="string", description="Your name", required=True)],
        execute=lambda person, **_: {"my_tasks": pj.my_tasks(person)}
    ))
    
    # Reports
    tools_registry.register(Tool(
        name="pj_overdue",
        description="Show all overdue tasks (past deadline, not done)",
        category="projects",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: {"overdue": pj.overdue_tasks()}
    ))
    
    tools_registry.register(Tool(
        name="pj_dashboard",
        description="Project dashboard: active projects, tasks by status, overdue, completed today",
        category="projects",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: pj.dashboard()
    ))
    
    print("Projects: 10 tools registered (projects=3, tasks=5, reports=2)")
