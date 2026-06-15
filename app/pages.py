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


@router.get("/cases", response_class=HTMLResponse)
async def cases():
    return HTMLResponse(content=_CASES)
