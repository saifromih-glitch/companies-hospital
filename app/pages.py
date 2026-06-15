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
