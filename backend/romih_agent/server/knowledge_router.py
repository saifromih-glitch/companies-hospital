"""
Dynamic Knowledge Router — injects domain knowledge on demand
Thin, fast, no overload — like how Rabie thinks
"""
import os

class KnowledgeRouter:
    """Detects what domain knowledge to inject based on user message"""
    
    DOMAINS = {
        "accounting": {
            "keywords": [
                "محاسب", "محاسبه", "محاسبة", "ضريبة", "ضريبه", "زكاة", "زكاه",
                "مدين", "دائن", "قيد", "قيود", "ميزانية", "ميزانيه",
                "قائمة دخل", "قائمه دخل", "تدفقات", "مخزون", "إهلاك", "اهلاك",
                "تسوية", "تسويه", "أصول", "خصوم", "حقوق", "ذمم",
                "VAT", "IFRS", "SOCPA", "IAS", "GAAP",
                "مراجعة", "مراجعه", "تدقيق", "ميزان", "رصيد",
                "نسبة التداول", "سيولة", "ربحية", "مخصص",
            ],
            "prompt": None  # loaded lazily
        },
        "marketing": {
            "keywords": [
                "تسويق", "تسويقي", "تسويقيه", "خطة تسويقية",
                "سوق", "عملاء", "عملاء", "زبائن", "منافسين", "منافس",
                "إعلان", "اعلان", "حملة", "براند", "علامة تجارية",
                "marketing", "branding", "social media",
            ],
            "prompt": None
        },
        "legal": {
            "keywords": [
                "قانوني", "قانون", "نظام", "لائحة", "لائحه",
                "عقد", "عقود", "شركة", "شركات", "مؤسسة", "مؤسسه",
                "سجل تجاري", "ترخيص", "تراخيص", "وزارة",
                "عمل", "موظف", "عامل", "عمال", "توظيف",
                "تأمينات", "تامينات", "GOSI", "مدني", "تجاري",
            ],
            "prompt": None
        },
        "engineering": {
            "keywords": [
                "ورشة", "ورشه", "سيارات", "هيدروليك", "ميكانيكا",
                "صيانة", "صيانه", "معدات", "آلات", "تصنيع",
                "مخزون", "قطع غيار", "engineer", "mechanical",
            ],
            "prompt": None
        },
    }
    
    def detect(self, message: str) -> list:
        """Return list of domains that match the message"""
        text = message.lower()
        matched = []
        for domain, config in self.DOMAINS.items():
            if any(kw in text for kw in config["keywords"]):
                matched.append(domain)
        return matched[:2]  # Max 2 domains to avoid overload
    
    def get_prompt(self, message: str) -> str:
        """Get relevant knowledge prompt for this message"""
        domains = self.detect(message)
        if not domains:
            return ""
        
        parts = []
        for domain in domains:
            prompt = self.DOMAINS[domain]["prompt"]
            if prompt:
                parts.append(prompt)
        
        if not parts:
            return ""
        
        return "\n\n=== المعرفة المتخصصة لهذا السؤال ===\n" + "\n".join(parts)
    
    def load_accounting(self):
        """Load accounting knowledge (lazy)"""
        if self.DOMAINS["accounting"]["prompt"]:
            return
        try:
            from .knowledge_accounting import get_accounting_prompt
            self.DOMAINS["accounting"]["prompt"] = get_accounting_prompt()
        except Exception:
            self.DOMAINS["accounting"]["prompt"] = "خبير محاسبي. استخدم IFRS و SOCPA."


# Global instance
knowledge = KnowledgeRouter()
