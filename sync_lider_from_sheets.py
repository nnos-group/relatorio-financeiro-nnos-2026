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
            return "R$ 0"
        neg = val < 0
        s = f"R$ {abs(val):,.0f}".replace(",", ".")
        return f"-{s}" if neg else s

    def fmt_pct(val):
        if val is None:
            return "0,0%"
        return f"{val:,.2f}%".replace(".", ",")

    # Iniciais dos líderes para avatar no ranking
    leader_iniciais = {
        "Vinicius Souza": "VS",
        "Beatriz Picorelli": "BP",
        "Jefferson Souza": "JS",
        "Caroline Amieva": "CA",
        "Fábio Canassa": "FC",
        "Joice Lage": "JL",
        "Leonardo Campos": "LC"
    }

    leader_avatar_bg = {
        "Vinicius Souza": "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300",
        "Beatriz Picorelli": "bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300",
        "Jefferson Souza": "bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300",
        "Caroline Amieva": "bg-pink-100 dark:bg-pink-950/60 text-pink-800 dark:text-pink-300",
        "Fábio Canassa": "bg-sky-100 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300",
        "Joice Lage": "bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300",
        "Leonardo Campos": "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300"
    }

    # Cores e avatares para cada líder nas raias kanban
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
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/15 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-500/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span> Alerta: Déficit ({fmt_pct(marg_pct)})</span>'
            header_border = "border-rose-300 dark:border-rose-500/30"
        elif marg_pct >= 30:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-500/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Alta Rentabilidade ({fmt_pct(marg_pct)})</span>'
            header_border = "border-emerald-300 dark:border-emerald-500/30"
        elif marg_pct >= 20:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-sky-500/15 text-sky-800 dark:text-sky-300 border border-sky-300 dark:border-sky-400/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-sky-500"></span> Margem Saudável ({fmt_pct(marg_pct)})</span>'
            header_border = "border-sky-300 dark:border-sky-500/30"
        else:
            status_badge = f'<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-400/40 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Margem Moderada ({fmt_pct(marg_pct)})</span>'
            header_border = "border-amber-300 dark:border-amber-500/30"

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
                bottom_bg = "bg-rose-100/90 dark:bg-rose-950/60 border-rose-300 dark:border-rose-500/40 text-rose-900 dark:text-rose-200"
                badge_bg = "bg-rose-600 text-white"
                card_border = "border-rose-300 dark:border-rose-500/40 hover:border-rose-500"
            elif p_marg_pct >= 30:
                bottom_bg = "bg-emerald-50 dark:bg-emerald-950/50 border-emerald-200 dark:border-emerald-500/30 text-emerald-900 dark:text-emerald-200"
                badge_bg = "bg-emerald-600 text-white"
                card_border = "border-slate-200/90 dark:border-white/10 hover:border-emerald-500/50"
            elif p_marg_pct >= 20:
                bottom_bg = "bg-sky-50 dark:bg-sky-950/50 border-sky-200 dark:border-sky-500/30 text-sky-900 dark:text-sky-200"
                badge_bg = "bg-sky-600 text-white"
                card_border = "border-slate-200/90 dark:border-white/10 hover:border-sky-500/50"
            else:
                bottom_bg = "bg-amber-50 dark:bg-amber-950/50 border-amber-200 dark:border-amber-500/30 text-amber-900 dark:text-amber-200"
                badge_bg = "bg-amber-500 text-white"
                card_border = "border-slate-200/90 dark:border-white/10 hover:border-amber-500/50"

            cards_html += f"""
        <article class="project-card group relative bg-white dark:bg-slate-900/80 rounded-2xl p-5 border {card_border} shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between" data-titulo="{p['titulo'].lower()}" data-lider="{nome.lower()}">
          <div class="space-y-4">
            <!-- Header do Card -->
            <div class="flex items-start justify-between gap-2 min-h-[44px]">
              <h4 class="font-bold text-slate-900 dark:text-white text-sm leading-snug group-hover:text-sky-600 dark:group-hover:text-sky-300 transition-colors">{p['titulo']}</h4>
            </div>

            <!-- Destaque de Receita -->
            <div class="bg-slate-50 dark:bg-slate-950/60 rounded-xl p-3 border border-slate-200/70 dark:border-white/5">
              <div class="flex justify-between items-center text-xs">
                <span class="text-slate-500 dark:text-gray-400 font-medium">RECEITA TOTAL</span>
                <span class="font-bold text-slate-400 dark:text-gray-500 tabular-nums">100,0%</span>
              </div>
              <div class="text-lg font-bold text-slate-900 dark:text-white tabular-nums mt-0.5">
                {fmt_brl(p_rec)}
              </div>
            </div>

            <!-- Distribuição Financeira -->
            <div class="space-y-2 text-xs">
              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-white/5">
                <span class="text-slate-600 dark:text-gray-400 flex items-center gap-1.5 font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Impostos
                </span>
                <div class="text-right tabular-nums">
                  <span class="font-semibold text-slate-800 dark:text-gray-300">{fmt_brl(p_imp)}</span>
                  <span class="text-[11px] text-slate-400 dark:text-gray-500 ml-1">({fmt_pct(p_imp_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-white/5">
                <span class="text-slate-600 dark:text-gray-400 flex items-center gap-1.5 font-medium">
                  <span class="w-1.5 h-1.5 rounded-full {'bg-rose-500' if p_cust_pct > 70 else 'bg-amber-400'}"></span> Custos Operacionais
                </span>
                <div class="text-right tabular-nums">
                  <span class="font-semibold {'text-rose-600 dark:text-rose-400 font-bold' if p_cust_pct > 70 else 'text-slate-800 dark:text-gray-300'}">{fmt_brl(p_cust)}</span>
                  <span class="text-[11px] {'text-rose-600 dark:text-rose-400 font-bold' if p_cust_pct > 70 else 'text-slate-400 dark:text-gray-500'} ml-1">({fmt_pct(p_cust_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-white/5">
                <span class="text-slate-600 dark:text-gray-400 flex items-center gap-1.5 font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span> Logística
                </span>
                <div class="text-right tabular-nums">
                  <span class="font-semibold text-slate-800 dark:text-gray-300">{fmt_brl(p_log)}</span>
                  <span class="text-[11px] text-slate-400 dark:text-gray-500 ml-1">({fmt_pct(p_log_pct)})</span>
                </div>
              </div>

              <div class="flex justify-between items-center py-1 border-b border-slate-100 dark:border-white/5">
                <span class="text-slate-600 dark:text-gray-400 flex items-center gap-1.5 font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Repasse
                </span>
                <div class="text-right tabular-nums">
                  <span class="font-semibold text-slate-800 dark:text-gray-300">{fmt_brl(p_rep)}</span>
                  <span class="text-[11px] text-slate-400 dark:text-gray-500 ml-1">({fmt_pct(p_rep_pct)})</span>
                </div>
              </div>
            </div>

            <!-- Barra de Distribuição Visual -->
            <div class="space-y-1">
              <div class="flex justify-between text-[10px] text-slate-500 dark:text-gray-400 font-medium">
                <span>Composição de Custos</span>
                <span class="{'text-rose-600 dark:text-rose-400 font-bold' if p_marg < 0 else 'text-emerald-700 dark:text-emerald-400 font-bold'}">Margem {fmt_pct(p_marg_pct)}</span>
              </div>
              <div class="w-full h-2 bg-slate-100 dark:bg-slate-950 rounded-full overflow-hidden flex border border-slate-200 dark:border-white/5">
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
              <span class="text-base font-bold tabular-nums">{fmt_brl(p_marg)}</span>
            </div>
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold tabular-nums shadow-sm {badge_bg}">
              {fmt_pct(p_marg_pct)}
            </span>
          </div>
        </article>"""

        swimlanes_html += f"""
    <!-- SWIMLANE: {nome.upper()} -->
    <section class="leader-swimlane space-y-4" data-leader-name="{nome.lower()}">
      <!-- Header da Raia / Líder -->
      <div class="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-white dark:bg-slate-900/90 border {header_border} shadow-sm dark:shadow-lg">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br {style['from']} {style['to']} flex items-center justify-center font-bold text-white text-base shadow-md flex-shrink-0">
            {iniciais}
          </div>
          <div>
            <div class="flex items-center gap-2.5 flex-wrap">
              <h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">{nome}</h3>
              <span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-gray-300 border border-slate-200 dark:border-white/15">
                {style['cargo']}
              </span>
              {status_badge}
              <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-gray-400">
                {len(projetos)} { "Projeto Ativo" if len(projetos) == 1 else "Projetos Ativos" }
              </span>
            </div>
            <p class="text-xs text-slate-500 dark:text-gray-400 mt-1">Consolidação executiva de contratos, rentabilidade e custos sob gestão.</p>
          </div>
        </div>

        <!-- Totais Consolidados do Líder -->
        <div class="flex items-center gap-5 bg-slate-50 dark:bg-slate-950/70 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-xs tabular-nums">
          <div>
            <span class="block text-[10px] text-slate-400 uppercase font-medium">Receita Portfólio</span>
            <span class="font-bold text-slate-900 dark:text-white text-sm">{fmt_brl(rec_tot)}</span>
          </div>
          <div class="h-8 w-px bg-slate-200 dark:bg-white/10"></div>
          <div>
            <span class="block text-[10px] text-slate-400 uppercase font-medium">Custos Consolidados</span>
            <span class="font-bold text-slate-900 dark:text-white text-sm">{fmt_brl(cust_tot)} <span class="text-[10px] text-slate-500 dark:text-gray-400 font-normal">({fmt_pct(cust_pct)})</span></span>
          </div>
          <div class="h-8 w-px bg-slate-200 dark:bg-white/10"></div>
          <div>
            <span class="block text-[10px] text-slate-400 uppercase font-medium">Margem Operacional</span>
            <span class="font-bold {'text-rose-600 dark:text-rose-400' if marg_tot < 0 else 'text-emerald-600 dark:text-emerald-400'} text-sm">{fmt_brl(marg_tot)} <span class="text-[10px] font-bold px-1.5 py-0.5 rounded {'bg-rose-100 dark:bg-rose-500/20 text-rose-800 dark:text-rose-300' if marg_tot < 0 else 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300'}">{fmt_pct(marg_pct)}</span></span>
          </div>
        </div>
      </div>

      <!-- Grade dos Cards Kanban -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {cards_html}
      </div>
    </section>
"""

    # Cálculos dos Top KPIs para o Ranking
    rec_top20 = sum(p.get("receita", 0) for p in mais_rentaveis)
    marg_top20 = sum(p.get("margem", 0) for p in mais_rentaveis)
    pct_top20 = (marg_top20 / rec_top20 * 100) if rec_top20 > 0 else 0
    deficit_bottom10 = sum(p.get("margem", 0) for p in menos_rentaveis if p.get("margem", 0) < 0)

    # Função auxiliar para gerar item do ranking Top 20
    def render_top20_item(p, rank):
        lider_nome = p.get("lider", "").strip()
        iniciais = leader_iniciais.get(lider_nome, "LP")
        av_class = leader_avatar_bg.get(lider_nome, "bg-slate-100 text-slate-700")

        if rank == 1:
            badge_pos = '<span class="flex-shrink-0 w-5 h-5 rounded bg-emerald-600 text-white font-extrabold text-[10px] flex items-center justify-center shadow-xs">1</span>'
            border_pos = "border-2 border-emerald-500/60 dark:border-emerald-500/40 hover:border-emerald-600"
            pct_badge = "bg-emerald-100 text-emerald-950 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-400 dark:border-emerald-500/40 font-black"
        elif rank <= 3:
            badge_pos = f'<span class="flex-shrink-0 w-5 h-5 rounded bg-[#1b365d] text-white font-extrabold text-[10px] flex items-center justify-center">{rank}</span>'
            border_pos = "border border-slate-300 dark:border-white/10 hover:border-blue-500"
            pct_badge = "bg-emerald-50 text-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-500/30 font-black"
        elif rank <= 10:
            badge_pos = f'<span class="flex-shrink-0 w-5 h-5 rounded bg-slate-700 text-white font-bold text-[10px] flex items-center justify-center">{rank}</span>'
            border_pos = "border border-slate-300 dark:border-white/10 hover:border-blue-500"
            pct_badge = "bg-teal-50 text-teal-900 dark:bg-teal-950/50 dark:text-teal-300 border border-teal-300 dark:border-teal-500/30 font-black"
        else:
            badge_pos = f'<span class="flex-shrink-0 w-5 h-5 rounded bg-slate-500 text-white font-bold text-[10px] flex items-center justify-center">{rank}</span>'
            border_pos = "border border-slate-300 dark:border-white/10 hover:border-blue-500"
            pct_badge = "bg-amber-50 text-amber-900 dark:bg-amber-950/50 dark:text-amber-300 border border-amber-300 dark:border-amber-500/30 font-black"

        return f"""
        <div class="ranking-item bg-white dark:bg-slate-900 rounded-lg p-2.5 {border_pos} shadow-sm hover:shadow transition-all" data-lider="{lider_nome.lower()}" data-rank="{rank}">
          <div class="flex items-center justify-between gap-1.5">
            <div class="flex items-center gap-1.5 min-w-0">
              {badge_pos}
              <span class="font-bold text-slate-950 dark:text-white text-xs truncate" title="{p['projeto']}">{p['projeto']}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0 tabular-nums">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-gray-200 border border-slate-300 dark:border-white/10"><span class="text-slate-500 dark:text-gray-400 font-medium text-[9px]">Rec:</span> {fmt_k(p['receita'])}</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] {pct_badge}">{fmt_pct(p['margemPct'])}</span>
            </div>
          </div>
          <div class="flex items-center justify-between mt-1.5 pt-1.5 border-t border-slate-200 dark:border-white/5 text-[11px]">
            <div class="flex items-center gap-1 text-slate-700 dark:text-gray-300 truncate">
              <span class="w-4 h-4 rounded-full {av_class} text-[8px] font-bold flex items-center justify-center flex-shrink-0">{iniciais}</span>
              <span class="truncate font-semibold">{lider_nome}</span>
            </div>
            <div class="text-right flex items-center gap-1 flex-shrink-0 tabular-nums">
              <span class="text-[10px] text-slate-500 dark:text-gray-400 font-medium">Margem:</span>
              <span class="font-black text-emerald-700 dark:text-emerald-400 text-xs">{fmt_brl(p['margem'])}</span>
            </div>
          </div>
        </div>"""

    # Gerar itens Coluna 1 (#1 a #10)
    top20_col1_html = "".join(render_top20_item(p, p["ranking"]) for p in mais_rentaveis[:10])

    # Gerar itens Coluna 2 (#11 a #20)
    top20_col2_html = "".join(render_top20_item(p, p["ranking"]) for p in mais_rentaveis[10:20])

    # Gerar itens Coluna 3 (Bottom 10)
    bottom10_html = ""
    for p in menos_rentaveis:
        rank = p["ranking"]
        lider_nome = p.get("lider", "").strip()
        iniciais = leader_iniciais.get(lider_nome, "LP")
        av_class = leader_avatar_bg.get(lider_nome, "bg-slate-100 text-slate-700")
        is_neg = p.get("margem", 0) < 0

        if is_neg:
            card_box = "ranking-item-danger bg-rose-50/90 dark:bg-rose-950/40 border-2 border-rose-300 dark:border-rose-500/40 hover:border-rose-400"
            badge_pos = f'<span class="flex-shrink-0 w-5 h-5 rounded bg-rose-600 text-white font-extrabold text-[10px] flex items-center justify-center shadow-xs">{rank}</span>'
            pct_badge = "bg-rose-600 text-white font-black"
            foot_label = "Prejuízo:"
            foot_val_class = "font-black text-rose-700 dark:text-rose-400"
            rec_pill = "bg-white dark:bg-slate-800 text-slate-900 dark:text-gray-200 border border-rose-300 dark:border-rose-500/30"
            border_bottom = "border-rose-200/90 dark:border-white/5"
        else:
            card_box = "bg-white dark:bg-slate-900 border border-slate-300 dark:border-white/10 hover:border-amber-400"
            badge_pos = f'<span class="flex-shrink-0 w-5 h-5 rounded bg-slate-500 text-white font-bold text-[10px] flex items-center justify-center">{rank}</span>'
            pct_badge = "bg-amber-50 dark:bg-amber-950/50 text-amber-900 dark:text-amber-300 border border-amber-300 dark:border-amber-500/30 font-black"
            foot_label = "Margem:"
            foot_val_class = "font-black text-slate-900 dark:text-gray-200"
            rec_pill = "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-gray-200 border border-slate-300 dark:border-white/10"
            border_bottom = "border-slate-200 dark:border-white/5"

        bottom10_html += f"""
        <div class="ranking-item rounded-lg p-2.5 {card_box} shadow-sm hover:shadow transition-all" data-lider="{lider_nome.lower()}" data-rank="{rank}">
          <div class="flex items-center justify-between gap-1.5">
            <div class="flex items-center gap-1.5 min-w-0">
              {badge_pos}
              <span class="font-bold text-slate-950 dark:text-white text-xs truncate" title="{p['projeto']}">{p['projeto']}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0 tabular-nums">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold {rec_pill}"><span class="text-slate-500 dark:text-gray-400 font-medium text-[9px]">Rec:</span> {fmt_k(p['receita'])}</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] {pct_badge}">{fmt_pct(p['margemPct'])}</span>
            </div>
          </div>
          <div class="flex items-center justify-between mt-1.5 pt-1.5 border-t {border_bottom} text-[11px]">
            <div class="flex items-center gap-1 text-slate-700 dark:text-gray-300 truncate">
              <span class="w-4 h-4 rounded-full {av_class} text-[8px] font-bold flex items-center justify-center flex-shrink-0">{iniciais}</span>
              <span class="truncate font-semibold">{lider_nome}</span>
            </div>
            <div class="text-right flex items-center gap-1 flex-shrink-0 tabular-nums">
              <span class="text-[10px] text-slate-500 dark:text-gray-400 font-medium">{foot_label}</span>
              <span class="{foot_val_class} text-xs">{fmt_brl(p['margem'])}</span>
            </div>
          </div>
        </div>"""

    # Formatação compacta para tabela de Metas (estilo 300K, 1,5M, 10,65M)
    def fmt_meta_compact(val):
        if val is None or val == 0:
            return "0"
        abs_v = abs(val)
        if abs_v >= 1e6:
            # Ex: 1,5M, 8,0M, 3,5M, 1,7M, 10,65M, 15,0M
            if (abs_v / 1e6) >= 10:
                s = f"{abs_v / 1e6:.2f}".rstrip('0').rstrip('.') if len(f"{abs_v / 1e6:.2f}".split('.')[1].rstrip('0')) > 1 else f"{abs_v / 1e6:.1f}"
            else:
                s = f"{abs_v / 1e6:.2f}".rstrip('0').rstrip('.') if len(f"{abs_v / 1e6:.2f}".split('.')[1].rstrip('0')) > 1 else f"{abs_v / 1e6:.1f}"
            return f"{s}M".replace(".", ",")
        elif abs_v >= 1e3:
            s = f"{abs_v / 1e3:.1f}" if (abs_v / 1e3) % 1 != 0 else f"{abs_v / 1e3:.0f}"
            return f"{s}K".replace(".", ",")
        else:
            return f"{abs_v:,.0f}".replace(".", ",")

    def get_pct_float(pct_str):
        if not pct_str or pct_str == "—":
            return 0.0
        clean = pct_str.replace('%', '').replace(',', '.').strip()
        try:
            return float(clean)
        except:
            return 0.0

    # Gerar Tabela: Metas por Área (Conforme modelo de inspiração)
    metas_rows_html = ""
    for m in metas_areas:
        is_total = m.get("isTotal", False)
        area_nome = m["area"].strip()
        area_upper = area_nome.upper()
        
        meta_val = m.get("meta", 0)
        real_val = m.get("realizado", 0)
        falta_val = m.get("falta", 0)
        
        meta_str = fmt_meta_compact(meta_val)
        real_str = fmt_meta_compact(real_val)
        falta_str = fmt_meta_compact(falta_val)
        
        atingido_str = m.get("atingidoPct", "—")
        falta_pct_str = m.get("faltaPct", "—")
        pct_num = get_pct_float(atingido_str)
        pct_clamped = min(100.0, max(0.0, pct_num))

        if is_total:
            metas_rows_html += f"""
        <tr class="bg-[#fef3c7] dark:bg-amber-950/60 border-t-2 border-amber-400 font-black">
          <td class="py-3.5 px-5 font-black text-slate-950 dark:text-amber-200 text-sm sm:text-base uppercase tracking-tight">
            META GERAL 2026
          </td>
          <td class="py-3.5 px-4 text-center font-black text-slate-950 dark:text-white tabular-nums text-sm sm:text-base">
            {meta_str}
          </td>
          <td class="py-3.5 px-4 text-center font-black text-slate-950 dark:text-white tabular-nums text-sm sm:text-base">
            {real_str}
          </td>
          <td class="py-3.5 px-5 text-left">
            <div class="flex items-center gap-3">
              <div class="w-24 sm:w-28 h-3.5 bg-amber-300/80 dark:bg-amber-950 rounded-full overflow-hidden p-0.5 border border-amber-500/40 flex-shrink-0">
                <div class="h-full rounded-full bg-gradient-to-r from-amber-600 to-amber-500 shadow-sm" style="width: {pct_clamped}%"></div>
              </div>
              <span class="font-black text-slate-950 dark:text-amber-200 tabular-nums text-xs sm:text-sm">{atingido_str}</span>
            </div>
          </td>
          <td class="py-3.5 px-4 text-center font-black text-slate-950 dark:text-white tabular-nums text-sm sm:text-base">
            {falta_str}
          </td>
          <td class="py-3.5 px-4 text-center font-black text-slate-950 dark:text-white tabular-nums text-sm sm:text-base">
            {falta_pct_str}
          </td>
          <td class="py-3.5 px-5 text-center">
            <span class="inline-flex items-center justify-center px-3.5 py-1 rounded-full text-xs font-black bg-amber-400 text-amber-950 border border-amber-500 shadow-sm">
              EM ANDAMENTO
            </span>
          </td>
        </tr>"""
        else:
            if "EDUCA" in area_upper:
                prog_bar_html = f"""
            <div class="flex items-center gap-3">
              <div class="w-24 sm:w-28 h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-200 dark:border-white/10 flex-shrink-0">
                <div class="h-full rounded-full bg-transparent" style="width: 0%"></div>
              </div>
              <span class="font-bold text-slate-400 dark:text-gray-500 text-xs sm:text-sm">—</span>
            </div>"""
                situacao_html = '<span class="inline-flex items-center justify-center px-3.5 py-1 rounded-full text-[11px] font-bold bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-600">SEM META</span>'
            else:
                prog_bar_html = f"""
            <div class="flex items-center gap-3">
              <div class="w-24 sm:w-28 h-3.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-200 dark:border-white/10 flex-shrink-0">
                <div class="h-full rounded-full bg-gradient-to-r from-sky-400 to-blue-600 shadow-sm" style="width: {pct_clamped}%"></div>
              </div>
              <span class="font-bold text-slate-800 dark:text-gray-200 tabular-nums text-xs sm:text-sm">{atingido_str}</span>
            </div>"""
                situacao_html = '<span class="inline-flex items-center justify-center px-3.5 py-1 rounded-full text-[11px] font-extrabold bg-[#fef3c7] dark:bg-amber-500/20 text-[#92400e] dark:text-amber-300 border border-[#fcd34d] dark:border-amber-500/40 shadow-xs">EM ANDAMENTO</span>'

            metas_rows_html += f"""
        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors border-b border-slate-100 dark:border-white/5">
          <td class="py-3 px-5 font-extrabold text-slate-900 dark:text-white text-xs sm:text-sm uppercase tracking-wide">
            {area_upper}
          </td>
          <td class="py-3 px-4 text-center font-bold text-slate-800 dark:text-gray-200 tabular-nums text-xs sm:text-sm">
            {meta_str}
          </td>
          <td class="py-3 px-4 text-center font-bold text-slate-800 dark:text-gray-200 tabular-nums text-xs sm:text-sm">
            {real_str}
          </td>
          <td class="py-3 px-5 text-left">
            {prog_bar_html}
          </td>
          <td class="py-3 px-4 text-center font-bold text-slate-800 dark:text-gray-200 tabular-nums text-xs sm:text-sm">
            {falta_str}
          </td>
          <td class="py-3 px-4 text-center font-bold text-slate-800 dark:text-gray-200 tabular-nums text-xs sm:text-sm">
            {falta_pct_str}
          </td>
          <td class="py-3 px-5 text-center">
            {situacao_html}
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>Painel Financeiro por Líder de Projeto | NNÓS Controladoria &amp; Gestão Financeira</title>

  <!-- Google Fonts: Plus Jakarta Sans (Sem números de máquina de escrever) -->
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
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
    (function() {{
      const saved = localStorage.getItem('nnos_theme') || 'dark';
      if (saved === 'light') {{
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }} else {{
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
      }}
    }})();
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
    /* Suporte a números tabulares limpos e amigáveis */
    .tabular-nums {{
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.01em;
    }}
    html {{ scroll-behavior: smooth; }}

    /* Custom scrollbars */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: rgba(15, 23, 42, 0.6);
    }}
    ::-webkit-scrollbar-thumb {{
      background: rgba(148, 163, 184, 0.4);
      border-radius: 9999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: rgba(148, 163, 184, 0.7);
    }}

    /* Adaptações do Tema Claro */
    html.light body {{
      background-color: #f1f5f9 !important;
      color: #0f172a !important;
    }}
    html.light .bg-slate-950,
    html.light .bg-slate-900 {{
      background-color: #ffffff !important;
      color: #0f172a !important;
    }}
    html.light [class*="border-white"] {{
      border-color: rgba(226, 232, 240, 0.9) !important;
    }}
    html.light .text-gray-300,
    html.light .text-gray-400 {{
      color: #64748b !important;
    }}
    html.light header {{
      background: #ffffff !important;
      border-bottom: 1px solid #e2e8f0 !important;
    }}
    html.light nav[class*="bg-slate-950"] {{
      background-color: rgba(255, 255, 255, 0.95) !important;
      border-bottom: 1px solid #e2e8f0 !important;
    }}
    html.light [class*="bg-slate-900"] {{
      background-color: #f8fafc !important;
      border-bottom: 1px solid #e2e8f0 !important;
    }}
    html.light [class*="bg-slate-950"] {{
      background-color: #f1f5f9 !important;
      border-color: #e2e8f0 !important;
    }}
    html.light .project-card {{
      background-color: #ffffff !important;
      border-color: #e2e8f0 !important;
      box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.05) !important;
    }}
    html.light .project-card:hover {{
      box-shadow: 0 10px 25px -4px rgba(0, 0, 0, 0.1) !important;
    }}

    /* 🎯 Regra de Ouro de Contraste: Barra/Badge/Fundo escuro SEMPRE tem fonte clara (branca) */
    html.light .bg-\[\#1b365d\],
    html.light .bg-\[\#1b365d\] *,
    html.light .bg-\[\#c24141\],
    html.light .bg-\[\#c24141\] *,
    html.light .bg-\[\#00223a\],
    html.light .bg-\[\#00223a\] *,
    html.light .bg-\[\#003865\],
    html.light .bg-\[\#003865\] *,
    html.light .bg-\[\#002b49\],
    html.light .bg-\[\#002b49\] *,
    html.light .bg-blue-600,
    html.light .bg-blue-600 *,
    html.light .bg-rose-600,
    html.light .bg-rose-600 *,
    html.light .bg-emerald-600,
    html.light .bg-emerald-600 *,
    html.light .bg-slate-700,
    html.light .bg-slate-700 *,
    html.light .bg-slate-500,
    html.light .bg-slate-500 *,
    html.light thead tr,
    html.light thead tr * {{
      color: #ffffff !important;
    }}

    /* Estilização dos cards do ranking no modo claro */
    html.light .ranking-item {{
      background-color: #ffffff !important;
      border-color: #cbd5e1 !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }}
    html.light .ranking-item-danger {{
      background-color: #fff1f2 !important;
      border-color: #fecdd3 !important;
    }}
    html.light #ranking-col-1,
    html.light #ranking-col-2,
    html.light #ranking-col-3 {{
      background-color: #f8fafc !important;
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen antialiased selection:bg-brand-500 selection:text-white transition-colors duration-200">

<!-- ═══════════ HEADER ═══════════ -->
<header class="relative overflow-hidden border-b border-white/10 bg-slate-950 transition-colors duration-200">
  <div class="absolute inset-0 z-0 pointer-events-none">
    <div class="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-brand-600/15 via-purple-600/10 to-transparent"></div>
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-brand-500/20 rounded-full blur-3xl"></div>
  </div>
  <div class="max-w-[1720px] mx-auto px-6 py-6 relative z-10">
    <div class="flex items-center justify-between gap-5 flex-wrap">
      <!-- Lado Esquerdo: Logo e Títulos -->
      <div class="flex items-center gap-5 flex-wrap">
        <img alt="NNÓS Logo" class="h-12 sm:h-14 w-auto object-contain flex-shrink-0 opacity-95" src="assets/logo-nnos.png"/>
        <div class="h-10 w-[1px] bg-slate-200 dark:bg-white/20 hidden sm:block"></div>
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">Painel Financeiro por Líder de Projeto</h1>
          </div>
          <p class="text-xs text-slate-500 dark:text-gray-400 mt-0.5">Controle de rentabilidade, centros de custos e margem operacional por contrato corporativo</p>
        </div>
      </div>
    </div>
  </div>
</header>

<!-- ═══════════ NAVBAR INTEGRADA ═══════════ -->
<nav class="sticky top-0 z-50 bg-white/95 dark:bg-slate-950/95 backdrop-blur-md border-b border-slate-200 dark:border-white/10 shadow-md transition-colors duration-200">
  <!-- Linha 1: Outros Relatórios e Ações Globais -->
  <div class="bg-slate-100/90 dark:bg-slate-900/90 px-6 py-1.5 border-b border-slate-200 dark:border-white/10">
    <div class="max-w-[1720px] mx-auto flex items-center justify-between gap-3 flex-wrap">
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
        <a href="booking.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-500/20 hover:bg-emerald-200 dark:hover:bg-emerald-500/30 border border-emerald-300 dark:border-emerald-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">trending_up</span> Performance Projetos
        </a>
        <a href="prospeccao.html" class="px-3 py-1.5 rounded-lg text-xs font-bold text-purple-700 dark:text-purple-300 bg-purple-100 dark:bg-purple-500/20 hover:bg-purple-200 dark:hover:bg-purple-500/30 border border-purple-300 dark:border-purple-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">explore</span> Prospecção
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
  <div class="max-w-[1720px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center gap-1.5 py-2 min-w-max">
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#resumo"><span class="material-symbols-outlined text-sm text-sky-500">monitoring</span> Resumo Geral</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#lideres"><span class="material-symbols-outlined text-sm text-sky-500">groups</span> Painel dos Líderes</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#ranking-rentabilidade"><span class="material-symbols-outlined text-sm text-emerald-500">stars</span> Ranking de Rentabilidade (Top 20 / Bottom 10)</a>
      <a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center gap-1.5" href="#metas"><span class="material-symbols-outlined text-sm text-amber-500">flag</span> Metas por Área</a>
    </div>
  </div>
</nav>

<!-- ═══════════ CONTEÚDO PRINCIPAL ═══════════ -->
<main class="max-w-[1720px] w-full mx-auto px-6 py-6 space-y-8">

  <!-- ──────── MACRO METRICS OVERVIEW ──────── -->
  <section id="resumo" class="scroll-mt-28 space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Métrica 1: Receita Bruta -->
      <div class="bg-white dark:bg-slate-900/90 border border-slate-200/90 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-lg relative overflow-hidden group">
        <div class="flex items-center justify-between text-slate-500 dark:text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Receita Bruta Consolidada</span>
          <div class="w-8 h-8 rounded-lg bg-sky-50 dark:bg-sky-500/20 text-sky-600 dark:text-sky-400 flex items-center justify-center font-bold text-sm">$</div>
        </div>
        <div class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white tabular-nums">
          {fmt_brl(macro.get('receita', 0))}
        </div>
        <p class="text-xs text-slate-400 dark:text-gray-400 mt-1.5">Soma de todos os 44 contratos sob gestão</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-sky-500 to-transparent"></div>
      </div>

      <!-- Métrica 2: Custos Operacionais -->
      <div class="bg-white dark:bg-slate-900/90 border border-slate-200/90 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-lg relative overflow-hidden group">
        <div class="flex items-center justify-between text-slate-500 dark:text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Custos Operacionais</span>
          <div class="w-8 h-8 rounded-lg bg-rose-50 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold text-sm">
            <span class="material-symbols-outlined text-base">trending_down</span>
          </div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white tabular-nums">{fmt_brl(macro.get('custos', 0))}</span>
          <span class="text-xs font-bold text-rose-600 dark:text-rose-400 tabular-nums">{fmt_pct(macro.get('custosPct', 0))}</span>
        </div>
        <p class="text-xs text-slate-400 dark:text-gray-400 mt-1.5">Custos diretos e contratações executadas</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-rose-500 to-transparent"></div>
      </div>

      <!-- Métrica 3: Margem Líquida Realizada -->
      <div class="bg-white dark:bg-slate-900/90 border border-slate-200/90 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-lg relative overflow-hidden group">
        <div class="flex items-center justify-between text-slate-500 dark:text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Margem Líquida Realizada</span>
          <div class="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-sm">%</div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400 tabular-nums">{fmt_brl(macro.get('margem', 0))}</span>
          <span class="text-xs font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-300 dark:border-emerald-500/30 tabular-nums">{fmt_pct(macro.get('margemPct', 0))}</span>
        </div>
        <p class="text-xs text-slate-400 dark:text-gray-400 mt-1.5">Resultado operacional livre após despesas e impostos</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-emerald-500 to-transparent"></div>
      </div>

      <!-- Métrica 4: Impostos & Logística -->
      <div class="bg-white dark:bg-slate-900/90 border border-slate-200/90 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-lg relative overflow-hidden group">
        <div class="flex items-center justify-between text-slate-500 dark:text-gray-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Impostos &amp; Logística</span>
          <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-sm">
            <span class="material-symbols-outlined text-base">receipt_long</span>
          </div>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white tabular-nums">{fmt_brl(macro.get('impostos', 0) + macro.get('logistica', 0))}</span>
          <span class="text-xs font-bold text-slate-500 dark:text-gray-400 tabular-nums">{fmt_pct(macro.get('impostosPct', 12.25) + macro.get('logisticaPct', 0))}</span>
        </div>
        <p class="text-xs text-slate-400 dark:text-gray-400 mt-1.5">Impostos: {fmt_pct(macro.get('impostosPct', 12.25))} | Logística: {fmt_pct(macro.get('logisticaPct', 0))}</p>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-indigo-500 to-transparent"></div>
      </div>
    </div>
  </section>

  <!-- ──────── FILTROS POR LÍDER E BUSCA ──────── -->
  <section class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-slate-900/90 border border-slate-200/90 dark:border-white/10 shadow-sm dark:shadow-lg">
    <!-- Filtros de Líderes -->
    <div class="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
      <span class="text-xs font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap mr-1">Filtrar Líder:</span>
      <button onclick="filtrarLider('todos')" data-filter="todos" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-sky-500 text-white border border-sky-400 transition-all cursor-pointer">
        Todos (7)
      </button>
      <button onclick="filtrarLider('beatriz picorelli')" data-filter="beatriz picorelli" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Beatriz
      </button>
      <button onclick="filtrarLider('caroline amieva')" data-filter="caroline amieva" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Caroline
      </button>
      <button onclick="filtrarLider('jefferson souza')" data-filter="jefferson souza" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Jefferson
      </button>
      <button onclick="filtrarLider('joice lage')" data-filter="joice lage" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Joice
      </button>
      <button onclick="filtrarLider('leonardo campos')" data-filter="leonardo campos" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Leonardo
      </button>
      <button onclick="filtrarLider('vinicius souza')" data-filter="vinicius souza" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Vinicius
      </button>
      <button onclick="filtrarLider('fábio canassa')" data-filter="fábio canassa" class="filter-btn px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer">
        Fábio
      </button>
    </div>

    <!-- Campo de Busca de Projetos -->
    <div class="relative min-w-[240px]">
      <span class="material-symbols-outlined text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 text-sm">search</span>
      <input id="searchProject" oninput="buscarProjetos()" type="text" placeholder="Filtrar contrato ou líder..." class="w-full pl-9 pr-3 py-2 text-xs bg-slate-100 dark:bg-slate-950/70 border border-slate-200 dark:border-white/10 rounded-xl text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/30 transition-all"/>
    </div>
  </section>

  <!-- ──────── RAIAS KANBAN DOS LÍDERES ──────── -->
  <section id="lideres" class="scroll-mt-28 space-y-10">
    {swimlanes_html}
  </section>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- 🏆 PAINEL FINANCEIRO - RANKING DE RENTABILIDADE DE PROJETOS        -->
  <!-- Layout Balanceado em 3 Colunas: Top 1-10, Top 11-20 e Bottom 10    -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <section id="ranking-rentabilidade" class="scroll-mt-28 space-y-4 pt-4 border-t border-slate-200 dark:border-white/10">

    <!-- Header da Seção de Rankings -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20 flex-shrink-0">
          <span class="material-symbols-outlined text-2xl">leaderboard</span>
        </div>
        <div>
          <h2 class="text-lg sm:text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">Painel Financeiro - Ranking de Rentabilidade</h2>
          <p class="text-xs text-slate-500 dark:text-gray-400">Visão consolidada Top 20 Mais Rentáveis &amp; Bottom 10 por centro de custo</p>
        </div>
      </div>
      <div class="inline-flex items-center gap-2">
        <span id="rankingStatusBadge" class="px-3 py-1 rounded-lg text-xs font-bold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-500/30">
          Top 20 Rentáveis &amp; Bottom 10
        </span>
      </div>
    </div>

    <!-- Top KPIs do Ranking (Compact Bar) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <!-- Card KPI 1: Receita Top 20 -->
      <div class="bg-white dark:bg-slate-900 rounded-xl px-4 py-3 border border-slate-200/90 dark:border-white/10 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-gray-400 block">Receita Top 20 Rentáveis</span>
          <div class="text-lg font-black text-slate-900 dark:text-white tabular-nums">{fmt_brl(rec_top20)}</div>
          <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">20 projetos consolidados</span>
        </div>
        <div class="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-xs shadow-inner">$</div>
      </div>

      <!-- Card KPI 2: Margem Nominal Top 20 -->
      <div class="bg-white dark:bg-slate-900 rounded-xl px-4 py-3 border border-slate-200/90 dark:border-white/10 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-gray-400 block">Margem Nominal Top 20</span>
          <div class="text-lg font-black text-emerald-600 dark:text-emerald-400 tabular-nums">{fmt_brl(marg_top20)}</div>
          <span class="text-[10px] text-slate-500 dark:text-gray-400 font-medium">Média consolidada: <strong class="text-slate-800 dark:text-gray-200 tabular-nums">{fmt_pct(pct_top20)}</strong></span>
        </div>
        <div class="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xs shadow-inner">%</div>
      </div>

      <!-- Card KPI 3: Déficit Bottom 10 -->
      <div class="bg-white dark:bg-slate-900 rounded-xl px-4 py-3 border border-rose-200 dark:border-rose-500/40 shadow-sm flex items-center justify-between bg-gradient-to-r from-white to-rose-50/30 dark:from-slate-900 dark:to-rose-950/20">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 block">Déficit Bottom 10 (Menos Rentáveis)</span>
          <div class="text-lg font-black text-rose-600 dark:text-rose-400 tabular-nums">{fmt_brl(deficit_bottom10)}</div>
          <span class="text-[10px] text-rose-600/90 dark:text-rose-400 font-medium">Impacto: <strong>NNOS Academy</strong> e <strong>Campus BH</strong></span>
        </div>
        <div class="w-8 h-8 rounded-lg bg-rose-50 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold text-xs shadow-inner">
          <span class="material-symbols-outlined text-base">arrow_downward</span>
        </div>
      </div>

      <!-- Card KPI 4: Critério de Ordenação -->
      <div class="bg-white dark:bg-slate-900 rounded-xl px-4 py-3 border border-slate-200/90 dark:border-white/10 shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-gray-400 block">Critério de Ordenação</span>
          <div class="text-sm font-extrabold text-slate-900 dark:text-white leading-snug">Margem Nominal Líquida</div>
          <span class="text-[10px] text-slate-500 dark:text-gray-400 font-medium">Ordenação prioritária em moeda (<strong class="text-slate-700 dark:text-gray-300">R$</strong>)</span>
        </div>
        <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs shadow-inner">
          <span class="material-symbols-outlined text-base">receipt_long</span>
        </div>
      </div>
    </div>

    <!-- Grade em 3 Colunas dos Rankings -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">

      <!-- ======================================================== -->
      <!-- COLUNA 1: TOP 20 MAIS RENTÁVEIS (POSIÇÕES 1 A 10)         -->
      <!-- ======================================================== -->
      <div class="flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-300 dark:border-white/10 shadow-sm overflow-hidden">
        <div class="bg-[#1b365d] px-3.5 py-2.5 flex items-center justify-between text-white border-b border-[#142948]">
          <div class="flex items-center gap-2">
            <span class="flex h-5 w-5 items-center justify-center rounded bg-emerald-500/20 text-[10px] font-extrabold text-emerald-300 border border-emerald-400/30">
              01
            </span>
            <h3 class="text-xs font-bold tracking-tight uppercase">Top 20 • Líderes (1 a 10)</h3>
          </div>
          <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 tabular-nums">
            Top 1-10
          </span>
        </div>
        <div id="ranking-col-1" class="p-2.5 space-y-2 flex-1 flex flex-col justify-start bg-slate-100/90 dark:bg-slate-950/40">
          {top20_col1_html}
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- COLUNA 2: TOP 20 MAIS RENTÁVEIS (POSIÇÕES 11 A 20)        -->
      <!-- ======================================================== -->
      <div class="flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-300 dark:border-white/10 shadow-sm overflow-hidden">
        <div class="bg-[#1b365d] px-3.5 py-2.5 flex items-center justify-between text-white border-b border-[#142948]">
          <div class="flex items-center gap-2">
            <span class="flex h-5 w-5 items-center justify-center rounded bg-emerald-500/20 text-[10px] font-extrabold text-emerald-300 border border-emerald-400/30">
              02
            </span>
            <h3 class="text-xs font-bold tracking-tight uppercase">Top 20 • Sequência (11 a 20)</h3>
          </div>
          <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 tabular-nums">
            Top 11-20
          </span>
        </div>
        <div id="ranking-col-2" class="p-2.5 space-y-2 flex-1 flex flex-col justify-start bg-slate-100/90 dark:bg-slate-950/40">
          {top20_col2_html}
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- COLUNA 3: 10 PROJETOS MENOS RENTÁVEIS (BOTTOM 10)         -->
      <!-- ======================================================== -->
      <div class="flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-300 dark:border-white/10 shadow-sm overflow-hidden">
        <div class="bg-[#c24141] px-3.5 py-2.5 flex items-center justify-between text-white border-b border-[#991b1b]">
          <div class="flex items-center gap-2">
            <span class="flex h-5 w-5 items-center justify-center rounded bg-white/20 text-[10px] font-extrabold text-white border border-white/20">
              10
            </span>
            <h3 class="text-xs font-bold tracking-tight uppercase">10 Projetos Menos Rentáveis</h3>
          </div>
          <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-white/20 text-white border border-white/20">
            Atenção Diretoria
          </span>
        </div>
        <div id="ranking-col-3" class="p-2.5 space-y-2 flex-1 flex flex-col justify-start bg-slate-100/90 dark:bg-slate-950/40">
          {bottom10_html}
        </div>
      </div>

    </div>
  </section>

  <!-- ──────── CONTROLE DE METAS POR ÁREA 2026 ──────── -->
  <section id="metas" class="scroll-mt-28 space-y-4 pt-6 border-t border-slate-200 dark:border-white/10">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3.5">
        <div class="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20 flex-shrink-0">
          <span class="material-symbols-outlined text-2xl">leaderboard</span>
        </div>
        <div>
          <h2 class="text-xl sm:text-2xl font-black tracking-tight text-slate-900 dark:text-white uppercase">
            CONTROLE DE METAS POR ÁREA <span class="text-[#b45309] dark:text-amber-500 font-black">| 2026</span>
          </h2>
          <p class="text-xs text-slate-500 dark:text-gray-400 mt-0.5">Acompanhamento consolidado entre a meta orçada e a receita realizada por unidade de negócio.</p>
        </div>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-500/20 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-500/40">
        Exercício 2026
      </span>
    </div>

    <!-- Tabela Estilizada conforme Modelo -->
    <div class="overflow-x-auto rounded-2xl border border-slate-200/90 dark:border-white/10 bg-white dark:bg-slate-900 shadow-md">
      <table class="w-full text-left border-collapse text-xs sm:text-sm">
        <thead>
          <tr class="bg-gradient-to-r from-[#00223a] via-[#003865] to-[#00223a] text-white font-black text-[11px] sm:text-xs uppercase tracking-wider">
            <th class="py-3 px-5 text-left">ÁREA</th>
            <th class="py-3 px-4 text-center">META</th>
            <th class="py-3 px-4 text-center">REALIZADO</th>
            <th class="py-3 px-5 text-left min-w-[190px]">ATINGIDO</th>
            <th class="py-3 px-4 text-center">FALTA</th>
            <th class="py-3 px-4 text-center">FALTA %</th>
            <th class="py-3 px-5 text-center">SITUAÇÃO</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-white/5">
          {metas_rows_html}
        </tbody>
      </table>
    </div>
  </section>

</main>

<!-- ═══════════ FOOTER ═══════════ -->
<footer class="bg-slate-950 border-t border-white/10 py-6 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1720px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS" class="h-11 md:h-12 w-auto object-contain" src="assets/logo-nnos-horizontal.png"/>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Setembro de 2026</div>
  </div>
</footer>

<!-- ═══════════ SCRIPTS INTERATIVOS ═══════════ -->
<script>
  // 🌓 Toggle Dark / Light Mode Global
  function applyTheme(theme) {{
    const html = document.documentElement;
    const icons = document.querySelectorAll('.theme-icon');
    const buttons = document.querySelectorAll('.theme-toggle-btn');
    if (theme === 'light') {{
      html.classList.remove('dark');
      html.classList.add('light');
      icons.forEach(ic => ic.textContent = 'dark_mode');
      buttons.forEach(btn => btn.setAttribute('title', 'Alternar para Modo Escuro'));
      localStorage.setItem('nnos_theme', 'light');
    }} else {{
      html.classList.remove('light');
      html.classList.add('dark');
      icons.forEach(ic => ic.textContent = 'light_mode');
      buttons.forEach(btn => btn.setAttribute('title', 'Alternar para Modo Claro'));
      localStorage.setItem('nnos_theme', 'dark');
    }}
  }}

  function toggleTheme() {{
    const isLight = document.documentElement.classList.contains('light');
    applyTheme(isLight ? 'dark' : 'light');
  }}

  // Inicializar tema com base na preferência salva
  (function() {{
    const saved = localStorage.getItem('nnos_theme') || 'dark';
    applyTheme(saved);
  }})();

  // 🔍 Filtro por Líder (Raias Kanban + Ranking de Rentabilidade)
  function filtrarLider(lider) {{
    const isTodos = (lider === 'todos');

    // 1. Atualizar visual dos botões de filtro
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      const filterVal = btn.getAttribute('data-filter');
      if (filterVal === lider) {{
        btn.classList.add('bg-sky-500', 'text-white', 'border-sky-400', 'shadow-sm');
        btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-gray-300');
      }} else {{
        btn.classList.remove('bg-sky-500', 'text-white', 'border-sky-400', 'shadow-sm');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-gray-300');
      }}
    }});

    // 2. Filtrar raias Kanban dos Líderes
    document.querySelectorAll('.leader-swimlane').forEach(lane => {{
      const laneName = lane.getAttribute('data-leader-name');
      if (isTodos || laneName === lider) {{
        lane.style.display = 'block';
      }} else {{
        lane.style.display = 'none';
      }}
    }});

    // 3. Filtrar e Destacar no Painel de Ranking de Rentabilidade (3 Colunas)
    let totalVisiveisRanking = 0;
    const colunas = ['ranking-col-1', 'ranking-col-2', 'ranking-col-3'];

    colunas.forEach(colId => {{
      const colEl = document.getElementById(colId);
      if (!colEl) return;
      const items = colEl.querySelectorAll('.ranking-item');
      let visiveisNaColuna = 0;

      items.forEach(item => {{
        const itemLider = (item.getAttribute('data-lider') || '').toLowerCase();
        if (isTodos || itemLider === lider) {{
          item.style.display = 'block';
          visiveisNaColuna++;
          totalVisiveisRanking++;
          if (!isTodos) {{
            item.classList.add('ring-2', 'ring-sky-500', 'shadow-md');
          }} else {{
            item.classList.remove('ring-2', 'ring-sky-500', 'shadow-md');
          }}
        }} else {{
          item.style.display = 'none';
          item.classList.remove('ring-2', 'ring-sky-500', 'shadow-md');
        }}
      }});

      // Exibir aviso se este líder não tiver projetos nesta coluna
      let emptyMsg = colEl.querySelector('.ranking-empty-msg');
      if (visiveisNaColuna === 0 && !isTodos) {{
        if (!emptyMsg) {{
          emptyMsg = document.createElement('div');
          emptyMsg.className = 'ranking-empty-msg p-4 text-center text-xs text-slate-500 dark:text-gray-400 bg-white/60 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-300 dark:border-white/10 my-auto flex flex-col items-center justify-center gap-1';
          emptyMsg.innerHTML = '<span class="material-symbols-outlined text-lg opacity-60">info</span><span>Nenhum projeto deste líder nesta faixa</span>';
          colEl.appendChild(emptyMsg);
        }}
        emptyMsg.style.display = 'flex';
      }} else if (emptyMsg) {{
        emptyMsg.style.display = 'none';
      }}
    }});

    // 4. Atualizar badge de status do ranking
    const rankingBadge = document.getElementById('rankingStatusBadge');
    if (rankingBadge) {{
      if (isTodos) {{
        rankingBadge.textContent = 'Top 20 Rentáveis & Bottom 10';
        rankingBadge.className = 'px-3 py-1 rounded-lg text-xs font-bold bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-500/30';
      }} else {{
        const nomeFormatado = lider.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        rankingBadge.textContent = `Projetos de ${{nomeFormatado}} (${{totalVisiveisRanking}} no ranking)`;
        rankingBadge.className = 'px-3 py-1 rounded-lg text-xs font-extrabold bg-sky-500 text-white border border-sky-400 shadow-sm';
      }}
    }}
  }}

  // 🔎 Busca de Contratos
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
