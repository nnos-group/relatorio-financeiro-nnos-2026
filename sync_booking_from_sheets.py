import os
import re
import json
import subprocess
import shutil

def sync_booking():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    booking_dir = os.path.abspath(os.path.join(repo_dir, "..", "Booking - Dashboard Executivo de Performance"))
    if not os.path.exists(booking_dir):
        booking_dir = r"C:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\Booking - Dashboard Executivo de Performance"
    
    if not os.path.exists(booking_dir):
        print(f"[AVISO] Pasta Booking não encontrada em: {booking_dir}")
        return False
        
    cred_file = os.path.join(booking_dir, "nnos-dashboard-9e61e1181de1.json")
    if not os.path.exists(cred_file):
        print(f"[AVISO] Arquivo de credenciais não encontrado: {cred_file}")
        return False

    print("1. Consultando Google Sheets API e atualizando dados-dashboard.json...")
    env = os.environ.copy()
    env["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
    env["GOOGLE_SHEET_ID"] = "1oyOo2Y5HXTEN_8LhW9ekMNRBssCxZ5uyCFFQnB9Z1PM"

    # 1. Update from Google Sheets
    cmd_sheets = ["node", "scripts/update-google-sheets.mjs"]
    res1 = subprocess.run(cmd_sheets, cwd=booking_dir, env=env, capture_output=True, text=True)
    if res1.returncode != 0:
        print(f"[ERRO] Falha ao atualizar Google Sheets: {res1.stderr}")
        return False
    print(f"   -> {res1.stdout.strip()}")

    # 2. Update Imobilizado from UVA
    cmd_imob = ["node", "scripts/update-imobilizado-from-uva.mjs"]
    res2 = subprocess.run(cmd_imob, cwd=booking_dir, env=env, capture_output=True, text=True)
    if res2.returncode != 0:
        print(f"[AVISO] Falha update imobilizado: {res2.stderr}")
    else:
        print(f"   -> {res2.stdout.strip()}")

    # 3. Build Booking HTML
    cmd_build = ["node", "scripts/build-dashboard.mjs"]
    res3 = subprocess.run(cmd_build, cwd=booking_dir, env=env, capture_output=True, text=True)
    if res3.returncode != 0:
        print(f"[ERRO] Falha build dashboard: {res3.stderr}")
        return False
    print(f"   -> {res3.stdout.strip()}")

    # 4. Ler o HTML gerado e integrar Navbar + Autenticação + Segurança
    raw_html_path = os.path.join(booking_dir, "index.html")
    with open(raw_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Injetar Script de Segurança & Autenticação e Tema no <head>
    security_auth_head = """
<script>
  (function() {
    const saved = localStorage.getItem('nnos_theme') || 'dark';
    if (saved === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  })();
  if (sessionStorage.getItem('nnos_auth') !== 'true') {
    window.location.href = 'index.html';
  }
  function logout() {
    sessionStorage.removeItem('nnos_auth');
    window.location.href = 'index.html';
  }

  // 🛡️ Camada de Segurança: Bloqueio de DevTools, Atalhos e Menu de Contexto
  document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
  }, false);

  document.addEventListener('keydown', function(e) {
    if (e.key === 'F12' || e.keyCode === 123) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (
        e.key === 'I' || e.key === 'i' || e.keyCode === 73 ||
        e.key === 'J' || e.key === 'j' || e.keyCode === 74 ||
        e.key === 'C' || e.key === 'c' || e.keyCode === 67
    )) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'U' || e.key === 'u' || e.keyCode === 85)) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'S' || e.key === 's' || e.keyCode === 83)) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
  }, false);
</script>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style id="light-theme-styles">
  html.light {
    --bg: #f8fafc;
    --bg2: #ffffff;
    --panel: #ffffff;
    --line: rgba(203, 213, 225, 0.8);
    --line2: rgba(59, 130, 246, 0.3);
    --text: #0f172a;
    --muted: #475569;
    --shadow: 0 10px 30px rgba(0,0,0,0.06);
  }
  html.light body {
    background: #f1f5f9 !important;
    color: #0f172a !important;
  }
  html.light .hero-code1,
  html.light .hero {
    background: #ffffff !important;
    border-bottom: 1px solid #e2e8f0 !important;
  }
  html.light .hero-code1:before,
  html.light .hero:before {
    display: none !important;
  }
  html.light .title-code1,
  html.light .hero-code1 h1 {
    color: #0f172a !important;
  }
  html.light .subtitle-code1,
  html.light .hero-code1 p {
    color: #475569 !important;
  }
  html.light .header-divider-code1 {
    background-color: #e2e8f0 !important;
  }
  html.light nav {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-bottom: 1px solid #e2e8f0 !important;
  }
  html.light nav > div:first-child {
    background-color: #f8fafc !important;
    border-bottom: 1px solid #e2e8f0 !important;
  }
  html.light .bg-slate-950,
  html.light .bg-slate-900 {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
  }
  html.light .card,
  html.light .panel,
  html.light .kpi-card,
  html.light .kpi {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #0f172a !important;
    box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05) !important;
  }
  html.light .card h2,
  html.light .card h3,
  html.light .panel h2,
  html.light .panel h3 {
    color: #0f172a !important;
  }
  html.light .card p,
  html.light .panel p,
  html.light .text-muted,
  html.light .text-gray-400,
  html.light .text-gray-300 {
    color: #64748b !important;
  }
  html.light [class*="border-white"] {
    border-color: #e2e8f0 !important;
  }

  /* 🌟 IMOBILIZADO & REFORMA (Print 5: Segregação Gerencial e cards nítidos) */
  html.light .immob-box {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05) !important;
  }
  html.light .immob-head .eyebrow {
    color: #b45309 !important;
  }
  html.light .immob-total {
    color: #b45309 !important;
  }
  html.light .immob-item {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
  }
  html.light .immob-item .eyebrow {
    color: #64748b !important;
  }
  html.light .immob-name {
    color: #0f172a !important;
  }
  html.light .immob-value {
    color: #b45309 !important;
  }
  html.light .immob-pct {
    color: #64748b !important;
  }

  /* 🌟 PERFORMANCE POR LÍDER (Print 5: Cards brancos com fontes escuras) */
  html.light .leader-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05) !important;
  }
  html.light .leader-card h3 {
    color: #0f172a !important;
  }
  html.light .leader-card .eyebrow {
    color: #64748b !important;
  }
  html.light .leader-share {
    color: #0284c7 !important;
  }
  html.light .leader-share span {
    color: #64748b !important;
  }
  html.light .leader-value {
    color: #0f172a !important;
  }
  html.light .leader-grid div {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
  html.light .leader-grid div span {
    color: #64748b !important;
  }
  html.light .leader-grid div strong {
    color: #0f172a !important;
  }

  /* 🌟 TABELAS, DRE E PORTFÓLIO */
  html.light table th {
    background-color: #f1f5f9 !important;
    color: #475569 !important;
    border-color: #e2e8f0 !important;
  }
  html.light table td {
    color: #0f172a !important;
    border-color: #e2e8f0 !important;
  }
  html.light table tr:hover td {
    background-color: #f8fafc !important;
  }
  html.light .chip {
    background: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
  }
  html.light .kpi-value,
  html.light .stat-value {
    color: #0f172a !important;
  }

  /* ===== NNÓS · Identidade clara (padrão Matriz) =====
     Regra: fundo escuro => texto claro | fundo claro => texto escuro */
  html.light body {
    background: linear-gradient(180deg, #eef4fa 0%, #f6f9fc 40%, #f4f7fb 100%) !important;
  }
  html.light .hero-code1, html.light .hero {
    background: linear-gradient(135deg, #ffffff 0%, #eaf3fb 100%) !important;
    border-bottom: 3px solid #0083ca !important;
  }
  html.light .title-code1, html.light .hero-code1 h1 { color: #1b365d !important; }
  html.light nav {
    background-color: #ffffff !important;
    border-bottom: 1px solid #dbe5ef !important;
    box-shadow: 0 2px 8px rgba(27,54,93,.06) !important;
  }
  html.light nav > div:first-child {
    background-color: #f1f6fb !important;
    border-bottom: 1px solid #dbe5ef !important;
  }
  html.light nav a[href^="#"] { color: #1b365d !important; }
  html.light nav a[href^="#"]:hover { background-color: #e0f2fe !important; color: #075985 !important; }
  html.light h2 { color: #1b365d !important; }
  html.light .card, html.light .panel, html.light .kpi-card, html.light .kpi,
  html.light .immob-box, html.light .immob-item, html.light .leader-card {
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 6px 18px -8px rgba(27,54,93,.18) !important;
  }
  /* Cabeçalho de tabela = barra escura => texto claro */
  html.light table thead tr, html.light table thead th, html.light table th {
    background-color: #1b365d !important;
    color: #ffffff !important;
    border-color: #1b365d !important;
  }
  html.light table tbody tr:nth-child(even) td { background-color: #f6f9fc !important; }
  html.light table tr:hover td { background-color: #e8f2fa !important; }
  html.light .chip { background: #e8f2fa !important; border: 1px solid #bcd3e6 !important; color: #1b365d !important; }
  html.light .text-emerald-400, html.light .text-emerald-300 { color: #047857 !important; }
  html.light .text-rose-400, html.light .text-rose-300 { color: #be123c !important; }
  html.light .text-amber-400, html.light .text-amber-300 { color: #b45309 !important; }
  html.light .logo-code1 {
    filter: none !important;
    opacity: 1 !important;
  }
  html.light .header-divider-code1 {
    background-color: #cbd5e1 !important;
  }
  html.light .dre-card {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27,54,93,.08) !important;
  }
  html.light .dre-card .l { color: #475569 !important; }
  html.light .dre-card .v { color: #0f172a !important; }
  html.light .dre-card.negative .v { color: #be123c !important; }
  html.light .dre-card.positive .v { color: #047857 !important; }
  html.light .dre-card.capex .v { color: #b45309 !important; }

  html.light .card.panel, html.light .card.kpi {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27,54,93,.06) !important;
  }
  html.light .card.kpi .label { color: #475569 !important; }
  html.light .card.kpi .value { color: #0f172a !important; }
  html.light .card.kpi.red .value { color: #be123c !important; }
  html.light .card.kpi.green .value { color: #047857 !important; }
  html.light .card.kpi.amber .value { color: #b45309 !important; }
  html.light .card.kpi.blue .value { color: #0284c7 !important; }
  html.light .card.kpi .note { color: #64748b !important; }
  html.light .card.panel h3 { color: #1b365d !important; }
  html.light .card.panel .sub { color: #475569 !important; }

  html.light footer, html.light footer[class] {
    background-color: #1b365d !important;
    border-top: 3px solid #0083ca !important;
  }
  html.light footer, html.light footer * { color: #e2e8f0 !important; }
  html.light ::-webkit-scrollbar-track { background: #e2e8f0; }
  html.light ::-webkit-scrollbar-thumb { background: #94a3b8; }
</style>
"""
    if '</head>' in html:
        if 'nnos_auth' not in html:
            html = html.replace('</head>', security_auth_head + '\n</head>')
        elif 'light-theme-styles' not in html:
            html = html.replace('</head>', '<style id="light-theme-styles">\n' + security_auth_head.split('<style id="light-theme-styles">')[1] + '\n</head>')

    favicon_tags = """
<link rel="icon" type="image/png" href="assets/logo-nnos.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png"/>
<link rel="icon" type="image/png" sizes="64x64" href="favicon.png"/>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
<link rel="apple-touch-icon" href="assets/logo-nnos.png"/>
"""
    if 'rel="icon"' not in html and '</head>' in html:
        html = html.replace('</head>', favicon_tags.strip() + '\n</head>')

    # Substituir Navbar simples pela Navbar integrada com links para Matriz, UVA e Menu (Outros Relatórios Acima)
    integrated_nav = """
<nav class="sticky top-0 z-50 bg-white/95 dark:bg-slate-950/95 backdrop-blur-md border-b border-slate-200 dark:border-white/10 shadow-md transition-colors duration-200">
  <!-- Linha 1: Outros Relatórios e Ações Globais -->
  <div class="bg-slate-100/90 dark:bg-slate-900/90 px-6 py-1.5 border-b border-slate-200 dark:border-white/10">
    <div class="max-w-[1440px] mx-auto flex items-center justify-between gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1.5 mr-1">
          <span class="material-symbols-outlined text-sm text-sky-500">alt_route</span> Outros Relatórios:
        </span>
        <a href="matriz.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-sky-700 dark:text-sky-300 bg-sky-100 dark:bg-sky-500/20 hover:bg-sky-200 dark:hover:bg-sky-500/30 border border-sky-300 dark:border-sky-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">monitoring</span> Matriz 2026
        </a>
        <a href="uva.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-amber-700 dark:text-amber-300 bg-amber-100 dark:bg-amber-500/20 hover:bg-amber-200 dark:hover:bg-amber-500/30 border border-amber-300 dark:border-amber-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">account_balance</span> Campus BH UVA
        </a>
        <a href="prospeccao.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-purple-700 dark:text-purple-300 bg-purple-100 dark:bg-purple-500/20 hover:bg-purple-200 dark:hover:bg-purple-500/30 border border-purple-300 dark:border-purple-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">explore</span> Prospecção
        </a>
        <a href="lider.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-500/20 hover:bg-blue-200 dark:hover:bg-blue-500/30 border border-blue-300 dark:border-blue-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">badge</span> Painel por Líder
        </a>
      </div>
      <div class="flex items-center gap-2 ml-auto">
        <button id="themeToggleBtn" onclick="toggleTheme()" class="theme-toggle-btn p-1.5 rounded-lg text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-white/10 border border-slate-300 dark:border-white/10 transition-colors flex items-center justify-center cursor-pointer shadow-sm" title="Alternar Modo Escuro / Claro">
          <span class="material-symbols-outlined text-base theme-icon">light_mode</span>
        </button>
        <a href="index.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-white/10 border border-slate-300 dark:border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">grid_view</span> Menu
        </a>
        <button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-100 dark:hover:bg-rose-500/20 border border-rose-300 dark:border-rose-500/30 transition-colors flex items-center gap-1 cursor-pointer" title="Encerrar Sessão">
          <span class="material-symbols-outlined text-sm">logout</span> Sair
        </button>
      </div>
    </div>
  </div>

  <!-- Linha 2: Seções do Relatório -->
  <div class="max-w-[1440px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#visao"><span class="material-symbols-outlined text-sm text-sky-500">monitoring</span> Visão executiva</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#imobilizado"><span class="material-symbols-outlined text-sm text-sky-500">inventory_2</span> Imobilizado &amp; Reforma</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#lideres"><span class="material-symbols-outlined text-sm text-sky-500">groups</span> Líderes</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#portfolio"><span class="material-symbols-outlined text-sm text-sky-500">analytics</span> Portfólio</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#dre"><span class="material-symbols-outlined text-sm text-sky-500">assessment</span> Resultado ajustado</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#logistica"><span class="material-symbols-outlined text-sm text-sky-500">flight_takeoff</span> Viagens &amp; Reembolsos</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#detalhe"><span class="material-symbols-outlined text-sm text-sky-500">table_chart</span> Detalhamento</a>
    </div>
  </div>
</nav>
"""
    # Substituir navbar simples ou navbar existente
    html = re.sub(r'<nav.*?</nav>', integrated_nav.strip(), html, flags=re.DOTALL)

    # Injetar script de alternância de tema no final
    theme_script = """
<script>
  function applyTheme(theme) {
    const html = document.documentElement;
    const icons = document.querySelectorAll('.theme-icon');
    const buttons = document.querySelectorAll('.theme-toggle-btn');
    if (theme === 'light') {
      html.classList.remove('dark');
      html.classList.add('light');
      icons.forEach(ic => ic.textContent = 'dark_mode');
      buttons.forEach(btn => btn.setAttribute('title', 'Alternar para Modo Escuro'));
      localStorage.setItem('nnos_theme', 'light');
    } else {
      html.classList.remove('light');
      html.classList.add('dark');
      icons.forEach(ic => ic.textContent = 'light_mode');
      buttons.forEach(btn => btn.setAttribute('title', 'Alternar para Modo Claro'));
      localStorage.setItem('nnos_theme', 'dark');
    }
  }

  function toggleTheme() {
    const isLight = document.documentElement.classList.contains('light');
    applyTheme(isLight ? 'dark' : 'light');
    location.reload();
  }

  (function() {
    const saved = localStorage.getItem('nnos_theme') || 'dark';
    applyTheme(saved);
  })();
</script>
"""
    if '</body>' in html and 'theme-toggle-btn' in html and 'applyTheme' not in html:
        html = html.replace('</body>', theme_script + '\n</body>')

    # Otimizar cabeçalho: logo ao lado do título com altura compacta
    optimized_hero_css = """
.hero-code1{position:relative;overflow:hidden;padding:16px 0 14px;border-bottom:1px solid rgba(255,255,255,.10);background:linear-gradient(90deg,rgba(1,49,84,.68) 0%,rgba(11,34,80,.84) 45%,rgba(18,28,91,.75) 100%)}
.hero-code1:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 0% 0%,rgba(0,131,202,.20),transparent 30%),radial-gradient(circle at 100% 0%,rgba(59,130,246,.12),transparent 24%);pointer-events:none}
.hero-code1-inner{position:relative;z-index:1}
.hero-code1-copy{max-width:1200px;display:flex;align-items:center;gap:20px}
.logo-code1{height:50px;margin-bottom:0;filter:brightness(0) invert(1);opacity:.95;display:block;flex-shrink:0}
.header-divider-code1{width:1px;height:44px;background:rgba(255,255,255,.2);flex-shrink:0}
.title-code1{font-size:clamp(22px,2.6vw,32px);font-weight:800;line-height:1.15;margin:0 0 4px;letter-spacing:-.03em;color:#fff;font-family:Manrope,Inter,sans-serif}
.subtitle-code1{color:#d7e3f3;font-size:13px;line-height:1.4;margin:0}
@media(max-width:768px){.hero-code1-copy{flex-direction:column;align-items:flex-start;gap:12px}.header-divider-code1{display:none}.logo-code1{height:38px}}
"""
    html = re.sub(r'\.hero-code1\{.*?@media\(max-width:620px\)\{\.subtitle-code1\{.*?\}\}', optimized_hero_css.strip(), html, flags=re.DOTALL)

    optimized_hero_html = """<div class="hero-code1-copy">
      <img alt="NNÓS Logo" class="logo-code1" src="assets/logo-nnos.png"/>
      <div class="header-divider-code1"></div>
      <div>
        <h1 class="title-code1">Dashboard Executivo de Performance de Projetos</h1>
        <p class="subtitle-code1">Análise consolidada de receita, margem, custos, rentabilidade e performance por líder — Fonte Gestão Financeira Projetos.</p>
      </div>
    </div>"""
    html = re.sub(r'<div class="hero-code1-copy">.*?</div>\s*</div>\s*</header>', optimized_hero_html + '\n  </div>\n</header>', html, flags=re.DOTALL)

    # Padronizar Rodapé
    standard_footer_booking = """
<!-- FOOTER -->
<footer class="bg-slate-950 border-t border-white/10 py-8 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS Logo" class="h-10 w-auto object-contain opacity-90" src="assets/logo-nnos.png"/>
      <span class="font-bold text-white">NNÓS Controladoria &amp; Gestão Financeira</span>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Dezembro de 2026</div>
  </div>
</footer>
"""
    html = re.sub(r'<footer class="footer">.*?</footer>', standard_footer_booking.strip(), html, flags=re.DOTALL)

    target_booking = os.path.join(repo_dir, "booking.html")
    target_dashboard = os.path.join(repo_dir, "dashboard-executivo-booking.html")

    with open(target_booking, "w", encoding="utf-8") as f:
        f.write(html)
    with open(target_dashboard, "w", encoding="utf-8") as f:
        f.write(html)

    # 5. Atualizar Card 3 no index.html com os números reais
    data_json_path = os.path.join(booking_dir, "data", "dados-dashboard.json")
    if os.path.exists(data_json_path):
        with open(data_json_path, "r", encoding="utf-8") as f:
            b_data = json.load(f)
        total_projects = len(b_data.get("projects", []))
        total_rec = b_data.get("portfolioRevenue") or sum(p.get("receita", 0) for p in b_data.get("projects", []))
        total_margem = sum(p.get("margem", 0) for p in b_data.get("projects", []))
        
        index_path = os.path.join(repo_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                idx_html = f.read()
            
            # Formatar valores
            rec_str = f"R$ {total_rec/1e6:.2f}M".replace(".", ",")
            marg_str = f"R$ {total_margem/1e6:.2f}M".replace(".", ",")

            # Atualizar Card 3: Projetos, Receita Total, Margem Bruta
            card3_pattern = r'(<!-- Card 3: Performance de Projetos.*?Projetos</div>\s*<div class="[^"]*">)\d+(</div>.*?Receita Total</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Margem Bruta</div>\s*<div class="[^"]*">)[^<]+(</div>)'
            
            def replace_card3(m):
                return f"{m.group(1)}{total_projects}{m.group(2)}{rec_str}{m.group(3)}{marg_str}{m.group(4)}"
                
            idx_html_updated = re.sub(card3_pattern, replace_card3, idx_html, flags=re.DOTALL)
            if idx_html_updated != idx_html:
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(idx_html_updated)
                print(f"[OK] Card 3 do index.html sincronizado: {total_projects} projetos, Receita {rec_str}, Margem {marg_str}")

    print("[OK] Sincronização do Booking via Google Sheets API finalizada com sucesso!")
    return True

if __name__ == "__main__":
    sync_booking()
