from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io, base64, os

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 250" width="400" height="250">
 <rect x="50" y="50" width="300" height="150" rx="10" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
 <rect x="60" y="60" width="40" height="130" fill="#aaa"/>
 <text x="70" y="125" font-size="20">N</text>
 <rect x="300" y="60" width="40" height="130" fill="#aaa"/>
 <text x="310" y="125" font-size="20">S</text>
 <circle cx="200" cy="125" r="30" fill="#eee" stroke="#888" stroke-width="2"/>
 <text x="180" y="130" font-size="12">Motor DC</text>
</svg>"""

try:
    drawing = svg2rlg(io.StringIO(svg))
    buf = io.BytesIO()
    renderPM.drawToFile(drawing, buf, fmt='PNG')
    print(f'Success! PNG size: {buf.tell()} bytes')
    with open('test_output.png', 'wb') as f:
        f.write(buf.getvalue())
    print('Saved test_output.png')
except Exception as e:
    print(f'Error: {e}')
