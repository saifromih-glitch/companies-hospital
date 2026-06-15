"""Static pages — All Arabic via HTML entities, served from code (no files).
Uses plain string concatenation to avoid f-string curly-brace conflicts with JavaScript."""
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["pages"])


def ae(text):
    """Convert non-ASCII chars to HTML entities — encoding-proof."""
    return ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in text)


def _page(title, body_css_js):
    return Response(
        content=('<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>'
                 + title + '</title></head>' + body_css_js + '</html>').encode('ascii'),
        media_type="text/html; charset=utf-8",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})


_LOGIN_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#0A1E3C,#1A3A6C);min-height:100vh;display:flex;align-items:center;justify-content:center;direction:rtl}
.container{background:white;border-radius:16px;padding:48px 40px;width:100%;max-width:440px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
.logo{text-align:center;margin-bottom:32px}
.logo h1{font-size:28px;color:#0A1E3C;margin-bottom:4px}
.logo p{color:#6B7280;font-size:14px}
.form-group{margin-bottom:20px}
label{display:block;font-size:14px;font-weight:600;color:#374151;margin-bottom:6px}
input{width:100%;padding:12px 16px;border:2px solid #E5E7EB;border-radius:10px;font-size:14px;text-align:right}
input:focus{outline:none;border-color:#DC8C28}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer}
.btn-primary{background:#0A1E3C;color:white;margin-bottom:12px}
.btn-primary:hover{opacity:0.9}
.btn-google{background:white;color:#374151;border:2px solid #E5E7EB;display:flex;align-items:center;justify-content:center;gap:10px}
.btn-google:hover{opacity:0.9}
.divider{text-align:center;margin:20px 0;color:#9CA3AF;font-size:13px;position:relative}
.divider::before,.divider::after{content:'';position:absolute;top:50%;width:40%;height:1px;background:#E5E7EB}
.divider::before{right:0}.divider::after{left:0}
.tab{display:flex;margin-bottom:24px;border-radius:10px;background:#F3F4F6;padding:4px}
.tab button{flex:1;padding:10px;border:none;background:transparent;border-radius:8px;font-weight:600;cursor:pointer;font-size:14px;color:#6B7280}
.tab button.active{background:white;color:#0A1E3C;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
.error{background:#FEF2F2;color:#DC2626;padding:12px;border-radius:8px;font-size:13px;margin-bottom:16px;display:none}
.error.show{display:block}
.hidden{display:none}
</style>"""

_LOGIN_JS = """<script>
var API='https://companies-hospital-production.up.railway.app';
function showError(msg){var e=document.getElementById('error');e.textContent=msg;e.classList.add('show');setTimeout(function(){e.classList.remove('show')},5000)}
function switchTab(tab){var b=document.querySelectorAll('.tab button');for(var i=0;i<b.length;i++){b[i].classList.toggle('active',(i===0&&tab==='login')||(i===1&&tab==='register'))}document.getElementById('login-form').classList.toggle('hidden',tab!=='login');document.getElementById('register-form').classList.toggle('hidden',tab!=='register')}
async function handleLogin(e){e.preventDefault();try{var res=await fetch(API+'/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('login-email').value,password:document.getElementById('login-password').value})});var data=await res.json();if(!res.ok)throw new Error(data.detail||'LOGIN_ERR');localStorage.setItem('token',data.access_token);window.location.href='/dashboard'}catch(err){showError(err.message)}}
async function handleRegister(e){e.preventDefault();try{var res=await fetch(API+'/api/v1/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('reg-name').value,email:document.getElementById('reg-email').value,password:document.getElementById('reg-password').value})});var data=await res.json();if(!res.ok)throw new Error(data.detail||'REGISTER_ERR');localStorage.setItem('token',data.access_token);window.location.href='/dashboard'}catch(err){showError(err.message)}}
function handleGoogleLogin(){window.location.href=API+'/api/v1/auth/google/login'}
</script>"""


@router.get("/login")
async def login():
    return _page(ae("تسجيل الدخول — مستشفى الشركات"), _LOGIN_CSS + '<body><div class="container">' +
        '<div class="logo"><h1>&#127973; ' + ae("مستشفى الشركات") + '</h1><p>' + ae("نظام تشغيل ذكي للشركات العربية") + '</p></div>' +
        '<div class="error" id="error"></div>' +
        '<div class="tab"><button class="active" onclick="switchTab(\'login\')">' + ae("دخول") + '</button>' +
        '<button onclick="switchTab(\'register\')">' + ae("حساب جديد") + '</button></div>' +
        '<form id="login-form" onsubmit="handleLogin(event)">' +
        '<div class="form-group"><label>' + ae("البريد الإلكتروني") + '</label><input type="email" id="login-email" required placeholder="example@domain.com"></div>' +
        '<div class="form-group"><label>' + ae("كلمة المرور") + '</label><input type="password" id="login-password" required placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;"></div>' +
        '<button type="submit" class="btn btn-primary">' + ae("تسجيل الدخول") + '</button></form>' +
        '<form id="register-form" class="hidden" onsubmit="handleRegister(event)">' +
        '<div class="form-group"><label>' + ae("الاسم الكامل") + '</label><input type="text" id="reg-name" required placeholder="' + ae("محمد أحمد") + '"></div>' +
        '<div class="form-group"><label>' + ae("البريد الإلكتروني") + '</label><input type="email" id="reg-email" required placeholder="example@domain.com"></div>' +
        '<div class="form-group"><label>' + ae("كلمة المرور") + '</label><input type="password" id="reg-password" required placeholder="' + ae("٨ أحرف على الأقل") + '"></div>' +
        '<button type="submit" class="btn btn-primary">' + ae("إنشاء حساب") + '</button></form>' +
        '<div class="divider">' + ae("أو") + '</div>' +
        '<button class="btn btn-google" onclick="handleGoogleLogin()"><svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>' + ae("متابعة بحساب Google") + '</button></div>' +
        _LOGIN_JS.replace('LOGIN_ERR', ae("فشل تسجيل الدخول")).replace('REGISTER_ERR', ae("فشل إنشاء الحساب")))


_EMPTY = '<body style="font-family:sans-serif;padding:40px;text-align:center;direction:rtl">'


@router.get("/register")
async def register_company():
    return _page(ae("تسجيل شركة — مستشفى الشركات"), _EMPTY + '<h1>' + ae("تحت الإنشاء") + '</h1></body>')


@router.get("/triage")
async def triage():
    css = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#0A1E3C,#1A3A6C);min-height:100vh;direction:rtl}
.header{background:rgba(255,255,255,.95);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.1)}
.header h1{font-size:20px;color:#0A1E3C}
.header nav a{margin-right:16px;color:#6B7280;text-decoration:none;font-size:14px;font-weight:600}
.header nav a:hover,.header nav a.active{color:#DC8C28}
.main{max-width:800px;margin:40px auto;padding:0 20px}
.card{background:white;border-radius:16px;padding:32px;box-shadow:0 10px 40px rgba(0,0,0,.15);margin-bottom:24px}
.card h2{font-size:22px;color:#0A1E3C;margin-bottom:8px}
.card p{color:#6B7280;font-size:14px;margin-bottom:24px}
.form-group{margin-bottom:18px}
label{display:block;font-size:14px;font-weight:600;color:#374151;margin-bottom:6px}
input,select,textarea{width:100%;padding:12px 16px;border:2px solid #E5E7EB;border-radius:10px;font-size:14px;text-align:right;font-family:'Segoe UI',Tahoma,sans-serif}
textarea{min-height:120px;resize:vertical}
input:focus,select:focus,textarea:focus{outline:none;border-color:#DC8C28}
.btn{padding:14px 32px;background:#0A1E3C;color:white;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer}
.btn:hover{opacity:.9}
.btn:disabled{opacity:.5;cursor:not-allowed}
.result{margin-top:24px;display:none}
.result.show{display:block}
.severity{display:inline-block;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:700;margin-right:8px}
.severity.critical{background:#FEE2E2;color:#DC2626}
.severity.high{background:#FEF3C7;color:#D97706}
.severity.medium{background:#DBEAFE;color:#2563EB}
.severity.low{background:#F3F4F6;color:#6B7280}
.triage-box{background:#F9FAFB;border-radius:12px;padding:20px;margin-top:16px}
.triage-box h3{font-size:16px;color:#374151;margin-bottom:12px}
.tag{display:inline-block;background:#E5E7EB;color:#374151;padding:4px 10px;border-radius:6px;font-size:12px;margin:2px}
.expert-tag{display:inline-block;background:#FEF3C7;color:#92400E;padding:4px 10px;border-radius:6px;font-size:12px;margin:2px}
.error{background:#FEF2F2;color:#DC2626;padding:12px;border-radius:8px;font-size:13px;margin-top:12px;display:none}
.error.show{display:block}
.loading{text-align:center;padding:20px;display:none}
.loading.show{display:block}
.spinner{border:3px solid #E5E7EB;border-top:3px solid #DC8C28;border-radius:50%;width:32px;height:32px;animation:spin .8s linear infinite;margin:0 auto 8px}
@keyframes spin{to{transform:rotate(360deg)}}
.diagnose-link{display:inline-block;margin-top:16px;padding:10px 20px;background:#DC8C28;color:white;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px}
</style>"""
    cats = ''.join(f'<option value="{v}">{l}</option>' for v,l in [
        ("", "اختر المجال"),("finance","💰 مالية"),("marketing","📈 تسويق ومبيعات"),
        ("operations","⚙️ عمليات"),("hr","👥 موارد بشرية"),("strategy","🧭 استراتيجية"),
        ("legal","⚖️ قانوني"),("technical","💻 تقني")])
    
    return _page(ae("استقبال — مستشفى الشركات"), css + '<body><div class="header"><h1>&#127973; ' +
        ae("مستشفى الشركات") + '</h1><nav><a href="/dashboard">' + ae("لوحة التحكم") +
        '</a><a href="/triage" class="active">' + ae("استقبال") + '</a><a href="/cases">' +
        ae("الحالات") + '</a></nav></div><div class="main"><div class="card"><h2>&#129657; ' +
        ae("استقبال حالة جديدة") + '</h2><p>' + ae("صف مشكلة شركتك وسيقوم النظام بفرزها وتوجيهها للتخصص المناسب") +
        '</p><div class="error" id="error"></div><form id="case-form" onsubmit="submitCase(event)"><div class="form-group"><label>' +
        ae("عنوان المشكلة") + '</label><input type="text" id="title" required placeholder="' +
        ae("مثال: انخفاض المبيعات في الربع الأخير") + '" minlength="5" maxlength="300"></div><div class="form-group"><label>' +
        ae("وصف تفصيلي") + '</label><textarea id="description" required placeholder="' +
        ae("اشرح المشكلة بالتفصيل... ما الذي يحدث؟ منذ متى؟ ما تأثيره على الشركة؟") +
        '" minlength="20"></textarea></div><div class="form-group"><label>' + ae("المجال") +
        '</label><select id="category" required>' + cats + '</select></div><button type="submit" class="btn" id="submit-btn">' +
        ae("ابدأ التشخيص") + '</button></form><div class="loading" id="loading"><div class="spinner"></div><p style="color:#6B7280;font-size:14px">' +
        ae("جاري فحص الحالة...") + '</p></div><div class="result" id="result"><div class="triage-box"><h3>' +
        ae("نتيجة الفرز") + '</h3><p style="margin-bottom:8px"><strong>' + ae("الخطورة:") +
        '</strong> <span id="severity-badge"></span></p><p style="margin-bottom:8px"><strong>' +
        ae("الكلمات المفتاحية:") + '</strong> <span id="keywords"></span></p><p><strong>' +
        ae("الخبراء المقترحون:") + '</strong> <span id="experts"></span></p></div>' +
        '<a href="#" class="diagnose-link" id="diagnose-btn" style="display:none" onclick="runDiagnose(event)">&#129504; ' +
        ae("شغّل التشخيص بالذكاء الاصطناعي") + '</a><div id="diagnosis-result" style="display:none;margin-top:16px"></div>' +
        '<a href="/cases" class="btn" style="display:inline-block;margin-top:16px;text-decoration:none">' +
        ae("عرض كل الحالات") + '</a></div></div></div><script>var API="https://companies-hospital-production.up.railway.app";' +
        'var currentCaseId=null;function showError(m){var e=document.getElementById("error");e.textContent=m;e.classList.add("show");setTimeout(function(){e.classList.remove("show")},6000)}' +
        'async function submitCase(e){e.preventDefault();var t=localStorage.getItem("token");if(!t){window.location.href="/login";return}' +
        'var b=document.getElementById("submit-btn");b.disabled=true;document.getElementById("loading").classList.add("show");' +
        'document.getElementById("result").classList.remove("show");document.getElementById("error").classList.remove("show");' +
        'try{var r=await fetch(API+"/api/v1/cases",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+t},' +
        'body:JSON.stringify({title:document.getElementById("title").value,description:document.getElementById("description").value,category:document.getElementById("category").value})});' +
        'var d=await r.json();if(!r.ok)throw new Error(d.detail||"' + ae("فشل إنشاء الحالة") + '");' +
        'currentCaseId=d.id;document.getElementById("severity-badge").innerHTML=\'<span class="severity \'+d.severity+\'">\'+severityLabel(d.severity)+\'</span>\';' +
        'document.getElementById("keywords").innerHTML=(d.triage_result.keywords||[]).map(function(k){return\'<span class="tag">\'+k+\'</span>\'}).join(" ");' +
        'document.getElementById("experts").innerHTML=(d.triage_result.suggested_experts||[]).map(function(e){return\'<span class="expert-tag">\'+e+\'</span>\'}).join(" ");' +
        'document.getElementById("result").classList.add("show");document.getElementById("diagnose-btn").style.display="inline-block";' +
        'document.getElementById("case-form").reset()}catch(err){showError(err.message)}finally{b.disabled=false;document.getElementById("loading").classList.remove("show")}}' +
        'function severityLabel(s){var m={critical:"&#128680; '+ae("حرجة")+'",high:"&#128308; '+ae("عالية")+'",medium:"&#128993; '+ae("متوسطة")+'",low:"&#128994; '+ae("منخفضة")+'"};return m[s]||s}' +
        'async function runDiagnose(e){e.preventDefault();if(!currentCaseId)return;var t=localStorage.getItem("token");' +
        'var b=document.getElementById("diagnose-btn");b.textContent="'+ae("جاري التشخيص...")+'";b.style.opacity="0.5";b.onclick=null;' +
        'try{var r=await fetch(API+"/api/v1/cases/"+currentCaseId+"/diagnose",{method:"POST",headers:{"Authorization":"Bearer "+t}});' +
        'var d=await r.json();var div=document.getElementById("diagnosis-result");div.style.display="block";' +
        'div.innerHTML="<div style=\\"background:#F9FAFB;border-radius:12px;padding:20px;margin-top:12px\\"><h3 style=\\"margin-bottom:12px;color:#0A1E3C\\">&#129504; '+ae("التشخيص بالذكاء الاصطناعي")+
        '</h3><p style=\\"white-space:pre-wrap;font-size:14px;line-height:1.8;color:#374151\\">"+(d.diagnosis.synthesis||"'+ae("اكتمل التحليل")+'")+"</p><p style=\\"margin-top:12px;font-size:12px;color:#6B7280\\">'+
        ae("الخبراء: ")+'"+(d.analyses||[]).map(function(a){return a.emoji+" "+a.expert_name}).join(" | ")+"</p></div>";' +
        'b.style.display="none"}catch(err){showError(err.message);b.textContent="&#129504; '+ae("شغّل التشخيص بالذكاء الاصطناعي")+'";b.style.opacity="1"}}' +
        '</script></body>')


@router.get("/cases")
async def cases():
    css = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#0A1E3C,#1A3A6C);min-height:100vh;direction:rtl}
.header{background:rgba(255,255,255,.95);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.1)}
.header h1{font-size:20px;color:#0A1E3C}
.header nav a{margin-right:16px;color:#6B7280;text-decoration:none;font-size:14px;font-weight:600}
.header nav a:hover,.header nav a.active{color:#DC8C28}
.main{max-width:1000px;margin:40px auto;padding:0 20px}
.card{background:white;border-radius:16px;padding:32px;box-shadow:0 10px 40px rgba(0,0,0,.15)}
.card h2{font-size:22px;color:#0A1E3C;margin-bottom:4px}
.subtitle{color:#6B7280;font-size:14px;margin-bottom:24px}
.filter-bar{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.filter-bar select{padding:8px 14px;border:2px solid #E5E7EB;border-radius:8px;font-size:13px;text-align:right}
.filter-bar select:focus{outline:none;border-color:#DC8C28}
table{width:100%;border-collapse:collapse}
th{text-align:right;padding:12px 16px;background:#F9FAFB;color:#374151;font-size:13px;font-weight:700;border-bottom:2px solid #E5E7EB}
td{padding:14px 16px;border-bottom:1px solid #F3F4F6;font-size:13px;color:#4B5563}
tr:hover{background:#F9FAFB}
.severity{display:inline-block;width:8px;height:8px;border-radius:50%;margin-left:6px}
.severity.critical{background:#DC2626}
.severity.high{background:#D97706}
.severity.medium{background:#2563EB}
.severity.low{background:#6B7280}
.status{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600}
.status.triage_complete{background:#FEF3C7;color:#92400E}
.status.diagnosed{background:#DBEAFE;color:#1E40AF}
.status.treatment{background:#D1FAE5;color:#065F46}
.action-btn{padding:6px 14px;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;background:#0A1E3C;color:white}
.action-btn:hover{opacity:.9}
.empty{text-align:center;padding:48px 20px;color:#9CA3AF}
.empty .icon{font-size:48px;margin-bottom:16px}
.empty .btn{display:inline-block;padding:12px 28px;background:#0A1E3C;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600}
.btn-new{display:inline-block;padding:10px 24px;background:#DC8C28;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;margin-left:12px}
.btn-new:hover{opacity:.9}
th:last-child,td:last-child{text-align:center}
</style>"""
    return _page(ae("الحالات — مستشفى الشركات"), css + '<body><div class="header"><h1>&#127973; ' +
        ae("مستشفى الشركات") + '</h1><nav><a href="/dashboard">' + ae("لوحة التحكم") +
        '</a><a href="/triage">' + ae("استقبال") + '</a><a href="/cases" class="active">' +
        ae("الحالات") + '</a></nav></div><div class="main"><div class="card"><div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"><div><h2>&#128203; ' +
        ae("الحالات") + '</h2><p class="subtitle">' + ae("جميع الحالات المسجلة لشركتك") +
        '</p></div><a href="/triage" class="btn-new">+ ' + ae("حالة جديدة") +
        '</a></div><div class="filter-bar"><select id="filter-severity" onchange="renderTable()"><option value="">' +
        ae("كل مستويات الخطورة") + '</option><option value="critical">&#128680; ' + ae("حرجة") +
        '</option><option value="high">&#128308; ' + ae("عالية") + '</option><option value="medium">&#128993; ' +
        ae("متوسطة") + '</option><option value="low">&#128994; ' + ae("منخفضة") +
        '</option></select><select id="filter-status" onchange="renderTable()"><option value="">' +
        ae("كل الحالات") + '</option><option value="triage_complete">' + ae("تم الفرز") +
        '</option><option value="diagnosed">' + ae("تم التشخيص") +
        '</option></select><select id="filter-category" onchange="renderTable()"><option value="">' +
        ae("كل المجالات") + '</option><option value="finance">&#128176; ' + ae("مالية") +
        '</option><option value="marketing">&#128200; ' + ae("تسويق") +
        '</option><option value="operations">&#9881; ' + ae("عمليات") +
        '</option><option value="hr">&#128101; ' + ae("موارد بشرية") +
        '</option><option value="strategy">&#129518; ' + ae("استراتيجية") +
        '</option><option value="legal">&#9878; ' + ae("قانوني") +
        '</option><option value="technical">&#128187; ' + ae("تقني") +
        '</option></select></div><div id="loading" style="text-align:center;padding:40px;color:#6B7280">' +
        ae("جاري تحميل الحالات...") + '</div><div id="empty" class="empty" style="display:none"><div class="icon">&#128236;</div><p>' +
        ae("لا توجد حالات بعد") + '</p><a href="/triage" class="btn">' + ae("سجل أول حالة") +
        '</a></div><table id="table" style="display:none"><thead><tr><th>' + ae("الحالة") + '</th><th>' +
        ae("المجال") + '</th><th>' + ae("الخطورة") + '</th><th>' + ae("الحالة") +
        '</th><th>' + ae("التاريخ") + '</th><th>' + ae("إجراء") +
        '</th></tr></thead><tbody id="tbody"></tbody></table></div></div><script>var API="https://companies-hospital-production.up.railway.app";' +
        'var cases=[];var catLabels={finance:"'+ae("مالية")+'",marketing:"'+ae("تسويق")+'",operations:"'+ae("عمليات")+'",hr:"'+ae("موارد بشرية")+'",strategy:"'+ae("استراتيجية")+'",legal:"'+ae("قانوني")+'",technical:"'+ae("تقني")+'"};' +
        'var sevLabels={critical:"&#128680; '+ae("حرجة")+'",high:"&#128308; '+ae("عالية")+'",medium:"&#128993; '+ae("متوسطة")+'",low:"&#128994; '+ae("منخفضة")+'"};' +
        'var statusLabels={triage_complete:"'+ae("تم الفرز")+'",diagnosed:"'+ae("تم التشخيص")+'",treatment:"'+ae("تحت العلاج")+'"};' +
        'async function loadCases(){var t=localStorage.getItem("token");if(!t){window.location.href="/login";return}' +
        'document.getElementById("loading").style.display="block";try{var r=await fetch(API+"/api/v1/cases",{headers:{"Authorization":"Bearer "+t}});' +
        'var d=await r.json();cases=d.cases||[];renderTable()}catch(e){cases=[];renderTable()}}' +
        'function renderTable(){document.getElementById("loading").style.display="none";' +
        'var s=document.getElementById("filter-severity").value;var st=document.getElementById("filter-status").value;var c=document.getElementById("filter-category").value;' +
        'var f=cases;if(s)f=f.filter(function(x){return x.severity===s});if(st)f=f.filter(function(x){return x.status===st});if(c)f=f.filter(function(x){return x.category===c});' +
        'if(!f.length){document.getElementById("table").style.display="none";document.getElementById("empty").style.display="block";return}' +
        'document.getElementById("empty").style.display="none";document.getElementById("table").style.display="table";' +
        'document.getElementById("tbody").innerHTML=f.map(function(x){return"<tr><td style=font-weight:600;color:#111827>"+esc(x.title)+"</td><td>"+(catLabels[x.category]||x.category)+"</td><td><span class=\\"severity "+x.severity+"\\"></span> "+(sevLabels[x.severity]||x.severity)+"</td><td><span class=\\"status "+x.status+"\\">"+(statusLabels[x.status]||x.status)+"</span></td><td>"+(x.created_at?new Date(x.created_at).toLocaleDateString("ar-SA"):"")+"</td><td><button class=action-btn onclick=viewCase(\""+x.id+"\")>'+ae("عرض")+'</button></td></tr>"}).join("")}' +
        'function viewCase(id){window.location.href="/triage?id="+id}function esc(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML}' +
        'loadCases();</script></body>')


_LANDING_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;direction:rtl}
.hero{background:linear-gradient(135deg,#0A1E3C,#1A3A6C);color:white;padding:80px 20px;text-align:center}
.hero h1{font-size:42px;margin-bottom:16px}
.hero p{font-size:18px;color:#D1D5DB;max-width:600px;margin:0 auto 32px;line-height:1.7}
.hero .btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.btn{padding:14px 32px;border-radius:10px;font-size:16px;font-weight:700;text-decoration:none;display:inline-block}
.btn-primary{background:#DC8C28;color:white}
.btn-secondary{background:rgba(255,255,255,0.15);color:white;border:2px solid rgba(255,255,255,0.3)}
.btn-primary:hover,.btn-secondary:hover{opacity:0.9}
.features{padding:64px 20px;max-width:1000px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}
.feat{text-align:center;padding:32px 20px}
.feat .icon{font-size:40px;margin-bottom:16px}
.feat h3{font-size:18px;color:#0A1E3C;margin-bottom:8px}
.feat p{font-size:14px;color:#6B7280;line-height:1.6}
.cta{background:#F9FAFB;padding:64px 20px;text-align:center}
.cta h2{font-size:28px;color:#0A1E3C;margin-bottom:16px}
.cta p{font-size:16px;color:#6B7280;margin-bottom:32px}
.footer{text-align:center;padding:24px;color:#9CA3AF;font-size:13px}
</style>"""


@router.get("/")
async def landing():
    return _page(ae("مستشفى الشركات — نظام تشغيل ذكي للشركات العربية"), _LANDING_CSS + '<body><div class="hero"><h1>&#127973; ' +
        ae("مستشفى الشركات") + '</h1><p>' + ae("أول نظام تشغيل عربي متكامل للشركات الصغيرة والمتوسطة. تشخيص ذكي بالميتافور الطبي — استقبال، تشخيص، علاج، متابعة — عبر ٢٢ خبير ذكاء اصطناعي.") +
        '</p><div class="btns"><a href="/login" class="btn btn-primary">' + ae("ابدأ الآن — مجاناً") +
        '</a><a href="#features" class="btn btn-secondary">' + ae("اكتشف المميزات") + '</a></div></div>' +
        '<div class="features" id="features">' +
        '<div class="feat"><div class="icon">&#129504;</div><h3>' + ae("٢٢ خبير AI") + '</h3><p>' + ae("خبراء متخصصون في المالية والتسويق والعمليات والموارد البشرية والاستراتيجية والقانون والتقنية — يحللون شركتك من كل الزوايا") + '</p></div>' +
        '<div class="feat"><div class="icon">#128172;</div><h3>' + ae("تحليل بالعربية") + '</h3><p>' + ae("كل التقارير والتحليلات والتوصيات باللغة العربية الفصحى — مفهومة ودقيقة وقابلة للتنفيذ الفوري") + '</p></div>' +
        '<div class="feat"><div class="icon">#9201;</div><h3>' + ae("نتائج فورية") + '</h3><p>' + ae("أدخل مشكلة شركتك واحصل على تشخيص كامل من فريق الخبراء في أقل من ٣٠ ثانية") + '</p></div>' +
        '<div class="feat"><div class="icon">#128274;</div><h3>' + ae("خصوصية وأمان") + '</h3><p>' + ae("بيانات شركتك مشفرة ولا تشارك مع أي طرف. دخول آمن عبر حساب Google") + '</p></div>' +
        '<div class="feat"><div class="icon">#128200;</div><h3>' + ae("خطة علاج") + '</h3><p>' + ae("بعد التشخيص — خطة علاج متكاملة مع خطوات تنفيذية ومؤشرات متابعة") + '</p></div>' +
        '<div class="feat"><div class="icon">#128259;</div><h3>' + ae("١٥ قطاع") + '</h3><p>' + ae("متخصصون في قطاعات التجزئة والضيافة والحج والعمرة والنقل والإعاشة والعقارات والصحة والتعليم والتقنية والمقاولات والصناعة والمالية والزراعة والطاقة") + '</p></div>' +
        '</div><div class="cta"><h2>' + ae("جاهز تبدأ رحلة التحسين؟") + '</h2><p>' + ae("سجل دخولك بحساب Google وابدأ أول تشخيص لشركتك الآن — مجاناً") + '</p><a href="/login" class="btn btn-primary">' + ae("ابدأ الآن") + '</a></div><div class="footer"><p>' + ae("مستشفى الشركات © ٢٠٢٦ — صنع في مكة المكرمة بكل حب 🇸🇦") + '</p></div></body>')


_DASH_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#F3F4F6;min-height:100vh;direction:rtl}
.header{background:white;padding:16px 32px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.header h1{font-size:20px;color:#0A1E3C}
.header nav a{margin-right:16px;color:#6B7280;text-decoration:none;font-size:14px;font-weight:600}
.header nav a:hover,.header nav a.active{color:#DC8C28}
.user-info{font-size:13px;color:#6B7280}
.main{max-width:1000px;margin:32px auto;padding:0 20px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:24px}
.card{background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.card .icon{font-size:28px;margin-bottom:8px}
.card .value{font-size:28px;font-weight:800;color:#0A1E3C}
.card .label{font-size:13px;color:#6B7280;margin-top:4px}
.card.primary{border-right:4px solid #DC8C28}
.actions{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.action-card{background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);text-decoration:none;display:block;transition:transform .2s}
.action-card:hover{transform:translateY(-2px)}
.action-card h3{font-size:16px;color:#0A1E3C;margin-bottom:8px}
.action-card p{font-size:13px;color:#6B7280}
.btn{display:inline-block;padding:10px 24px;background:#DC8C28;color:white;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;margin-top:12px}
</style>"""


@router.get("/dashboard")
async def dashboard():
    return _page(ae("لوحة التحكم — مستشفى الشركات"), _DASH_CSS + '<body><div class="header"><h1>&#127973; ' +
        ae("مستشفى الشركات") + '</h1><nav><a href="/dashboard" class="active">' + ae("لوحة التحكم") +
        '</a><a href="/triage">' + ae("استقبال") + '</a><a href="/cases">' + ae("الحالات") +
        '</a></nav><span class="user-info" id="user-name"></span></div><div class="main"><div class="cards">' +
        '<div class="card primary"><div class="icon">&#127973;</div><div class="value" id="stats-company">-</div><div class="label">' + ae("الشركة") + '</div></div>' +
        '<div class="card"><div class="icon">&#128203;</div><div class="value" id="stats-cases">-</div><div class="label">' + ae("الحالات") + '</div></div>' +
        '<div class="card"><div class="icon">&#129504;</div><div class="value" id="stats-experts">22</div><div class="label">' + ae("خبير AI") + '</div></div>' +
        '<div class="card"><div class="icon">&#9889;</div><div class="value" id="stats-diagnosed">-</div><div class="label">' + ae("تم تشخيصها") + '</div></div>' +
        '</div><div class="actions">' +
        '<a href="/triage" class="action-card"><h3>&#129657; ' + ae("حالة جديدة") + '</h3><p>' + ae("أدخل مشكلة شركتك وسيقوم الذكاء الاصطناعي بتشخيصها") + '</p><span class="btn">' + ae("ابدأ الآن") + '</span></a>' +
        '<a href="/cases" class="action-card"><h3>&#128203; ' + ae("الحالات السابقة") + '</h3><p>' + ae("راجع كل الحالات السابقة وتوصيات الخبراء") + '</p><span class="btn">' + ae("استعرض") + '</span></a>' +
                '</div></div><script>var API="https://companies-hospital-production.up.railway.app";var p=new URLSearchParams(window.location.search);var t=p.get("token");if(t){localStorage.setItem("token",t);window.history.replaceState({},document.title,"/dashboard")}t=localStorage.getItem("token");if(!t){window.location.href="/login"}try{var u=await fetch(API+"/api/v1/auth/me",{headers:{Authorization:"Bearer "+t}});var d=await u.json();document.getElementById("user-name").textContent=d.name;var cs=await fetch(API+"/api/v1/cases",{headers:{Authorization:"Bearer "+t}});var cd=await cs.json();var cases=cd.cases||[];document.getElementById("stats-cases").textContent=cd.total;var diagnosed=cases.filter(function(c){return c.status==="diagnosed"}).length;document.getElementById("stats-diagnosed").textContent=diagnosed;var co=await fetch(API+"/api/v1/companies",{headers:{Authorization:"Bearer "+t}});try{var cod=await co.json();if(cod.cases&&cod.total)document.getElementById("stats-company").textContent=cod.total}else{document.getElementById("stats-company").textContent="1"}}catch(e){console.error(e)}})();</script></body>')
