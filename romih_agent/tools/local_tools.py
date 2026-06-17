"""
Romih Agent - Local Tools Registry
===================================
Registers all locally-available tools that are NOT stubs.
These call real APIs (AutoGLM, browser agent, etc.).
"""
import json
from tools.registry import ToolRegistry, Tool, ToolParam, RiskLevel


# ═══ Real Implementations ═══


def _generate_image_real(prompt: str) -> str:
    """
    Generate an image using the AutoGLM text-to-image API.
    Token auto-fetched from http://127.0.0.1:18432/get_token.
    
    Returns JSON with image_url and markdown, or error info.
    """
    try:
        from tools.image_gen_tool import generate_image
        return generate_image(prompt)
    except ImportError as e:
        return json.dumps({"error": f"Cannot import image_gen_tool: {e}", "image_url": None})
    except Exception as e:
        return json.dumps({"error": str(e), "image_url": None})


def _browse_web_real(url: str, action: str = "browse") -> str:
    """
    Automated web browsing via AutoGLM browser agent (autoclaw CLI).
    
    Args:
        url: Starting URL (optional if session exists)
        action: Browser action/task description
    
    Returns:
        str: Browser agent result or error message.
    """
    import os
    import subprocess

    bin_dir = os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\bin")
    autoclaw_path = os.path.join(bin_dir, "autoglm.exe")
    config_path = os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\config.json")

    # Check if browser config is ready
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        if not config.get("browser") or not config.get("extension_confirmed"):
            return json.dumps({
                "error": "Browser not configured. Run setup first (browser + extension required).",
                "needs_setup": True,
            }, ensure_ascii=False)
    except FileNotFoundError:
        return json.dumps({
            "error": "AutoGLM browser config not found. Install autoglm-browser-agent first.",
            "needs_setup": True,
        }, ensure_ascii=False)

    # Build command
    if url:
        autoclaw_path_str = f'"{autoclaw_path}"' if ' ' in autoclaw_path else autoclaw_path
        task_escaped = action.replace('"', "'")
        cmd = f'{autoclaw_path_str} task="{task_escaped}" start_url="{url}"'
    else:
        cmd = f'"{autoclaw_path}" task="{action.replace(chr(34), chr(39))}"'

    try:
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True,
            timeout=600,  # 10 min for browser tasks
            cwd=os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\workspace")
        )
        output = result.stdout or result.stderr
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated)"
        return output
    except subprocess.TimeoutExpired:
        return "⏱️ Browser task timed out (10 minutes)"
    except Exception as e:
        return f"❌ Browser agent error: {e}"


def _search_image_real(query: str) -> str:
    """
    Search for images using AutoGLM image search API.
    """
    try:
        from tools.image_gen_tool import _get_token, _build_headers
    except ImportError:
        return json.dumps({"error": "image_gen_tool not available"})

    try:
        token = _get_token()
    except Exception as e:
        return json.dumps({"error": f"Token error: {e}"})

    headers = _build_headers(token)
    payload = json.dumps({"query": query}).encode("utf-8")
    search_url = "https://autoglm-api.autoglm.ai/agentdr/v1/assistant/skills/search-image"

    try:
        import urllib.request
        req = urllib.request.Request(search_url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {e}"})


# ═══ Registration ═══


def register(tool_registry: ToolRegistry):
    """
    Register all locally-available tools with real implementations.
    Overrides any existing stub tools with the same names.
    
    Call this from RomihAgent.__init__ or ToolRegistry.__init__.
    """
    real_tools = [
        # Generate Image - AutoGLM API (real, not stub)
        Tool(
            name="generate_image",
            description="توليد صور بالذكاء الاصطناعي - AutoGLM API حقيقي",
            category="creative",
            risk=RiskLevel.LOW,
            params=[
                ToolParam("prompt", "str", "وصف الصورة المطلوبة"),
            ],
            execute=_generate_image_real,
        ),

        # Browse Web - AutoGLM browser agent (real)
        Tool(
            name="browse_web",
            description="تصفح ويب آلي - فتح مواقع، تعبئة نماذج، بحث، شراء",
            category="browser",
            risk=RiskLevel.HIGH,
            params=[
                ToolParam("url", "str", "رابط الصفحة"),
                ToolParam("action", "str", "المهمة المطلوبة", required=False, default="browse"),
            ],
            execute=_browse_web_real,
            requires_approval=True,
        ),

        # Search Images - AutoGLM API
        Tool(
            name="search_image",
            description="بحث عن صور عبر AutoGLM API",
            category="creative",
            risk=RiskLevel.LOW,
            params=[
                ToolParam("query", "str", "استعلام البحث عن صور"),
            ],
            execute=_search_image_real,
        ),
    ]

    for tool in real_tools:
        tool_registry.register(tool)

    return len(real_tools)


# Quick test
if __name__ == "__main__":
    dummy = type("Dummy", (), {"tools": {}})()
    dummy.register = dummy.tools.__setitem__
    n = register(dummy)
    print(f"✅ Registered {n} real local tools:")
    for name, t in dummy.tools.items():
        print(f"  • {name}: {t.description[:60]}")
