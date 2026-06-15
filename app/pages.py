"""Static pages with proper Arabic — served from Python, encoding-proof."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])


def ae(text):
    """Convert non-ASCII chars to HTML entities."""
    return ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in text)


def load_page(name):
    """Load HTML template and convert Arabic to entities."""
    import os
    path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', name)
    if not os.path.isfile(path):
        return f"<h1>404: {name} not found</h1>"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return ae(content)


# Build pages at import time (converted to entities once)
_LOGIN = load_page('login.html')
_REGISTER = load_page('register-company.html')
_TRIAGE = load_page('triage.html')
_CASES = load_page('cases.html')


@router.get("/login", response_class=HTMLResponse)
async def login():
    return HTMLResponse(content=_LOGIN)


@router.get("/register", response_class=HTMLResponse)
async def register_company():
    return HTMLResponse(content=_REGISTER)


@router.get("/triage", response_class=HTMLResponse)
async def triage():
    return HTMLResponse(content=_TRIAGE)


@router.get("/test-arabic", response_class=HTMLResponse)
async def test_arabic():
    from fastapi.responses import Response
    html = """<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>&#1578;&#1580;&#1585;&#1576;&#1577;</title></head>
<body style="font-family:sans-serif;padding:40px;text-align:center">
<h1>&#1575;&#1604;&#1593;&#1585;&#1576;&#1610; &#1588;&#1594;&#1575;&#1604;!</h1>
<p>&#1573;&#1584;&#1575; &#1603;&#1606;&#1578; &#1578;&#1602;&#1585;&#1571; &#1607;&#1584;&#1575; &#1601;&#1575;&#1604;&#1578;&#1585;&#1605;&#1610;&#1586; &#1587;&#1604;&#1610;&#1605;</p>
<p style="color:green;font-size:24px">&#10004; Test passed</p>
</body></html>"""
    return Response(content=html.encode('ascii'), media_type="text/html; charset=utf-8",
                    headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})


@router.get("/raw-arabic", response_class=HTMLResponse)
async def raw_arabic():
    """Minimal test — Arabic via HTML entities in plain text."""
    from fastapi.responses import Response
    body = """<pre>
&#1575;&#1604;&#1593;&#1585;&#1576;&#1610; &#1588;&#1594;&#1575;&#1604;!
&#1575;&#1604;&#1581;&#1585;&#1608;&#1601; = Arabic letters
&#1578;&#1587;&#1580;&#1610;&#1604; &#1575;&#1604;&#1583;&#1582;&#1608;&#1604; = Login
&#1605;&#1587;&#1578;&#1588;&#1601;&#1609; &#1575;&#1604;&#1588;&#1585;&#1603;&#1575;&#1578; = Companies Hospital
&#10004; This is pure ASCII
</pre>"""
    return Response(content=body.encode('ascii'), media_type="text/html; charset=utf-8",
                    headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})


@router.get("/cases", response_class=HTMLResponse)
async def cases():
    return HTMLResponse(content=_CASES)
