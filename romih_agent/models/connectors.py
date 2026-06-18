"""
Romih Agent - Model Connectors
===============================
Ollama (محلي) + OpenRouter (سحابي) + Auto Router
"""
import os
import json
import httpx
from typing import Optional, AsyncGenerator
from dataclasses import dataclass, field


@dataclass
class ModelResponse:
    content: str
    model: str
    tokens: int = 0
    provider: str = ""


class OllamaConnector:
    """موصل Ollama - النماذج المحلية"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def list_models(self) -> list[str]:
        """قائمة النماذج المحلية المتاحة"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/tags", timeout=10)
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]

    async def chat(self, model: str, messages: list[dict],
                   temperature: float = 0.7) -> ModelResponse:
        """محادثة مع نموذج Ollama"""
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature}
            }
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            data = resp.json()
            if "error" in data:
                raise RuntimeError(f"Ollama error: {data['error']}")
            if "message" not in data:
                raise RuntimeError(f"Ollama unexpected response: {list(data.keys())}")
            return ModelResponse(
                content=data["message"]["content"],
                model=model,
                tokens=data.get("eval_count", 0),
                provider="ollama"
            )

    async def stream_chat(self, model: str, messages: list[dict]):
        """بث مباشر من Ollama"""
        async with httpx.AsyncClient(timeout=300) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            async with client.stream("POST",
                f"{self.base_url}/api/chat", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if chunk.get("message", {}).get("content"):
                                yield chunk["message"]["content"]
                        except json.JSONDecodeError:
                            continue


class OpenRouterConnector:
    """موصل OpenRouter - كل النماذج السحابية"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat(self, model: str, messages: list[dict],
                   temperature: float = 0.7) -> ModelResponse:
        """محادثة مع نموذج OpenRouter"""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY غير موجود")

        async with httpx.AsyncClient(timeout=120) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://romih.ai",
                "X-Title": "Romih Agent"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload, headers=headers
            )
            data = resp.json()
            return ModelResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", model),
                tokens=data.get("usage", {}).get("total_tokens", 0),
                provider="openrouter"
            )

    async def stream_chat(self, model: str, messages: list[dict]):
        """بث مباشر من OpenRouter"""
        async with httpx.AsyncClient(timeout=300) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {"model": model, "messages": messages, "stream": True}
            async with client.stream("POST",
                f"{self.base_url}/chat/completions",
                json=payload, headers=headers) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk = json.loads(line[6:])
                        content = chunk["choices"][0].get("delta", {}).get("content", "")
                        if content:
                            yield content


class ZhipuConnector:
    """موصل Zhipu GLM - نماذج GLM-4-flash المجانية"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("GLM_API_KEY", "")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

    async def chat(self, model: str, messages: list[dict],
                   temperature: float = 0.7) -> ModelResponse:
        """محادثة مع GLM-4-flash (مجاني، سريع، عربي ممتاز)"""
        if not self.api_key:
            raise ValueError("GLM_API_KEY غير موجود")

        async with httpx.AsyncClient(timeout=60) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model or "glm-4-flash",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096
            }
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload, headers=headers
            )
            data = resp.json()
            if "choices" not in data:
                raise RuntimeError(f"Zhipu error: {data}")
            return ModelResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", model),
                tokens=data.get("usage", {}).get("total_tokens", 0),
                provider="zhipu"
            )


class AutoRouter:
    """موجه ذكي - يختار النموذج المناسب تلقائياً"""

    # الأولويات حسب نوع المهمة
    CODE_MODELS = {
        "local": ["qwen2.5-coder:7b", "gemma4:12b"],
        "cloud": ["qwen/qwen3-next-80b-a3b-instruct:free", "nvidia/nemotron-3-super-120b-a12b:free"]
    }

    ARABIC_MODELS = {
        "local": ["gemma4:12b"],
        "cloud": ["nvidia/nemotron-3-super-120b-a12b:free", "google/gemma-4-31b-it:free"]
    }

    REASONING_MODELS = {
        "local": ["gemma4:12b"],
        "cloud": ["qwen/qwen3-next-80b-a3b-instruct:free", "nvidia/nemotron-3-super-120b-a12b:free"]
    }

    FAST_MODELS = {
        "local": ["qwen3.5:4b"],
        "cloud": ["liquid/lfm-2.5-1.2b-instruct:free", "qwen/qwen3-next-80b-a3b-instruct:free"]
    }

    def __init__(self, ollama: OllamaConnector):
        self.ollama = ollama
        self._local_models_cache = []

    async def get_local_models(self) -> list[str]:
        """النماذج المحلية المتاحة"""
        if not self._local_models_cache:
            try:
                self._local_models_cache = await self.ollama.list_models()
            except Exception:
                self._local_models_cache = []
        return self._local_models_cache

    async def route(self, task_type: str = "chat",
                    prefer_local: bool = False,
                    need_privacy: bool = False,
                    need_speed: bool = False) -> tuple[str, str]:
        """
        يختار أفضل نموذج للمهمة.
        Returns: (model_id, provider)
        """

        # خصوصية أو محلي مفضل ← النموذج المحلي
        if need_privacy or prefer_local:
            local_models = await self.get_local_models()

            if task_type == "code":
                candidates = self.CODE_MODELS["local"]
            elif task_type == "arabic":
                candidates = self.ARABIC_MODELS["local"]
            elif task_type == "reasoning":
                candidates = self.REASONING_MODELS["local"]
            elif need_speed:
                candidates = self.FAST_MODELS["local"]
            else:
                candidates = self.ARABIC_MODELS["local"]

            for model in candidates:
                if model in local_models:
                    return model, "ollama"

            # Fallback: أي نموذج محلي
            if local_models:
                return local_models[0], "ollama"

            # لا يوجد محلي ← سحابي
            return self.route_cloud(task_type)

        # سحابي
        return self.route_cloud(task_type, need_speed)

    def route_cloud(self, task_type: str, need_speed: bool = False) -> tuple[str, str]:
        """اختيار نموذج سحابي — Zhipu GLM-4-flash أولاً (مجاني)، OpenRouter احتياط"""
        # Zhipu GLM-4-flash is free, fast, excellent Arabic
        if os.environ.get("GLM_API_KEY"):
            return "glm-4-flash", "zhipu"
        # Fallback to OpenRouter free models
        if need_speed:
            return self.FAST_MODELS["cloud"][0], "openrouter"
        if task_type == "code":
            return self.CODE_MODELS["cloud"][0], "openrouter"
        elif task_type == "arabic":
            return self.ARABIC_MODELS["cloud"][0], "openrouter"
        elif task_type == "reasoning":
            return self.REASONING_MODELS["cloud"][0], "openrouter"
        else:
            return self.ARABIC_MODELS["cloud"][0], "openrouter"


# Connectors جاهزون
ollama = OllamaConnector()
openrouter = OpenRouterConnector()
zhipu = ZhipuConnector()
router = AutoRouter(ollama)
