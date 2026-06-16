# -*- coding: utf-8 -*-
"""
Cloud-Compatible Tools
=======================
Overrides for tools that need to work on Railway (no local AutoClaw).
Uses HTTP APIs instead of local file system.
"""
import httpx
import asyncio


def web_search(query: str) -> str:
    """Search the web using DuckDuckGo HTML (free, no API key)"""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        r = httpx.get(url, timeout=15, follow_redirects=True,
                      headers={"User-Agent": "RomihAgent/1.0"})
        if r.status_code != 200:
            return f"Search failed: HTTP {r.status_code}"
        
        text = r.text
        # Extract results
        results = []
        import re
        # DuckDuckGo HTML results
        snippets = re.findall(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', text)
        titles = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', text)
        urls = re.findall(r'<a[^>]*class="result__url"[^>]*>(.*?)</a>', text)
        
        # Clean HTML tags
        def clean(s):
            return re.sub(r'<[^>]+>', '', s).strip()
        
        for i in range(min(5, len(snippets))):
            title = clean(titles[i]) if i < len(titles) else ""
            snippet = clean(snippets[i]) if i < len(snippets) else ""
            url = urls[i].strip() if i < len(urls) else ""
            results.append(f"**{title}**\n{snippet}\n{url}")
        
        if not results:
            return f"No results found for: {query}"
        
        return f"🔍 Search: {query}\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Search error: {e}"


def recognize_image(url: str) -> str:
    """Analyze image using OpenRouter's vision model"""
    try:
        import os
        key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY", "")
        if not key:
            return "Image recognition requires OpenRouter key"
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail in Arabic"},
                {"type": "image_url", "image_url": {"url": url}}
            ]
        }]
        
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "google/gemini-2.5-flash", "messages": messages, "max_tokens": 500},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Image analysis failed: {r.status_code}"
    except Exception as e:
        return f"Image analysis error: {e}"


def deep_research(query: str) -> str:
    """Deep research using OpenRouter with tool calling"""
    try:
        import os
        key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY", "")
        if not key:
            return "Research requires OpenRouter key"
        
        messages = [
            {"role": "system", "content": "You are a research assistant. Do thorough research on the topic and provide a detailed analysis in Arabic."},
            {"role": "user", "content": f"""Research this topic in depth and provide a comprehensive Arabic analysis:
            {query}
            
            Include:
            1. Key findings
            2. Important data/statistics
            3. Trends and implications
            4. Summary"""}
        ]
        
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "google/gemini-2.5-flash", "messages": messages, "max_tokens": 1500},
            timeout=60
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Research failed: {r.status_code}"
    except Exception as e:
        return f"Research error: {e}"
