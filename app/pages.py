"""Static pages with Arabic-safe rendering — HTML entities instead of raw UTF-8 bytes.
This avoids ALL browser/server encoding issues across Docker, Railway, and proxies."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])


# ═══ Helper: encode Arabic text as HTML entities ═══
def ae(text: str) -> str:
    """Convert Arabic/Unicode chars to HTML entities. ASCII passes through."""
    result = []
    for ch in text:
        code = ord(ch)
        if code > 127:
            result.append(f'&#{code};')
        else:
            result.append(ch)
    return ''.join(result)


# ═══ Pages ═══

@router.get("/login", response_class=HTMLResponse)
async def login():
    title = ae("تسجيل الدخول — مستشفى الشركات")
    subtitle = ae("نظام تشغيل ذكي للشركات العربية")
    login_btn = ae("تسجيل الدخول")
    register_btn = ae("إنشاء حساب")
    tab_login = ae("دخول")
    tab_register = ae("حساب جديد")
    label_email = ae("البريد الإلكتروني")
    label_pass = ae("كلمة المرور")
    label_name = ae("الاسم الكامل")
    label_pass2 = ae("كلمة المرور")
    pass_hint = ae("٨ أحرف على الأقل")
    name_placeholder = ae("محمد أحمد")
    divider = ae("أو")
    google_btn = ae("متابعة بحساب Google")
    platform = ae("مستشفى الشركات")
    err_login = ae("فشل تسجيل الدخول")
    err_register = ae("فشل إنشاء الحساب")

    return HTMLResponse(f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #0A1E3C, #1A3A6C); min-height: 100vh; display: flex; align-items: center; justify-content: center; direction: rtl; }}
        .container {{ background: white; border-radius: 16px; padding: 48px 40px; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .logo {{ text-align: center; margin-bottom: 32px; }}
        .logo h1 {{ font-size: 28px; color: #0A1E3C; margin-bottom: 4px; }}
        .logo p {{ color: #6B7280; font-size: 14px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 6px; }}
        input {{ width: 100%; padding: 12px 16px; border: 2px solid #E5E7EB; border-radius: 10px; font-size: 14px; text-align: right; }}
        input:focus {{ outline: none; border-color: #DC8C28; }}
        .btn {{ width: 100%; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; }}
        .btn-primary {{ background: #0A1E3C; color: white; margin-bottom: 12px; }}
        .btn-primary:hover {{ opacity: 0.9; }}
        .btn-google {{ background: white; color: #374151; border: 2px solid #E5E7EB; display: flex; align-items: center; justify-content: center; gap: 10px; }}
        .btn-google:hover {{ opacity: 0.9; }}
        .divider {{ text-align: center; margin: 20px 0; color: #9CA3AF; font-size: 13px; position: relative; }}
        .divider::before, .divider::after {{ content: ''; position: absolute; top: 50%; width: 40%; height: 1px; background: #E5E7EB; }}
        .divider::before {{ right: 0; }} .divider::after {{ left: 0; }}
        .tab {{ display: flex; margin-bottom: 24px; border-radius: 10px; background: #F3F4F6; padding: 4px; }}
        .tab button {{ flex: 1; padding: 10px; border: none; background: transparent; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; color: #6B7280; }}
        .tab button.active {{ background: white; color: #0A1E3C; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .error {{ background: #FEF2F2; color: #DC2626; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }}
        .error.show {{ display: block; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
<div class="container">
    <div class="logo">
        <h1>🏥 {platform}</h1>
        <p>{subtitle}</p>
    </div>
    <div class="error" id="error"></div>
    <div class="tab">
        <button class="active" onclick="switchTab('login')">{tab_login}</button>
        <button onclick="switchTab('register')">{tab_register}</button>
    </div>
    <form id="login-form" onsubmit="handleLogin(event)">
        <div class="form-group"><label>{label_email}</label><input type="email" id="login-email" required placeholder="example@domain.com"></div>
        <div class="form-group"><label>{label_pass}</label><input type="password" id="login-password" required placeholder="••••••••"></div>
        <button type="submit" class="btn btn-primary">{login_btn}</button>
    </form>
    <form id="register-form" class="hidden" onsubmit="handleRegister(event)">
        <div class="form-group"><label>{label_name}</label><input type="text" id="reg-name" required placeholder="{name_placeholder}"></div>
        <div class="form-group"><label>{label_email}</label><input type="email" id="reg-email" required placeholder="example@domain.com"></div>
        <div class="form-group"><label>{label_pass2}</label><input type="password" id="reg-password" required placeholder="{pass_hint}"></div>
        <button type="submit" class="btn btn-primary">{register_btn}</button>
    </form>
    <div class="divider">{divider}</div>
    <button class="btn btn-google" onclick="handleGoogleLogin()">
        <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        {google_btn}
    </button>
</div>
<script>
const API = 'https://companies-hospital-production.up.railway.app';
function showError(msg) {{ var e=document.getElementById('error'); e.textContent=msg; e.classList.add('show'); setTimeout(function(){{e.classList.remove('show')}},5000); }}
function switchTab(tab) {{ document.querySelectorAll('.tab button').forEach(function(b,i){{ b.classList.toggle('active', (i===0&&tab==='login')||(i===1&&tab==='register')); }}); document.getElementById('login-form').classList.toggle('hidden', tab!=='login'); document.getElementById('register-form').classList.toggle('hidden', tab!=='register'); }}
async function handleLogin(e) {{ e.preventDefault(); try {{ var res=await fetch(API+'/api/v1/auth/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:document.getElementById('login-email').value,password:document.getElementById('login-password').value}})}}); var data=await res.json(); if(!res.ok) throw new Error(data.detail||'{err_login}'); localStorage.setItem('token',data.access_token); window.location.href='/dashboard'; }} catch(err) {{ showError(err.message); }} }}
async function handleRegister(e) {{ e.preventDefault(); try {{ var res=await fetch(API+'/api/v1/auth/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{name:document.getElementById('reg-name').value,email:document.getElementById('reg-email').value,password:document.getElementById('reg-password').value}})}}); var data=await res.json(); if(!res.ok) throw new Error(data.detail||'{err_register}'); localStorage.setItem('token',data.access_token); window.location.href='/dashboard'; }} catch(err) {{ showError(err.message); }} }}
function handleGoogleLogin() {{ window.location.href = API+'/api/v1/auth/google/login'; }}
</script>
</body>
</html>""")


