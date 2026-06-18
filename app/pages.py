"""Unified app - single page handles auth + dashboard + triage + cases"""
from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["app"])


def ae(text):
    return ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in text)


def _page(title, body):
    html = '<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>' + title + '</title>' + body + '</html>'
    return Response(content=ae(html).encode('ascii'), media_type="text/html; charset=utf-8",
                    headers={"Cache-Control": "no-store"})


_APP_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#F3F4F6;direction:rtl;min-height:100vh}
.header{background:white;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,.08);position:sticky;top:0;z-index:10}
.header h1{font-size:18px;color:#0A1E3C}
.header nav a{margin-right:12px;color:#6B7280;text-decoration:none;font-size:13px;font-weight:600}
.header nav a.active{color:#DC8C28}
.user-info{font-size:12px;color:#6B7280}
.main{max-width:800px;margin:24px auto;padding:0 16px}
.card{background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.06);margin-bottom:16px}
.card h2{font-size:20px;color:#0A1E3C;margin-bottom:8px}
.card p{font-size:13px;color:#6B7280;margin-bottom:16px}
.form-group{margin-bottom:14px}
label{display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:4px}
input,select,textarea{width:100%;padding:10px 14px;border:2px solid #E5E7EB;border-radius:8px;font-size:14px;text-align:right;font-family:'Segoe UI',Tahoma,sans-serif}
textarea{min-height:100px;resize:vertical}
input:focus,select:focus,textarea:focus{outline:none;border-color:#DC8C28}
.btn{display:inline-block;padding:12px 24px;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;text-decoration:none}
.btn-primary{background:#0A1E3C;color:white}
.btn-gold{background:#DC8C28;color:white}
.btn:hover{opacity:.9}
.btn-google{background:white;color:#374151;border:2px solid #E5E7EB;display:flex;align-items:center;justify-content:center;gap:8px;width:100%}
.severity{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:700;margin:0 4px}
.severity.critical{background:#FEE2E2;color:#DC2626}
.severity.high{background:#FEF3C7;color:#D97706}
.severity.medium{background:#DBEAFE;color:#2563EB}
.severity.low{background:#F3F4F6;color:#6B7280}
.status{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600}
.status.triage_complete{background:#FEF3C7;color:#92400E}
.status.diagnosed{background:#DBEAFE;color:#1E40AF}
.tag{display:inline-block;background:#E5E7EB;color:#374151;padding:3px 8px;border-radius:6px;font-size:11px;margin:2px}
.expert-tag{display:inline-block;background:#FEF3C7;color:#92400E;padding:3px 8px;border-radius:6px;font-size:11px;margin:2px}
.hidden{display:none}
.error{background:#FEF2F2;color:#DC2626;padding:10px;border-radius:8px;font-size:12px;margin:8px 0;display:none}
.success{background:#F0FDF4;color:#16A34A;padding:10px;border-radius:8px;font-size:12px;margin:8px 0;display:none}
.error.show,.success.show{display:block}
.loading{text-align:center;padding:20px;display:none}
.loading.show{display:block}
.spinner{border:3px solid #E5E7EB;border-top:3px solid #DC8C28;border-radius:50%;width:28px;height:28px;animation:spin .8s linear infinite;margin:0 auto 8px}
@keyframes spin{to{transform:rotate(360deg)}}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:16px}
.stat{background:white;border-radius:10px;padding:16px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.stat .v{font-size:24px;font-weight:800;color:#0A1E3C}
.stat .l{font-size:11px;color:#6B7280;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{text-align:right;padding:10px 12px;background:#F9FAFB;color:#374151;font-size:12px;font-weight:700;border-bottom:2px solid #E5E7EB}
td{padding:10px 12px;border-bottom:1px solid #F3F4F6;color:#4B5563}
tr:hover{background:#F9FAFB}
.tab-bar{display:flex;gap:0;margin-bottom:16px}
.tab-bar button{flex:1;padding:10px;border:none;background:#E5E7EB;font-size:13px;font-weight:600;cursor:pointer;color:#6B7280}
.tab-bar button.active{background:#0A1E3C;color:white}
.tab-bar button:first-child{border-radius:0 8px 8px 0}
.tab-bar button:last-child{border-radius:8px 0 0 8px}
@media(max-width:500px){.header h1{font-size:15px}.header nav a{font-size:11px;margin-right:8px}}
@media(max-width:640px){
  .main{padding:0 8px;margin:8px auto;width:100%}
  .header{padding:8px 10px;flex-wrap:wrap;gap:4px}
  .header h1{font-size:15px}
  .header nav{margin-top:4px;width:100%;display:flex;flex-wrap:wrap;gap:4px}
  .header nav a{font-size:11px;padding:4px 8px;margin-right:0}
  .card{padding:14px;border-radius:10px;margin-bottom:10px;width:100%}
  .card h2{font-size:16px;margin-bottom:6px}
  .card p{font-size:12px;margin-bottom:10px}
  .btn{padding:12px 14px;font-size:14px;width:100%}
  .btn-google{font-size:12px}
  table{font-size:10px}
  th,td{padding:6px 4px}
  .tab-bar button{font-size:11px;padding:8px 6px}
  .stats{grid-template-columns:repeat(2,1fr);gap:6px}
  .stat{padding:10px 6px}
  .stat .v{font-size:18px}
  .stat .l{font-size:10px}
  input,select,textarea{font-size:16px;padding:10px 10px;width:100%;max-width:100%}
  textarea{min-height:80px}
  #cases-table-wrapper{overflow-x:auto;-webkit-overflow-scrolling:touch}
  .severity{font-size:9px;padding:2px 4px}
  .status{font-size:9px;padding:2px 4px}
  .tag,.expert-tag{font-size:10px;padding:2px 6px}
  .user-info{font-size:10px}
  .error,.success{padding:8px;font-size:11px}
  .loading p{font-size:11px}
}
</style>"""


@router.get("/app")
async def unified_app():
    title = ae("مستشفى الشركات")
    subtitle = ae("نظام تشغيل ذكي للشركات العربية")
    login_btn = ae("تسجيل الدخول")
    reg_btn = ae("إنشاء حساب")
    google_btn = ae("متابعة بحساب Google")
    email_lbl = ae("البريد الإلكتروني")
    pass_lbl = ae("كلمة المرور")
    name_lbl = ae("الاسم الكامل")
    tab_login = ae("دخول")
    tab_reg = ae("حساب جديد")
    dashboard_tab = ae("لوحة التحكم")
    triage_tab = ae("استقبال")
    cases_tab = ae("الحالات")
    welcome = ae("أهلاً بك في مستشفى الشركات")
    dash_desc = ae("من هنا تدير كل شيء - استقبال، تشخيص، متابعة")
    new_case_btn = ae("+ حالة جديدة")
    err_login = ae("فشل تسجيل الدخول")
    err_reg = ae("فشل إنشاء الحساب")
    err_case = ae("فشل إنشاء الحالة")

    return _page(title, _APP_CSS + '<body><div id="app"><div class="header"><h1>&#127973; ' + title +
        '</h1><nav id="nav" class="hidden"><a href="#" onclick="showTab(\'dashboard\')" class="active" data-tab="dashboard">' + dashboard_tab +
        '</a><a href="#" onclick="showTab(\'triage\')" data-tab="triage">' + triage_tab +
        '</a><a href="#" onclick="showTab(\'cases\')" data-tab="cases">' + cases_tab +
        '</a></nav><span class="user-info" id="user-name"></span></div>' +
        # LOGIN VIEW
        '<div id="view-login"><div class="main"><div class="card" style="max-width:400px;margin:60px auto"><h2>' + title + '</h2><p>' + subtitle + '</p>' +
        '<div class="tab-bar"><button class="active" onclick="switchAuthTab(\'login\')">' + tab_login + '</button><button onclick="switchAuthTab(\'register\')">' + tab_reg + '</button></div>' +
        '<div class="error" id="auth-error"></div>' +
        '<form id="login-form" onsubmit="doLogin(event)"><div class="form-group"><label>' + email_lbl + '</label><input type="email" id="le" required></div><div class="form-group"><label>' + pass_lbl + '</label><input type="password" id="lp" required></div><button type="submit" class="btn btn-primary" style="width:100%">' + login_btn + '</button></form>' +
        '<form id="register-form" class="hidden" onsubmit="doRegister(event)"><div class="form-group"><label>' + name_lbl + '</label><input type="text" id="rn" required></div><div class="form-group"><label>' + email_lbl + '</label><input type="email" id="re" required></div><div class="form-group"><label>' + pass_lbl + '</label><input type="password" id="rp" required minlength="8"></div><button type="submit" class="btn btn-primary" style="width:100%">' + reg_btn + '</button></form>' +
        '<div style="text-align:center;margin:16px 0;color:#9CA3AF;font-size:12px">' + ae("أو") + '</div>' +
        '<button class="btn btn-google" onclick="doGoogleLogin()"><svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>' + google_btn + '</button></div></div></div>' +
        # DASHBOARD VIEW
        '<div id="view-dashboard" class="hidden"><div class="main"><h2 style="margin-bottom:16px;color:#0A1E3C">' + welcome + '</h2><div class="stats"><div class="stat"><div class="v" id="st-company">-</div><div class="l">' + ae("الشركة") + '</div></div><div class="stat"><div class="v" id="st-cases">-</div><div class="l">' + ae("الحالات") + '</div></div><div class="stat"><div class="v">22</div><div class="l">' + ae("خبير AI") + '</div></div><div class="stat"><div class="v" id="st-diagnosed">-</div><div class="l">' + ae("تم تشخيصها") + '</div></div></div><div class="card"><h2>&#129657; ' + ae("استقبال حالة جديدة") + '</h2><p>' + ae("صف مشكلة شركتك وسيقوم الذكاء الاصطناعي بتشخيصها فوراً") + '</p><div class="error" id="case-error"></div><form onsubmit="doTriage(event)"><div class="form-group"><label>' + ae("عنوان المشكلة") + '</label><input type="text" id="ct" required></div><div class="form-group"><label>' + ae("وصف تفصيلي") + '</label><textarea id="cd" required></textarea></div><div class="form-group"><label>' + ae("المجال") + '</label><select id="cc" required><option value="">' + ae("اختر المجال") + '</option><option value="finance">' + ae("مالية") + '</option><option value="marketing">' + ae("تسويق ومبيعات") + '</option><option value="operations">' + ae("عمليات") + '</option><option value="hr">' + ae("موارد بشرية") + '</option><option value="strategy">' + ae("استراتيجية") + '</option><option value="legal">' + ae("قانوني") + '</option><option value="technical">' + ae("تقني") + '</option></select></div><button type="submit" class="btn btn-gold">' + ae("ابدأ التشخيص") + '</button></form><div class="loading" id="triage-loading"><div class="spinner"></div><p style="font-size:12px;color:#6B7280">' + ae("جاري التحليل...") + '</p></div><div id="triage-result" class="hidden"></div></div></div></div>' +
        # CASES VIEW
        '<div id="view-cases" class="hidden"><div class="main"><div class="card"><h2>&#128203; ' + ae("الحالات") + '</h2><div class="loading" id="cases-loading">' + ae("جاري التحميل...") + '</div><div id="cases-empty" class="hidden" style="text-align:center;padding:32px;color:#9CA3AF"><p style="font-size:32px;margin-bottom:8px">&#128236;</p><p>' + ae("لا توجد حالات بعد") + '</p></div><div id="cases-table-wrapper" style="overflow-x:auto;-webkit-overflow-scrolling:touch"><table id="cases-table" class="hidden"><thead><tr><th>' + ae("الحالة") + '</th><th>' + ae("المجال") + '</th><th>' + ae("الخطورة") + '</th><th>' + ae("الحالة") + '</th><th>' + ae("التاريخ") + '</th></tr></thead><tbody id="cases-body"></tbody></table></div></div></div></div>' +
        '</div><script>var A="https://companies-hospital-production.up.railway.app";' +
        'function T(){var m=document.cookie.match(/ch_token=([^;]+)/);return m?m[1]:localStorage.getItem("token")}' +
        'function E(id,m){var e=document.getElementById(id);e.textContent=m;e.classList.add("show");setTimeout(function(){e.classList.remove("show")},5e3)}' +
        'function $(id){return document.getElementById(id)}' +
        'function showTab(t){document.querySelectorAll("#nav a").forEach(function(a){a.classList.toggle("active",a.dataset.tab===t)});["dashboard","triage","cases"].forEach(function(v){$("view-"+v).classList.toggle("hidden",v!==t)});if(t==="cases")loadCases()}' +
        'function switchAuthTab(t){document.querySelectorAll(".tab-bar button").forEach(function(b,i){b.classList.toggle("active",(i===0&&t==="login")||(i===1&&t==="register"))});$("login-form").classList.toggle("hidden",t!=="login");$("register-form").classList.toggle("hidden",t!=="register")}' +
        'async function doLogin(e){e.preventDefault();try{var r=await fetch(A+"/api/v1/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:$("le").value,password:$("lp").value})});var d=await r.json();if(!r.ok)throw new Error(d.detail||"' + err_login + '");localStorage.setItem("token",d.access_token);init()' + '}catch(err){E("auth-error",err.message)}}' +
        'async function doRegister(e){e.preventDefault();try{var r=await fetch(A+"/api/v1/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:$("rn").value,email:$("re").value,password:$("rp").value})});var d=await r.json();if(!r.ok)throw new Error(d.detail||"' + err_reg + '");localStorage.setItem("token",d.access_token);init()' + '}catch(err){E("auth-error",err.message)}}' +
        'function doGoogleLogin(){window.location.href=A+"/api/v1/auth/google/login"}' +
        'async function doTriage(e){e.preventDefault();$("case-error").classList.remove("show");$("triage-loading").classList.add("show");$("triage-result").classList.add("hidden");var t=T();try{var r=await fetch(A+"/api/v1/cases",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+t},body:JSON.stringify({title:$("ct").value,description:$("cd").value,category:$("cc").value})});var d=await r.json();if(!r.ok)throw new Error(d.detail||"' + err_case + '");$("triage-result").innerHTML="<div style=\\"background:#F9FAFB;border-radius:10px;padding:16px\\"><p><strong>' + ae("الخطورة:") + '</strong> <span class=\\"severity \\"+d.severity+\\">"+["'+ae('حرجة')+'","'+ae('عالية')+'","'+ae('متوسطة')+'","'+ae('منخفضة')+'"][{critical:0,high:1,medium:2,low:3}[d.severity]]+"</span></p><p style=\\"margin-top:8px\\"><strong>' + ae("الكلمات المفتاحية:") + '</strong> "+(d.triage_result.keywords||[]).map(function(k){return"<span class=tag>"+k+"</span>"}).join(" ")+"</p><p style=\\"margin-top:8px\\"><strong>' + ae("الخبراء:") + '</strong> "+(d.triage_result.suggested_experts||[]).map(function(e){return"<span class=expert-tag>"+e+"</span>"}).join(" ")+"</p><button class=\\"btn btn-gold\\" style=\\"margin-top:12px\\" onclick=doDiagnose(\\""+d.id+"\\")>&#129504; ' + ae("شغّل الذكاء الاصطناعي") + '</button><div id=\\"diag-"+d.id+"\\"></div></div>";' +
        '$("triage-result").classList.remove("hidden");$("ct").value="";$("cd").value=""}catch(err){E("case-error",err.message)}finally{$("triage-loading").classList.remove("show")}}' +
        'async function doDiagnose(id){var di=$("diag-"+id);di.innerHTML="<div class=loading><div class=spinner></div><p>' + ae("جاري تشغيل الخبراء...") + '</p></div>";var t=T();try{var r=await fetch(A+"/api/v1/cases/"+id+"/diagnose",{method:"POST",headers:{"Authorization":"Bearer "+t}});var d=await r.json();di.innerHTML="<div style=\\"background:#F9FAFB;border-radius:10px;padding:16px;margin-top:12px\\"><h3 style=\\"color:#0A1E3C;margin-bottom:8px\\">&#129504; ' + ae("التشخيص") + '</h3><div style=\\"white-space:pre-wrap;font-size:13px;line-height:1.8;color:#374151\\">"+(d.diagnosis.synthesis||d.diagnosis.themes.join(", "))+"</div><p style=\\"margin-top:8px;font-size:11px;color:#6B7280\\">' + ae("الخبراء:") + ' "+(d.analyses||[]).map(function(a){return a.emoji+" "+a.expert_name}).join(" | ")+" | ' + ae("التوافق:") + ' "+Math.round(d.diagnosis.consensus_score*100)+"%</p></div>"}catch(err){di.innerHTML="<p style=color:#DC2626>"+err.message+"</p>"}}' +
        'async function loadCases(){var t=T();try{var r=await fetch(A+"/api/v1/cases",{headers:{"Authorization":"Bearer "+t}});var d=await r.json();var cs=d.cases||[];$("cases-loading").classList.add("hidden");if(!cs.length){$("cases-empty").classList.remove("hidden");return}$("cases-table").classList.remove("hidden");' +
        'var labels={finance:"' + ae("مالية") + '",marketing:"' + ae("تسويق") + '",operations:"' + ae("عمليات") + '",hr:"' + ae("موارد بشرية") + '",strategy:"' + ae("استراتيجية") + '",legal:"' + ae("قانوني") + '",technical:"' + ae("تقني") + '"};' +
        'var sev={critical:"' + ae("حرجة") + '",high:"' + ae("عالية") + '",medium:"' + ae("متوسطة") + '",low:"' + ae("منخفضة") + '"};' +
        'var sts={triage_complete:"' + ae("تم الفرز") + '",diagnosed:"' + ae("تم التشخيص") + '"};' +
        '$("cases-body").innerHTML=cs.map(function(c){return"<tr><td style=font-weight:600;color:#111827>"+c.title+"</td><td>"+(labels[c.category]||c.category)+"</td><td><span class=\\"severity \\"+c.severity+"\\"></span> "+(sev[c.severity]||c.severity)+"</td><td><span class=\\"status \\"+c.status+"\\">"+(sts[c.status]||c.status)+"</span></td><td>"+(c.created_at?new Date(c.created_at).toLocaleDateString("ar-SA"):"")+"</td></tr>"}).join("")}catch(e){$("cases-loading").textContent="' + ae("خطأ في التحميل") + '"}}' +
        'async function init(){var t=T();var p=new URLSearchParams(window.location.search);var tu=p.get("token");if(tu){localStorage.setItem("token",tu);t=tu;window.history.replaceState({},document.title,"/app")}if(!t){$("view-login").classList.remove("hidden");$("nav").classList.add("hidden");return}$("view-login").classList.add("hidden");$("nav").classList.remove("hidden");$("view-dashboard").classList.remove("hidden");try{var u=await fetch(A+"/api/v1/auth/me",{headers:{"Authorization":"Bearer "+t}});var ud=await u.json();$("user-name").textContent=ud.name;var cr=await fetch(A+"/api/v1/cases",{headers:{"Authorization":"Bearer "+t}});var cd=await cr.json();$("st-cases").textContent=cd.total;$("st-diagnosed").textContent=(cd.cases||[]).filter(function(c){return c.status==="diagnosed"}).length;$("st-company").textContent="1"}catch(e){console.error(e)}}' +
        'init();</script></body>')


@router.get("/demo")
async def demo():
    """Demo mode - no auth needed, token created on the fly."""
    import httpx
    title = ae("مستشفى الشركات - تجريبي")
    subtitle = ae("نظام تشغيل ذكي للشركات العربية")
    welcome = ae("أهلاً بك")
    dash_desc = ae("من هنا تدير كل شيء")
    new_case_btn = ae("+ حالة جديدة")
    err_case = ae("فشل إنشاء الحالة")
    
    return _page(title, _APP_CSS + '<body><div id="app"><div class="header"><h1>&#127973; ' + title +
        '</h1><nav><a href="#" onclick="showTab(\'dashboard\')" class="active" data-tab="dashboard">' + ae("لوحة التحكم") +
        '</a><a href="#" onclick="showTab(\'triage\')" data-tab="triage">' + ae("استقبال") +
        '</a><a href="#" onclick="showTab(\'cases\')" data-tab="cases">' + ae("الحالات") +
        '</a></nav><span class="user-info">' + ae("وضع تجريبي") + '</span></div>' +
        '<div id="view-dashboard"><div class="main"><h2 style="margin-bottom:16px;color:#0A1E3C">' + welcome + '</h2><div class="stats"><div class="stat"><div class="v">1</div><div class="l">' + ae("الشركة") + '</div></div><div class="stat"><div class="v" id="st-cases">-</div><div class="l">' + ae("الحالات") + '</div></div><div class="stat"><div class="v">22</div><div class="l">' + ae("خبير AI") + '</div></div><div class="stat"><div class="v" id="st-diagnosed">-</div><div class="l">' + ae("تم تشخيصها") + '</div></div></div><div class="card"><h2>&#129657; ' + ae("استقبال حالة جديدة") + '</h2><p>' + ae("صف مشكلة شركتك وسيقوم الذكاء الاصطناعي بتشخيصها فوراً") + '</p><div class="error" id="case-error"></div><form onsubmit="doTriage(event)"><div class="form-group"><label>' + ae("عنوان المشكلة") + '</label><input type="text" id="ct" required></div><div class="form-group"><label>' + ae("وصف تفصيلي") + '</label><textarea id="cd" required></textarea></div><div class="form-group"><label>' + ae("المجال") + '</label><select id="cc" required><option value="">' + ae("اختر المجال") + '</option><option value="finance">' + ae("مالية") + '</option><option value="marketing">' + ae("تسويق ومبيعات") + '</option><option value="operations">' + ae("عمليات") + '</option><option value="hr">' + ae("موارد بشرية") + '</option><option value="strategy">' + ae("استراتيجية") + '</option><option value="legal">' + ae("قانوني") + '</option><option value="technical">' + ae("تقني") + '</option></select></div><button type="submit" class="btn btn-gold">' + ae("ابدأ التشخيص") + '</button></form><div class="loading" id="triage-loading"><div class="spinner"></div><p style="font-size:12px;color:#6B7280">' + ae("جاري التحليل...") + '</p></div><div id="triage-result" class="hidden"></div></div></div></div>' +
        '<div id="view-cases" class="hidden"><div class="main"><div class="card"><h2>&#128203; ' + ae("الحالات") + '</h2><div class="loading" id="cases-loading">' + ae("جاري التحميل...") + '</div><div id="cases-empty" class="hidden" style="text-align:center;padding:32px;color:#9CA3AF"><p style="font-size:32px;margin-bottom:8px">&#128236;</p><p>' + ae("لا توجد حالات بعد") + '</p></div><div style="overflow-x:auto;-webkit-overflow-scrolling:touch"><table id="cases-table" class="hidden"><thead><tr><th>' + ae("الحالة") + '</th><th>' + ae("المجال") + '</th><th>' + ae("الخطورة") + '</th><th>' + ae("الحالة") + '</th><th>' + ae("التاريخ") + '</th></tr></thead><tbody id="cases-body"></tbody></table></div></div></div></div>' +
        '</div><script>var A="https://companies-hospital-production.up.railway.app";var DT="demo";' +
        'function E(id,m){var e=document.getElementById(id);e.textContent=m;e.classList.add("show");setTimeout(function(){e.classList.remove("show")},5e3)}' +
        'function $(id){return document.getElementById(id)}' +
        'function showTab(t){document.querySelectorAll("#app nav a").forEach(function(a){a.classList.toggle("active",a.dataset.tab===t)});$("view-dashboard").classList.toggle("hidden",t!=="dashboard");$("view-triage").classList.toggle("hidden",t!=="triage");$("view-cases").classList.toggle("hidden",t!=="cases");if(t==="cases")loadCases()}' +
        'async function doTriage(e){e.preventDefault();$("case-error").classList.remove("show");$("triage-loading").classList.add("show");$("triage-result").classList.add("hidden");try{var r=await fetch(A+"/api/v1/cases",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer demo"},body:JSON.stringify({title:$("ct").value,description:$("cd").value,category:$("cc").value})});var d=await r.json();if(!r.ok)throw new Error(d.detail||"' + err_case + '");$("triage-result").innerHTML="<div style=\\"background:#F9FAFB;border-radius:10px;padding:16px\\"><p><strong>' + ae("الخطورة:") + '</strong> <span class=\\"severity \\"+d.severity+\\">"+["' + ae('حرجة') + '","' + ae('عالية') + '","' + ae('متوسطة') + '","' + ae('منخفضة') + '"][{critical:0,high:1,medium:2,low:3}[d.severity]]+"</span></p><p style=\\"margin-top:8px\\"><strong>' + ae("الكلمات المفتاحية:") + '</strong> "+(d.triage_result.keywords||[]).map(function(k){return"<span class=tag>"+k+"</span>"}).join(" ")+"</p><p style=\\"margin-top:8px\\"><strong>' + ae("الخبراء:") + '</strong> "+(d.triage_result.suggested_experts||[]).map(function(ex){return"<span class=expert-tag>"+ex+"</span>"}).join(" ")+"</p><button class=\\"btn btn-gold\\" style=\\"margin-top:12px\\" onclick=doDiagnose(\\""+d.id+"\\")>&#129504; ' + ae("شغّل الذكاء الاصطناعي") + '</button><div id=\\"diag-"+d.id+"\\"></div></div>";' +
        '$("triage-result").classList.remove("hidden");$("ct").value="";$("cd").value=""}catch(err){E("case-error",err.message)}finally{$("triage-loading").classList.remove("show")}}' +
        'async function doDiagnose(id){var di=$("diag-"+id);di.innerHTML="<div class=loading><div class=spinner></div><p>' + ae("جاري تشغيل الخبراء...") + '</p></div>";try{var r=await fetch(A+"/api/v1/cases/"+id+"/diagnose",{method:"POST",headers:{"Authorization":"Bearer demo"}});var d=await r.json();di.innerHTML="<div style=\\"background:#F9FAFB;border-radius:10px;padding:16px;margin-top:12px\\"><h3 style=\\"color:#0A1E3C;margin-bottom:8px\\">&#129504; ' + ae("التشخيص") + '</h3><div style=\\"white-space:pre-wrap;font-size:13px;line-height:1.8;color:#374151\\">"+(d.diagnosis.synthesis||d.diagnosis.themes.join(", "))+"</div><p style=\\"margin-top:8px;font-size:11px;color:#6B7280\\">' + ae("الخبراء:") + ' "+(d.analyses||[]).map(function(a){return a.emoji+" "+a.expert_name}).join(" | ")+" | ' + ae("التوافق:") + ' "+Math.round(d.diagnosis.consensus_score*100)+"%</p></div>"}catch(err){di.innerHTML="<p style=color:#DC2626>"+err.message+"</p>"}}' +
        'async function loadCases(){try{var r=await fetch(A+"/api/v1/cases",{headers:{"Authorization":"Bearer demo"}});var d=await r.json();var cs=d.cases||[];$("cases-loading").classList.add("hidden");if(!cs.length){$("cases-empty").classList.remove("hidden");return}$("cases-table").classList.remove("hidden");var labels={finance:"' + ae("مالية") + '",marketing:"' + ae("تسويق") + '",operations:"' + ae("عمليات") + '",hr:"' + ae("موارد بشرية") + '",strategy:"' + ae("استراتيجية") + '",legal:"' + ae("قانوني") + '",technical:"' + ae("تقني") + '"};var sev={critical:"' + ae("حرجة") + '",high:"' + ae("عالية") + '",medium:"' + ae("متوسطة") + '",low:"' + ae("منخفضة") + '"};var sts={triage_complete:"' + ae("تم الفرز") + '",diagnosed:"' + ae("تم التشخيص") + '"};$("cases-body").innerHTML=cs.map(function(c){return"<tr><td style=font-weight:600;color:#111827>"+c.title+"</td><td>"+(labels[c.category]||c.category)+"</td><td><span class=\\"severity \\"+c.severity+"\\"></span> "+(sev[c.severity]||c.severity)+"</td><td><span class=\\"status \\"+c.status+"\\">"+(sts[c.status]||c.status)+"</span></td><td>"+(c.created_at?new Date(c.created_at).toLocaleDateString("ar-SA"):"")+"</td></tr>"}).join("")}catch(e){$("cases-loading").textContent="' + ae("خطأ في التحميل") + '"}}' +
        '(async function(){try{var r=await fetch(A+"/api/v1/cases",{headers:{"Authorization":"Bearer demo"}});var d=await r.json();$("st-cases").textContent=d.total;$("st-diagnosed").textContent=(d.cases||[]).filter(function(c){return c.status==="diagnosed"}).length}catch(e){}})();</script></body>')


@router.get("/login")
async def login():
    """Redirect /login to unified app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@router.get("/dashboard")
async def dashboard():
    """Redirect /dashboard to unified app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@router.get("/triage")
async def triage():
    """Redirect /triage to unified app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@router.get("/cases")
async def cases():
    """Redirect /cases to unified app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@router.get("/register")
async def register():
    """Redirect /register to unified app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


#@router.get("/")  # disabled: Romih landing takes root
async def landing():
    """Landing page redirects to app."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")