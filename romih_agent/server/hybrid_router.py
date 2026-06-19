"""
Hybrid Router — GLM-4 for text, OpenRouter Free for files
Thin layer, no core changes, safe to deploy
"""
import os, json, asyncio
import httpx


class HybridRouter:
    """Tiny router that sends file requests to OpenRouter free models"""
    
    FILE_KEYWORDS = [
        "ملف اكسيل", "ملف إكسيل", "excel", "اكسيل", "إكسيل", "xlsx",
        "ملف وورد", "word", "docx", "وورد",
        "باوربوينت", "powerpoint", "pptx", "عرض تقديمي",
        "pdf", "بي دي إف",
        "csv", "ملف بيانات",
        "/pdf", "/xlsx", "/docx", "/pptx", "/csv",
    ]
    
    FILE_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def is_file_request(self, text: str) -> bool:
        """Check if the message is asking for a file"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.FILE_KEYWORDS)
    
    async def generate_file(self, system_prompt: str, user_message: str) -> str:
        """Use OpenRouter free model to generate file JSON"""
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return None
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a file for this request: {user_message}\n\nRespond ONLY with a JSON tool call in format:\n```json\n{{\"tool\": \"create_TYPE\", \"args\": {{...}}}}\n```\nWhere TYPE is xlsx/csv/docx/pptx/pdf.\nDo NOT include markdown tables. Just the JSON block."}
        ]
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    self.OPENROUTER_URL,
                    json={
                        "model": self.FILE_MODEL,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.3,
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
                else:
                    print(f"HybridRouter: HTTP {r.status_code}")
                    return None
        except Exception as e:
            print(f"HybridRouter: {e}")
            return None


# Global instance
router = HybridRouter()
