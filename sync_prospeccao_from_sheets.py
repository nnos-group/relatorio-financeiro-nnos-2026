import os
import json
import subprocess
import re

def sync_prospeccao():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_script = os.path.join(repo_dir, "fetch_prospeccao_sheets.mjs")
    data_json = os.path.join(repo_dir, "prospeccao_data.json")

    print("1. Consultando Google Sheets API e sincronizando Prospecção...")
    if os.path.exists(fetch_script):
        try:
            res = subprocess.run(["node", fetch_script], cwd=repo_dir, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"   -> {res.stdout.strip()}")
            else:
                print(f"   [AVISO] Node fetch retornou erro, tentando ler cache: {res.stderr}")
        except Exception as e:
            print(f"   [AVISO] Falha ao rodar node fetch: {e}")

    if not os.path.exists(data_json):
        print(f"[ERRO] Arquivo de dados {data_json} não encontrado.")
        return False

    with open(data_json, "r", encoding="utf-8") as f:
        atividades = json.load(f)

    SIGLAS = {
        'NNÓS', 'NNOS', 'MG', 'SP', 'PR', 'RJ', 'EUA', 'USA', 'PAR', 'CT', 'UVA', 
        'TRP', 'LATAM', 'BI', 'ADS', 'NH', 'IA', 'IVECO', 'DAF', 'BH', 'RH', 'NY', 
        'VOA', 'DRE', 'ROI', 'YTD', 'CRM', 'ERP', 'SODECIA', 'JAECCO'
    }

    LOWERCASE_WORDS = {
        'de', 'da', 'do', 'das', 'dos', 'em', 'com', 'para', 'por', 'e', 'a', 'ao', 'aos', 'à', 'às'
    }

    def clean_title_case(text):
        if not text:
            return text
        def format_word(match, is_first):
            w = match.group(0)
            upper_w = w.upper()
            for s in SIGLAS:
                if upper_w == s.upper():
                    return s
            if not is_first and upper_w.lower() in LOWERCASE_WORDS:
                return upper_w.lower()
            return w.capitalize()

        parts = re.split(r'(\s*[-–—/\\+&]\s*|\s*\(\s*|\s*\)\s*)', text)
        res_parts = []
        for part in parts:
            if re.match(r'^\s*[-–—/\\+&]\s*$|^\s*[\(\)]\s*$', part):
                res_parts.append(part)
                continue
            words = re.findall(r'[\wÀ-ÿ]+|[^\w\sÀ-ÿ]+|\s+', part)
            part_out = []
            is_first = True
            for token in words:
                if re.match(r'^[\wÀ-ÿ]+$', token):
                    part_out.append(format_word(re.match(r'^[\wÀ-ÿ]+$', token), is_first))
                    is_first = False
                else:
                    part_out.append(token)
                    if token.strip() in {':', '.', '!'}:
                        is_first = True
            res_parts.append(''.join(part_out))
        
        res = ''.join(res_parts)
        res = re.sub(r'\bProspeção\b', 'Prospecção', res, flags=re.IGNORECASE)
        res = re.sub(r'\bProspecçao\b', 'Prospecção', res, flags=re.IGNORECASE)
        res = re.sub(r'\bAssunçao\b', 'Assunção', res, flags=re.IGNORECASE)
        return res

    for a in atividades:
        nome = a.get("nome", "")
        if nome.startswith("eunião"):
            nome = "R" + nome
        a["nome"] = clean_title_case(nome)
        a["local"] = clean_title_case(a.get("local", ""))
        if a.get("projeto"):
            a["projeto"] = clean_title_case(a.get("projeto", ""))

    total_gasto = sum(a["valor"] for a in atividades)
    total_atividades = len(atividades)
    ticket_medio = total_gasto / total_atividades if total_atividades > 0 else 0
    total_intl = sum(a["valor"] for a in atividades if a["tipo"] == "intl")
    total_nac = sum(a["valor"] for a in atividades if a["tipo"] == "nac")
    pct_intl = (total_intl / total_gasto * 100) if total_gasto > 0 else 0
    pct_nac = (total_nac / total_gasto * 100) if total_gasto > 0 else 0

    # Meses Jan a Set
    mes_order = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set"]
    mes_gastos = {m: 0.0 for m in mes_order}
    mes_counts = {m: 0 for m in mes_order}
    for a in atividades:
        m = a.get("mes", "Outro")
        if m in mes_gastos:
            mes_gastos[m] += a["valor"]
            mes_counts[m] += 1

    num_meses = len([m for m in mes_order if mes_counts[m] > 0])
    media_mensal = total_gasto / num_meses if num_meses > 0 else 0
    projecao_anual = media_mensal * 12

    # Categorias
    cat_order = [
        "Viagens Internacionais", "Planejamento & Diretoria", "Visitas Técnicas",
        "Eventos & Feiras", "Prospecção", "Treinamentos", "Refeições de Negócio", "Outros"
    ]
    cat_totais = {c: 0.0 for c in cat_order}
    for a in atividades:
        c = a.get("categoria", "Outros")
        if c in cat_totais:
            cat_totais[c] += a["valor"]
        else:
            cat_totais["Outros"] += a["valor"]

    # Top Destinos
    dest_totais = {}
    for a in atividades:
        d = a["local"]
        if "Las Vegas" in d: d = "Las Vegas/EUA"
        elif "China" in d: d = "China"
        elif "Campus UVA" in d or "Belo Horizonte" in d or "Nova Lima" in d: d = "BH/Nova Lima/MG"
        elif "São Paulo" in d: d = "São Paulo/SP"
        elif "Curitiba" in d: d = "Curitiba/PR"
        elif "Nova Iorque" in d: d = "Nova Iorque/EUA"
        elif "Ribeirão Preto" in d: d = "Ribeirão Preto/SP"
        elif "Pouso Alegre" in d: d = "Pouso Alegre/MG"
        elif "Assunção" in d or "Paraguai" in d or "Paraguay" in d or "Tape" in d: d = "Assunción/PAR"
        elif "Sete Lagoas" in d: d = "Sete Lagoas/MG"
        elif "Sorocaba" in d: d = "Sorocaba/SP"
        elif "Betim" in d: d = "Betim/MG"
        elif "Toledo" in d: d = "Toledo/PR"
        elif "Juiz de Fora" in d: d = "Juiz de Fora/MG"
        dest_totais[d] = dest_totais.get(d, 0.0) + a["valor"]

    top10_destinos = sorted(dest_totais.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top 10 Atividades
    top10_atividades = sorted(atividades, key=lambda x: x["valor"], reverse=True)[:10]

    # Cenários
    cenario_prospeccao = [a for a in atividades if a.get("categoria") == "Prospecção"]
    cenario_intl = [a for a in atividades if a.get("tipo") == "intl"]
    cenario_plan = [a for a in atividades if a.get("categoria") == "Planejamento & Diretoria"]
    cenario_refeicoes = [a for a in atividades if a.get("categoria") == "Refeições de Negócio"]
    cenario_eventos = [a for a in atividades if a.get("categoria") == "Eventos & Feiras"]

    def fmt_brl(val):
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_k(val):
        return f"R$ {val/1e3:,.1f}K".replace(".", ",")

    def clean_name(nome):
        # Corrigir potenciais truncamentos como "eunião" -> "Reunião"
        if nome.startswith("eunião"):
            return "R" + nome
        return nome

    # Carregar template base code.html
    code_path = os.path.join(repo_dir, "code.html")
    with open(code_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Favicons & Auth Head Script
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
<link rel="icon" type="image/png" href="assets/logo-nnos.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png"/>
<link rel="icon" type="image/png" sizes="64x64" href="favicon.png"/>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
<link rel="apple-touch-icon" href="assets/logo-nnos.png"/>
"""
    if 'sessionStorage.getItem' not in html:
        html = html.replace("</head>", security_auth_head + "\n</head>")

    # 2. Header: Período, Total, Atividades, Destinos & Logo ao lado do Título
    destinos_unicos = len(set(a["local"] for a in atividades))
    header_html = f"""<!-- ═══════════ HEADER ═══════════ -->
<header class="relative overflow-hidden border-b border-surface-variant">
  <div class="absolute inset-0 z-0">
    <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-brand-blue/10 to-transparent"></div>
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-brand-blue/20 rounded-full blur-3xl"></div>
  </div>
  <div class="max-w-[1440px] mx-auto px-6 py-8 relative z-10">
    <div class="flex items-center gap-5 mb-5">
      <img alt="NNÓS Logo" class="h-14 sm:h-16 w-auto object-contain flex-shrink-0 opacity-95" src="assets/logo-nnos.png"/>
      <div class="h-12 w-[1px] bg-white/20 hidden sm:block"></div>
      <div>
        <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold font-display text-text-primary tracking-tight">Dashboard Executivo de Despesas Operacionais</h1>
        <p class="text-text-muted text-sm sm:text-base mt-1">Análise consolidada de viagens e atividades corporativas — NNÓS Business Solutions</p>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-3 text-xs sm:text-sm font-medium">
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface border border-surface-variant whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-blue text-sm">calendar_month</span> Jan/2026 a Set/2026
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface border border-surface-variant font-bold text-white whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-blue text-sm">payments</span> Total: {fmt_brl(total_gasto)}
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface border border-surface-variant whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-blue text-sm">assignment</span> {total_atividades} Atividades
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-surface-container text-on-surface border border-surface-variant whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-blue text-sm">public</span> {destinos_unicos} Destinos
      </span>
    </div>
  </div>
</header>"""
    html = re.sub(
        r'(<!-- ═══════════ HEADER ═══════════ -->\s*)?<header.*?</header>',
        header_html,
        html,
        flags=re.DOTALL
    )

    # 3. Substituição da Navbar: Padronização em 2 Linhas (Outros Relatórios Acima)
    standard_nav = """
<nav class="sticky top-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-white/10 shadow-xl">
  <!-- Linha 1: Outros Relatórios e Ações Globais -->
  <div class="bg-slate-900/90 px-6 py-1.5 border-b border-white/10">
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
        <a href="booking.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-emerald-300 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">trending_up</span> Performance Projetos
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

  <!-- Linha 2: Seções do Relatório -->
  <div class="max-w-[1440px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#kpis"><span class="material-symbols-outlined text-sm text-purple-400">monitoring</span> KPIs</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#mensal"><span class="material-symbols-outlined text-sm text-purple-400">show_chart</span> Gasto Mensal</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#categorias"><span class="material-symbols-outlined text-sm text-purple-400">category</span> Categorias</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#geografico"><span class="material-symbols-outlined text-sm text-purple-400">map</span> Geográfico</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#top10"><span class="material-symbols-outlined text-sm text-purple-400">local_fire_department</span> Top 10</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#atividades"><span class="material-symbols-outlined text-sm text-purple-400">list_alt</span> Atividades</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#cenarios"><span class="material-symbols-outlined text-sm text-purple-400">explore</span> Cenários</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#timeline"><span class="material-symbols-outlined text-sm text-purple-400">timeline</span> Timeline</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#alertas"><span class="material-symbols-outlined text-sm text-purple-400">warning</span> Alertas</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#recomendacoes"><span class="material-symbols-outlined text-sm text-purple-400">lightbulb</span> Recomendações</a>
    </div>
  </div>
</nav>
"""
    html = re.sub(r'<nav.*?</nav>', standard_nav.strip(), html, flags=re.DOTALL)

    # Padronizar Rodapé (sem o texto duplicado da direita)
    standard_footer_prosp = """
<!-- FOOTER -->
<footer class="bg-slate-950 border-t border-white/10 py-8 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS Logo" class="h-10 w-auto object-contain opacity-90" src="assets/logo-nnos.png"/>
      <span class="font-bold text-white">NNÓS Controladoria &amp; Gestão Financeira</span>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Setembro de 2026</div>
  </div>
</footer>
"""
    html = re.sub(r'(<!-- FOOTER -->\s*)?<footer.*?</footer\s*>', standard_footer_prosp.strip(), html, flags=re.DOTALL)

    # 4. Atualizar KPIs Cards (Seção #kpis)
    kpis_html = f"""
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-brand-blue">account_balance_wallet</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-brand-blue border border-surface-variant">
            <span class="material-symbols-outlined">payments</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Gasto Total</div>
        </div>
        <div class="data-number text-white mb-1">{fmt_brl(total_gasto).split(',')[0]}</div>
        <div class="text-xs text-text-muted">{num_meses} meses de operação</div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-brand-blue to-transparent"></div>
      </div>
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-brand-blue">task</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-brand-blue border border-surface-variant">
            <span class="material-symbols-outlined">assignment</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Atividades</div>
        </div>
        <div class="data-number text-white mb-1">{total_atividades}</div>
        <div class="text-xs text-text-muted">Média {total_atividades/num_meses:.1f}/mês</div>
      </div>
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-brand-blue">analytics</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-brand-blue border border-surface-variant">
            <span class="material-symbols-outlined">calculate</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Ticket Médio</div>
        </div>
        <div class="data-number text-white mb-1">{fmt_brl(ticket_medio).split(',')[0]}</div>
        <div class="text-xs text-text-muted">Por atividade</div>
      </div>
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-brand-blue">flight_takeoff</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-brand-blue border border-surface-variant">
            <span class="material-symbols-outlined">public</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Internacional</div>
        </div>
        <div class="data-number text-white mb-1">{fmt_brl(total_intl).split(',')[0]}</div>
        <div class="text-xs text-brand-blue font-medium">{pct_intl:.1f}% do total</div>
      </div>
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-brand-blue">location_on</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-brand-blue border border-surface-variant">
            <span class="material-symbols-outlined">map</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Nacional</div>
        </div>
        <div class="data-number text-white mb-1">{fmt_brl(total_nac).split(',')[0]}</div>
        <div class="text-xs text-text-muted">{pct_nac:.1f}% do total</div>
      </div>
      <div class="glass-card rounded-lg p-5 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span class="material-symbols-outlined text-5xl text-accent-amber">trending_up</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-surface-container-high flex items-center justify-center text-accent-amber border border-surface-variant">
            <span class="material-symbols-outlined">event_upcoming</span>
          </div>
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Projeção Anual</div>
        </div>
        <div class="data-number text-white mb-1">~{fmt_k(projecao_anual)}</div>
        <div class="text-xs text-text-muted">Base: {fmt_brl(media_mensal).split(',')[0]}/mês</div>
      </div>
"""
    html = re.sub(
        r'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">.*?</div>\s*</section>',
        f'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">{kpis_html}</div>\n  </section>',
        html,
        flags=re.DOTALL
    )

    # 5. Filtros e Tabela: Opções de Agosto e Setembro
    html = re.sub(
        r'<option value="Jul">Julho</option>\s*</select>',
        '<option value="Jul">Julho</option>\n<option value="Ago">Agosto</option>\n<option value="Set">Setembro</option>\n</select>',
        html
    )

    # Renderizar todas as 50 linhas na tabela estática
    static_table_rows = ""
    for idx, a in enumerate(atividades, start=1):
        tipo_badge = '<span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-error/10 text-error border border-error/20"><span class="material-symbols-outlined text-[14px]">public</span> Intl</span>' if a["tipo"] == "intl" else '<span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-brand-blue/10 text-brand-blue border border-brand-blue/20"><span class="material-symbols-outlined text-[14px]">map</span> Nac</span>'
        static_table_rows += f"""<tr class="hover:bg-surface-container-high/50 transition-colors">
      <td class="py-3 px-4 text-text-muted">{idx}</td>
      <td class="py-3 px-4 font-medium text-white">{clean_name(a['nome'])}</td>
      <td class="py-3 px-4 text-text-muted">{a['local']}</td>
      <td class="py-3 px-4 text-text-muted">{a['mes']}</td>
      <td class="py-3 px-4">{tipo_badge}</td>
      <td class="py-3 px-4 text-right font-medium text-brand-blue font-mono">{fmt_brl(a['valor'])}</td>
    </tr>"""

    html = re.sub(
        r'<h3 class="font-medium text-white flex items-center gap-2" id="tableTitle">.*?</h3>',
        f'<h3 class="font-medium text-white flex items-center gap-2" id="tableTitle"><span class="material-symbols-outlined text-brand-blue">list</span> {total_atividades} atividades encontradas</h3>',
        html
    )
    html = re.sub(
        r'<tbody class="divide-y divide-surface-variant" id="tabelaBody">.*?</tbody>',
        f'<tbody class="divide-y divide-surface-variant" id="tabelaBody">{static_table_rows}</tbody>',
        html,
        flags=re.DOTALL
    )

    # 6. Helper para gerar linhas de tabela de cenário
    def render_scenario_rows(lista):
        rows = ""
        for a in sorted(lista, key=lambda x: x["valor"], reverse=True):
            rows += f"<tr><td class=\"py-2.5 px-3 text-white\">{clean_name(a['nome'])}</td><td class=\"py-2.5 px-3 text-text-muted\">{a['local']}</td><td class=\"py-2.5 px-3 text-text-muted\">{a['mes']}</td><td class=\"py-2.5 px-3 text-right font-medium text-brand-blue font-mono\">{fmt_brl(a['valor'])}</td></tr>\n"
        return rows

    # Cenário 0: Prospecção
    total_cen_prosp = sum(a["valor"] for a in cenario_prospeccao)
    count_cen_prosp = len(cenario_prospeccao)
    pct_cen_prosp = (total_cen_prosp / total_gasto * 100) if total_gasto > 0 else 0
    tkt_cen_prosp = total_cen_prosp / count_cen_prosp if count_cen_prosp > 0 else 0
    prosp_rows_html = render_scenario_rows(cenario_prospeccao)

    cenario0_html = f"""
    <!-- Cenário 0: Prospecção -->
    <div class="scenario-content glass-card rounded-lg p-6 border border-surface-variant" id="cenario0">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Investido</div>
          <div class="data-number text-white mt-1">{fmt_brl(total_cen_prosp)}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Atividades</div>
          <div class="data-number text-white mt-1">{count_cen_prosp}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">% do Total</div>
          <div class="data-number text-white mt-1">{pct_cen_prosp:.1f}%</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Ticket Médio</div>
          <div class="data-number text-white mt-1">{fmt_brl(tkt_cen_prosp).split(',')[0]}</div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm scenario-table">
          <thead>
            <tr class="bg-surface-container/50">
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Atividade</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Local</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Mês</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant">
            {prosp_rows_html}
          </tbody>
        </table>
      </div>
      <p class="mt-4 p-3 rounded-lg text-sm bg-brand-blue/10 text-brand-blue border border-brand-blue/20">
        💡 <strong>Insight Estratégico:</strong> 7 frentes corporativas ativas de prospecção comercial (DAF, Porsche Jan e Mar, Mercedes SP, BH, Pouso Alegre, Betim). Recomenda-se correlacionar com a taxa de conversão do CRM de Vendas.
      </p>
    </div>
"""

    # Cenário 1: Internacional
    total_cen_intl = sum(a["valor"] for a in cenario_intl)
    count_cen_intl = len(cenario_intl)
    pct_cen_intl = (total_cen_intl / total_gasto * 100) if total_gasto > 0 else 0
    tkt_cen_intl = total_cen_intl / count_cen_intl if count_cen_intl > 0 else 0
    intl_rows_html = render_scenario_rows(cenario_intl)

    cenario1_html = f"""
    <!-- Cenário 1: Internacional -->
    <div class="scenario-content glass-card rounded-lg p-6 border border-surface-variant hidden" id="cenario1">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Internacional</div>
          <div class="data-number text-white mt-1">{fmt_brl(total_cen_intl)}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Viagens</div>
          <div class="data-number text-white mt-1">{count_cen_intl}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">% do Total</div>
          <div class="data-number text-white mt-1">{pct_cen_intl:.1f}%</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Países</div>
          <div class="data-number text-white mt-1">3</div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm scenario-table">
          <thead>
            <tr class="bg-surface-container/50">
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Atividade</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Local</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Mês</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant">
            {intl_rows_html}
          </tbody>
        </table>
      </div>
      <p class="mt-4 p-3 rounded-lg text-sm bg-accent-amber/10 text-accent-amber border border-accent-amber/20">
        ⚠️ <strong>Atenção:</strong> EUA e China concentram {((19757.53 + 1554.50 + 5500.00 + 19181.83) / total_cen_intl * 100):.1f}% do desembolso internacional (CONEXPO, Missão China, Summit NY).
      </p>
    </div>
"""

    # Cenário 2: Planejamento & Diretoria
    total_cen_plan = sum(a["valor"] for a in cenario_plan)
    count_cen_plan = len(cenario_plan)
    pct_cen_plan = (total_cen_plan / total_gasto * 100) if total_gasto > 0 else 0
    tkt_cen_plan = total_cen_plan / count_cen_plan if count_cen_plan > 0 else 0
    plan_rows_html = render_scenario_rows(cenario_plan)

    cenario2_html = f"""
    <!-- Cenário 2: Planejamento & Diretoria -->
    <div class="scenario-content glass-card rounded-lg p-6 border border-surface-variant hidden" id="cenario2">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Planejamento</div>
          <div class="data-number text-white mt-1">{fmt_brl(total_cen_plan)}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Atividades</div>
          <div class="data-number text-white mt-1">{count_cen_plan}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">% do Total</div>
          <div class="data-number text-white mt-1">{pct_cen_plan:.1f}%</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Ticket Médio</div>
          <div class="data-number text-white mt-1">{fmt_brl(tkt_cen_plan).split(',')[0]}</div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm scenario-table">
          <thead>
            <tr class="bg-surface-container/50">
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Atividade</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Local</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Mês</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant">
            {plan_rows_html}
          </tbody>
        </table>
      </div>
      <p class="mt-4 p-3 rounded-lg text-sm bg-error/10 text-error border border-error/20">
        🔴 <strong>Destaque:</strong> O Planejamento Estratégico de fevereiro consumiu <strong>R$ 31.785,07</strong> somando todos os custos relacionados (coordenação, Patricia, alimentação e gráficas).
      </p>
    </div>
"""

    # Cenário 3: Refeições
    total_cen_ref = sum(a["valor"] for a in cenario_refeicoes)
    count_cen_ref = len(cenario_refeicoes)
    pct_cen_ref = (total_cen_ref / total_gasto * 100) if total_gasto > 0 else 0
    tkt_cen_ref = total_cen_ref / count_cen_ref if count_cen_ref > 0 else 0
    ref_rows_html = render_scenario_rows(cenario_refeicoes)

    cenario3_html = f"""
    <!-- Cenário 3: Refeições -->
    <div class="scenario-content glass-card rounded-lg p-6 border border-surface-variant hidden" id="cenario3">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Refeições</div>
          <div class="data-number text-white mt-1">{fmt_brl(total_cen_ref)}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Eventos</div>
          <div class="data-number text-white mt-1">{count_cen_ref}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">% do Total</div>
          <div class="data-number text-white mt-1">{pct_cen_ref:.1f}%</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Ticket Médio</div>
          <div class="data-number text-white mt-1">{fmt_brl(tkt_cen_ref).split(',')[0]}</div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm scenario-table">
          <thead>
            <tr class="bg-surface-container/50">
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Atividade</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Local</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Mês</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant">
            {ref_rows_html}
          </tbody>
        </table>
      </div>
    </div>
"""

    # Cenário 4: Eventos & Feiras
    total_cen_ev = sum(a["valor"] for a in cenario_eventos)
    count_cen_ev = len(cenario_eventos)
    pct_cen_ev = (total_cen_ev / total_gasto * 100) if total_gasto > 0 else 0
    tkt_cen_ev = total_cen_ev / count_cen_ev if count_cen_ev > 0 else 0
    ev_rows_html = render_scenario_rows(cenario_eventos)

    cenario4_html = f"""
    <!-- Cenário 4: Eventos & Feiras -->
    <div class="scenario-content glass-card rounded-lg p-6 border border-surface-variant hidden" id="cenario4">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Eventos</div>
          <div class="data-number text-white mt-1">{fmt_brl(total_cen_ev)}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Atividades</div>
          <div class="data-number text-white mt-1">{count_cen_ev}</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">% do Total</div>
          <div class="data-number text-white mt-1">{pct_cen_ev:.1f}%</div>
        </div>
        <div class="bg-surface-container-high/60 border-l-2 border-brand-blue rounded-lg p-4">
          <div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Ticket Médio</div>
          <div class="data-number text-white mt-1">{fmt_brl(tkt_cen_ev).split(',')[0]}</div>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-sm scenario-table">
          <thead>
            <tr class="bg-surface-container/50">
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Atividade</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Local</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant">Mês</th>
              <th class="py-2.5 px-3 text-xs font-semibold text-text-muted uppercase tracking-wider border-b border-surface-variant text-right">Valor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant">
            {ev_rows_html}
          </tbody>
        </table>
      </div>
    </div>
"""

    all_cenarios_html = f"""<!-- ──────── CENÁRIOS ──────── -->
  <section class="scroll-mt-24" id="cenarios">
    <div class="mb-8">
      <h2 class="text-2xl font-display font-semibold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Cenários Estratégicos
      </h2>
      <p class="text-text-muted mt-2 ml-4">Análises segmentadas por tipo de atividade para tomada de decisão.</p>
    </div>
    <div class="flex flex-wrap gap-2 mb-6" id="scenarioTabs">
      <button onclick="showScenario(0)" class="scenario-tab-active px-5 py-2.5 rounded-lg text-sm font-medium border border-surface-variant transition-colors flex items-center gap-2" data-idx="0">
        <span class="material-symbols-outlined text-lg">target</span> Prospecção
      </button>
      <button onclick="showScenario(1)" class="px-5 py-2.5 rounded-lg text-sm font-medium border border-surface-variant text-text-muted hover:text-white hover:border-brand-blue transition-colors flex items-center gap-2" data-idx="1">
        <span class="material-symbols-outlined text-lg">public</span> Internacional
      </button>
      <button onclick="showScenario(2)" class="px-5 py-2.5 rounded-lg text-sm font-medium border border-surface-variant text-text-muted hover:text-white hover:border-brand-blue transition-colors flex items-center gap-2" data-idx="2">
        <span class="material-symbols-outlined text-lg">groups</span> Planejamento & Diretoria
      </button>
      <button onclick="showScenario(3)" class="px-5 py-2.5 rounded-lg text-sm font-medium border border-surface-variant text-text-muted hover:text-white hover:border-brand-blue transition-colors flex items-center gap-2" data-idx="3">
        <span class="material-symbols-outlined text-lg">restaurant</span> Refeições de Negócio
      </button>
      <button onclick="showScenario(4)" class="px-5 py-2.5 rounded-lg text-sm font-medium border border-surface-variant text-text-muted hover:text-white hover:border-brand-blue transition-colors flex items-center gap-2" data-idx="4">
        <span class="material-symbols-outlined text-lg">celebration</span> Eventos & Feiras
      </button>
    </div>
{cenario0_html}
{cenario1_html}
{cenario2_html}
{cenario3_html}
{cenario4_html}
  </section>"""

    html = re.sub(
        r'<!-- ──────── CENÁRIOS ──────── -->.*?</section>',
        lambda m: all_cenarios_html,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 7. Atualizar Timeline: Todos os 9 meses (Jan a Set)
    all_timeline_html = f"""<!-- ──────── TIMELINE ──────── -->
  <section class="scroll-mt-24" id="timeline">
    <div class="mb-8">
      <h2 class="text-2xl font-display font-semibold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Linha do Tempo
      </h2>
      <p class="text-text-muted mt-2 ml-4">Principais marcos e atividades executadas mês a mês.</p>
    </div>
    <div class="relative pl-10 border-l-2 border-surface-variant space-y-4">
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 JANEIRO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Jan'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Jan']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">Concentração de <strong class="text-white">Reuniões de Diretoria (R$ 10.442,93)</strong> • Início prospecção Porsche • Back Office Curitiba • Assunção/Paraguai • RH Leadership Xperience</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 FEVEREIRO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Fev'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Fev']} atividades</span>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-error/10 text-error border border-error/20">🔥 MÊS PICO</span>
        </div>
        <p class="text-sm text-on-surface">★ <strong class="text-white">Planejamento Estratégico consolidado (R$ 31.785,07)</strong> — maior gasto do período • Viagem Tape/Paraguai • Workshop Manutenção em Sorocaba • Visita Diretoria UVA</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 MARÇO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Mar'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Mar']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">★ <strong class="text-white">CONEXPO Las Vegas (R$ 19,7K)</strong> • Visitas a São Paulo + JAECCO • Segundo maior mês em gastos</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 ABRIL</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Abr'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Abr']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">★ <strong class="text-white">Missão China (R$ 19,2K)</strong> • Agrishow Ribeirão Preto (R$ 9,7K) • Maior ticket médio do período</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 MAIO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Mai'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Mai']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">Summit VOA NY • Acelera TRP Curitiba • Jantares de relacionamento • Visita Sodecia</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 JUNHO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Jun'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Jun']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">Prospecções DAF e Pouso Alegre • Jantar Dealer em Toledo • NNÓS Day</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 JULHO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Jul'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Jul']} atividade</span>
        </div>
        <p class="text-sm text-on-surface">Jantar NH Construction em BH • Mês com menor desembolso registrado</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 AGOSTO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Ago'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Ago']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">★ <strong class="text-white">Prospecção SP Mercedes (R$ 2.248,94)</strong> • Visita Terceiros CT Sorocaba (R$ 1.575,31) • Prospecção BH (R$ 1.042,17) • Almoços Comerciais UVA e Tecar</p>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant relative timeline-item">
        <div class="flex items-center gap-3 mb-2 flex-wrap">
          <div class="text-white font-display font-semibold">📅 SETEMBRO</div>
          <div class="text-brand-blue font-mono font-bold">{fmt_brl(mes_gastos['Set'])}</div>
          <span class="text-text-muted text-sm">| {mes_counts['Set']} atividades</span>
        </div>
        <p class="text-sm text-on-surface">★ <strong class="text-white">Visita Técnica à Volvo em Curitiba (R$ 3.436,15)</strong> • Almoço em SP com Stellantis (R$ 209,08) • Suporte Visita Volvo / Almoço Comercial UVA (R$ 170,04)</p>
      </div>
    </div>
  </section>"""

    html = re.sub(
        r'<!-- ──────── TIMELINE ──────── -->.*?</section>',
        lambda m: all_timeline_html,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 8. Alertas e Insights atualizados
    alertas_html = f"""<!-- ──────── ALERTAS ──────── -->
  <section class="scroll-mt-24" id="alertas">
    <div class="mb-8">
      <h2 class="text-2xl font-display font-semibold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Alertas e Insights
      </h2>
      <p class="text-text-muted mt-2 ml-4">Pontos de atenção atualizados com base no consolidado de 50 atividades.</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="glass-card rounded-lg p-5 border-l-4 border-error">
        <div class="flex items-center gap-2 mb-2 text-error">
          <span class="material-symbols-outlined">trending_up</span>
          <h4 class="font-display font-semibold text-white">Fevereiro: mês-pico</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Com a inclusão dos custos de alimentação e gráfica, fevereiro saltou para <strong class="text-white">{fmt_brl(mes_gastos['Fev'])} (24,6% do total)</strong>, superando março.</p>
      </div>
      <div class="glass-card rounded-lg p-5 border-l-4 border-accent-amber">
        <div class="flex items-center gap-2 mb-2 text-accent-amber">
          <span class="material-symbols-outlined">groups</span>
          <h4 class="font-display font-semibold text-white">Planejamento consome 27,3%</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Planejamento & Diretoria é a <strong class="text-white">maior categoria individual</strong>, totalizando {fmt_brl(cat_totais['Planejamento & Diretoria'])} — superando visitas e eventos.</p>
      </div>
      <div class="glass-card rounded-lg p-5 border-l-4 border-emerald-500">
        <div class="flex items-center gap-2 mb-2 text-emerald-400">
          <span class="material-symbols-outlined">check_circle</span>
          <h4 class="font-display font-semibold text-white">Consolidação de 50 Atividades</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Todos os <strong class="text-white">{total_atividades} registros</strong> apurados de Janeiro a Setembro de 2026, totalizando {fmt_brl(total_gasto)}.</p>
      </div>
      <div class="glass-card rounded-lg p-5 border-l-4 border-accent-amber">
        <div class="flex items-center gap-2 mb-2 text-accent-amber">
          <span class="material-symbols-outlined">event_upcoming</span>
          <h4 class="font-display font-semibold text-white">Projeção anual atualizada</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Média apurada: <strong class="text-white">{fmt_brl(media_mensal).split(',')[0]}/mês</strong>. Projeção anual: ~{fmt_k(projecao_anual)} — estabilidade orçamentária no 2º semestre.</p>
      </div>
      <div class="glass-card rounded-lg p-5 border-l-4 border-emerald-500">
        <div class="flex items-center gap-2 mb-2 text-emerald-400">
          <span class="material-symbols-outlined">calendar_month</span>
          <h4 class="font-display font-semibold text-white">Q1 concentra 62,9% dos gastos</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Janeiro a março somam <strong class="text-white">{fmt_brl(mes_gastos['Jan'] + mes_gastos['Fev'] + mes_gastos['Mar'])}</strong> — avaliar desconcentração para Q2 e Q3 nos próximos ciclos.</p>
      </div>
      <div class="glass-card rounded-lg p-5 border-l-4 border-error">
        <div class="flex items-center gap-2 mb-2 text-error">
          <span class="material-symbols-outlined">warning</span>
          <h4 class="font-display font-semibold text-white">Planejamento de Fevereiro</h4>
        </div>
        <p class="text-sm text-on-surface-variant">Somando coordenação + Patricia + alimentação + gráficas: <strong class="text-white">R$ 31.785,07</strong> em um único evento.</p>
      </div>
    </div>
  </section>"""

    html = re.sub(
        r'<!-- ──────── ALERTAS ──────── -->.*?</section>',
        lambda m: alertas_html,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 9. Recomendações atualizadas
    recomendacoes_html = f"""<!-- ──────── RECOMENDAÇÕES ──────── -->
  <section class="scroll-mt-24" id="recomendacoes">
    <div class="mb-8">
      <h2 class="text-2xl font-display font-semibold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Recomendações para a Diretoria
      </h2>
      <p class="text-text-muted mt-2 ml-4">Ações estratégicas revisadas com base na nova realidade dos dados consolidados.</p>
    </div>
    <div class="space-y-4">
      <div class="glass-card rounded-lg p-5 border border-surface-variant flex gap-4 items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-primary flex items-center justify-center text-white font-display font-bold">1</div>
        <div>
          <h4 class="text-white font-display font-semibold mb-1">Revisão do Orçamento 2027</h4>
          <p class="text-sm text-on-surface-variant">Projeção revisada para ~{fmt_k(projecao_anual)}/ano. Recomenda-se margem de 20% sobre esse valor (total ~R$ 250K) para cobrir imprevistos e oscilações cambiais.</p>
        </div>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant flex gap-4 items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-primary flex items-center justify-center text-white font-display font-bold">2</div>
        <div>
          <h4 class="text-white font-display font-semibold mb-1">Planejamento Estratégico: centro de custo dedicado</h4>
          <p class="text-sm text-on-surface-variant">Criar um centro de custo específico para o Planejamento Estratégico (R$ 31,8K em 2026), segregando alimentação, gráfica e logística.</p>
        </div>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant flex gap-4 items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-primary flex items-center justify-center text-white font-display font-bold">3</div>
        <div>
          <h4 class="text-white font-display font-semibold mb-1">Alçada para viagens internacionais</h4>
          <p class="text-sm text-on-surface-variant">Implementar aprovação em dois níveis para viagens acima de R$ 10K, com análise prévia de ROI e cotação em ao menos dois fornecedores.</p>
        </div>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant flex gap-4 items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-primary flex items-center justify-center text-white font-display font-bold">4</div>
        <div>
          <h4 class="text-white font-display font-semibold mb-1">Desconcentração do Q1</h4>
          <p class="text-sm text-on-surface-variant">62,9% dos gastos concentram-se no primeiro trimestre. Avaliar mover parte das reuniões de diretoria para o segundo semestre, diluindo o impacto.</p>
        </div>
      </div>
      <div class="glass-card rounded-lg p-5 border border-surface-variant flex gap-4 items-start">
        <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-brand-blue to-primary flex items-center justify-center text-white font-display font-bold">5</div>
        <div>
          <h4 class="text-white font-display font-semibold mb-1">Métricas de ROI por atividade</h4>
          <p class="text-sm text-on-surface-variant">Implementar tag obrigatória de "retorno esperado" (prospecção, relacionamento, evento, capacitação) em cada lançamento para futura correlação com resultados comerciais.</p>
        </div>
      </div>
    </div>
  </section>"""

    html = re.sub(
        r'<!-- ──────── RECOMENDAÇÕES ──────── -->.*?</section>',
        lambda m: recomendacoes_html,
        html,
        count=1,
        flags=re.DOTALL
    )

    # 10. Atualizar JavaScript com Dados Dinâmicos e Chart.js Configs
    script_patch = f"""
