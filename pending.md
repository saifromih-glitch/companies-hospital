# 📋 PENDING.md — ملاحظات ومؤجلات
> لا تنسى — راجع قبل كل جلسة عمل

---

## 🔴 عاجل (يحتاج تدخل محمد)

| # | الملاحظة | التبعية | التاريخ |
|---|---|---|---|
| 1 | ~~Google OAuth — يحتاج Client ID + Secret~~ ✅ تم | المهمة 2.2 | ١٥ يونيو |
| 2 | تفعيل LLM — ~~يحتاج API key~~ ✅ OpenRouter $5 مفعل | المهمة 3.5 | ١٥ يونيو |
| 3 | Vercel — إنشاء مشروع جديد واستيراد repo | المهمة 4.x | ١٥ يونيو |

## 🟠 عالي (تحسينات ضرورية)

| # | الملاحظة | السبب | التاريخ |
|---|---|---|---|
| 4 | تحسين اللاندنج بيج (/): أيقونات، صور، أسعار، دفع | الصفحة شغالة لكن basic | ١٦ يونيو |
| 5 | صفحات Triage + Cases كاملة (مش placeholder) | الصفحات حالياً "تحت الإنشاء" | ١٦ يونيو |
| 6 | Semantic Cache (Layer 2 — embeddings) | يحتاج sentence-transformers + LLM | ١٦ يونيو |
| 7 | تكاملات (واتساب، إيميل، Google Calendar) | بعد المرحلة الأساسية | مؤجل |

## 🟡 متوسط

| # | الملاحظة | السبب | التاريخ |
|---|---|---|---|
| 8 | تحويل صفحات HTML إلى Next.js RTL كامل | الصفحات الحالية Python strings | ١٦ يونيو |
| 9 | تفعيل Alembic migrations بدل create_all | أمان للبيانات الإنتاجية | ١٦ يونيو |
| 10 | Role-Based Access Control (RBAC) | حالياً الكل owner | ١٦ يونيو |
| 11 | قسم أسعار (Free / 199 / 499 / Enterprise SAR) | من الخطة الأصلية | ١٦ يونيو |
| 12 | Stripe/PayPal دفع | يحتاج حسابات تجارية | لاحقاً |

## 🟢 منخفض (لاحقاً)

| # | الملاحظة | التاريخ |
|---|---|---|
| 13 | شهادات عملاء وهمية للاندنج | ١٦ يونيو |
| 14 | نظام إشعارات (email, push, in-app) | لاحقاً |
| 15 | SEO + PWA + Google Analytics | لاحقاً |
| 16 | دومين مخصص (romih.cc أو غيره) | لاحقاً |

---

## ⚡ ملاحظات تقنية آنية

- **HTML entities للعربي** — الحل الوحيد المضمون: `&#1575;` بدل الحرف العربي الخام
- **f-strings + JS curly braces** — خطر! استخدم string concat
- **OpenRouter** — `google/gemini-2.5-flash` (مدفوع $0.15/M input) مش `:free`
- **Postgres** — مستخدم من مشروع modest-warmth القديم
- **Railway domain** — `companies-hospital-production.up.railway.app`
- **Google OAuth** — redirect URI: `/api/v1/auth/google/callback` → redirects to `/dashboard?token=XXX`
- **رمز JWT** — `APP_URL` محتاج يكون مضبوط في Railway vars
