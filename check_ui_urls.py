import re
with open('romih_agent/server/ui.html', 'r', encoding='utf-8') as f:
    html = f.read()
urls = re.findall(r"""fetch\(['"]([^'"]+)['"]""", html)
for u in urls:
    print(u)
