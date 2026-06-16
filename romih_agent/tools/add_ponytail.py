"""Add Ponytail to Rabie Brain registry"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

PONYTAIL_CODE = '''
        # Ponytail - lazy senior dev
        try:
            from tools.rabie_brain import ponytail_check
            tool = Tool("ponytail_check", "Ponytail: 6-step ladder before writing code", "brain", RiskLevel.LOW,
                [ToolParam("task", "str", "Task to analyze")], ponytail_check)
            self.register(tool)
        except Exception:
            pass
'''

with open('tools/registry.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert at end of _register_rabie_brain
marker = 'self.register(tool)'
# Find the last occurrence in _register_rabie_brain
# Look for the last self.register before get_tools_prompt
pos = content.rfind('\n    def get_tools_prompt')
if pos == -1:
    print("Not found")
    sys.exit(1)

# Find the last self.register before this
brain_start = content.rfind('_register_rabie_brain', 0, pos)
last_register = content.rfind('            self.register(tool)', brain_start, pos)

if last_register == -1:
    print("Could not find last register in rabie_brain")
    sys.exit(1)

# Find end of that line
line_end = content.index('\n', last_register)
new_content = content[:line_end+1] + PONYTAIL_CODE + content[line_end+1:]

with open('tools/registry.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Ponytail tool added to registry")
