"""Static pages served from Python — avoids Docker encoding issues with Arabic HTML files"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])

LOGIN_PAGE = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول — مستشفى الشركات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #0A1E3C, #1A3A6C); min-height: 100vh; display: flex; align-items: center; justify-content: center; direction: rtl; }
        .container { background: white; border-radius: 16px; padding: 48px 40px; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .logo { text-align: center; margin-bottom: 32px; }
        .logo h1 { font-size: 28px; color: #0A1E3C; margin-bottom: 4px; }
        .logo p { color: #6B7280; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px; }
        input { width: 100%; padding: 12px 16px; border: 2px solid #E5E7EB; border-radius: 10px; font-size: 14px; text-align: right; transition: border-color .2s; }
        input:focus { outline: none; border-color: #DC8C28; }
        .btn { width: 100%; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; transition: opacity .2s; }
        .btn-primary { background: #0A1E3C; color: white; margin-bottom: 12px; }
        .btn-google { background: white; color: #374151; border: 2px solid #E5E7EB; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .btn:hover { opacity: .9; }
        .divider { text-align: center; margin: 20px 0; color: #9CA3AF; font-size: 13px; position: relative; }
        .divider::before, .divider::after { content: ''; position: absolute; top: 50%; width: 40%; height: 1px; background: #E5E7EB; }
        .divider::before { right: 0; } .divider::after { left: 0; }
        .tab { display: flex; margin-bottom: 24px; border-radius: 10px; background: #F3F4F6; padding: 4px; }
        .tab button { flex: 1; padding: 10px; border: none; background: transparent; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; color: #6B7280; }
        .tab button.active { background: white; color: #0A1E3C; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .error { background: #FEF2F2; color: #DC2626; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }
        .error.show { display: block; }
        .hidden { display: none; }
    </style>
</head>
<body>
<div class="container">
    <div class="logo">
        <h1>🏥 مستشفى الشركات</h1>
        <p>نظام تشغيل ذكي للشركات العربية</p>
    </div>
    <div class="error" id="error"></div>
    <div class="tab">
        <button class="active" onclick="switchTab('login')">دخول</button>
        <button onclick="switchTab('register')">حساب جديد</button>
    </div>
    <form id="login-form" onsubmit="handleLogin(event)">
        <div class="form-group"><label>البريد الإلكتروني</label><input type="email" id="login-email" required placeholder="example@domain.com"></div>
        <div class="form-group"><label>كلمة المرور</label><input type="password" id="login-password" required placeholder="••••••••"></div>
        <button type="submit" class="btn btn-primary">تسجيل الدخول</button>
    </form>
    <form id="register-form" class="hidden" onsubmit="handleRegister(event)">
        <div class="form-group"><label>الاسم الكامل</label><input type="text" id="reg-name" required placeholder="محمد أحمد"></div>
        <div class="form-group"><label>البريد الإلكتروني</label><input type="email" id="reg-email" required placeholder="example@domain.com"></div>
        <div class="form-group"><label>كلمة المرور</label><input type="password" id="reg-password" required placeholder="٨ أحرف على الأقل"></div>
        <button type="submit" class="btn btn-primary">إنشاء حساب</button>
    </form>
    <div class="divider">أو</div>
    <button class="btn btn-google" onclick="handleGoogleLogin()">
        <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        متابعة بحساب Google
    </button>
</div>
<script>
const API = 'https://companies-hospital-production.up.railway.app';
let activeTab = 'login';
function showError(msg) { const e = document.getElementById('error'); e.textContent = msg; e.classList.add('show'); setTimeout(() => e.classList.remove('show'), 5000); }
function switchTab(tab) { activeTab = tab; document.querySelectorAll('.tab button').forEach((b,i) => { b.classList.toggle('active', (i===0 && tab==='login') || (i===1 && tab==='register')); }); document.getElementById('login-form').classList.toggle('hidden', tab !== 'login'); document.getElementById('register-form').classList.toggle('hidden', tab !== 'register'); }
async function handleLogin(e) { e.preventDefault(); try { const res = await fetch(API+'/api/v1/auth/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email: document.getElementById('login-email').value, password: document.getElementById('login-password').value}) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || 'فشل تسجيل الدخول'); localStorage.setItem('token', data.access_token); window.location.href = '/dashboard'; } catch(err) { showError(err.message); } }
async function handleRegister(e) { e.preventDefault(); try { const res = await fetch(API+'/api/v1/auth/register', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name: document.getElementById('reg-name').value, email: document.getElementById('reg-email').value, password: document.getElementById('reg-password').value}) }); const data = await res.json(); if (!res.ok) throw new Error(data.detail || 'فشل إنشاء الحساب'); localStorage.setItem('token', data.access_token); window.location.href = '/dashboard'; } catch(err) { showError(err.message); } }
function handleGoogleLogin() { window.location.href = API+'/api/v1/auth/google/login'; }
</script>
</body>
</html>"""

