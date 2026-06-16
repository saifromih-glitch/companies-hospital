"""OpenRouter LLM Connector"""
import os
import json
import httpx
import logging

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"
FALLBACK_MODEL = "google/gemini-2.0-flash-lite-001"

_api_key = os.environ.get("OPENROUTER_API_KEY", "")


def is_available() -> bool:
    """Check if OpenRouter is configured."""
    return bool(_api_key)


async def generate(prompt: str, system: str = "", model: str = None, max_tokens: int = 1024) -> str:
    """
    Call OpenRouter API and return the response text.

    Args:
        prompt: User prompt
        system: System prompt
        model: Model to use (defaults to Gemini Flash free)
        max_tokens: Max output tokens

    Returns:
        Generated text, or error message
    """
    if not _api_key:
        return "[OpenRouter غير مهيأ - OPENROUTER_API_KEY مفقود]"

    model = model or DEFAULT_MODEL

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://companies-hospital-production.up.railway.app",
        "X-Title": "Companies Hospital",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)

            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "[لا يوجد رد من النموذج]"
            elif resp.status_code == 400 and "not supported" in resp.text:
                # Try fallback model
                logger.warning(f"Model {model} failed, trying fallback {FALLBACK_MODEL}")
                payload["model"] = FALLBACK_MODEL
                resp2 = await client.post(OPENROUTER_URL, json=payload, headers=headers)
                if resp2.status_code == 200:
                    data = resp2.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                return "[النموذج غير متاح - جرب لاحقاً]"
            else:
                err = resp.text[:200]
                logger.error(f"OpenRouter error {resp.status_code}: {err}")
                return f"[خطأ {resp.status_code}: {err}]"
    except httpx.TimeoutException:
        return "[انتهت مهلة الاتصال بـ OpenRouter]"
    except Exception as e:
        logger.error(f"OpenRouter exception: {e}")
        return f"[خطأ في الاتصال: {e}]"


def generate_sync(prompt: str, system: str = "", model: str = None, max_tokens: int = 1024) -> str:
    """Synchronous wrapper for generate()."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in an async context - use run_coroutine_threadsafe
            import concurrent.futures
            future = concurrent.futures.Future()
            async def _run():
                try:
                    result = await generate(prompt, system, model, max_tokens)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
            loop.create_task(_run())
            return future.result(timeout=50)
        else:
            return loop.run_until_complete(generate(prompt, system, model, max_tokens))
    except RuntimeError:
        return asyncio.run(generate(prompt, system, model, max_tokens))
