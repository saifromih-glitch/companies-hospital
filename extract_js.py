import re
with open('romih_agent/server/ui.html', 'r', encoding='utf-8') as f:
    html = f.read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
with open('ui_scripts.txt', 'w', encoding='utf-8') as out:
    for i, s in enumerate(scripts):
        out.write(f'--- Script {i+1} ({len(s)} chars) ---\n')
        out.write(s[:500])
        out.write('\n...\n')
print(f'Found {len(scripts)} scripts')
