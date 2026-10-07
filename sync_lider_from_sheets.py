import os
import json
import subprocess
import re

def sync_lider():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_script = os.path.join(repo_dir, "fetch_lider_sheets.mjs")
    data_json = os.path.join(repo_dir, "lider_data.json")

    print("1. Consultando Google Sheets API e sincronizando Painel por Líder...")
    if os.path.exists(fetch_script):
        try:
            res = subprocess.run(["node", fetch_script], cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
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
        data = json.load(f)

    macro = data.get("macro", {})
    leaders = data.get("leaders", [])
    mais_rentaveis = data.get("maisRentaveis", [])
    menos_rentaveis = data.get("menosRentaveis", [])
    metas_areas = data.get("metasAreas", [])

    def fmt_brl(val):
        if val is None:
            return "R$ 0,00"
        neg = val < 0
        s = f"R$ {abs(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"-{s}" if neg else s

    def fmt_k(val):
        if val is None:
            return "R$ 0K"
        neg = val < 0
        s = f"R$ {abs(val)/1e3:,.1f}K".replace(".", ",")
        return f"-{s}" if neg else s

    def fmt_pct(val):
        if val is None:
            return "0,0%"
        return f"{val:,.2f}%".replace(".", ",")

    # Cores e avatares para cada líder
    leader_styles = {
        "Beatriz Picorelli": {"from": "from-purple-600", "to": "to-indigo-500", "accent": "purple", "cargo": "Líder de Projetos Corporativos"},
        "Caroline Amieva": {"from": "from-amber-600", "to": "to-orange-500", "accent": "amber", "cargo": "Líder de Gestão Organizacional"},
        "Jefferson Souza": {"from": "from-sky-600", "to": "to-blue-500", "accent": "sky", "cargo": "Líder de Desenvolvimento de Negócios"},
        "Joice Lage": {"from": "from-rose-600", "to": "to-red-500", "accent": "rose", "cargo": "Líder Educacional & Campus"},
        "Leonardo Campos": {"from": "from-violet-600", "to": "to-fuchsia-500", "accent": "violet", "cargo": "Líder de Inovação & Academy"},
        "Vinicius Souza": {"from": "from-emerald-600", "to": "to-teal-500", "accent": "emerald", "cargo": "Líder de Operações & Outsourcing"},
        "Fábio Canassa": {"from": "from-blue-600", "to": "to-cyan-500", "accent": "blue", "cargo": "Líder de Consultoria Automotiva"}
    }

    # Gerar Swimlanes dos Líderes
    swimlanes_html = ""
    for l in leaders:
        nome = l["nome"]
        iniciais = l["iniciais"]
        total = l.get("total") or {}
        projetos = l.get("projetos", [])
        style = leader_styles.get(nome, {"from": "from-slate-600", "to": "to-slate-500", "accent": "blue", "cargo": "Líder de Projetos"})

        rec_tot = total.get("receita", 0)
        cust_tot = total.get("custos", 0)
        cust_pct = total.get("custosPct", 0)
        marg_tot = total.get("margem", 0)
        marg_pct = total.get("margemPct", 0)

        # Status badge do líder
        if marg_tot < 0:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span> Alerta: Déficit ({fmt_pct(marg_pct)})</span>'
            header_border = "border-rose-500/30"
        elif marg_pct >= 30:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Alta Rentabilidade ({fmt_pct(marg_pct)})</span>'
            header_border = "border-emerald-500/30"
        elif marg_pct >= 20:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-sky-500/20 text-sky-300 border border-sky-400/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span> Margem Saudável ({fmt_pct(marg_pct)})</span>'
            header_border = "border-sky-500/30"
        else:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-400/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> Margem Moderada ({fmt_pct(marg_pct)})</span>'
            header_border = "border-amber-500/30"

        # Cards de projetos
        cards_html = ""
        for p in projetos:
            p_rec = p.get("receita", 0)
            p_imp = p.get("impostos", 0)
            p_imp_pct = p.get("impostosPct", 12.25)
            p_cust = p.get("custos", 0)
            p_cust_pct = p.get("custosPct", 0)
            p_log = p.get("logistica", 0)
            p_log_pct = p.get("logisticaPct", 0)
            p_rep = p.get("repasse", 0)
            p_rep_pct = p.get("repassePct", 0)
            p_marg = p.get("margem", 0)
            p_marg_pct = p.get("margemPct", 0)

            # Barra proporcional
            w_imp = min(100, max(0, p_imp_pct))
            w_cust = min(100 - w_imp, max(0, p_cust_pct))
            w_log = min(100 - w_imp - w_cust, max(0, p_log_pct))
            w_marg = max(0, min(100 - w_imp - w_cust - w_log, p_marg_pct if p_marg > 0 else 0))

            # Bottom styling
            if p_marg < 0:
                bottom_bg = "bg-rose-950/60 border-rose-500/40 text-rose-300"
                badge_bg = "bg-rose-500 text-white"
                card_border = "border-rose-500/30 hover:border-rose-500/60"
            elif p_marg_pct >= 30:
                bottom_bg = "bg-emerald-950/50 border-emerald-500/30 text-emerald-300"
                badge_bg = "bg-emerald-500 text-white"
                card_border = "border-white/10 hover:border-emerald-500/50"
            elif p_marg_pct >= 20:
                bottom_bg = "bg-sky-950/50 border-sky-500/30 text-sky-300"
                badge_bg = "bg-sky-500 text-white"
                card_border = "border-white/10 hover:border-sky-500/50"
            else:
                bottom_bg = "bg-amber-950/50 border-amber-500/30 text-amber-300"
                badge_bg = "bg-amber-500 text-white"
                card_border = "border-white/10 hover:border-amber-500/50"

            cards_html += f"""
        <article class="project-card group relative bg-slate-900/80 rounded-2xl p-5 border {card_border} shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between backdrop-blur" data-titulo="{p['titulo'].lower()}" data-lider="{nome.lower()}">
          <div class="space-y-4">
            <!-- Header do Card -->
            <div class="flex items-start justify-between gap-2 min-h-[44px]">
              <h4 class="font-bold text-white text-sm leading-snug group-hover:text-sky-300 transition-colors">{p['titulo']}</h4>
            </div>

            <!-- Destaque de Receita -->
            <div class="bg-slate-950/60 rounded-xl p-3 border border-white/5">
              <div class="flex justify-between items-center text-xs">
                <span class="text-gray-400 font-medium">RECEITA TOTAL</span>
                <span class="font-bold text-gray-500 font-mono">100,0%</span>
              </div>
              <div class="text-lg font-bold text-white font-mono mt-0.5">
                {fmt_brl(p_rec)}
              </div>
            </div>

            <!-- Distribuição Financeira -->
            <div class="space-y-2 text-xs font-mono">
              <div class="flex justify-between items-center py-1 border-b border-white/5">
                <span class="text-gray-400 flex items-center gap-1.5 font-sans">
                  <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Impostos
                </span>
                <div class="text-right">
                  <span class="font-semibold text-gray-300">{fmt_brl(p_imp)}</span>
                  <span class="text-[11px] text-gray-500 ml-1">({fmt_pct(p_imp_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-white/5">
                <span class="text-gray-400 flex items-center gap-1.5 font-sans">
                  <span class="w-1.5 h-1.5 rounded-full {'bg-rose-500' if p_cust_pct > 70 else 'bg-amber-400'}"></span> Custos Operacionais
                </span>
                <div class="text-right">
                  <span class="font-semibold {'text-rose-400 font-bold' if p_cust_pct > 70 else 'text-gray-300'}">{fmt_brl(p_cust)}</span>
                  <span class="text-[11px] {'text-rose-400 font-bold' if p_cust_pct > 70 else 'text-gray-500'} ml-1">({fmt_pct(p_cust_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-white/5">
                <span class="text-gray-400 flex items-center gap-1.5 font-sans">
                  <span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span> Logística
                </span>
                <div class="text-right">
                  <span class="font-semibold text-gray-300">{fmt_brl(p_log)}</span>
                  <span class="text-[11px] text-gray-500 ml-1">({fmt_pct(p_log_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-white/5">
                <span class="text-gray-400 flex items-center gap-1.5 font-sans">
                  <span class="w-1.5 h-1.5 rounded-full bg-slate-500"></span> Repasse
                </span>
                <div class="text-right">
                  <span class="font-semibold text-gray-300">{fmt_brl(p_rep)}</span>
                  <span class="text-[11px] text-gray-500 ml-1">({fmt_pct(p_rep_pct)})</span>
                </div>
              </div>
            </div>

            <!-- Barra de Distribuição Visual -->
            <div class="space-y-1">
              <div class="flex justify-between text-[10px] text-gray-400 font-medium">
                <span>Composição de Custos</span>
                <span class="{'text-rose-400 font-bold' if p_marg < 0 else 'text-emerald-400 font-bold'}">Margem {fmt_pct(p_marg_pct)}</span>
              </div>
              <div class="w-full h-2 bg-slate-950 rounded-full overflow-hidden flex border border-white/5">
                <div class="bg-slate-400 h-full" style="width: {w_imp}%" title="Impostos: {p_imp_pct:.1f}%"></div>
                <div class="{'bg-rose-500' if p_cust_pct > 70 else 'bg-amber-400'} h-full" style="width: {w_cust}%" title="Custos: {p_cust_pct:.1f}%"></div>
                <div class="bg-sky-400 h-full" style="width: {w_log}%" title="Logística: {p_log_pct:.1f}%"></div>
                <div class="{'bg-rose-600' if p_marg < 0 else 'bg-emerald-500'} h-full" style="width: {w_marg}%" title="Margem: {p_marg_pct:.1f}%"></div>
              </div>
            </div>
          </div>

          <!-- Bottom: Margem Destacada -->
          <div class="mt-5 pt-3.5 border-t -mx-5 -mb-5 px-5 py-3 rounded-b-2xl flex items-center justify-between {bottom_bg}">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider block opacity-80">MARGEM LÍQUIDA</span>
              <span class="text-base font-bold font-mono">{fmt_brl(p_marg)}</span>
            </div>
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold font-mono shadow-sm {badge_bg}">
              {fmt_pct(p_marg_pct)}
            </span>
          </div>
        </article>"""

        swimlanes_html += f"""
    <!-- SWIMLANE: {nome.upper()} -->
    <section class="leader-swimlane space-y-4" data-leader-name="{nome.lower()}">
      <!-- Header da Raia / Líder -->
      <div class="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/90 border {header_border} shadow-lg backdrop-blur">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br {style['from']} {style['to']} flex items-center justify-center font-bold text-white text-base shadow-lg shadow-black/40 flex-shrink-0">
            {iniciais}
          </div>
          <div>
            <div class="flex items-center gap-2.5 flex-wrap">
              <h3 class="text-lg font-bold text-white tracking-tight">{nome}</h3>
              <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-white/10 text-gray-300 border border-white/15">
                {style['cargo']}
              </span>
              {status_badge}
              <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-gray-400">
                {len(projetos)} { "Projeto Ativo" if len(projetos) == 1 else "Projetos Ativos" }
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-1">Consolidação executiva de contratos, rentabilidade e custos sob gestão.</p>
          </div>
        </div>

        <!-- Totais Consolidados do Líder -->
        <div class="flex items-center gap-5 bg-slate-950/70 px-4 py-2.5 rounded-xl border border-white/10 text-xs font-mono">
          <div>
            <span class="block text-[10px] text-gray-400 uppercase font-sans font-medium">Receita Portfólio</span>
            <span class="font-bold text-white text-sm">{fmt_brl(rec_tot)}</span>
          </div>
          <div class="h-8 w-px bg-white/10"></div>
          <div>
            <span class="block text-[10px] text-gray-400 uppercase font-sans font-medium">Custos Consolidados</span>
            <span class="font-bold text-white text-sm">{fmt_brl(cust_tot)} <span class="text-[10px] text-gray-400 font-sans font-normal">({fmt_pct(cust_pct)})</span></span>
          </div>
          <div class="h-8 w-px bg-white/10"></div>
          <div>
            <span class="block text-[10px] text-gray-400 uppercase font-sans font-medium">Margem Operacional</span>
            <span class="font-bold {'text-rose-400' if marg_tot < 0 else 'text-emerald-400'} text-sm">{fmt_brl(marg_tot)} <span class="text-[10px] font-sans font-bold px-1.5 py-0.5 rounded {'bg-rose-500/20 text-rose-300' if marg_tot < 0 else 'bg-emerald-500/20 text-emerald-300'}">{fmt_pct(marg_pct)}</span></span>
          </div>
        </div>
      </div>

      <!-- Grade dos Cards Kanban -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {cards_html}
      </div>
    </section>
"""

    # Gerar Tabela: 20 Projetos Mais Rentáveis
    mais_rows_html = ""
    for p in mais_rentaveis:
        rank = p["ranking"]
        badge_rank = f'<span class="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold {"bg-amber-400 text-slate-950 shadow-md" if rank == 1 else "bg-slate-300 text-slate-950" if rank == 2 else "bg-amber-700 text-white" if rank == 3 else "bg-slate-800 text-gray-300"}">{rank}</span>'
        mais_rows_html += f"""
        <tr class="hover:bg-slate-800/50 transition-colors border-b border-white/5">
          <td class="py-3 px-4 text-center">{badge_rank}</td>
          <td class="py-3 px-4 font-bold text-white">{p['projeto']}</td>
          <td class="py-3 px-4 text-gray-300 text-xs font-medium">{p['lider']}</td>
          <td class="py-3 px-4 text-right font-mono text-gray-300">{fmt_brl(p['receita'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold text-emerald-400">{fmt_brl(p['margem'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold text-emerald-300">{fmt_pct(p['margemPct'])}</td>
        </tr>"""

    # Gerar Tabela: 10 Projetos Menos Rentáveis
    menos_rows_html = ""
    for p in menos_rentaveis:
        rank = p["ranking"]
        is_neg = p["margem"] < 0
        badge_rank = f'<span class="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold {"bg-rose-500 text-white shadow-md animate-pulse" if is_neg else "bg-slate-800 text-gray-300"}">{rank}</span>'
        menos_rows_html += f"""
        <tr class="hover:bg-slate-800/50 transition-colors border-b border-white/5 {'bg-rose-950/20' if is_neg else ''}">
          <td class="py-3 px-4 text-center">{badge_rank}</td>
          <td class="py-3 px-4 font-bold {'text-rose-300' if is_neg else 'text-white'}">{p['projeto']}</td>
          <td class="py-3 px-4 text-gray-300 text-xs font-medium">{p['lider']}</td>
          <td class="py-3 px-4 text-right font-mono text-gray-300">{fmt_brl(p['receita'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold {'text-rose-400' if is_neg else 'text-emerald-400'}">{fmt_brl(p['margem'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold {'text-rose-300' if is_neg else 'text-emerald-300'}">{fmt_pct(p['margemPct'])}</td>
        </tr>"""

    # Gerar Tabela: Metas por Área
    metas_rows_html = ""
    for m in metas_areas:
        is_total = m.get("isTotal", False)
        row_class = "bg-slate-800/80 font-bold border-t-2 border-sky-500/50" if is_total else "hover:bg-slate-800/50 border-b border-white/5"
        metas_rows_html += f"""
        <tr class="{row_class} transition-colors">
          <td class="py-3 px-4 {'text-sky-300 font-bold' if is_total else 'text-white'}">{m['area']}</td>
          <td class="py-3 px-4 text-right font-mono text-gray-300">{fmt_brl(m['meta'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold text-emerald-400">{fmt_brl(m['realizado'])}</td>
          <td class="py-3 px-4 text-right font-mono font-bold text-sky-400">{m['atingidoPct']}</td>
          <td class="py-3 px-4 text-right font-mono text-amber-300">{fmt_brl(m['falta'])}</td>
          <td class="py-3 px-4 text-right font-mono text-gray-400">{m['faltaPct']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>Painel por Líder de Projeto | NNÓS Controladoria &amp; Gestão Financeira</title>

  <!-- Google Fonts: Plus Jakarta Sans & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }},
          colors: {{
            brand: {{
              50: '#f0f7ff',
              100: '#e0effe',
              500: '#0284c7',
              600: '#0369a1',
              700: '#075985',
              900: '#082f49',
              950: '#041c2c',
            }}
          }}
        }}
      }}
    }}
  </script>

  <!-- Favicons -->
  <link rel="icon" type="image/png" href="assets/logo-nnos.png"/>
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png"/>
  <link rel="icon" type="image/png" sizes="64x64" href="favicon.png"/>
  <link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
  <link rel="apple-touch-icon" href="assets/logo-nnos.png"/>

  <!-- Camada de Autenticação e Segurança -->
  <script>
    if (sessionStorage.getItem('nnos_auth') !== 'true') {{
      window.location.href = 'index.html';
    }}
    function logout() {{
      sessionStorage.removeItem('nnos_auth');
      window.location.href = 'index.html';
    }}
    document.addEventListener('contextmenu', function(e) {{ e.preventDefault(); }}, false);
    document.addEventListener('keydown', function(e) {{
      if (e.key === 'F12' || e.keyCode === 123) {{ e.preventDefault(); return false; }}
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.keyCode === 73 || e.key === 'J' || e.key === 'j' || e.keyCode === 74 || e.key === 'C' || e.key === 'c' || e.keyCode === 67)) {{ e.preventDefault(); return false; }}
      if ((e.ctrlKey || e.metaKey) && (e.key === 'U' || e.key === 'u' || e.keyCode === 85)) {{ e.preventDefault(); return false; }}
      if ((e.ctrlKey || e.metaKey) && (e.key === 'S' || e.key === 's' || e.keyCode === 83)) {{ e.preventDefault(); return false; }}
    }}, false);
  </script>

  <style>
    /* Estilos de rolagem suave */
    html {{ scroll-behavior: smooth; }}
    .glass-card {{
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen antialiased selection:bg-brand-500 selection:text-white">

<!-- ═══════════ HEADER ═══════════ -->
<header class="relative overflow-hidden border-b border-white/10 bg-slate-950">
  <div class="absolute inset-0 z-0 pointer-events-none">
    <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-brand-600/15 via-purple-600/10 to-transparent"></div>
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-brand-500/20 rounded-full blur-3xl"></div>
  </div>
  <div class="max-w-[1720px] mx-auto px-6 py-8 relative z-10">
    <div class="flex items-center gap-5 mb-5 flex-wrap">
      <img alt="NNÓS Logo" class="h-14 sm:h-16 w-auto object-contain flex-shrink-0 opacity-95" src="assets/logo-nnos.png"/>
      <div class="h-12 w-[1px] bg-white/20 hidden sm:block"></div>
      <div>
        <div class="flex items-center gap-3 flex-wrap">
          <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">Painel Financeiro por Líder de Projeto</h1>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-ping"></span>
            Dados Sincronizados
          </span>
        </div>
        <p class="text-xs sm:text-sm text-gray-400 mt-1">Controle de rentabilidade, centros de custos e margem operacional por contrato corporativo — Fonte Google Sheets.</p>
      </div>
    </div>

    <!-- Tags / Badges Rápidas -->
    <div class="flex flex-wrap items-center gap-3 text-xs sm:text-sm font-medium">
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-gray-300 border border-white/10 whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-500 text-sm">calendar_month</span> YTD 2026
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-white border border-white/10 font-bold whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-500 text-sm">payments</span> Total: {fmt_brl(macro.get('receita', 0))}
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-gray-300 border border-white/10 whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-500 text-sm">groups</span> {macro.get('totalLideres', 7)} Líderes
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-gray-300 border border-white/10 whitespace-nowrap">
        <span class="material-symbols-outlined text-brand-500 text-sm">assignment</span> {macro.get('totalProjetos', 44)} Projetos Ativos
      </span>
      <span class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-emerald-400 border border-white/10 font-bold whitespace-nowrap">
        <span class="material-symbols-outlined text-emerald-400 text-sm">trending_up</span> Margem Geral: {fmt_pct(macro.get('margemPct', 0))}
      </span>
    </div>
  </div>
</header>

<!-- ═══════════ NAVBAR INTEGRADA ═══════════ -->
<nav class="sticky top-0 z-50 bg-slate-950/95 backdrop-blur-md border-b border-white/10 shadow-xl">
  <!-- Linha 1: Outros Relatórios e Ações Globais -->
  <div class="bg-slate-900/90 px-6 py-1.5 border-b border-white/10">
    <div class="max-w-[1720px] mx-auto flex items-center justify-between gap-3 flex-wrap">
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

  <!-- Linha 2: Seções do Relatório -->
  <div class="max-w-[1720px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#resumo"><span class="material-symbols-outlined text-sm text-sky-400">monitoring</span> Resumo Geral</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#lideres"><span class="material-symbols-outlined text-sm text-sky-400">groups</span> Painel dos Líderes</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#mais-rentaveis"><span class="material-symbols-outlined text-sm text-emerald-400">stars</span> 20 Mais Rentáveis</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#menos-rentaveis"><span class="material-symbols-outlined text-sm text-rose-400">warning</span> 10 Menos Rentáveis</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#metas"><span class="material-symbols-outlined text-sm text-amber-400">flag</span> Metas por Área</a>
    </div>
  </div>
</nav>

<!-- ═══════════ CONTEÚDO PRINCIPAL ═══════════ -->
<main class="max-w-[1720px] w-full mx-auto px-6 py-8 space-y-10">

  <!-- ──────── MACRO METRICS OVERVIEW ──────── -->
  <section id="resumo" class="scroll-mt-28 space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Métrica 1: Receita Bruta -->
      <div class="bg-slate-900/90 border border-white/10 rounded-2xl p-5 shadow-lg backdrop-blur relative overflow-hidden group">
        <div class="flex items-center justify-between text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Receita Bruta Consolidada</span>
          <div class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-sm">$</div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-white font-mono">
          {fmt_brl(macro.get('receita', 0))}
        </div>
        <p class="text-xs text-gray-400 mt-1.5">Soma de todos os 44 contratos sob gestão</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-sky-500 to-transparent"></div>
      </div>

      <!-- Métrica 2: Custos Operacionais -->
      <div class="bg-slate-900/90 border border-white/10 rounded-2xl p-5 shadow-lg backdrop-blur relative overflow-hidden group">
        <div class="flex items-center justify-between text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Custos Operacionais</span>
          <div class="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-sm">
            <span class="material-symbols-outlined text-base">trending_down</span>
          </div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-white font-mono">{fmt_brl(macro.get('custos', 0))}</span>
          <span class="text-xs font-bold text-rose-400">{fmt_pct(macro.get('custosPct', 0))}</span>
        </div>
        <p class="text-xs text-gray-400 mt-1.5">Custos diretos e contratações executadas</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-rose-500 to-transparent"></div>
      </div>

      <!-- Métrica 3: Margem Líquida Realizada -->
      <div class="bg-slate-900/90 border border-white/10 rounded-2xl p-5 shadow-lg backdrop-blur relative overflow-hidden group">
        <div class="flex items-center justify-between text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Margem Líquida Realizada</span>
          <div class="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">%</div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-emerald-400 font-mono">{fmt_brl(macro.get('margem', 0))}</span>
          <span class="text-xs font-bold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">{fmt_pct(macro.get('margemPct', 0))}</span>
        </div>
        <p class="text-xs text-gray-400 mt-1.5">Resultado operacional livre após despesas e impostos</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-emerald-500 to-transparent"></div>
      </div>

      <!-- Métrica 4: Impostos & Logística -->
      <div class="bg-slate-900/90 border border-white/10 rounded-2xl p-5 shadow-lg backdrop-blur relative overflow-hidden group">
        <div class="flex items-center justify-between text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Impostos &amp; Logística</span>
          <div class="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">
            <span class="material-symbols-outlined text-base">receipt_long</span>
          </div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-white font-mono">{fmt_brl(macro.get('impostos', 0) + macro.get('logistica', 0))}</span>
          <span class="text-xs font-bold text-indigo-400">{fmt_pct((macro.get('impostos', 0) + macro.get('logistica', 0)) / macro.get('receita', 1) * 100)}</span>
        </div>
        <p class="text-xs text-gray-400 mt-1.5">Impostos: 12,25% fixos • Logística: 7,21%</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-indigo-500 to-transparent"></div>
      </div>
    </div>
  </section>

  <!-- ──────── FILTROS RÁPIDOS INTERATIVOS ──────── -->
  <section class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/90 border border-white/10 backdrop-blur">
    <div class="flex items-center gap-3 flex-wrap">
      <span class="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
        <span class="material-symbols-outlined text-sm text-sky-400">filter_alt</span> Filtrar Líder:
      </span>
      <button onclick="filtrarLider('todos')" class="filter-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-500 text-white border border-sky-400 transition-all cursor-pointer" data-filter="todos">
        Todos (7)
      </button>
      {" ".join([f'<button onclick="filtrarLider(\'{l["nome"].lower()}\')" class="filter-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 text-gray-300 hover:text-white hover:bg-slate-700 border border-white/10 transition-all cursor-pointer" data-filter="{l["nome"].lower()}">{l["nome"]}</button>' for l in leaders])}
    </div>

    <!-- Campo de Busca por Projeto -->
    <div class="relative min-w-[260px]">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-base">search</span>
      <input id="searchProject" onkeyup="buscarProjetos()" type="text" placeholder="Buscar contrato ou projeto..." class="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-950/80 rounded-lg border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-all"/>
    </div>
  </section>

  <!-- ──────── SEÇÃO SWIMLANES DOS LÍDERES ──────── -->
  <section id="lideres" class="scroll-mt-28 space-y-8">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <div class="w-1.5 h-6 bg-sky-500 rounded-full"></div>
          Painel Financeiro por Líder
        </h2>
        <p class="text-xs sm:text-sm text-gray-400 mt-1">Visão detalhada em cards kanban para cada líder corporativo e seus projetos ativos.</p>
      </div>
      <div class="text-xs text-gray-400 flex items-center gap-3">
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> &gt; 30% Margem</span>
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-sky-400"></span> 20% a 30%</span>
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-400"></span> 0% a 20%</span>
        <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-rose-400"></span> Déficit</span>
      </div>
    </div>

    <div class="space-y-8">
      {swimlanes_html}
    </div>
  </section>

  <!-- ──────── 20 PROJETOS MAIS RENTÁVEIS ──────── -->
  <section id="mais-rentaveis" class="scroll-mt-28 space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <div class="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
          20 Projetos Mais Rentáveis
        </h2>
        <p class="text-xs sm:text-sm text-gray-400 mt-1">Ranking consolidado dos contratos com maior geração de margem líquida em valor monetário (R$).</p>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
        Critério: Margem em Valor (R$)
      </span>
    </div>

    <div class="overflow-x-auto rounded-2xl border border-white/10 bg-slate-900/90 shadow-xl backdrop-blur">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-950/80 text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-white/10">
            <th class="py-3.5 px-4 text-center w-16">Ranking</th>
            <th class="py-3.5 px-4">Projeto / Contrato</th>
            <th class="py-3.5 px-4">Líder do Projeto</th>
            <th class="py-3.5 px-4 text-right">Receita (R$)</th>
            <th class="py-3.5 px-4 text-right">Margem Líquida (R$)</th>
            <th class="py-3.5 px-4 text-right">Margem (%)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          {mais_rows_html}
        </tbody>
      </table>
    </div>
  </section>

  <!-- ──────── 10 PROJETOS MENOS RENTÁVEIS ──────── -->
  <section id="menos-rentaveis" class="scroll-mt-28 space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <div class="w-1.5 h-6 bg-rose-500 rounded-full"></div>
          10 Projetos Menos Rentáveis / Déficit
        </h2>
        <p class="text-xs sm:text-sm text-gray-400 mt-1">Projetos com menor geração de margem ou déficit operacional apurado no período.</p>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
        Atenção da Diretoria
      </span>
    </div>

    <div class="overflow-x-auto rounded-2xl border border-white/10 bg-slate-900/90 shadow-xl backdrop-blur">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-950/80 text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-white/10">
            <th class="py-3.5 px-4 text-center w-16">Ranking</th>
            <th class="py-3.5 px-4">Projeto / Contrato</th>
            <th class="py-3.5 px-4">Líder do Projeto</th>
            <th class="py-3.5 px-4 text-right">Receita (R$)</th>
            <th class="py-3.5 px-4 text-right">Margem (R$)</th>
            <th class="py-3.5 px-4 text-right">Margem (%)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          {menos_rows_html}
        </tbody>
      </table>
    </div>
  </section>

  <!-- ──────── CONTROLE DE METAS POR ÁREA 2026 ──────── -->
  <section id="metas" class="scroll-mt-28 space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h2 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <div class="w-1.5 h-6 bg-amber-500 rounded-full"></div>
          Controle de Metas por Área | 2026
        </h2>
        <p class="text-xs sm:text-sm text-gray-400 mt-1">Acompanhamento consolidado entre a meta orçada e a receita realizada por unidade de negócio.</p>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
        Exercício 2026
      </span>
    </div>

    <div class="overflow-x-auto rounded-2xl border border-white/10 bg-slate-900/90 shadow-xl backdrop-blur">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="bg-slate-950/80 text-[11px] font-bold text-gray-400 uppercase tracking-wider border-b border-white/10">
            <th class="py-3.5 px-4">Área / Unidade</th>
            <th class="py-3.5 px-4 text-right">Meta 2026 (R$)</th>
            <th class="py-3.5 px-4 text-right">Realizado (R$)</th>
            <th class="py-3.5 px-4 text-right">Atingido (%)</th>
            <th class="py-3.5 px-4 text-right">Falta (R$)</th>
            <th class="py-3.5 px-4 text-right">Falta (%)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          {metas_rows_html}
        </tbody>
      </table>
    </div>
  </section>

</main>

<!-- ═══════════ FOOTER ═══════════ -->
<footer class="bg-slate-950 border-t border-white/10 py-8 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1720px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS Logo" class="h-10 w-auto object-contain opacity-90" src="assets/logo-nnos.png"/>
      <span class="font-bold text-white">NNÓS Controladoria &amp; Gestão Financeira</span>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Setembro de 2026</div>
  </div>
</footer>

<!-- ═══════════ SCRIPTS INTERATIVOS ═══════════ -->
<script>
  function filtrarLider(lider) {{
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      if (btn.getAttribute('data-filter') === lider) {{
        btn.classList.add('bg-sky-500', 'text-white', 'border-sky-400');
        btn.classList.remove('bg-slate-800', 'text-gray-300');
      }} else {{
        btn.classList.remove('bg-sky-500', 'text-white', 'border-sky-400');
        btn.classList.add('bg-slate-800', 'text-gray-300');
      }}
    }});

    document.querySelectorAll('.leader-swimlane').forEach(lane => {{
      const laneName = lane.getAttribute('data-leader-name');
      if (lider === 'todos' || laneName === lider) {{
        lane.style.display = 'block';
      }} else {{
        lane.style.display = 'none';
      }}
    }});
  }}

  function buscarProjetos() {{
    const q = document.getElementById('searchProject').value.toLowerCase().trim();
    document.querySelectorAll('.project-card').forEach(card => {{
      const titulo = card.getAttribute('data-titulo') || '';
      const lider = card.getAttribute('data-lider') || '';
      if (!q || titulo.includes(q) || lider.includes(q)) {{
        card.style.display = 'flex';
      }} else {{
        card.style.display = 'none';
      }}
    }});
  }}
</script>

</body>
</html>
"""

    out_lider = os.path.join(repo_dir, "lider.html")
    out_dash = os.path.join(repo_dir, "painel-por-lider.html")

    with open(out_lider, "w", encoding="utf-8") as f:
        f.write(html)
    with open(out_dash, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Gerado com sucesso: {out_lider}")
    print(f"[OK] Gerado com sucesso: {out_dash}")
    return True

if __name__ == "__main__":
    sync_lider()
