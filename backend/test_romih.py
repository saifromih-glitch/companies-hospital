import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'romih_agent')

from app.romih_router import router, agent
print(f'Router OK: {len(router.routes)} routes')
print(f'Agent tools: {len(agent.tools.tools)}')
print(f'Import SUCCESS')
