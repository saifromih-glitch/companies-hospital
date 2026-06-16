import re
with open('romih_agent/server/ui.html', 'r', encoding='utf-8') as f:
    html = f.read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
with open('ui_full_js.txt', 'w', encoding='utf-8') as out:
    out.write(scripts[0])
print(f'Written {len(scripts[0])} chars')
