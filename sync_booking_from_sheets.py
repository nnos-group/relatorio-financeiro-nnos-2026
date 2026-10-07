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

    # Injetar Script de Segurança & Autenticação no <head>
    security_auth_head = """
<script>
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
"""
    if '</head>' in html and 'nnos_auth' not in html:
        html = html.replace('</head>', security_auth_head + '\n</head>')

    favicon_tags = """
<link rel="icon" type="image/png" href="assets/logo-nnos.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png"/>
<link rel="icon" type="image/png" sizes="64x64" href="favicon.png"/>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
<link rel="apple-touch-icon" href="assets/logo-nnos.png"/>
"""
    if 'rel="icon"' not in html and '</head>' in html:
        html = html.replace('</head>', favicon_tags.strip() + '\n</head>')

    # Substituir Navbar simples pela Navbar integrada com links para Matriz, UVA e Menu
    integrated_nav = """
<nav class="sticky top-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-white/10 shadow-xl">
  <!-- Linha 1: Seções do Relatório -->
  <div class="max-w-[1440px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#visao"><span class="material-symbols-outlined text-sm text-sky-400">monitoring</span> Visão executiva</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#imobilizado"><span class="material-symbols-outlined text-sm text-sky-400">inventory_2</span> Imobilizado & Reforma</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#lideres"><span class="material-symbols-outlined text-sm text-sky-400">groups</span> Líderes</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#portfolio"><span class="material-symbols-outlined text-sm text-sky-400">analytics</span> Portfólio</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#dre"><span class="material-symbols-outlined text-sm text-sky-400">assessment</span> Resultado ajustado</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#logistica"><span class="material-symbols-outlined text-sm text-sky-400">flight_takeoff</span> Viagens & Reembolsos</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#detalhe"><span class="material-symbols-outlined text-sm text-sky-400">table_chart</span> Detalhamento</a>
    </div>
  </div>

  <!-- Linha 2: Ações Rápidas Fixadas Abaixo do Menu -->
  <div class="border-t border-white/10 bg-slate-900/90 px-6 py-1.5">
    <div class="max-w-[1440px] mx-auto flex items-center justify-between gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <span class="text-[11px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5 mr-1">
          <span class="material-symbols-outlined text-sm text-sky-400">alt_route</span> Outros Relatórios:
        </span>
        <a href="matriz.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-sky-300 bg-sky-500/20 hover:bg-sky-500/30 border border-sky-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">monitoring</span> Matriz 2026
        </a>
        <a href="uva.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-amber-300 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">account_balance</span> Campus BH UVA
        </a>
        <a href="prospeccao.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-purple-300 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">explore</span> Prospecção
        </a>
      </div>
      <div class="flex items-center gap-2 ml-auto">
        <a href="index.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">grid_view</span> Menu
        </a>
        <button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-400 hover:bg-rose-500/20 border border-rose-500/30 transition-colors flex items-center gap-1 cursor-pointer" title="Encerrar Sessão">
          <span class="material-symbols-outlined text-sm">logout</span> Sair
        </button>
      </div>
    </div>
  </div>
</nav>
"""
    # Substituir navbar simples se presente
    html = re.sub(r'<nav class="nav">.*?</nav>', integrated_nav.strip(), html, flags=re.DOTALL)

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