// ═══════════ DADOS DINÂMICOS CONSOLIDADOS (GOOGLE SHEETS) ═══════════
const atividades = {json.dumps(atividades, indent=2, ensure_ascii=False)};

// ═══════════ TABELA ═══════════
function renderTabela(lista) {{
  const tbody = document.getElementById("tabelaBody");
  tbody.innerHTML = "";
  lista.forEach(function(a, i) {{
    const tipoBadge = a.tipo === "intl"
      ? '<span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-error/10 text-error border border-error/20"><span class="material-symbols-outlined text-[14px]">public</span> Intl</span>'
      : '<span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-brand-blue/10 text-brand-blue border border-brand-blue/20"><span class="material-symbols-outlined text-[14px]">map</span> Nac</span>';
    const valor = a.valor.toLocaleString("pt-BR", {{minimumFractionDigits:2, maximumFractionDigits:2}});
    tbody.innerHTML += "<tr class='hover:bg-surface-container-high/50 transition-colors'>" +
      "<td class='py-3 px-4 text-text-muted'>" + (i+1) + "</td>" +
      "<td class='py-3 px-4 font-medium text-white'>" + a.nome + "</td>" +
      "<td class='py-3 px-4 text-text-muted'>" + a.local + "</td>" +
      "<td class='py-3 px-4 text-text-muted'>" + a.mes + "</td>" +
      "<td class='py-3 px-4'>" + tipoBadge + "</td>" +
      "<td class='py-3 px-4 text-right font-medium text-brand-blue font-mono'>R$ " + valor + "</td>" +
    "</tr>";
  }});
  document.getElementById("tableTitle").innerHTML = '<span class="material-symbols-outlined text-brand-blue">list</span> ' + lista.length + " atividades encontradas";
}}

