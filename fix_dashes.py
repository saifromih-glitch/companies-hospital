with open('romih_agent/core/agent.py', 'r', encoding='utf-8') as f:
    content = f.read()
# Replace em-dash and en-dash with regular dash
content = content.replace('\u2014', '-')  # em-dash
content = content.replace('\u2013', '-')  # en-dash
with open('romih_agent/core/agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed em-dashes')
