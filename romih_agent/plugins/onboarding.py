# -*- coding: utf-8 -*-
"""
Romih Agent - Onboarding Interview
===================================
First-time user experience: Romih interviews the user,
learns their business, and customizes itself.

Dynamic + Adaptive + Persistent profile
"""
import json, os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Industry(str, Enum):
    WORKSHOP = "workshop"
    HOTEL = "hotel"
    UMRAH = "umrah"
    GENERAL = "general"
    RETAIL = "retail"
    CONSTRUCTION = "construction"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"


class BusinessSize(str, Enum):
    SOLO = "solo"       # 1 person
    SMALL = "small"     # 2-10
    MEDIUM = "medium"   # 11-50
    LARGE = "large"     # 51-200
    ENTERPRISE = "enterprise"  # 200+


@dataclass
class UserProfile:
    """Saved user profile from onboarding"""
    name: str = ""
    industry: list[str] = field(default_factory=list)  # can be multiple
    sub_industry: str = ""  # more specific
    business_size: str = ""
    employee_count: int = 0
    current_tools: str = ""  # what they use now
    biggest_pain: str = ""  # what takes most time
    goals: list[str] = field(default_factory=list)
    language: str = "arabic"
    tone: str = "professional"  # professional, friendly, mixed
    onboarding_complete: bool = False
    enabled_plugins: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class OnboardingInterview:
    """
    Dynamic interview flow.
    Questions branch based on answers.
    Saves profile for persistent personalization.
    """
    
    def __init__(self, profile_path: str = "user_profile.json"):
        self.profile_path = profile_path
        self.profile = UserProfile()
        self.current_step = 0
        self._load_profile()
    
    def _load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.profile = UserProfile(**data)
            except:
                pass
    
    def _save_profile(self):
        self.profile.updated_at = datetime.now().isoformat()
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.profile.__dict__, f, ensure_ascii=False, indent=2)
    
    def is_complete(self) -> bool:
        return self.profile.onboarding_complete
    
    def get_welcome(self) -> str:
        """First message when user opens Romih"""
        if self.is_complete():
            return f"""أهلاً بك من جديد {self.profile.name or 'يا صديقي'}! 🌸

أنا مخصص لـ: {', '.join(self.profile.industry) if self.profile.industry else 'عملك'}

اكتب /help للأوامر  |  /goal لتنفيذ مهمة  |  /onboarding لتغيير الإعدادات"""
        
        return """🌸 أهلاً بك! أنا Romih — مساعدك الذكي.

عشان أقدر أخدمك بأفضل شكل يناسب عملك، هسألك شوية أسئلة سريعة (٣-٥ دقايق).

في النهاية هخصص نفسي لمجالك بالضبط — وما تكررهاش تاني.

جاهز نبدأ؟ اكتب: **نعم** أو **يلا** ✨"""
    
    def ask(self, answer: str = "") -> tuple[str, bool]:
        """
        Process an answer and return next question.
        Returns (question_text, is_complete)
        """
        answer = answer.strip()
        step = self.current_step
        
        # Save previous answer
        if answer and step > 0:
            self._save_answer(step, answer)
        
        # Branch: user said no to starting
        if step == 0 and answer and answer not in ["نعم", "يلا", "yes", "ok", "طيب", "تمام", "go", "start"]:
            self.profile.onboarding_complete = True
            self._save_profile()
            return """تمام! خلينا نبدأ بشكل عام — كل الأدوات متاحة لك.

اكتب /help للتعرف على الأوامر، أو /goal لبدء مهمة 🌸""", True
        
        if step == 1:
            return self._q_industry()
        elif step == 2:
            return self._q_details()
        elif step == 3:
            return self._q_size()
        elif step == 4:
            return self._q_tools()
        elif step == 5:
            return self._q_pain()
        elif step == 6:
            return self._finalize()
        
        # Step 0 - initial welcome already shown
        self.current_step = 1
        return """**السؤال الأول: إيه مجال شغلك؟** (ممكن تختار أكتر من واحد)

1️⃣ ورشة / ميكانيكا
2️⃣ فندق / شقق مفروشة
3️⃣ شركة عمرة وحج
4️⃣ شركة عامة / خدمات
5️⃣ تجارة / بيع بالتجزئة
6️⃣ مقاولات / إنشاءات
7️⃣ صحة / مستشفيات
8️⃣ تعليم / تدريب
9️⃣ غيره (اكتب المجال)

مثال: 3 أو 2,3 أو شركة برمجة""", False
    
    def _q_industry(self) -> tuple[str, bool]:
        """Branch based on industry selection"""
        # Parse answer (numbers or text)
        industries = self.profile.industry
        if not industries:
            # Try to detect from text
            text = self._last_answer.lower()
            mapping = {
                "1": ["workshop"], "2": ["hotel"], "3": ["umrah"],
                "4": ["general"], "5": ["retail"], "6": ["construction"],
                "7": ["healthcare"], "8": ["education"]
            }
            for num, ind in mapping.items():
                if num in text:
                    industries = ind
                    break
            if not industries:
                industries = ["general"]
            self.profile.industry = industries
        
        # Dynamic follow-up based on industry
        if "umrah" in industries or "hotel" in industries:
            return """**تفاصيل أكثر عن شغلك:**

بتقدم خدمات:
أ) عمرة فقط
ب) حج فقط
ج) عمرة وحج مع بعض
د) فنادق فقط
هـ) فنادق + عمرة (باقة متكاملة)
و) غيره (اكتب)

مثال: هـ""", False
        
        if "workshop" in industries:
            return """**تفاصيل الورشة:**

بتشتغل في:
أ) هيدروليك
ب) ميكانيكا عامة
ج) كهرباء سيارات
د) كل ده
هـ) غيره (اكتب)""", False
        
        if "retail" in industries:
            return """**تفاصيل التجارة:**

عندك:
أ) محل واحد
ب) أكتر من فرع
ج) متجر إلكتروني
د) كل ده""", False
        
        return self._q_size()
    
    def _q_details(self) -> tuple[str, bool]:
        self.profile.sub_industry = self._last_answer
        return self._q_size()
    
    def _q_size(self) -> tuple[str, bool]:
        """Business size question"""
        return """**حجم عملك:**

كم عدد الموظفين/العمال عندك تقريباً؟

أ) أنا فقط (فردي)
ب) ٢-١٠
ج) ١١-٥٠
د) ٥١-٢٠٠
هـ) أكثر من ٢٠٠""", False
    
    def _q_tools(self) -> tuple[str, bool]:
        # Save size
        text = self._last_answer.lower()
        size_map = {"أ": "solo", "ب": "small", "ج": "medium", "د": "large", "هـ": "enterprise"}
        for k, v in size_map.items():
            if k in text:
                self.profile.business_size = v
                break
        
        return """**إزاي بتدير شغلك دلوقتي؟**

أ) ورق وأقلام / يدوي
ب) Excel / Google Sheets
ج) برنامج محاسبي (مثل: SMACC، Zoho)
د) نظام ERP متكامل
هـ) مفيش نظام — عشوائي""", False
    
    def _q_pain(self) -> tuple[str, bool]:
        self.profile.current_tools = self._last_answer
        
        return """**إيه أكتر حاجة بتاخد وقتك وبتتعبك في شغلك؟**

مثلاً:
- متابعة العملاء والفواتير
- إدارة الموظفين والرواتب
- تنظيم الحجوزات
- متابعة المخزون
- التقارير اليومية
- كل ده 😅

اكتب باختصار...""", False
    
    def _finalize(self) -> tuple[str, bool]:
        self.profile.biggest_pain = self._last_answer
        
        # Determine which plugins to enable
        plugins = []
        if "workshop" in self.profile.industry:
            plugins.append("workshop")
        if "hotel" in self.profile.industry:
            plugins.append("hotels")
        if "umrah" in self.profile.industry:
            plugins.append("umrah")
        
        # Always include core business plugins
        plugins.extend(["hr", "finance", "projects"])
        plugins = list(set(plugins))
        self.profile.enabled_plugins = plugins
        
        # Mark complete
        self.profile.onboarding_complete = True
        self._save_profile()
        
        # Build personalized welcome
        industry_names = {
            "workshop": "الورش", "hotel": "الفنادق", "umrah": "العمرة والحج",
            "general": "الشركات", "retail": "التجارة", "construction": "المقاولات",
            "healthcare": "الصحة", "education": "التعليم"
        }
        industry_str = " و ".join([industry_names.get(i, i) for i in self.profile.industry[:2]])
        
        plugin_names = {
            "workshop": "🏭 إدارة الورش (عملاء، تصليحات، قطع غيار)",
            "hotels": "🏨 إدارة الفنادق (حجوزات، غرف، صيانة)",
            "umrah": "🕋 إدارة العمرة (حجاج، باقات، مجموعات)",
            "hr": "👥 الموارد البشرية (موظفين، رواتب، إجازات)",
            "finance": "💰 المالية (فواتير، مصروفات، تقارير)",
            "projects": "📋 المشاريع (مهام، مواعيد)"
        }
        plugins_str = "\n".join([plugin_names.get(p, p) for p in plugins])
        
        return f"""✨ **تم! Romih جاهز ومخصص لعملك**

📊 **ملفك التعريفي:**
• المجال: {industry_str}
• الحجم: {self.profile.business_size or 'غير محدد'}
• الألم الأكبر: {self.profile.biggest_pain or 'غير محدد'}

🔧 **الأدوات المفعلة:**
{plugins_str}

🎯 **الآن:**
• اكتب /goal لأي مهمة
• Romih يفكر وينفذ بنفسه
• جرب: /goal اعمل تقرير اليوم

أنا معاك — خلينا نبدأ! 🚀""", True
    
    @property
    def _last_answer(self) -> str:
        """Get the last saved answer"""
        return ""  # Simplified - answers are passed directly
    
    def _save_answer(self, step: int, answer: str):
        """Save answer to appropriate field"""
        if step == 1:  # name
            self.profile.name = answer if answer != "نعم" and answer != "يلا" else ""
        # Other steps handled in their respective methods
    
    def reset(self):
        """Reset onboarding for re-interview"""
        self.profile = UserProfile()
        self.current_step = 0
        if os.path.exists(self.profile_path):
            os.remove(self.profile_path)
    
    def get_industry_specific_prompt(self) -> str:
        """Get a specialized system prompt based on user's industry"""
        if not self.is_complete():
            return ""
        
        industries = self.profile.industry
        prompts = []
        
        if "workshop" in industries:
            prompts.append("You are helping a mechanical workshop owner. Use workshop terminology. Focus on repairs, customers, spare parts.")
        if "hotel" in industries:
            prompts.append("You are helping a hotel manager. Use hospitality terminology. Focus on bookings, rooms, guests, maintenance.")
        if "umrah" in industries:
            prompts.append("You are helping an Umrah/Hajj operator. Use pilgrimage terminology. Focus on pilgrims, groups, packages, transport.")
        
        if prompts:
            return "\n".join(prompts)
        return "You are helping a Saudi business owner. Be practical, direct, and action-oriented."