function aplicarFiltros() {{
  const mes = document.getElementById("filterMes").value;
  const tipo = document.getElementById("filterTipo").value;
  const valor = document.getElementById("filterValor").value;
  let lista = atividades.slice();
  if (mes) lista = lista.filter(function(a) {{ return a.mes === mes; }});
  if (tipo) lista = lista.filter(function(a) {{ return a.tipo === tipo; }});
  if (valor === "alto") lista = lista.filter(function(a) {{ return a.valor > 5000; }});
  else if (valor === "medio") lista = lista.filter(function(a) {{ return a.valor >= 1000 && a.valor <= 5000; }});
  else if (valor === "baixo") lista = lista.filter(function(a) {{ return a.valor < 1000; }});
  renderTabela(lista);
}}

function limparFiltros() {{
  document.getElementById("filterMes").value = "";
  document.getElementById("filterTipo").value = "";
  document.getElementById("filterValor").value = "";
  renderTabela(atividades);
}}

document.getElementById("filterMes").addEventListener("change", aplicarFiltros);
document.getElementById("filterTipo").addEventListener("change", aplicarFiltros);
document.getElementById("filterValor").addEventListener("change", aplicarFiltros);

// ═══════════ CENÁRIOS ═══════════
function showScenario(idx) {{
  const tabs = document.querySelectorAll("#scenarioTabs button");
  const contents = document.querySelectorAll(".scenario-content");
  tabs.forEach(function(t, i) {{
    if (i === idx) {{
      t.classList.add("scenario-tab-active");
      t.classList.remove("text-text-muted");
    }} else {{
      t.classList.remove("scenario-tab-active");
      t.classList.add("text-text-muted");
    }}
  }});
  contents.forEach(function(c, i) {{
    if (i === idx) {{
      c.classList.remove("hidden");
    }} else {{
      c.classList.add("hidden");
    }}
  }});
}}

