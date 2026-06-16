import re
with open('romih_agent/server/ui.html', 'r', encoding='utf-8') as f:
    html = f.read()
# Check for common HTML issues
print('Has doctype:', 'DOCTYPE' in html[:100])
print('Has closing html:', '</html>' in html)
print('Has closing body:', '</body>' in html)
print('Has closing script:', '</script>' in html)
# Check for event handlers
print('Has onclick send:', 'onclick' in html and 'sendMessage' in html)
# Check form structure
body = html[html.find('<body'):html.find('</body>')]
print('Body length:', len(body))
print('Has send button:', 'send-btn' in body)
# Check JS errors potential
js_start = html.find('<script>')
js_end = html.find('</script>')
js = html[js_start:js_end]
print('JS length:', len(js))
# Check for problematic chars
for i, line in enumerate(js.split('\n'), 1):
    if '\u200f' in line or '\u200e' in line:
        print(f'Bidi mark in JS line {i}')
    if i < 5:
        print(f'JS line {i}: {line.strip()[:80]}')
