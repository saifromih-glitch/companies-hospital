from fastapi.responses import HTMLResponse

_HTML = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Romih Agent - &#1608;&#1603;&#1610;&#1604;&#1603; &#1575;&#1604;&#1584;&#1603;&#1610; &#1576;&#1575;&#1604;&#1593;&#1585;&#1576;&#1610;</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#0a0a2e 0%,#1a1a4e 50%,#0d0d35 100%);color:#fff;min-height:100vh;overflow-x:hidden}
.container{max-width:1100px;margin:0 auto;padding:20px}

/* Hero */
.hero{text-align:center;padding:80px 20px 40px}
.hero h1{font-size:3em;background:linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:16px}
.hero .sub{font-size:1.3em;color:#94a3b8;margin-bottom:32px;line-height:1.8}
.hero .badge{display:inline-block;background:rgba(167,139,250,0.2);color:#a78bfa;padding:8px 20px;border-radius:20px;font-size:0.9em;margin-bottom:20px;border:1px solid rgba(167,139,250,0.3)}
.hero .stats{display:flex;justify-content:center;gap:40px;margin:32px 0;flex-wrap:wrap}
.hero .stat{text-align:center}
.hero .stat .num{font-size:2em;font-weight:800;color:#60a5fa}
.hero .stat .label{color:#94a3b8;font-size:0.9em;margin-top:4px}

/* Buttons */
.btn{display:inline-block;padding:14px 36px;border-radius:12px;font-size:1.1em;font-weight:700;text-decoration:none;transition:all 0.3s;margin:8px;cursor:pointer}
.btn-primary{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;box-shadow:0 4px 20px rgba(124,58,237,0.4)}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(124,58,237,0.6)}
.btn-outline{border:2px solid #a78bfa;color:#a78bfa;background:transparent}
.btn-outline:hover{background:rgba(167,139,250,0.1);transform:translateY(-2px)}
.btn-telegram{background:#0088cc;color:#fff;box-shadow:0 4px 20px rgba(0,136,204,0.4)}
.btn-telegram:hover{transform:translateY(-2px)}

/* Section */
.section{padding:60px 20px}
.section h2{font-size:2em;text-align:center;margin-bottom:40px;color:#e2e8f0}
.section h2 span{background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}

/* Features */
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}
.card{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:28px;transition:all 0.3s}
.card:hover{background:rgba(255,255,255,0.08);transform:translateY(-4px);border-color:rgba(167,139,250,0.3)}
.card .icon{font-size:2.5em;margin-bottom:16px}
.card h3{font-size:1.3em;margin-bottom:8px;color:#e2e8f0}
.card p{color:#94a3b8;line-height:1.7;font-size:0.95em}

/* Plugins grid */
.plugins{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
.plugin-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:20px;text-align:center}
.plugin-card .icon{font-size:2.5em;margin-bottom:8px}
.plugin-card h4{color:#e2e8f0;margin-bottom:4px}
.plugin-card .tier{font-size:0.8em;color:#a78bfa;background:rgba(167,139,250,0.15);display:inline-block;padding:3px 12px;border-radius:10px}

/* Pricing */
.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}
.price-card{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:32px;text-align:center;transition:all 0.3s;position:relative}
.price-card:hover{transform:translateY(-4px);border-color:rgba(167,139,250,0.3)}
.price-card.featured{border-color:#7c3aed;box-shadow:0 0 40px rgba(124,58,237,0.15)}
.price-card .tag{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#7c3aed;color:#fff;padding:4px 16px;border-radius:10px;font-size:0.8em}
.price-card .plan{font-size:1.4em;color:#e2e8f0;margin-bottom:16px}
.price-card .price{font-size:2.5em;font-weight:800;color:#60a5fa}
.price-card .price span{font-size:0.5em;color:#94a3b8}
.price-card ul{list-style:none;margin:24px 0;color:#94a3b8;text-align:right}
.price-card li{padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)}

/* CTA */
.cta{text-align:center;padding:80px 20px}
.cta h2{font-size:2.5em;margin-bottom:20px}

/* Footer */
footer{text-align:center;padding:40px;color:#64748b;border-top:1px solid rgba(255,255,255,0.05)}
footer span{color:#a78bfa}

@media(max-width:768px){
  .hero h1{font-size:2em}
  .hero .stats{gap:20px}
  .hero .stat .num{font-size:1.5em}
}
</style>
</head>
<body>

<!-- Hero -->
<header class="hero">
  <div class="badge">&#1605;&#1589;&#1606;&#1608;&#1593; &#1601;&#1610; &#1605;&#1603;&#1577; &#1575;&#1604;&#1605;&#1603;&#1585;&#1605;&#1577; &#127757;</div>
  <h1>Romih Agent</h1>
  <p class="sub">&#1608;&#1603;&#1610;&#1604;&#1603; &#1575;&#1604;&#1584;&#1603;&#1610; &#1575;&#1604;&#1571;&#1608;&#1604; &#1576;&#1575;&#1604;&#1593;&#1585;&#1576;&#1610; &#1604;&#1604;&#1588;&#1585;&#1603;&#1575;&#1578; &#1575;&#1604;&#1587;&#1593;&#1608;&#1583;&#1610;&#1577;<br>&#1610;&#1583;&#1610;&#1585; &#1608;&#1585;&#1588;&#1578;&#1603;&#1548; &#1601;&#1606;&#1583;&#1602;&#1603;&#1548; &#1605;&#1588;&#1585;&#1608;&#1593;&#1603;&#1548; &#1605;&#1575;&#1604;&#1610;&#1578;&#1603; — &#1603;&#1604;&#1607; &#1601;&#1610; &#1605;&#1603;&#1575;&#1606; &#1608;&#1575;&#1581;&#1583;</p>

  <div class="stats">
    <div class="stat"><div class="num">170+</div><div class="label">&#1571;&#1583;&#1575;&#1577; &#1584;&#1603;&#1610;&#1577;</div></div>
    <div class="stat"><div class="num">7</div><div class="label">&#1576;&#1604;&#1580;&#1606;&#1586; &#1605;&#1578;&#1582;&#1589;&#1589;&#1577;</div></div>
    <div class="stat"><div class="num">100%</div><div class="label">&#1593;&#1585;&#1576;&#1610;</div></div>
    <div class="stat"><div class="num">24/7</div><div class="label">&#1605;&#1578;&#1589;&#1604; &#1576;&#1575;&#1604;&#1587;&#1581;&#1575;&#1576;&#1577;</div></div>
  </div>

  <a href="/romih/download" class="btn btn-primary">&#x1f4e5; &#1581;&#1605;&#1617;&#1604; &#1575;&#1604;&#1606;&#1587;&#1582;&#1577; &#1575;&#1604;&#1605;&#1581;&#1604;&#1610;&#1577;</a>
  <a href="https://t.me/RomihAgentbot" class="btn btn-telegram">&#x2708; &#1580;&#1585;&#1617;&#1576; &#1593;&#1604;&#1609; &#1578;&#1610;&#1604;&#1610;&#1580;&#1585;&#1575;&#1605;</a>
  <a href="/romih/dashboard" class="btn btn-outline">&#x1f4ca; &#1583;&#1575;&#1588;&#1576;&#1608;&#1585;&#1583; &#1605;&#1576;&#1575;&#1588;&#1585;</a>
</header>

<!-- Features -->
<section class="section">
  <h2>&#1604;&#1605;&#1575;&#1584;&#1575; <span>Romih</span>&#1567;</h2>
  <div class="features">
    <div class="card">
      <div class="icon">&#x1f9e0;</div>
      <h3>&#1584;&#1603;&#1575;&#1569; &#1605;&#1578;&#1602;&#1583;&#1605; &#1576;&#1575;&#1604;&#1593;&#1585;&#1576;&#1610;</h3>
      <p>&#1610;&#1601;&#1603;&#1585; &#1608;&#1610;&#1582;&#1591;&#1591; &#1608;&#1610;&#1606;&#1601;&#1584; &#1576;&#1606;&#1601;&#1587;&#1607; — &#1605;&#1588; &#1605;&#1580;&#1585;&#1583; &#1588;&#1575;&#1578;. &#1610;&#1601;&#1607;&#1605; &#1575;&#1604;&#1593;&#1585;&#1576;&#1610;&#1577; &#1575;&#1604;&#1591;&#1576;&#1610;&#1593;&#1610;&#1577; &#1608;&#1610;&#1585;&#1583; &#1576;&#1604;&#1594;&#1578;&#1603;.</p>
    </div>
    <div class="card">
      <div class="icon">&#x1f3e0;</div>
      <h3>&#1576;&#1610;&#1575;&#1606;&#1575;&#1578;&#1603; &#1593;&#1606;&#1583;&#1603;</h3>
      <p>&#1575;&#1604;&#1606;&#1587;&#1582;&#1577; &#1575;&#1604;&#1605;&#1581;&#1604;&#1610;&#1577; &#1578;&#1593;&#1606;&#1610; &#1582;&#1589;&#1608;&#1589;&#1610;&#1577; &#1603;&#1575;&#1605;&#1604;&#1577;. &#1576;&#1610;&#1575;&#1606;&#1575;&#1578;&#1603; &#1578;&#1576;&#1602;&#1609; &#1593;&#1604;&#1609; &#1580;&#1607;&#1575;&#1586;&#1603; — &#1604;&#1575; &#1578;&#1589;&#1593;&#1583; &#1604;&#1604;&#1587;&#1581;&#1575;&#1576;&#1577;.</p>
    </div>
    <div class="card">
      <div class="icon">&#x1f527;</div>
      <h3>170+ &#1571;&#1583;&#1575;&#1577; &#1580;&#1575;&#1607;&#1586;&#1577;</h3>
      <p>&#1573;&#1583;&#1575;&#1585;&#1577; &#1593;&#1605;&#1604;&#1575;&#1569;&#1548; &#1578;&#1589;&#1604;&#1610;&#1581;&#1575;&#1578;&#1548; &#1601;&#1608;&#1575;&#1578;&#1610;&#1585;&#1548; &#1585;&#1608;&#1575;&#1578;&#1576;&#1548; &#1608;&#1571;&#1603;&#1579;&#1585; — &#1603;&#1604;&#1607;&#1575; &#1601;&#1610; &#1605;&#1603;&#1575;&#1606; &#1608;&#1575;&#1581;&#1583;.</p>
    </div>
    <div class="card">
      <div class="icon">&#x1f4f1;</div>
      <h3>&#1608;&#1610;&#1576; + &#1578;&#1610;&#1604;&#1610;&#1580;&#1585;&#1575;&#1605;</h3>
      <p>&#1575;&#1587;&#1578;&#1582;&#1583;&#1605; Romih &#1605;&#1606; &#1575;&#1604;&#1605;&#1578;&#1589;&#1601;&#1581; &#1571;&#1608; &#1578;&#1610;&#1604;&#1610;&#1580;&#1585;&#1575;&#1605; — &#1601;&#1610; &#1571;&#1610; &#1608;&#1602;&#1578; &#1608;&#1605;&#1606; &#1571;&#1610; &#1605;&#1603;&#1575;&#1606;.</p>
    </div>
    <div class="card">
      <div class="icon">&#x1f4c8;</div>
      <h3>&#1578;&#1593;&#1604;&#1605; &#1608;&#1578;&#1591;&#1608;&#1585;</h3>
      <p>&#1603;&#1604; &#1605;&#1575; &#1578;&#1587;&#1578;&#1582;&#1583;&#1605;&#1607; &#1610;&#1578;&#1593;&#1604;&#1605;&#1607; Romih — &#1610;&#1589;&#1576;&#1581; &#1571;&#1584;&#1603;&#1609; &#1605;&#1593; &#1575;&#1604;&#1608;&#1602;&#1578;. &#1578;&#1580;&#1585;&#1576;&#1577; &#1601;&#1585;&#1610;&#1583;&#1577; &#1604;&#1603;&#1604; &#1575;&#1604;&#1605;&#1587;&#1578;&#1582;&#1583;&#1605;&#1610;&#1606;.</p>
    </div>
    <div class="card">
      <div class="icon">&#x1f1f8;&#x1f1e6;</div>
      <h3>&#1605;&#1589;&#1605;&#1605; &#1604;&#1604;&#1587;&#1608;&#1602; &#1575;&#1604;&#1587;&#1593;&#1608;&#1583;&#1610;</h3>
      <p>&#1576;&#1604;&#1580;&#1606;&#1586; &#1605;&#1578;&#1582;&#1589;&#1589;&#1577;: &#1575;&#1604;&#1593;&#1605;&#1585;&#1577;&#1548; &#1575;&#1604;&#1601;&#1606;&#1575;&#1583;&#1602;&#1548; &#1575;&#1604;&#1608;&#1585;&#1588; — &#1580;&#1605;&#1610;&#1593; &#1605;&#1575; &#1610;&#1581;&#1578;&#1575;&#1580;&#1607; &#1575;&#1604;&#1587;&#1608;&#1602; &#1575;&#1604;&#1587;&#1593;&#1608;&#1583;&#1610;.</p>
    </div>
  </div>
</section>

<!-- Plugins -->
<section class="section">
  <h2>&#1576;&#1604;&#1580;&#1606;&#1586; <span>&#1605;&#1578;&#1582;&#1589;&#1589;&#1577;</span></h2>
  <div class="plugins">
    <div class="plugin-card"><div class="icon">&#x1f3ed;</div><h4>&#1573;&#1583;&#1575;&#1585;&#1577; &#1575;&#1604;&#1608;&#1585;&#1588;</h4><div class="tier">&#1575;&#1581;&#1578;&#1585;&#1575;&#1601;&#1610;</div></div>
    <div class="plugin-card"><div class="icon">&#x1f3e8;</div><h4>&#1573;&#1583;&#1575;&#1585;&#1577; &#1575;&#1604;&#1601;&#1606;&#1575;&#1583;&#1602;</h4><div class="tier">&#1605;&#1572;&#1587;&#1587;&#1610;</div></div>
    <div class="plugin-card"><div class="icon">&#x1f54b;</div><h4>&#1575;&#1604;&#1593;&#1605;&#1585;&#1577; &#1608;&#1575;&#1604;&#1581;&#1580;</h4><div class="tier">&#1605;&#1572;&#1587;&#1587;&#1610;</div></div>
    <div class="plugin-card"><div class="icon">&#x1f465;</div><h4>&#1575;&#1604;&#1605;&#1608;&#1575;&#1585;&#1583; &#1575;&#1604;&#1576;&#1588;&#1585;&#1610;&#1577;</h4><div class="tier">&#1575;&#1581;&#1578;&#1585;&#1575;&#1601;&#1610;</div></div>
    <div class="plugin-card"><div class="icon">&#x1f4b0;</div><h4>&#1575;&#1604;&#1605;&#1575;&#1604;&#1610;&#1577;</h4><div class="tier">&#1575;&#1581;&#1578;&#1585;&#1575;&#1601;&#1610;</div></div>
    <div class="plugin-card"><div class="icon">&#x1f4cb;</div><h4>&#1575;&#1604;&#1605;&#1588;&#1575;&#1585;&#1610;&#1593;</h4><div class="tier">&#1575;&#1581;&#1578;&#1585;&#1575;&#1601;&#1610;</div></div>
  </div>
</section>

<!-- Pricing -->
<section class="section">
  <h2>&#1575;&#1604;&#1576;&#1575;&#1602;&#1575;&#1578; <span>&#1575;&#1604;&#1587;&#1593;&#1585;&#1610;&#1577;</span></h2>
  <div class="pricing">
    <div class="price-card">
      <div class="plan">Basic</div>
      <div class="price">&#1605;&#1580;&#1575;&#1606;&#1610;<span>/&#1604;&#1604;&#1571;&#1576;&#1583;</span></div>
      <ul>
        <li>&#10003; &#1606;&#1587;&#1582;&#1577; &#1605;&#1581;&#1604;&#1610;&#1577;</li>
        <li>&#10003; Web UI + Telegram</li>
        <li>&#10003; &#1576;&#1604;&#1580;&#1606; &#1608;&#1575;&#1581;&#1583;</li>
        <li>&#10003; 14 &#1610;&#1608;&#1605; &#1578;&#1580;&#1585;&#1576;&#1577;</li>
      </ul>
      <a href="/romih/download" class="btn btn-outline" style="width:100%">&#1575;&#1576;&#1583;&#1571; &#1605;&#1580;&#1575;&#1606;&#1575;&#1611;</a>
    </div>
    <div class="price-card featured">
      <div class="tag">&#1575;&#1604;&#1571;&#1603;&#1579;&#1585; &#1591;&#1604;&#1576;&#1575;&#1611;</div>
      <div class="plan">Pro</div>
      <div class="price">$19<span>/&#1588;&#1607;&#1585;</span></div>
      <ul>
        <li>&#10003; 3 &#1576;&#1604;&#1580;&#1606;&#1586;</li>
        <li>&#10003; Dashboard &#1608;&#1578;&#1602;&#1575;&#1585;&#1610;&#1585;</li>
        <li>&#10003; Telegram Bot</li>
        <li>&#10003; &#1583;&#1593;&#1605; &#1601;&#1606;&#1610;</li>
        <li>&#10003; &#1578;&#1581;&#1604;&#1610;&#1604;&#1575;&#1578;</li>
      </ul>
      <a href="https://t.me/RomihAgentbot" class="btn btn-primary" style="width:100%">&#1575;&#1576;&#1583;&#1571; &#1575;&#1604;&#1578;&#1580;&#1585;&#1576;&#1577; &#1575;&#1604;&#1605;&#1580;&#1575;&#1606;&#1610;&#1577;</a>
    </div>
    <div class="price-card">
      <div class="plan">Enterprise</div>
      <div class="price">$99<span>/&#1588;&#1607;&#1585;</span></div>
      <ul>
        <li>&#10003; &#1603;&#1604; &#1575;&#1604;&#1576;&#1604;&#1580;&#1606;&#1586;</li>
        <li>&#10003; Bot &#1582;&#1575;&#1589;</li>
        <li>&#10003; API &#1582;&#1575;&#1589;</li>
        <li>&#10003; &#1583;&#1593;&#1605; &#1601;&#1606;&#1610; 24/7</li>
        <li>&#10003; &#1578;&#1582;&#1589;&#1610;&#1589; &#1603;&#1575;&#1605;&#1604;</li>
        <li>&#10003; SLA</li>
      </ul>
      <a href="https://t.me/RomihAgentbot" class="btn btn-outline" style="width:100%">&#1578;&#1608;&#1575;&#1589;&#1604; &#1605;&#1593;&#1606;&#1575;</a>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta">
  <h2>&#1580;&#1575;&#1607;&#1586; &#1604;&#1578;&#1581;&#1608;&#1610;&#1604; &#1593;&#1605;&#1604;&#1603;&#1567;</h2>
  <p style="color:#94a3b8;font-size:1.2em;margin-bottom:32px">&#1581;&#1605;&#1617;&#1604; &#1575;&#1604;&#1606;&#1587;&#1582;&#1577; &#1575;&#1604;&#1605;&#1581;&#1604;&#1610;&#1577; &#1571;&#1608; &#1580;&#1585;&#1576; &#1605;&#1576;&#1575;&#1588;&#1585;&#1577; &#1593;&#1604;&#1609; &#1578;&#1610;&#1604;&#1610;&#1580;&#1585;&#1575;&#1605; — 14 &#1610;&#1608;&#1605; &#1605;&#1580;&#1575;&#1606;&#1575;&#1611;</p>
  <a href="/romih/download" class="btn btn-primary" style="font-size:1.3em;padding:20px 50px">&#x1f4e5; &#1581;&#1605;&#1617;&#1604; &#1575;&#1604;&#1570;&#1606;</a>
  <p style="color:#64748b;margin-top:16px;font-size:0.9em">&#1605;&#1575; &#1578;&#1581;&#1578;&#1575;&#1580; &#1576;&#1591;&#1575;&#1602;&#1577; &#1575;&#1574;&#1578;&#1605;&#1575;&#1606;</p>
</section>

<footer>
  &#169; 2026 <span>Romih Agent</span> — &#1605;&#1589;&#1606;&#1608;&#1593; &#1601;&#1610; &#1605;&#1603;&#1577; &#1575;&#1604;&#1605;&#1603;&#1585;&#1605;&#1577; &#127757;
</footer>

</body>
</html>'''


def get_landing_html():
    return _HTML
