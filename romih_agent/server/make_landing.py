# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')

ae = lambda t: ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in t)

html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ae("Romih Agent — العقل المؤسسي الذكي")}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0f1e;color:#e2e8f0;font:16px/1.7 'Segoe UI',system-ui;overflow-x:hidden}}

/* Hero */
.hero{{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f172a 100%);padding:60px 24px 80px;text-align:center;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(circle at 30% 50%,rgba(56,189,248,0.1) 0%,transparent 50%)}}
.hero h1{{font-size:clamp(28px,5vw,48px);color:#38bdf8;position:relative;margin-bottom:12px}}
.hero p{{font-size:18px;color:#94a3b8;max-width:600px;margin:0 auto 24px;position:relative}}
.hero .badge{{display:inline-flex;gap:16px;margin-bottom:20px;position:relative}}
.hero .badge span{{background:#1e293b;border:1px solid #334155;padding:6px 16px;border-radius:20px;font-size:13px;color:#94a3b8}}
.hero .badge span b{{color:#38bdf8}}
.btn{{display:inline-block;background:#38bdf8;color:#0f172a;padding:12px 32px;border-radius:10px;font-weight:700;font-size:16px;text-decoration:none;transition:all .2s;border:none;cursor:pointer}}
.btn:hover{{background:#7dd3fc;transform:translateY(-2px)}}
.btn-outline{{background:transparent;border:2px solid #38bdf8;color:#38bdf8;margin-right:12px}}
.btn-outline:hover{{background:#38bdf8;color:#0f172a}}

/* Stats */
.stats{{display:flex;justify-content:center;gap:32px;flex-wrap:wrap;margin:-36px 24px 40px;position:relative;z-index:2}}
.stat-card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px 32px;text-align:center;min-width:140px}}
.stat-card .num{{font-size:36px;font-weight:800;color:#38bdf8;display:block}}
.stat-card .label{{font-size:13px;color:#64748b;margin-top:4px}}

/* Sections */
.section{{padding:48px 24px;max-width:1100px;margin:0 auto}}
.section h2{{font-size:28px;color:#f1f5f9;text-align:center;margin-bottom:8px}}
.section .sub{{text-align:center;color:#64748b;margin-bottom:32px;font-size:15px}}

/* Features grid */
.features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}
.feature{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px;transition:all .2s;cursor:default}}
.feature:hover{{border-color:#38bdf8;transform:translateY(-4px)}}
.feature .icon{{font-size:32px;margin-bottom:12px}}
.feature h3{{font-size:17px;color:#f1f5f9;margin-bottom:8px}}
.feature p{{font-size:13px;color:#94a3b8;line-height:1.8}}
.feature .count{{display:inline-block;background:#0f172a;color:#38bdf8;padding:2px 10px;border-radius:10px;font-size:11px;margin-top:8px}}

/* Dashboard preview */
.preview{{background:#0f172a;border:1px solid #334155;border-radius:16px;overflow:hidden}}
.preview-header{{background:#1e293b;padding:12px 16px;display:flex;gap:8px;align-items:center}}
.preview-dot{{width:10px;height:10px;border-radius:50%}}
.preview-dot.r{{background:#ef4444}} .preview-dot.y{{background:#eab308}} .preview-dot.g{{background:#22c55e}}
.preview-body{{padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}
.pv-card{{background:#1e293b;border-radius:8px;padding:14px}}
.pv-card .pv-title{{font-size:11px;color:#64748b;text-transform:uppercase;margin-bottom:8px}}
.pv-card .pv-val{{font-size:22px;font-weight:700;color:#38bdf8}}
.pv-card .pv-sub{{font-size:12px;color:#94a3b8;margin-top:4px}}

/* CTA */
.cta{{background:linear-gradient(135deg,#1e3a5f,#0f172a);text-align:center;padding:60px 24px}}
.cta h2{{color:#f1f5f9;margin-bottom:12px}}
.cta p{{color:#94a3b8;margin-bottom:24px;max-width:500px;margin-left:auto;margin-right:auto}}

/* Footer */
.footer{{text-align:center;padding:24px;color:#475569;font-size:13px;border-top:1px solid #1e293b}}
</style>
</head>
<body>

<!-- Hero -->
<div class="hero">
  <div class="badge">
    <span>v1.0</span>
    <span>{ae("أدوات: ")}<b>113</b></span>
    <span>{ae("بلجنز: ")}<b>4</b></span>
  </div>
  <h1>{ae("Romih Agent — العقل المؤسسي الذكي")}</h1>
  <p>{ae("أول وكيل AI عربي متكامل. يدير ورشتك، شركتك، أعمالك — من تيليجرام أو الويب. فكّر، خطّط، نفّذ.")}</p>
  <a href="/romih/" class="btn">{ae("جرّب الآن")}</a>
  <a href="/romih/dashboard" class="btn btn-outline">{ae("لوحة التحكم")}</a>
</div>

<!-- Stats -->
<div class="stats">
  <div class="stat-card"><span class="num">113</span><span class="label">{ae("أداة ذكية")}</span></div>
  <div class="stat-card"><span class="num">4</span><span class="label">{ae("بلجن مؤسسي")}</span></div>
  <div class="stat-card"><span class="num">24/7</span><span class="label">{ae("تشغيل مستمر")}</span></div>
  <div class="stat-card"><span class="num">0.2s</span><span class="label">{ae("سرعة استجابة")}</span></div>
</div>

<!-- Features -->
<div class="section">
  <h2>{ae("نظام ERP متكامل بالعربي")}</h2>
  <p class="sub">{ae("كل ما تحتاجه شركتك في مكان واحد")}</p>
  <div class="features">
    <div class="feature">
      <div class="icon">🏭</div>
      <h3>{ae("إدارة الورش")}</h3>
      <p>{ae("عملاء، تصليحات، قطع غيار، فواتير. متابعة كل معاملة من البداية للنهاية.")}</p>
      <span class="count">12 {ae("أداة")}</span>
    </div>
    <div class="feature">
      <div class="icon">👥</div>
      <h3>{ae("الموارد البشرية")}</h3>
      <p>{ae("موظفين، إجازات، رواتب، تقييم أداء. كل بيانات فريقك في نظام واحد.")}</p>
      <span class="count">16 {ae("أداة")}</span>
    </div>
    <div class="feature">
      <div class="icon">💰</div>
      <h3>{ae("المالية")}</h3>
      <p>{ae("فواتير، مصروفات، حسابات بنكية، تقارير أرباح وخسائر. ضريبة القيمة المضافة تلقائياً.")}</p>
      <span class="count">12 {ae("أداة")}</span>
    </div>
    <div class="feature">
      <div class="icon">📋</div>
      <h3>{ae("المشاريع")}</h3>
      <p>{ae("مشاريع، مهام، مواعيد، توزيع عمل. تابع كل مشروع من البداية للتسليم.")}</p>
      <span class="count">10 {ae("أداة")}</span>
    </div>
  </div>
</div>

<!-- Dashboard Preview -->
<div class="section">
  <h2>{ae("لوحة تحكم واحدة لكل شيء")}</h2>
  <p class="sub">{ae("راقب أعمالك من مكان واحد — محدثة تلقائياً")}</p>
  <div class="preview">
    <div class="preview-header">
      <div class="preview-dot r"></div><div class="preview-dot y"></div><div class="preview-dot g"></div>
      <span style="color:#64748b;font-size:12px;margin-right:8px">Romih Dashboard v1.0</span>
    </div>
    <div class="preview-body">
      <div class="pv-card">
        <div class="pv-title">{ae("تصليحات نشطة")}</div>
        <div class="pv-val">127</div>
        <div class="pv-sub">{ae("+12 اليوم")}</div>
      </div>
      <div class="pv-card">
        <div class="pv-title">{ae("موظفين")}</div>
        <div class="pv-val">45</div>
        <div class="pv-sub">4 {ae("أقسام")}</div>
      </div>
      <div class="pv-card">
        <div class="pv-title">{ae("إيرادات الشهر")}</div>
        <div class="pv-val">85,400</div>
        <div class="pv-sub">{ae("ريال سعودي")}</div>
      </div>
      <div class="pv-card">
        <div class="pv-title">{ae("مشاريع")}</div>
        <div class="pv-val">8</div>
        <div class="pv-sub">3 {ae("على وشك التسليم")}</div>
      </div>
    </div>
  </div>
</div>

<!-- CTA -->
<div class="cta">
  <h2>{ae("جاهز تبدأ؟")}</h2>
  <p>{ae("جرّب Romih Agent مجاناً. بوت تيليجرام + لوحة تحكم. عربي ١٠٠٪.")}</p>
  <a href="https://t.me/RomihAgentbot" class="btn" style="font-size:18px;padding:14px 40px">{ae("تحدث مع Romih الآن ←")}</a>
</div>

<div class="footer">
  {ae("Romih Agent © 2026 — بُني بفخر في مكة المكرمة 🕋")}
</div>
</body>
</html>'''

with open(r'C:\Users\saifr\.openclaw-autoclaw\workspace\companies-hospital\romih_agent\server\landing.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Landing page written')