// ═══════════ CHART.JS INITIALIZATION ═══════════
document.addEventListener("DOMContentLoaded", function() {{
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.color = "#9CA3AF";

  const brandBlue = "#0083CA";
  const cores = [
    "#0083CA", "#E87154", "#FBBF24", "#34D399",
    "#A78BFA", "#F472B6", "#60A5FA", "#F87171",
    "#818CF8", "#4ADE80"
  ];

  const tooltipBase = {{
    backgroundColor: "#191f2f",
    titleColor: "#FFFFFF",
    bodyColor: "#dce2f7",
    borderColor: "#2e3545",
    borderWidth: 1,
    padding: 10
  }};

  // Gasto Mensal (Jan a Set)
  new Chart(document.getElementById("chartMensal"), {{
    type: "bar",
    data: {{
      labels: {json.dumps(mes_order)},
      datasets: [{{
        label: "Gasto Mensal (R$)",
        data: [{', '.join(str(round(mes_gastos[m], 2)) for m in mes_order)}],
        backgroundColor: {json.dumps([f"{'#E87154' if m == 'Fev' else '#0083CA'}99" for m in mes_order])},
        borderColor: {json.dumps(['#E87154' if m == 'Fev' else '#0083CA' for m in mes_order])},
        borderWidth: 1,
        borderRadius: 6
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{ return "R$ " + ctx.parsed.y.toLocaleString("pt-BR", {{minimumFractionDigits:2}}); }}
          }}
        }})
      }},
      scales: {{
        y: {{
          beginAtZero: true,
          ticks: {{ callback: function(v) {{ return "R$ " + (v/1000).toFixed(0) + "K"; }}, color: "#9CA3AF" }},
          grid: {{ color: "rgba(255,255,255,0.05)" }}
        }},
        x: {{ ticks: {{ color: "#9CA3AF" }}, grid: {{ display: false }} }}
      }}
    }}
  }});

  // Atividades por Mês (Jan a Set)
  new Chart(document.getElementById("chartAtividadesMes"), {{
    type: "line",
    data: {{
      labels: {json.dumps(mes_order)},
      datasets: [{{
        label: "Atividades",
        data: [{', '.join(str(mes_counts[m]) for m in mes_order)}],
        borderColor: brandBlue,
        backgroundColor: "rgba(0, 131, 202, 0.15)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: brandBlue,
        borderWidth: 2
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }}, tooltip: tooltipBase }},
      scales: {{
        y: {{
          beginAtZero: true,
          ticks: {{ stepSize: 2, color: "#9CA3AF" }},
          grid: {{ color: "rgba(255,255,255,0.05)" }}
        }},
        x: {{ ticks: {{ color: "#9CA3AF" }}, grid: {{ display: false }} }}
      }}
    }}
  }});

  // Composição por Categoria (Donut)
  new Chart(document.getElementById("chartCategorias"), {{
    type: "doughnut",
    data: {{
      labels: {json.dumps(cat_order)},
      datasets: [{{
        data: [{', '.join(str(round(cat_totais[c], 2)) for c in cat_order)}],
        backgroundColor: cores.slice(0, {len(cat_order)}),
        borderWidth: 0
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: "right", labels: {{ color: "#9CA3AF", padding: 12, font: {{ size: 11 }} }} }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((ctx.parsed / total) * 100).toFixed(1);
              return " R$ " + ctx.parsed.toLocaleString("pt-BR", {{minimumFractionDigits:2}}) + " (" + pct + "%)";
            }}
          }}
        }})
      }}
    }}
  }});

  // Valor por Categoria (Barras Horizontais)
  new Chart(document.getElementById("chartCategoriasBar"), {{
    type: "bar",
    data: {{
      labels: {json.dumps([c.replace('Viagens ', '').replace(' de Negócio', '') for c in cat_order[:-1]])},
      datasets: [{{
        label: "Valor (R$)",
        data: [{', '.join(str(round(cat_totais[c], 2)) for c in cat_order[:-1])}],
        backgroundColor: cores.slice(0, 7).map(c => c + "99"),
        borderColor: cores.slice(0, 7),
        borderWidth: 1,
        borderRadius: 6
      }}]
    }},
    options: {{
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{ return "R$ " + ctx.parsed.x.toLocaleString("pt-BR", {{minimumFractionDigits:2}}); }}
          }}
        }})
      }},
      scales: {{
        x: {{
          beginAtZero: true,
          ticks: {{ callback: function(v) {{ return "R$ " + (v/1000).toFixed(0) + "K"; }}, color: "#9CA3AF" }},
          grid: {{ color: "rgba(255,255,255,0.05)" }}
        }},
        y: {{ ticks: {{ color: "#9CA3AF" }}, grid: {{ display: false }} }}
      }}
    }}
  }});

  // Destinos
  new Chart(document.getElementById("chartDestinos"), {{
    type: "bar",
    data: {{
      labels: {json.dumps([d[0] for d in top10_destinos])},
      datasets: [{{
        label: "Gasto (R$)",
        data: [{', '.join(str(round(d[1], 2)) for d in top10_destinos)}],
        backgroundColor: cores.map(c => c + "99"),
        borderColor: cores,
        borderWidth: 1,
        borderRadius: 6
      }}]
    }},
    options: {{
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{ return "R$ " + ctx.parsed.x.toLocaleString("pt-BR", {{minimumFractionDigits:2}}); }}
          }}
        }})
      }},
      scales: {{
        x: {{
          beginAtZero: true,
          ticks: {{ callback: function(v) {{ return "R$ " + (v/1000).toFixed(0) + "K"; }}, color: "#9CA3AF" }},
          grid: {{ color: "rgba(255,255,255,0.05)" }}
        }},
        y: {{ ticks: {{ color: "#9CA3AF" }}, grid: {{ display: false }} }}
      }}
    }}
  }});

  // Nacional vs Internacional
  new Chart(document.getElementById("chartNacIntl"), {{
    type: "pie",
    data: {{
      labels: ["Nacional ({fmt_brl(total_nac).split(',')[0]})", "Internacional ({fmt_brl(total_intl).split(',')[0]})"],
      datasets: [{{ data: [{round(total_nac, 2)}, {round(total_intl, 2)}], backgroundColor: [cores[3], cores[1]], borderWidth: 0 }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: "bottom", labels: {{ color: "#9CA3AF", padding: 15, font: {{ size: 12 }} }} }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((ctx.parsed / total) * 100).toFixed(1);
              return " R$ " + ctx.parsed.toLocaleString("pt-BR", {{minimumFractionDigits:2}}) + " (" + pct + "%)";
            }}
          }}
        }})
      }}
    }}
  }});

  // Top 10
  const top10 = atividades.slice().sort((a, b) => b.valor - a.valor).slice(0, 10);
  new Chart(document.getElementById("chartTop10"), {{
    type: "bar",
    data: {{
      labels: top10.map(a => a.nome.startsWith("eunião") ? "R" + a.nome : a.nome),
      datasets: [{{
        label: "Valor (R$)",
        data: top10.map(a => a.valor),
        backgroundColor: top10.map((a, i) => a.tipo === "intl" ? cores[1] + "99" : cores[i % 10] + "99"),
        borderColor: top10.map((a, i) => a.tipo === "intl" ? cores[1] : cores[i % 10]),
        borderWidth: 1,
        borderRadius: 6
      }}]
    }},
    options: {{
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: Object.assign({{}}, tooltipBase, {{
          callbacks: {{
            label: function(ctx) {{ return "R$ " + ctx.parsed.x.toLocaleString("pt-BR", {{minimumFractionDigits:2}}); }},
            title: function(items) {{
              const item = top10[items[0].dataIndex];
              const nome = item.nome.startsWith("eunião") ? "R" + item.nome : item.nome;
              return nome + " (" + item.local + ")";
            }}
          }}
        }})
      }},
      scales: {{
        x: {{
          beginAtZero: true,
          ticks: {{ callback: function(v) {{ return "R$ " + (v/1000).toFixed(0) + "K"; }}, color: "#9CA3AF" }},
          grid: {{ color: "rgba(255,255,255,0.05)" }}
        }},
        y: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }}, color: "#9CA3AF" }} }}
      }}
    }}
  }});

  // Render tabela inicial
  renderTabela(atividades);

  // Scroll suave
  document.querySelectorAll("nav a").forEach(function(a) {{
    a.addEventListener("click", function(e) {{
      const href = a.getAttribute("href");
      if (href && href.startsWith("#")) {{
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) target.scrollIntoView({{behavior: "smooth", block: "start"}});
      }}
    }});
  }});
}});
"""

    html = re.sub(
        r'<script>\s*// ═══════════ DADOS.*?// (?:Scroll suave|Smooth scroll).*?</script>',
        lambda m: f'<script>\n{script_patch}\n</script>',
        html,
        flags=re.DOTALL
    )

    # 11. Salvar em prospeccao.html e dashboard-executivo-prospeccao.html
    target_prosp = os.path.join(repo_dir, "prospeccao.html")
    target_dash = os.path.join(repo_dir, "dashboard-executivo-prospeccao.html")

    with open(target_prosp, "w", encoding="utf-8") as f:
        f.write(html)
    with open(target_dash, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Gerado com sucesso: {target_prosp}")
    print(f"[OK] Gerado com sucesso: {target_dash}")
    return True

if __name__ == "__main__":
    sync_prospeccao()