@router.get("/register", response_class=HTMLResponse)
async def register():
    title = ae("تسجيل شركة — مستشفى الشركات")
    subtitle = ae("ابدأ رحلة تشخيص وتحسين شركتك")
    platform = ae("مستشفى الشركات")
    label_name = ae("اسم الشركة (بالعربية)")
    label_name_en = ae("اسم الشركة (بالإنجليزية — اختياري)")
    label_sector = ae("القطاع")
    label_size = ae("حجم الشركة")
    label_city = ae("المدينة")
    label_year = ae("سنة التأسيس")
    label_employees = ae("عدد الموظفين")
    label_cr = ae("السجل التجاري (اختياري)")
    btn = ae("تسجيل الشركة وبدء التشخيص")
    skip = ae("تخطي ← الذهاب للوحة التحكم")
    success_msg = ae("✅ تم تسجيل الشركة بنجاح! جاري التوجيه...")
    err_msg = ae("فشل تسجيل الشركة")
    city_placeholder = ae("مكة المكرمة")
    
    return HTMLResponse(f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #0A1E3C, #1A3A6C); min-height: 100vh; display: flex; align-items: center; justify-content: center; direction: rtl; }}
        .container {{ background: white; border-radius: 16px; padding: 48px 40px; width: 100%; max-width: 520px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .logo {{ text-align: center; margin-bottom: 28px; }}
        .logo h1 {{ font-size: 28px; color: #0A1E3C; margin-bottom: 4px; }}
        .logo p {{ color: #6B7280; font-size: 14px; }}
        .form-group {{ margin-bottom: 16px; }}
        .row {{ display: flex; gap: 12px; }} .row .form-group {{ flex: 1; }}
        label {{ display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 4px; }}
        input, select {{ width: 100%; padding: 10px 14px; border: 2px solid #E5E7EB; border-radius: 8px; font-size: 14px; text-align: right; }}
        input:focus, select:focus {{ outline: none; border-color: #DC8C28; }}
        .btn {{ width: 100%; padding: 14px; background: #0A1E3C; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 12px; }}
        .btn:hover {{ opacity: .9; }}
        .error {{ background: #FEF2F2; color: #DC2626; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }}
        .error.show {{ display: block; }}
        .success {{ background: #F0FDF4; color: #16A34A; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 16px; display: none; }}
        .success.show {{ display: block; }}
        .skip {{ text-align: center; margin-top: 16px; font-size: 13px; color: #6B7280; }}
        .skip a {{ color: #DC8C28; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
<div class="container">
    <div class="logo"><h1>🏢 {platform}</h1><p>{subtitle}</p></div>
    <div class="error" id="error"></div>
    <div class="success" id="success"></div>
    <form onsubmit="handleSubmit(event)">
        <div class="form-group"><label>{label_name}</label><input type="text" id="name_ar" required placeholder="{ae('مثال: شركة النور للتجارة')}"></div>
        <div class="form-group"><label>{label_name_en}</label><input type="text" id="name_en" placeholder="Al-Noor Trading Co."></div>
        <div class="row"><div class="form-group"><label>{label_sector}</label><select id="sector" required><option value="">{ae('اختر القطاع')}</option><option value="retail">{ae('تجارة التجزئة')}</option><option value="hospitality">{ae('فنادق وضيافة')}</option><option value="hajj_umrah">{ae('حج وعمرة')}</option><option value="transport">{ae('نقل ومواصلات')}</option><option value="catering">{ae('إعاشة وتموين')}</option><option value="realestate">{ae('عقارات')}</option><option value="healthcare">{ae('رعاية صحية')}</option><option value="education">{ae('تعليم')}</option><option value="technology">{ae('تقنية')}</option><option value="construction">{ae('مقاولات وإنشاءات')}</option><option value="manufacturing">{ae('صناعة')}</option><option value="finance">{ae('خدمات مالية')}</option><option value="agriculture">{ae('زراعة')}</option><option value="energy">{ae('طاقة')}</option><option value="other">{ae('أخرى')}</option></select></div><div class="form-group"><label>{label_size}</label><select id="size" required><option value="">{ae('اختر الحجم')}</option><option value="micro">{ae('متناهية الصغر (١-٥)')}</option><option value="small">{ae('صغيرة (٦-٤٩)')}</option><option value="medium">{ae('متوسطة (٥٠-٢٤٩)')}</option><option value="large">{ae('كبيرة (٢٥٠+)')}</option></select></div></div>
        <div class="row"><div class="form-group"><label>{label_city}</label><input type="text" id="city" placeholder="{city_placeholder}"></div><div class="form-group"><label>{label_year}</label><input type="number" id="founded_year" placeholder="2020" min="1900" max="2026"></div></div>
        <div class="row"><div class="form-group"><label>{label_employees}</label><input type="number" id="employees_count" placeholder="10" min="1"></div><div class="form-group"><label>{label_cr}</label><input type="text" id="commercial_reg" placeholder="403xxxxxxxxx"></div></div>
        <button type="submit" class="btn">{btn}</button>
    </form>
    <div class="skip"><a href="/dashboard">{skip}</a></div>
</div>
<script>
const API = 'https://companies-hospital-production.up.railway.app';
function showError(msg) {{ var e=document.getElementById('error'); e.textContent=msg; e.classList.add('show'); setTimeout(function(){{e.classList.remove('show')}},5000); }}
async function handleSubmit(e) {{ e.preventDefault(); var token=localStorage.getItem('token'); if(!token){{window.location.href='/login';return;}} var data={{name_ar:document.getElementById('name_ar').value,name_en:document.getElementById('name_en').value||null,sector:document.getElementById('sector').value,size:document.getElementById('size').value,city:document.getElementById('city').value||null,founded_year:document.getElementById('founded_year').value?parseInt(document.getElementById('founded_year').value):null,employees_count:document.getElementById('employees_count').value?parseInt(document.getElementById('employees_count').value):null,commercial_reg:document.getElementById('commercial_reg').value||null}}; try{{ var res=await fetch(API+'/api/v1/companies',{{method:'POST',headers:{{'Content-Type':'application/json','Authorization':'Bearer '+token}},body:JSON.stringify(data)}}); var result=await res.json(); if(!res.ok) throw new Error(result.detail||'{err_msg}'); document.getElementById('success').textContent='{success_msg}'; document.getElementById('success').classList.add('show'); setTimeout(function(){{window.location.href='/dashboard';}},1500); }} catch(err) {{ showError(err.message); }} }}
</script>
</body>
</html>""")


@router.get("/triage", response_class=HTMLResponse)
async def triage():
    return HTMLResponse(content=f"""<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{ae('استقبال — مستشفى الشركات')}</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#0A1E3C,#1A3A6C);min-height:100vh;direction:rtl}}.header{{background:rgba(255,255,255,.95);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.1)}}.header h1{{font-size:20px;color:#0A1E3C}}.header nav a{{margin-right:16px;color:#6B7280;text-decoration:none;font-size:14px;font-weight:600}}.header nav a:hover,.header nav a.active{{color:#DC8C28}}.main{{max-width:800px;margin:40px auto;padding:0 20px}}.card{{background:white;border-radius:16px;padding:32px;box-shadow:0 10px 40px rgba(0,0,0,.15);margin-bottom:24px}}.card h2{{font-size:22px;color:#0A1E3C;margin-bottom:8px}}.card p{{color:#6B7280;font-size:14px;margin-bottom:24px}}.form-group{{margin-bottom:18px}}label{{display:block;font-size:14px;font-weight:600;color:#374151;margin-bottom:6px}}input,select,textarea{{width:100%;padding:12px 16px;border:2px solid #E5E7EB;border-radius:10px;font-size:14px;text-align:right;font-family:'Segoe UI',Tahoma,sans-serif}}textarea{{min-height:120px;resize:vertical}}input:focus,select:focus,textarea:focus{{outline:none;border-color:#DC8C28}}.btn{{padding:14px 32px;background:#0A1E3C;color:white;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer}}.btn:disabled{{opacity:.5;cursor:not-allowed}}.result{{margin-top:24px;display:none}}.result.show{{display:block}}.severity{{display:inline-block;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:700;margin-right:8px}}.severity.critical{{background:#FEE2E2;color:#DC2626}}.severity.high{{background:#FEF3C7;color:#D97706}}.severity.medium{{background:#DBEAFE;color:#2563EB}}.severity.low{{background:#F3F4F6;color:#6B7280}}.triage-box{{background:#F9FAFB;border-radius:12px;padding:20px;margin-top:16px}}.triage-box h3{{font-size:16px;color:#374151;margin-bottom:12px}}.tag{{display:inline-block;background:#E5E7EB;color:#374151;padding:4px 10px;border-radius:6px;font-size:12px;margin:2px}}.expert-tag{{display:inline-block;background:#FEF3C7;color:#92400E;padding:4px 10px;border-radius:6px;font-size:12px;margin:2px}}.error{{background:#FEF2F2;color:#DC2626;padding:12px;border-radius:8px;font-size:13px;margin-top:12px;display:none}}.error.show{{display:block}}.loading{{text-align:center;padding:20px;display:none}}.loading.show{{display:block}}.spinner{{border:3px solid #E5E7EB;border-top:3px solid #DC8C28;border-radius:50%;width:32px;height:32px;animation:spin .8s linear infinite;margin:0 auto 8px}}@keyframes spin{{to{{transform:rotate(360deg)}}}}</style></head><body><div class="header"><h1>🏥 {ae('مستشفى الشركات')}</h1><nav><a href="/dashboard">{ae('لوحة التحكم')}</a><a href="/triage" class="active">{ae('استقبال')}</a><a href="/cases">{ae('الحالات')}</a></nav></div><div class="main"><div class="card"><h2>🩺 {ae('استقبال حالة جديدة')}</h2><p>{ae('صف مشكلة شركتك وسيقوم النظام بفرزها وتوجيهها للتخصص المناسب')}</p><div class="error" id="error"></div><form id="case-form" onsubmit="submitCase(event)"><div class="form-group"><label>{ae('عنوان المشكلة')}</label><input type="text" id="title" required placeholder="{ae('مثال: انخفاض المبيعات في الربع الأخير')}" minlength="5" maxlength="300"></div><div class="form-group"><label>{ae('وصف تفصيلي')}</label><textarea id="description" required placeholder="{ae('اشرح المشكلة بالتفصيل...')}" minlength="20"></textarea></div><div class="form-group"><label>{ae('المجال')}</label><select id="category" required><option value="">{ae('اختر المجال')}</option><option value="finance">💰 {ae('مالية')}</option><option value="marketing">📈 {ae('تسويق ومبيعات')}</option><option value="operations">⚙️ {ae('عمليات')}</option><option value="hr">👥 {ae('موارد بشرية')}</option><option value="strategy">🧭 {ae('استراتيجية')}</option><option value="legal">⚖️ {ae('قانوني')}</option><option value="technical">💻 {ae('تقني')}</option></select></div><button type="submit" class="btn" id="submit-btn">{ae('ابدأ التشخيص')}</button></form><div class="loading" id="loading"><div class="spinner"></div><p style="color:#6B7280;font-size:14px">{ae('جاري فحص الحالة...')}</p></div><div class="result" id="result"><div class="triage-box"><h3>{ae('نتيجة الفرز')}</h3><p style="margin-bottom:8px"><strong>{ae('الخطورة:')}</strong> <span id="severity-badge"></span></p><p style="margin-bottom:8px"><strong>{ae('الكلمات المفتاحية:')}</strong> <span id="keywords"></span></p><p><strong>{ae('الخبراء المقترحون:')}</strong> <span id="experts"></span></p></div><a href="/cases" class="btn" style="display:inline-block;margin-top:16px;text-decoration:none">{ae('عرض كل الحالات')}</a></div></div></div><script>var API='https://companies-hospital-production.up.railway.app';function showError(msg){{var e=document.getElementById('error');e.textContent=msg;e.classList.add('show');setTimeout(function(){{e.classList.remove('show')}},6000)}}async function submitCase(e){{e.preventDefault();var token=localStorage.getItem('token');if(!token){{window.location.href='/login';return}}var btn=document.getElementById('submit-btn');btn.disabled=true;document.getElementById('loading').classList.add('show');document.getElementById('result').classList.remove('show');document.getElementById('error').classList.remove('show');try{{var res=await fetch(API+'/api/v1/cases',{{method:'POST',headers:{{'Content-Type':'application/json','Authorization':'Bearer '+token}},body:JSON.stringify({{title:document.getElementById('title').value,description:document.getElementById('description').value,category:document.getElementById('category').value}})}});var data=await res.json();if(!res.ok)throw new Error(data.detail||'{ae("فشل إنشاء الحالة")}');document.getElementById('severity-badge').innerHTML='<span class=\"severity '+data.severity+'\">'+severityLabel(data.severity)+'</span>';document.getElementById('keywords').innerHTML=(data.triage_result.keywords||[]).map(function(k){{return'<span class=\"tag\">'+k+'</span>'}}).join(' ');document.getElementById('experts').innerHTML=(data.triage_result.suggested_experts||[]).map(function(e){{return'<span class=\"expert-tag\">'+e+'</span>'}}).join(' ');document.getElementById('result').classList.add('show');document.getElementById('case-form').reset()}}catch(err){{showError(err.message)}}finally{{btn.disabled=false;document.getElementById('loading').classList.remove('show')}}}}function severityLabel(s){{var m={{critical:'🚨 {ae("حرجة")}',high:'🔴 {ae("عالية")}',medium:'🟡 {ae("متوسطة")}',low:'🟢 {ae("منخفضة")}'}};return m[s]||s}}</script></body></html>""")


@router.get("/cases", response_class=HTMLResponse)
async def cases():
    return HTMLResponse(content=f"""<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{ae('الحالات — مستشفى الشركات')}</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#0A1E3C,#1A3A6C);min-height:100vh;direction:rtl}}.header{{background:rgba(255,255,255,.95);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.1)}}.header h1{{font-size:20px;color:#0A1E3C}}.header nav a{{margin-right:16px;color:#6B7280;text-decoration:none;font-size:14px;font-weight:600}}.header nav a:hover,.header nav a.active{{color:#DC8C28}}.main{{max-width:1000px;margin:40px auto;padding:0 20px}}.card{{background:white;border-radius:16px;padding:32px;box-shadow:0 10px 40px rgba(0,0,0,.15)}}.card h2{{font-size:22px;color:#0A1E3C;margin-bottom:4px}}.subtitle{{color:#6B7280;font-size:14px;margin-bottom:24px}}.filter-bar{{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}}.filter-bar select{{padding:8px 14px;border:2px solid #E5E7EB;border-radius:8px;font-size:13px;text-align:right}}table{{width:100%;border-collapse:collapse}}th{{text-align:right;padding:12px 16px;background:#F9FAFB;color:#374151;font-size:13px;font-weight:700;border-bottom:2px solid #E5E7EB}}td{{padding:14px 16px;border-bottom:1px solid #F3F4F6;font-size:13px;color:#4B5563}}tr:hover{{background:#F9FAFB}}.severity{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-left:6px}}.severity.critical{{background:#DC2626}}.severity.high{{background:#D97706}}.severity.medium{{background:#2563EB}}.severity.low{{background:#6B7280}}.status{{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600}}.status.triage_complete{{background:#FEF3C7;color:#92400E}}.status.diagnosed{{background:#DBEAFE;color:#1E40AF}}.action-btn{{padding:6px 14px;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;background:#0A1E3C;color:white}}.empty{{text-align:center;padding:48px 20px;color:#9CA3AF}}.empty .icon{{font-size:48px;margin-bottom:16px}}.empty .btn{{display:inline-block;padding:12px 28px;background:#0A1E3C;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600}}.btn-new{{display:inline-block;padding:10px 24px;background:#DC8C28;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;margin-left:12px}}th:last-child{{text-align:center}}td:last-child{{text-align:center}}</style></head><body><div class="header"><h1>🏥 {ae('مستشفى الشركات')}</h1><nav><a href="/dashboard">{ae('لوحة التحكم')}</a><a href="/triage">{ae('استقبال')}</a><a href="/cases" class="active">{ae('الحالات')}</a></nav></div><div class="main"><div class="card"><div style="display:flex;align-items:center;justify-content:space-between"><div><h2>📋 {ae('الحالات')}</h2><p class="subtitle">{ae('جميع الحالات المسجلة لشركتك')}</p></div><a href="/triage" class="btn-new">+ {ae('حالة جديدة')}</a></div><div class="filter-bar"><select id="filter-severity" onchange="renderTable()"><option value="">{ae('كل مستويات الخطورة')}</option><option value="critical">🚨 {ae('حرجة')}</option><option value="high">🔴 {ae('عالية')}</option><option value="medium">🟡 {ae('متوسطة')}</option><option value="low">🟢 {ae('منخفضة')}</option></select><select id="filter-status" onchange="renderTable()"><option value="">{ae('كل الحالات')}</option><option value="triage_complete">{ae('تم الفرز')}</option><option value="diagnosed">{ae('تم التشخيص')}</option></select><select id="filter-category" onchange="renderTable()"><option value="">{ae('كل المجالات')}</option><option value="finance">💰 {ae('مالية')}</option><option value="marketing">📈 {ae('تسويق')}</option><option value="operations">⚙️ {ae('عمليات')}</option><option value="hr">👥 {ae('موارد بشرية')}</option><option value="strategy">🧭 {ae('استراتيجية')}</option><option value="legal">⚖️ {ae('قانوني')}</option><option value="technical">💻 {ae('تقني')}</option></select></div><div id="loading" style="text-align:center;padding:40px;color:#6B7280">{ae('جاري تحميل الحالات...')}</div><div id="empty" class="empty" style="display:none"><div class="icon">📭</div><p>{ae('لا توجد حالات بعد')}</p><a href="/triage" class="btn">{ae('سجل أول حالة')}</a></div><table id="table" style="display:none"><thead><tr><th>{ae('الحالة')}</th><th>{ae('المجال')}</th><th>{ae('الخطورة')}</th><th>{ae('الحالة')}</th><th>{ae('التاريخ')}</th><th>{ae('إجراء')}</th></tr></thead><tbody id="tbody"></tbody></table></div></div><script>var API='https://companies-hospital-production.up.railway.app';var cases=[];var catLabels={{finance:'{ae("مالية")}',marketing:'{ae("تسويق")}',operations:'{ae("عمليات")}',hr:'{ae("موارد بشرية")}',strategy:'{ae("استراتيجية")}',legal:'{ae("قانوني")}',technical:'{ae("تقني")}'}};var sevLabels={{critical:'🚨 {ae("حرجة")}',high:'🔴 {ae("عالية")}',medium:'🟡 {ae("متوسطة")}',low:'🟢 {ae("منخفضة")}'}};var statusLabels={{triage_complete:'{ae("تم الفرز")}',diagnosed:'{ae("تم التشخيص")}'}};async function loadCases(){{var token=localStorage.getItem('token');if(!token){{window.location.href='/login';return}}document.getElementById('loading').style.display='block';try{{var res=await fetch(API+'/api/v1/cases',{{headers:{{'Authorization':'Bearer '+token}}}});var data=await res.json();cases=data.cases||[];renderTable()}}catch(err){{cases=[];renderTable()}}}function renderTable(){{document.getElementById('loading').style.display='none';var sev=document.getElementById('filter-severity').value;var st=document.getElementById('filter-status').value;var cat=document.getElementById('filter-category').value;var filtered=cases;if(sev)filtered=filtered.filter(function(c){{return c.severity===sev}});if(st)filtered=filtered.filter(function(c){{return c.status===st}});if(cat)filtered=filtered.filter(function(c){{return c.category===cat}});if(!filtered.length){{document.getElementById('table').style.display='none';document.getElementById('empty').style.display='block';return}}document.getElementById('empty').style.display='none';document.getElementById('table').style.display='table';document.getElementById('tbody').innerHTML=filtered.map(function(c){{return'<tr><td style=font-weight:600;color:#111827>'+esc(c.title)+'</td><td>'+(catLabels[c.category]||c.category)+'</td><td><span class=\"severity '+c.severity+'\"></span> '+(sevLabels[c.severity]||c.severity)+'</td><td><span class=\"status '+c.status+'\">'+(statusLabels[c.status]||c.status)+'</span></td><td>'+(c.created_at?new Date(c.created_at).toLocaleDateString('ar-SA'):'')+'</td><td><button class=action-btn onclick=viewCase(\"'+c.id+'\")>{ae("عرض")}</button></td></tr>'}}).join('')}}function viewCase(id){{window.location.href='/cases/'+id}}function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}loadCases();</script></body></html>""")
