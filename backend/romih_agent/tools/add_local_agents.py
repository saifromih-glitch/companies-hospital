"""Add Hermes+Mimo+Pi Agent skills to registry.py"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

LOCAL_SKILLS_CODE = '''
    def _register_local_agents(self):
        """Register Hermes, Mimo, Pi Agent as tools"""
        from tools.local_agents import ALL_LOCAL_SKILLS

        local_tools = [
            # Hermes Agent v0.15.2
            ("hermes_code", "hermes_code", "Hermes: Full coding task (analyze-build-test)", "dev", "MEDIUM",
                [("task", "str", "Programming task"), ("model", "str", "Model", False, "ollama/gemma4:12b")], False),
            ("hermes_refactor", "hermes_refactor", "Hermes: Refactor and improve code", "dev", "MEDIUM",
                [("file_path", "str", "File to refactor"), ("instructions", "str", "Refactoring instructions")], False),
            ("hermes_debug", "hermes_debug", "Hermes: Debug from error logs", "dev", "LOW",
                [("error_log", "str", "Error log"), ("file_path", "str", "File path", False, "")], False),
            ("hermes_dashboard", "hermes_dashboard", "Hermes: Open web dashboard (port 9120)", "dev", "LOW",
                [("port", "int", "Port", False, 9120)], False),

            # Mimo v0.1.1
            ("mimo_plan", "mimo_plan", "Mimo: Project planning and analysis", "dev", "MEDIUM",
                [("project_description", "str", "Project description")], False),
            ("mimo_execute", "mimo_execute", "Mimo: Execute plan and build", "dev", "HIGH",
                [("task_description", "str", "Build task")], True),
            ("mimo_build", "mimo_build", "Mimo: Build complete project from scratch", "dev", "HIGH",
                [("task", "str", "What to build"), ("framework", "str", "Framework", False, "nextjs")], True),

            # Pi Agent v0.1.0
            ("pi_agent_run", "pi_agent_run", "Pi Agent: Agent Loop with tools", "dev", "MEDIUM",
                [("task", "str", "Agent task"), ("tools", "str", "Tools", False, "")], False),
            ("pi_agent_swarm", "pi_agent_swarm", "Pi Agent: Parallel agent swarm", "dev", "MEDIUM",
                [("task", "str", "Swarm task"), ("num_agents", "int", "Number of agents", False, 3)], False),
        ]

        for (skill_name, name, desc, cat, risk_str, params_raw, needs_approval) in local_tools:
            if skill_name in ALL_LOCAL_SKILLS:
                skill_def = ALL_LOCAL_SKILLS[skill_name]
                risk = getattr(RiskLevel, risk_str)
                params = []
                for p in params_raw:
                    required = True if len(p) == 3 else p[3]
                    default = p[4] if len(p) == 5 else None
                    params.append(ToolParam(p[0], p[1], p[2], required, default))
                fn = skill_def["execute"]
                tool = Tool(name, desc, cat, risk, params, fn)
                tool.requires_approval = needs_approval
                self.register(tool)
'''

with open('tools/registry.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Insert after _register_skills closes
for i, line in enumerate(lines):
    if 'self.register(tool)' in line and i > 50:
        # Find the closing of _register_skills
        # Insert _register_local_agents right after
        while i < len(lines) and not lines[i].strip().startswith('def get_tools_prompt'):
            i += 1
        insert_at = i
        break

# Write at insertion point
with open('tools/registry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the right spot - before get_tools_prompt
marker = '\n    def get_tools_prompt'
pos = content.rfind(marker)
if pos == -1:
    print("Marker not found")
    sys.exit(1)

new_content = content[:pos] + LOCAL_SKILLS_CODE + '\n' + content[pos:]

with open('tools/registry.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Local agent skills added to registry")
