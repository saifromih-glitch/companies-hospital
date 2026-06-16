with open('romih_agent/server/ui.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace('/api/', '/romih/')
with open('romih_agent/server/ui.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Fixed UI paths')
