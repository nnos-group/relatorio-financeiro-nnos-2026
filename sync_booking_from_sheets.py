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
<script id="tailwind-config">
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        colors: {
          "brand-blue": "#0083ca",
          "surface": "#0c1322",
          "surface-container": "#191f2f",
          "surface-container-high": "#232a3a"
        },
        fontFamily: {
          sans: ["Inter", "sans-serif"],
          display: ["Manrope", "sans-serif"]
        }
      }
    }
  }
</script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style id="light-theme-styles">
  /* ========================================================
     NAVBAR & MENU: MODO ESCURO (CORREÇÃO CRÍTICA DO PRINT)
     Garante que a barra de navegação seja 100% escura no modo escuro
     ======================================================== */
  html.dark nav {
    background-color: rgba(7, 16, 30, 0.96) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.10) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
  }
  html.dark nav > div:first-child {
    background-color: rgba(13, 29, 51, 0.95) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  }
  html.dark nav a[href^="#"],
  html.dark nav a[href="index.html"] {
    color: #cbd5e1 !important;
  }
  html.dark nav a[href^="#"]:hover,
  html.dark nav a[href="index.html"]:hover {
    background-color: rgba(255, 255, 255, 0.10) !important;
    color: #ffffff !important;
  }
  html.dark .theme-toggle-btn {
    color: #94a3b8 !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
  }
  html.dark .theme-toggle-btn:hover {
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.12) !important;
  }

  /* ========================================================
     NAVBAR & MENU: MODO CLARO (PADRÃO MATRIZ)
     ======================================================== */
  html.light nav {
    background-color: #ffffff !important;
    border-bottom: 1px solid #dbe5ef !important;
    box-shadow: 0 2px 8px rgba(27, 54, 93, 0.06) !important;
  }
  html.light nav > div:first-child {
    background-color: #f1f6fb !important;
    border-bottom: 1px solid #dbe5ef !important;
  }
  html.light nav a[href^="#"],
  html.light nav a[href="index.html"] {
    color: #1b365d !important;
  }
  html.light nav a[href^="#"]:hover,
  html.light nav a[href="index.html"]:hover {
    background-color: #e0f2fe !important;
    color: #075985 !important;
  }
  html.light .theme-toggle-btn {
    color: #475569 !important;
    border-color: #cbd5e1 !important;
    background-color: #f1f5f9 !important;
  }
  html.light .theme-toggle-btn:hover {
    color: #0f172a !important;
    background-color: #e2e8f0 !important;
  }

  /* ========================================================
     IDENTIDADE VISUAL MODO CLARO (REPLICAÇÃO TOTAL MATRIZ)
     ======================================================== */
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
    background: linear-gradient(180deg, #eef4fa 0%, #f6f9fc 40%, #f4f7fb 100%) !important;
    color: #0f172a !important;
  }
  html.light body:before { display: none !important; }

  /* Cabeçalho Hero */
  html.light .hero-code1, html.light .hero {
    background: linear-gradient(135deg, #ffffff 0%, #eaf3fb 100%) !important;
    border-bottom: 3px solid #0083ca !important;
  }
  html.light .hero-code1:before, html.light .hero:before, html.light .hero:after { display: none !important; }
  html.light .title-code1, html.light .hero-code1 h1 { color: #1b365d !important; }
  html.light .subtitle-code1, html.light .hero-code1 p { color: #475569 !important; }
  html.light .logo-code1 { filter: none !important; opacity: 1 !important; }
  html.light .header-divider-code1 { background-color: #cbd5e1 !important; }

  /* Títulos e Tipografia Geral */
  html.light h1, html.light h2, html.light h3 { color: #1b365d !important; }
  html.light p, html.light .sub { color: #475569 !important; }
  html.light .section-head p { color: #475569 !important; }
  html.light .line-title:before {
    background: linear-gradient(#0083ca, #38bdf8) !important;
    box-shadow: 0 0 10px rgba(0, 131, 202, 0.25) !important;
  }

  /* Cards, Painéis e KPIs */
  html.light .card,
  html.light .panel,
  html.light .kpi-card,
  html.light .kpi {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    color: #0f172a !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .card.kpi .label, html.light .kpi .label { color: #475569 !important; font-weight: 700 !important; }
  html.light .card.kpi .value, html.light .kpi .value { color: #0f172a !important; font-weight: 800 !important; }
  html.light .card.kpi.blue .value, html.light .kpi.blue .value { color: #0284c7 !important; }
  html.light .card.kpi.green .value, html.light .kpi.green .value { color: #047857 !important; }
  html.light .card.kpi.violet .value, html.light .kpi.violet .value { color: #6d28d9 !important; }
  html.light .card.kpi.amber .value, html.light .kpi.amber .value { color: #b45309 !important; }
  html.light .card.kpi.red .value, html.light .kpi.red .value { color: #be123c !important; }
  html.light .card.kpi .note, html.light .kpi .note { color: #64748b !important; }
  html.light .card.panel h3 { color: #1b365d !important; }
  html.light .card.panel .sub { color: #475569 !important; }

  /* Imobilizado & Reforma (Cards, Barra e Grid) */
  html.light .immob-highlight {
    background: linear-gradient(135deg, #ffffff 0%, #fefce8 100%) !important;
    border: 1px solid #fde68a !important;
    box-shadow: 0 4px 14px -2px rgba(180, 83, 9, 0.08) !important;
  }
  html.light .immob-highlight .kicker,
  html.light .immob-top .kicker { color: #b45309 !important; font-weight: 800 !important; }
  html.light .immob-number { color: #b45309 !important; font-weight: 800 !important; }
  html.light .immob-meta { color: #78350f !important; }
  html.light .immob-progress {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .immob-progress-row { color: #0f172a !important; }
  html.light .immob-progress-row strong { color: #1b365d !important; }
  html.light .immob-progress-row span { color: #475569 !important; }
  html.light .immob-progress div { color: #64748b !important; }
  html.light .bar { background: #f1f5f9 !important; border: 1px solid #cbd5e1 !important; }
  html.light .bar i { background: linear-gradient(90deg, #059669, #0284c7) !important; }
  html.light .immob-grid .immob-item {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 12px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .immob-item .eyebrow { color: #64748b !important; }
  html.light .immob-name { color: #0f172a !important; }
  html.light .immob-value { color: #b45309 !important; }
  html.light .immob-pct { color: #64748b !important; }

  /* Performance por Líder */
  html.light .leader-card {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .leader-card.good { border-color: #a7f3d0 !important; }
  html.light .leader-card.mid { border-color: #bae6fd !important; }
  html.light .leader-card.warn { border-color: #fde68a !important; }
  html.light .leader-card.bad { border-color: #fecdd3 !important; }
  html.light .leader-head h3 { color: #1b365d !important; }
  html.light .leader-head .eyebrow { color: #64748b !important; }
  html.light .leader-share { color: #0284c7 !important; }
  html.light .leader-share span { color: #64748b !important; }
  html.light .leader-value { color: #0f172a !important; }
  html.light .leader-grid div {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
  html.light .leader-grid div span { color: #64748b !important; }
  html.light .leader-grid div strong { color: #0f172a !important; }
  html.light .progress { background: #e2e8f0 !important; }
  html.light .progress i { background: linear-gradient(90deg, #0083ca, #38bdf8) !important; }

  /* DRE Consolidado Ajustado */
  html.light .dre-card {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .dre-card .l { color: #475569 !important; font-weight: 700 !important; }
  html.light .dre-card .v { color: #0f172a !important; font-weight: 800 !important; }
  html.light .dre-card.positive .v { color: #047857 !important; }
  html.light .dre-card.capex .v { color: #b45309 !important; }
  html.light .dre-card.negative .v { color: #be123c !important; }
  html.light .adjust-note {
    background: linear-gradient(135deg, #f0fdf4 0%, #e6f9ed 100%) !important;
    border: 1px solid #bbf7d0 !important;
    color: #166534 !important;
  }
  html.light .adjust-note strong { color: #14532d !important; }

  /* Viagens & Reembolsos */
  html.light .travel-card {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light .travel-card h3 { color: #1b365d !important; }
  html.light .travel-card .sub { color: #475569 !important; }
  html.light .travel-coverage { color: #475569 !important; }
  html.light .travel-coverage strong { color: #047857 !important; }
  html.light .travel-month-title { color: #0284c7 !important; font-weight: 800 !important; }
  html.light .travel-label { color: #475569 !important; font-weight: 600 !important; }
  html.light .travel-track { background: #e2e8f0 !important; border: 1px solid #cbd5e1 !important; }
  html.light .travel-hero { background: #f0fdf4 !important; border: 1px solid #bbf7d0 !important; }
  html.light .travel-hero.negative { background: #fff1f2 !important; border: 1px solid #fecdd3 !important; }
  html.light .travel-hero .ey { color: #475569 !important; font-weight: 700 !important; }
  html.light .travel-hero .big { color: #047857 !important; }
  html.light .travel-hero.negative .big { color: #be123c !important; }
  html.light .travel-hero .desc { color: #64748b !important; }
  html.light .travel-summary-row {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #1e293b !important;
  }
  html.light .travel-summary-row span { color: #475569 !important; font-weight: 600 !important; }
  html.light .travel-summary-row.exp strong { color: #be123c !important; }
  html.light .travel-summary-row.reimb strong { color: #047857 !important; }
  html.light .travel-summary-row.prosp strong { color: #b45309 !important; }
  html.light .travel-divider { background: #e2e8f0 !important; }
  html.light .travel-caption { color: #64748b !important; }

  /* Tabela e Toolbar de Filtros */
  html.light .toolbar input,
  html.light .toolbar select {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
  }
  html.light .toolbar input::placeholder { color: #94a3b8 !important; }
  html.light .toolbar select option { background: #ffffff !important; color: #0f172a !important; }
  html.light .toolbar button {
    background: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    color: #1b365d !important;
  }
  html.light .toolbar button:hover {
    background: #e0f2fe !important;
    border-color: #7dd3fc !important;
    color: #0369a1 !important;
  }
  html.light .table-wrap {
    background: #ffffff !important;
    border: 1px solid #dbe5ef !important;
    box-shadow: 0 4px 14px -2px rgba(27, 54, 93, 0.06) !important;
  }
  html.light table { background: #ffffff !important; }
  html.light table thead tr,
  html.light table thead th,
  html.light table th {
    background-color: #1b365d !important;
    color: #ffffff !important;
    border-bottom: 2px solid #0083ca !important;
  }
  html.light table tbody td {
    color: #0f172a !important;
    border-bottom: 1px solid #e2e8f0 !important;
  }
  html.light table tbody tr:nth-child(even) td { background-color: #f8fafc !important; }
  html.light table tbody tr:hover td { background-color: #e0f2fe !important; }
  html.light .project-name { color: #0f172a !important; font-weight: 700 !important; }

  /* Badges de Status da Tabela */
  html.light .status.excelente { background: #d1fae5 !important; color: #047857 !important; border: 1px solid #6ee7b7 !important; }
  html.light .status.meta { background: #e0f2fe !important; color: #0284c7 !important; border: 1px solid #7dd3fc !important; }
  html.light .status.atencao { background: #fef3c7 !important; color: #b45309 !important; border: 1px solid #fcd34d !important; }
  html.light .status.critico { background: #ffe4e6 !important; color: #be123c !important; border: 1px solid #fda4af !important; }

  /* Rodapé */
  html.light footer, html.light footer[class] {
    background-color: #1b365d !important;
    border-top: 3px solid #0083ca !important;
  }
  html.light footer, html.light footer * { color: #e2e8f0 !important; }
  html.light footer .font-bold { color: #ffffff !important; }
  html.light ::-webkit-scrollbar-track { background: #e2e8f0; }
  html.light ::-webkit-scrollbar-thumb { background: #94a3b8; }
</style>
"""
    if '</head>' in html:
        if 'nnos_auth' not in html:
            html = html.replace('</head>', security_auth_head + '\n</head>')
        elif 'light-theme-styles' not in html:
            html = html.replace('</head>', '<style id="light-theme-styles">\n' + security_auth_head.split('<style id="light-theme-styles">')[1] + '\n</head>')
        else:
            # Substituir estilos existentes se já presentes
            html = re.sub(r'<style id="light-theme-styles">.*?</style>', security_auth_head.split('<style id="light-theme-styles">')[1].split('</style>')[0].join(['<style id="light-theme-styles">\n', '\n</style>']), html, flags=re.DOTALL)
            if 'tailwind-config' not in html:
                tailwind_cfg = """<script id="tailwind-config">
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        colors: {
          "brand-blue": "#0083ca",
          "surface": "#0c1322",
          "surface-container": "#191f2f",
          "surface-container-high": "#232a3a"
        },
        fontFamily: {
          sans: ["Inter", "sans-serif"],
          display: ["Manrope", "sans-serif"]
        }
      }
    }
  }
</script>"""
                html = html.replace('</head>', tailwind_cfg + '\n</head>')

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
<nav class="sticky top-0 z-50 bg-slate-950/95 dark:bg-slate-950/95 backdrop-blur-md border-b border-white/10 dark:border-white/10 shadow-md transition-colors duration-200">
  <!-- Linha 1: Outros Relatórios e Ações Globais -->
  <div class="bg-slate-900/90 dark:bg-slate-900/90 px-6 py-1.5 border-b border-white/10 dark:border-white/10">
    <div class="max-w-[1720px] mx-auto flex items-center justify-between gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-bold text-slate-400 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1.5 mr-1">
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
        <button id="themeToggleBtn" onclick="toggleTheme()" class="theme-toggle-btn p-1.5 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center justify-center cursor-pointer shadow-sm" title="Alternar Modo Escuro / Claro">
          <span class="material-symbols-outlined text-base theme-icon">light_mode</span>
        </button>
        <a href="index.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">grid_view</span> Menu
        </a>
        <button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-400 hover:bg-rose-500/20 border border-rose-500/30 transition-colors flex items-center gap-1 cursor-pointer" title="Encerrar Sessão">
          <span class="material-symbols-outlined text-sm">logout</span> Sair
        </button>
      </div>
    </div>
  </div>

  <!-- Linha 2: Seções do Relatório -->
  <div class="max-w-[1720px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#visao"><span class="material-symbols-outlined text-sm text-sky-500">monitoring</span> Visão executiva</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#imobilizado"><span class="material-symbols-outlined text-sm text-sky-500">inventory_2</span> Imobilizado &amp; Reforma</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#lideres"><span class="material-symbols-outlined text-sm text-sky-500">groups</span> Líderes</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#portfolio"><span class="material-symbols-outlined text-sm text-sky-500">analytics</span> Portfólio</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#logistica"><span class="material-symbols-outlined text-sm text-sky-500">flight_takeoff</span> Viagens &amp; Reembolsos</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#detalhe"><span class="material-symbols-outlined text-sm text-sky-500">table_chart</span> Detalhamento</a>
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

    # Otimizar cabeçalho padronizado com referência Contas a Pagar | Campus BH UVA
    optimized_hero_css = """
.hero-code1{position:relative;overflow:hidden;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.10);background:linear-gradient(90deg,rgba(1,49,84,.68) 0%,rgba(11,34,80,.84) 45%,rgba(18,28,91,.75) 100%)}
.hero-code1:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 0% 0%,rgba(0,131,202,.20),transparent 30%),radial-gradient(circle at 100% 0%,rgba(59,130,246,.12),transparent 24%);pointer-events:none}
.hero-code1-inner{position:relative;z-index:1}
.hero-code1-copy{max-width:1720px;margin:0 auto;padding:0 24px;display:flex;align-items:center;gap:20px}
.logo-code1{height:64px;width:auto;object-fit:contain;margin-bottom:0;opacity:.95;flex-shrink:0}
.logo-dark{display:block;}
.logo-light{display:none;}
html.light .logo-dark{display:none!important;}
html.light .logo-light{display:block!important;}
html.light .hero-code1{background:#ffffff!important;border-bottom:1px solid #e2e8f0!important;}
html.light .title-code1{color:#1b365d!important;}
html.light .subtitle-code1{color:#475569!important;}
html.light .header-divider-code1{background:rgba(0,0,0,0.15)!important;}
.header-divider-code1{width:1px;height:48px;background:rgba(255,255,255,.2);flex-shrink:0}
.title-code1{font-size:clamp(24px,2.8vw,30px);font-weight:700;line-height:1.25;margin:0;letter-spacing:-.02em;color:#fff;font-family:Manrope,Inter,sans-serif;white-space:nowrap}
.subtitle-code1{color:#e2e8f0;font-size:15px;line-height:1.4;margin:2px 0 0;white-space:nowrap}
@media(max-width:768px){.hero-code1-copy{flex-direction:column;align-items:flex-start;gap:12px}.header-divider-code1{display:none}.logo-code1{height:48px}}
"""
    html = re.sub(r'\.hero-code1\{.*?\@media\(max-width:768px\)\{.*?\}\s*\}', optimized_hero_css.strip(), html, flags=re.DOTALL)
    if 'height:64px' not in html and '</style>' in html:
        html = html.replace('</style>', optimized_hero_css.strip() + '\n</style>', 1)

    optimized_hero_html = """<div class="hero-code1-copy">
      <img alt="NNÓS Logo" class="logo-code1 logo-dark" src="assets/logo-nnos-white.png"/>
      <img alt="NNÓS Logo" class="logo-code1 logo-light" src="assets/logo-nnos.png"/>
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
<footer class="bg-slate-950 border-t border-white/10 py-6 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1720px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS" class="h-11 md:h-12 w-auto object-contain" src="assets/logo-nnos-horizontal.png"/>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Dezembro de 2026</div>
  </div>
</footer>
"""
    html = re.sub(r'<footer class="footer">.*?</footer>', standard_footer_booking.strip(), html, flags=re.DOTALL)
    html = re.sub(r'<footer class="bg-(?:white|slate-950).*?</footer>', standard_footer_booking.strip(), html, flags=re.DOTALL)

    # Padronizar largura lateral do Booking para 1720px (referência Painel por Líder)
    html = html.replace("width:min(1480px,calc(100% - 40px))", "width:min(1720px,calc(100% - 40px))")
    html = html.replace("width:min(100% - 24px,1480px)", "width:min(100% - 24px,1720px)")
    html = html.replace(".wrap{width:min(1480px", ".wrap{width:min(1720px")

    # Ajuste dinâmico de gráficos e tabela de acordo com o tema
    chart_tweak = """const isLight = document.documentElement.classList.contains('light');
Chart.defaults.font.family="'Inter', sans-serif";
Chart.defaults.color = isLight ? '#1b365d' : '#aebed2';
const gridColor = isLight ? 'rgba(27, 54, 93, 0.08)' : 'rgba(148,163,184,.11)';
const tooltip = isLight ? {backgroundColor:'#ffffff',titleColor:'#1b365d',bodyColor:'#0f172a',borderColor:'#cbd5e1',borderWidth:1,padding:12,displayColors:false} : {backgroundColor:'#10243e',titleColor:'#fff',bodyColor:'#d9e5f3',borderColor:'rgba(148,163,184,.22)',borderWidth:1,padding:12,displayColors:false};"""
    html = re.sub(r"Chart\.defaults\.font\.family=.*?const tooltip=\{.*?\};", chart_tweak.strip(), html, flags=re.DOTALL)
    html = html.replace("p.margem<0?'#ff9bae':'#9bd7ff'", "p.margem<0?'#be123c':(isLight?'#047857':'#9bd7ff')")

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
