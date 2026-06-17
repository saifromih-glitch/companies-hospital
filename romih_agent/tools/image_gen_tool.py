"""
Romih Agent - AutoGLM Image Generation Tool
============================================
Real implementation wrapping the AutoGLM text-to-image API.
Token is auto-fetched from local service at http://127.0.0.1:18432/get_token.
"""
import sys
import json
import hashlib
import time
import urllib.request

APP_ID  = "100003"
APP_KEY = "38d2391985e2369a5fb8227d8e6cd5e5"
URL     = "https://autoglm-api.autoglm.ai/agentdr/v1/assistant/skills/generate-image"
TOKEN_URL = "http://127.0.0.1:18432/get_token"


def _get_token() -> str:
    """Fetch Bearer token from the local AutoGLM service."""
    try:
        with urllib.request.urlopen(TOKEN_URL, timeout=5) as resp:
            token = resp.read().decode("utf-8").strip()
        if not token:
            raise RuntimeError("Empty token received from local service")
        if not token.lower().startswith("bearer "):
            token = f"Bearer {token}"
        return token
    except Exception as e:
        raise RuntimeError(f"Failed to get token from {TOKEN_URL}: {e}")


def _build_headers(token: str) -> dict:
    """Build signed request headers."""
    timestamp = str(int(time.time()))
    sign_data = f"{APP_ID}&{timestamp}&{APP_KEY}"
    sign = hashlib.md5(sign_data.encode("utf-8")).hexdigest()
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "X-Auth-Appid": APP_ID,
        "X-Auth-TimeStamp": timestamp,
        "X-Auth-Sign": sign,
    }


def generate_image(prompt: str) -> str:
    """
    Generate an image from a text prompt using AutoGLM API.
    
    Args:
        prompt: Text description of the image to generate.
    
    Returns:
        str: JSON string with the image URL or error information.
    """
    try:
        token = _get_token()
    except RuntimeError as e:
        return json.dumps({"error": str(e), "image_url": None}, ensure_ascii=False)

    headers = _build_headers(token)
    payload = json.dumps({"text": prompt}).encode("utf-8")

    try:
        req = urllib.request.Request(URL, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return json.dumps({"error": f"API request failed: {e}", "image_url": None}, ensure_ascii=False)

    # Extract image URL from response
    code = result.get("code", -1)
    if code == 0:
        image_url = result.get("data", {}).get("image_url", "")
        if image_url:
            return json.dumps({
                "success": True,
                "image_url": image_url,
                "markdown": f"![Generated image]({image_url})",
            }, ensure_ascii=False)
        else:
            return json.dumps({"error": "No image_url in response", "raw": result}, ensure_ascii=False)
    else:
        msg = result.get("msg", "Unknown error")
        return json.dumps({"error": f"API returned code={code}: {msg}", "raw": result}, ensure_ascii=False)


# CLI entry point for subprocess calls
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_gen_tool.py \"image description\"")
        sys.exit(1)
    prompt = sys.argv[1]
    result = generate_image(prompt)
    print(result)