REGISTER_PAGE = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل شركة — مستشفى الشركات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #0A1E3C, #1A3A6C); min-height: 100vh; display: flex; align-items: center; justify-content: center; direction: rtl; }
        .container { background: white; border-radius: 16px; padding: 48px 40px; width: 100%; max-width: 520px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .logo { text-align: center; margin-bottom: 28px; }
        .logo h1 { font-size: 28px; color: #0A1E3C; margin-bottom: 4px; }
        .logo p { color: #6B7280; font-size: 14px; }
        .form-group { margin-bottom: 16px; }
        .row { display: flex; gap: 12px; } .row .form-group { flex: 1; }
        label { display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 4px; }
        input, select { width: 100%; padding: 10px 14px; border: 2px solid #E5E7EB; border-radius: 8px; font-size: 14px; text-align: right; transition: border-color .2s; }
        input:focus, select:focus { outline: none; border-color: #DC8C28; }
        .btn { width: 100%; padding: 14px; background: #0A1E3C; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 12px; }
        .btn:hover { opacity: .9; }
        .error { background: #FEF2F2; color: #DC2626; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }
        .error.show { display: block; }
        .success { background: #F0FDF4; color: #16A34A; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }
        .success.show { display: block; }
        .skip { text-align: center; margin-top: 16px; font-size: 13px; color: #6B7280; }
        .skip a { color: #DC8C28; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
<div class="container">
    <div class="logo"><h1>🏢 سجل شركتك</h1><p>ابدأ رحلة تشخيص وتحسين شركتك</p></div>
    <div class="error" id="error"></div>
    <div class="success" id="success"></div>
    <form onsubmit="handleSubmit(event)">
        <div class="form-group"><label>اسم الشركة (بالعربية)</label><input type="text" id="name_ar" required placeholder="مثال: شركة النور للتجارة"></div>
        <div class="form-group"><label>اسم الشركة (بالإنجليزية — اختياري)</label><input type="text" id="name_en" placeholder="Al-Noor Trading Co."></div>
        <div class="row">
            <div class="form-group"><label>القطاع</label><select id="sector" required><option value="">اختر القطاع</option><option value="retail">تجارة التجزئة</option><option value="hospitality">فنادق وضيافة</option><option value="hajj_umrah">حج وعمرة</option><option value="transport">نقل ومواصلات</option><option value="catering">إعاشة وتموين</option><option value="realestate">عقارات</option><option value="healthcare">رعاية صحية</option><option value="education">تعليم</option><option value="technology">تقنية</option><option value="construction">مقاولات وإنشاءات</option><option value="manufacturing">صناعة</option><option value="finance">خدمات مالية</option><option value="agriculture">زراعة</option><option value="energy">طاقة</option><option value="other">أخرى</option></select></div>
            <div class="form-group"><label>حجم الشركة</label><select id="size" required><option value="">اختر الحجم</option><option value="micro">متناهية الصغر (١-٥)</option><option value="small">صغيرة (٦-٤٩)</option><option value="medium">متوسطة (٥٠-٢٤٩)</option><option value="large">كبيرة (٢٥٠+)</option></select></div>
        </div>
        <div class="row"><div class="form-group"><label>المدينة</label><input type="text" id="city" placeholder="مكة المكرمة"></div><div class="form-group"><label>سنة التأسيس</label><input type="number" id="founded_year" placeholder="٢٠٢٠" min="1900" max="2026"></div></div>
        <div class="row"><div class="form-group"><label>عدد الموظفين</label><input type="number" id="employees_count" placeholder="١٠" min="1"></div><div class="form-group"><label>السجل التجاري (اختياري)</label><input type="text" id="commercial_reg" placeholder="٤٠٣xxxxxxxxx"></div></div>
        <button type="submit" class="btn">تسجيل الشركة وبدء التشخيص</button>
    </form>
    <div class="skip"><a href="/dashboard">تخطي ← الذهاب للوحة التحكم</a></div>
</div>
<script>
const API = 'https://companies-hospital-production.up.railway.app';
function showError(msg) { const e=document.getElementById('error'); e.textContent=msg; e.classList.add('show'); setTimeout(()=>e.classList.remove('show'),5000); }
async function handleSubmit(e) { e.preventDefault(); const token=localStorage.getItem('token'); if(!token){window.location.href='/login';return;}
const data={name_ar:document.getElementById('name_ar').value,name_en:document.getElementById('name_en').value||null,sector:document.getElementById('sector').value,size:document.getElementById('size').value,city:document.getElementById('city').value||null,founded_year:document.getElementById('founded_year').value?parseInt(document.getElementById('founded_year').value):null,employees_count:document.getElementById('employees_count').value?parseInt(document.getElementById('employees_count').value):null,commercial_reg:document.getElementById('commercial_reg').value||null};
try{const res=await fetch(API+'/api/v1/companies',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},body:JSON.stringify(data)});const result=await res.json();if(!res.ok)throw new Error(result.detail||'فشل تسجيل الشركة');
document.getElementById('success').textContent='✅ تم تسجيل الشركة بنجاح! جاري التوجيه...';document.getElementById('success').classList.add('show');setTimeout(()=>{window.location.href='/dashboard';},1500);}catch(err){showError(err.message);}}
</script>
</body>
</html>"""


@router.get("/login", response_class=HTMLResponse)
async def login():
    return HTMLResponse(content=LOGIN_PAGE)


@router.get("/register", response_class=HTMLResponse)
async def register_company():
    return HTMLResponse(content=REGISTER_PAGE)
