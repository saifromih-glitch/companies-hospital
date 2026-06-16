"""Add Rabie Brain skills to registry.py"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

RABIE_CODE = '''
    def _register_rabie_brain(self):
        """Register Rabie Brain - 17 experts + 8 methodologies"""
        from tools.rabie_brain import EXPERTS, METHODOLOGIES, consult_expert, apply_methodology, get_all_experts, get_all_methodologies

        rabie_tools = [
            ("consult_expert", "Rabie: Consult a legendary expert", "brain", "LOW",
                [("expert_key", "str", "Expert (strategist, finance, codemaster...)"),
                 ("problem", "str", "Problem to analyze")], consult_expert, False),
            ("apply_methodology", "Rabie: Apply a methodology", "brain", "LOW",
                [("methodology_key", "str", "Methodology (north_star, debug_methodology...)"),
                 ("context", "str", "Context", False, "")], apply_methodology, False),
            ("list_experts", "Rabie: List all 17 experts", "brain", "LOW",
                [], lambda **kw: get_all_experts(), False),
            ("list_methodologies", "Rabie: List all 8 methodologies", "brain", "LOW",
                [], lambda **kw: get_all_methodologies(), False),
        ]

        for (name, desc, cat, risk_str, params_raw, fn, needs_approval) in rabie_tools:
            risk = getattr(RiskLevel, risk_str)
            params = []
            for p in params_raw:
                required = True if len(p) == 3 else p[3]
                default = p[4] if len(p) == 5 else None
                params.append(ToolParam(p[0], p[1], p[2], required, default))
            tool = Tool(name, desc, cat, risk, params, fn)
            tool.requires_approval = needs_approval
            self.register(tool)
'''

with open('tools/registry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert after _register_local_agents
marker = '\n    def get_tools_prompt'
pos = content.rfind(marker)
if pos == -1:
    print("Marker not found")
    sys.exit(1)

new_content = content[:pos] + RABIE_CODE + '\n' + content[pos:]

with open('tools/registry.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Rabie Brain skills added to registry")
