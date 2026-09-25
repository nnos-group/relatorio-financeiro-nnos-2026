import os
import glob
import csv
import json
import re
from collections import defaultdict

def run():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    uva_dir = os.path.abspath(os.path.join(repo_dir, "..", "UVA"))
    
    # 1. Procurar CSV do UVA mais recente (na pasta UVA ou na pasta do repo)
    candidates = []
    if os.path.exists(uva_dir):
        candidates.extend(glob.glob(os.path.join(uva_dir, "Relat*UVA*.csv")))
    candidates.extend(glob.glob(os.path.join(repo_dir, "Relat*UVA*.csv")))
    
    if not candidates:
        print("Aviso: Nenhum arquivo CSV do UVA encontrado.")
        return

    # Ordenar por data de modificação decrescente
    candidates.sort(key=os.path.getmtime, reverse=True)
    uva_csv = candidates[0]
    print(f"Processando base UVA: {os.path.basename(uva_csv)}")
    
    # Detectar o mês de referência do nome do arquivo (ex: SET-26 ou AGO-26)
    mes_ref = "SET/2026"
    if "SET" in os.path.basename(uva_csv).upper():
        mes_ref = "SET/2026"
    elif "AGO" in os.path.basename(uva_csv).upper():
        mes_ref = "AGO/2026"
    elif "OUT" in os.path.basename(uva_csv).upper():
        mes_ref = "OUT/2026"

    # 2. Ler e agregar dados do CSV
    lancamentos = []
    fornecedores = defaultdict(float)
    categorias = defaultdict(float)
    formas_pag = defaultdict(float)
    mensal_quit = defaultdict(float)
    mensal_aberto = defaultdict(float)

    imobilizado_total = 0.0
    imobilizado_quit = 0.0
    imobilizado_aberto = 0.0
    imob_titulos = 0
    imob_forn = defaultdict(float)

    def parse_val(s):
        if not s: return 0.0
        return float(s.replace('.', '').replace(',', '.'))

    with open(uva_csv, 'r', encoding='latin1') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        for r in reader:
            if len(r) >= 6:
                forn = r[0].strip()
                dt_comp = r[1].strip()
                dt_venc = r[2].strip()
                desc = r[3].strip()
                sit = r[4].strip().lower()
                val = parse_val(r[5])
                forma = r[6].strip() if len(r) > 6 else ''
                cat = r[8].strip() if len(r) > 8 else ''
                
                is_quit = 'quit' in sit or 'pago' in sit or 'liquid' in sit
                lancamentos.append({
                    "forn": forn, "val": val, "is_quit": is_quit,
                    "dt_venc": dt_venc, "cat": cat, "forma": forma, "desc": desc
                })
                fornecedores[forn] += val
                if cat: categorias[cat] += val
                if forma: formas_pag[forma] += val
                
                # Mês de vencimento MM/YYYY
                try:
                    parts = dt_venc.split('/')
                    m_key = f"{int(parts[1]):02d}/{parts[2]}"
                except:
                    m_key = "Outro"
                    
                if is_quit:
                    mensal_quit[m_key] += val
                else:
                    mensal_aberto[m_key] += val
                    
                # Classificação de Imobilizado & Obras
                cat_l = cat.lower()
                desc_l = desc.lower()
                forn_l = forn.lower()
                is_imob = (
                    'predial' in cat_l or 'reforma' in desc_l or 'imobiliz' in cat_l or 
                    'móveis' in cat_l or 'moveis' in cat_l or 'instalações' in cat_l or 
                    'instalacoes' in cat_l or 'máquinas' in cat_l or 'maquinas' in cat_l or 
                    'equipamentos' in cat_l or 'mr engenharia' in forn_l or 'othon' in forn_l or 
                    'noronha' in forn_l or 'thermobras' in forn_l or 'aco inox' in forn_l or 
                    'deflex' in forn_l or 'andrades' in forn_l
                )
                if is_imob:
                    imobilizado_total += val
                    imob_titulos += 1
                    imob_forn[forn] += val
                    if is_quit: imobilizado_quit += val
                    else: imobilizado_aberto += val

    tot_geral = sum(x['val'] for x in lancamentos)
    tot_quit = sum(x['val'] for x in lancamentos if x['is_quit'])
    tot_aberto = tot_geral - tot_quit
    pct_quit = (tot_quit / tot_geral * 100) if tot_geral > 0 else 0
    pct_aberto = (tot_aberto / tot_geral * 100) if tot_geral > 0 else 0

    num_lanc = len(lancamentos)
    num_forn = len(fornecedores)
    ticket_medio = tot_geral / num_lanc if num_lanc > 0 else 0

    fmt_br = lambda v: f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    print(f"Totais calculados UVA:")
    print(f"  Total: {fmt_br(tot_geral)}")
    print(f"  Quitado: {fmt_br(tot_quit)} ({pct_quit:.2f}%)")
    print(f"  A Vencer: {fmt_br(tot_aberto)} ({pct_aberto:.2f}%)")
    print(f"  Títulos: {num_lanc} | Fornecedores: {num_forn}")

    # Meses ordenados
    all_months = sorted(set(list(mensal_quit.keys()) + list(mensal_aberto.keys())))
    # Converter para formato curto Jan/26
    month_name_map = {
        '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
        '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
        '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
    }
    chart_months_labels = []
    chart_quit_data = []
    chart_aberto_data = []
    for m in all_months:
        p = m.split('/')
        m_str = month_name_map.get(p[0], p[0])
        ano_str = p[1][-2:]
        chart_months_labels.append(f"{m_str}/{ano_str}")
        chart_quit_data.append(round(mensal_quit[m], 2))
        chart_aberto_data.append(round(mensal_aberto[m], 2))

    # Top 10 Fornecedores
    top10_forn = sorted(fornecedores.items(), key=lambda x: x[1], reverse=True)[:10]

    # Categorias principais (Top 7 + Outros)
    sorted_cats = sorted(categorias.items(), key=lambda x: x[1], reverse=True)
    cat_labels = []
    cat_data = []
    outros_val = 0.0
    for idx, (c, v) in enumerate(sorted_cats):
        if idx < 7:
            # simplificar nome longo
            short_c = c.split(' - ')[0]
            if len(short_c) > 25: short_c = short_c[:22] + "..."
            cat_labels.append(short_c)
            cat_data.append(round(v, 2))
        else:
            outros_val += v
    if outros_val > 0:
        cat_labels.append("Outros")
        cat_data.append(round(outros_val, 2))

    # Formas de pagamento
    fp_labels = []
    fp_data = []
    for fp, v in sorted(formas_pag.items(), key=lambda x: x[1], reverse=True):
        fp_name = fp.capitalize()
        if 'instant' in fp.lower() or 'pix' in fp.lower():
            if 'instant' in fp.lower(): fp_name = "Pagamento Instantâneo (PIX)"
            else: fp_name = "Cobrança PIX"
        fp_labels.append(fp_name)
        fp_data.append(round(v, 2))

    # Imobilizado principais parceiros
    mr_eng_val = fornecedores.get("MR ENGENHARIA", 0.0)
    othon_val = fornecedores.get("OTHON DE CARVALHO", 0.0)
    noronha_val = fornecedores.get("NORONHA COMUNICACAO VISUAL", 0.0)
    thermo_val = fornecedores.get("THERMOBRAS AR CONDICIONADO", 0.0)
    moveis_val = categorias.get("Móveis, Utensílios e Instalações Comerciais", 0.0) + categorias.get("Máquinas, Equipamentos e Instalações Industriais", 0.0)

    # 3. Ler arquivo HTML modelo atual
    uva_html_file = os.path.join(repo_dir, "contas-a-pagar-uva.html")
    if not os.path.exists(uva_html_file):
        uva_html_file = os.path.join(repo_dir, "uva.html")

    with open(uva_html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Atualizar Title e Badges de Header
    html = re.sub(
        r'<title>NNÓS Group \| Contas a Pagar — Campus BH UVA \| [^<]+</title>',
        f'<title>NNÓS Group | Contas a Pagar — Campus BH UVA | {mes_ref}</title>',
        html
    )

    # Badges do Topo
    # Período: ex: Jan/2026 a Dez/2026
    periodo_geral = f"{chart_months_labels[0]} a {chart_months_labels[-1]}"
    html = re.sub(
        r'<span class="material-symbols-outlined text-sky-400 text-sm">calendar_month</span>\s*[^<]+',
        f'<span class="material-symbols-outlined text-sky-400 text-sm">calendar_month</span> {periodo_geral}',
        html
    )
    html = re.sub(
        r'<span class="material-symbols-outlined text-sky-400 text-sm">payments</span>\s*Total:\s*R\$ [^<]+',
        f'<span class="material-symbols-outlined text-sky-400 text-sm">payments</span> Total: {fmt_br(tot_geral)}',
        html
    )
    html = re.sub(
        r'<span class="material-symbols-outlined text-sky-400 text-sm">receipt_long</span>\s*\d+\s*Lançamentos',
        f'<span class="material-symbols-outlined text-sky-400 text-sm">receipt_long</span> {num_lanc} Lançamentos',
        html
    )
    html = re.sub(
        r'<span class="material-symbols-outlined text-sky-400 text-sm">domain</span>\s*\d+\s*Fornecedores',
        f'<span class="material-symbols-outlined text-sky-400 text-sm">domain</span> {num_forn} Fornecedores',
        html
    )
    html = re.sub(
        r'<span class="material-symbols-outlined [^"]+ text-sm[^"]*">[^<]+</span>\s*[A-Z]{3}/\d{4}',
        f'<span class="material-symbols-outlined text-emerald-400 text-sm">update</span> {mes_ref}',
        html
    )

    # Subtítulo de introdução
    html = re.sub(
        r'Visão geral dos valores compromissados, quitados e projeções a vencer do Campus BH UVA\. Atualizado: [^<]+',
        f'Visão geral dos valores compromissados, quitados e projeções a vencer do Campus BH UVA. Atualizado: {mes_ref}.',
        html
    )

    # KPI 1 - Total Geral
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Geral</div>\s*</div>\s*<div class="text-3xl font-extrabold font-sans text-white mb-1 tracking-tight">)R\$ [^<]+(</div>\s*<div class="text-xs text-text-muted">)[^<]+(</div>)',
        rf'\g<1>{fmt_br(tot_geral)}\g<2>{num_lanc} títulos de {periodo_geral}\g<3>',
        html
    )

    # KPI 2 - Quitado
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase tracking-wider">Quitado</div>\s*</div>\s*<div class="text-3xl font-extrabold font-sans text-emerald-400 mb-1 tracking-tight">)R\$ [^<]+(</div>\s*<div class="text-xs text-emerald-300 font-medium">)[^<]+(</div>)',
        rf'\g<1>{fmt_br(tot_quit)}\g<2>{pct_quit:.2f}% do total liquidado\g<3>',
        html
    )

    # KPI 3 - A Vencer
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase tracking-wider">A Vencer / Em Aberto</div>\s*</div>\s*<div class="text-3xl font-extrabold font-sans text-rose-400 mb-1 tracking-tight">)R\$ [^<]+(</div>\s*<div class="text-xs text-rose-300 font-medium">)[^<]+(</div>)',
        rf'\g<1>{fmt_br(tot_aberto)}\g<2>{pct_aberto:.2f}% projeções futuras\g<3>',
        html
    )

    # KPI 4 - Imobilizado
    pct_imob_tot = (imobilizado_total / tot_geral * 100) if tot_geral > 0 else 0
    html = re.sub(
        r'(<div class="text-xs font-semibold text-amber-300 uppercase tracking-wider">Imobilizado &amp; Reforma</div>\s*</div>\s*<div class="text-3xl font-extrabold font-sans text-amber-300 mb-1 tracking-tight">)R\$ [^<]+(</div>\s*<div class="text-xs text-amber-200 font-medium">)[^<]+(</div>)',
        rf'\g<1>{fmt_br(imobilizado_total)}\g<2>{pct_imob_tot:.2f}% do total · {imob_titulos} títulos\g<3>',
        html
    )

    # Barra Execução Financeira
    html = re.sub(
        r'Quitado: R\$ [0-9.,]+ \([0-9.,]+%\)',
        f'Quitado: {fmt_br(tot_quit)} ({pct_quit:.2f}%)',
        html
    )
    html = re.sub(
        r'A Vencer: R\$ [0-9.,]+ \([0-9.,]+%\)',
        f'A Vencer: {fmt_br(tot_aberto)} ({pct_aberto:.2f}%)',
        html
    )
    html = re.sub(
        r'style="width:\s*[0-9.,]+%;"',
        f'style="width: {pct_quit:.2f}%;"',
        html
    )

    # Imobilizado Detalhes
    html = re.sub(
        r'(<div class="text-xs text-text-muted uppercase mb-1 font-semibold">MR Engenharia \(Obras\)</div>\s*<div class="text-xl font-extrabold text-amber-300 font-sans">)R\$ [^<]+(</div>)',
        rf'\g<1>{fmt_br(mr_eng_val)}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs text-text-muted uppercase mb-1 font-semibold">Móveis &amp; Equipamentos</div>\s*<div class="text-xl font-extrabold text-amber-300 font-sans">)R\$ [^<]+(</div>)',
        rf'\g<1>{fmt_br(moveis_val)}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs text-text-muted uppercase mb-1 font-semibold">Climatização \(Thermobras\)</div>\s*<div class="text-xl font-extrabold text-amber-300 font-sans">)R\$ [^<]+(</div>)',
        rf'\g<1>{fmt_br(thermo_val)}\g<2>',
        html
    )

    # Imobilizado Quitado vs A Vencer
    pct_imob_quit = (imobilizado_quit / imobilizado_total * 100) if imobilizado_total > 0 else 0
    pct_imob_aberto = (imobilizado_aberto / imobilizado_total * 100) if imobilizado_total > 0 else 0
    html = re.sub(
        r'(<div class="text-xs text-slate-400">Total Liquidado \(Quitado\)</div>\s*<div class="text-lg font-extrabold text-emerald-400 font-sans">)R\$ [^<]+<span class="text-xs text-slate-300 font-normal">\([^)]+\)</span>',
        rf'\g<1>{fmt_br(imobilizado_quit)} <span class="text-xs text-slate-300 font-normal">({pct_imob_quit:.2f}%)</span>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs text-slate-400">Saldo a Vencer</div>\s*<div class="text-lg font-extrabold text-rose-400 font-sans">)R\$ [^<]+<span class="text-xs text-slate-300 font-normal">\([^)]+\)</span>',
        rf'\g<1>{fmt_br(imobilizado_aberto)} <span class="text-xs text-slate-300 font-normal">({pct_imob_aberto:.2f}%)</span>',
        html
    )

    # Detalhamento Top 10 Fornecedores HTML List
    top10_html = ""
    for idx, (f_name, f_val) in enumerate(top10_forn, 1):
        f_pct = (f_val / tot_geral * 100) if tot_geral > 0 else 0
        top10_html += f'''<div class="flex items-center justify-between p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/60 shadow-sm hover:bg-slate-800/80 transition-colors">
<span class="font-semibold text-sm text-white">{idx}. {f_name}</span>
<div class="flex items-center gap-2">
<span class="font-sans font-bold text-base text-sky-300">{fmt_br(f_val)}</span>
<span class="text-xs font-semibold text-slate-300 bg-slate-800 px-2 py-0.5 rounded-md border border-slate-700">({f_pct:.2f}%)</span>
</div>
</div>\n'''

    html = re.sub(
        r'(<div class="space-y-3 overflow-y-auto max-h-\[360px\] pr-2">)[\s\S]*?(</div>\s*</div>\s*</div>\s*</section>)',
        rf'\g<1>\n{top10_html}\g<2>',
        html
    )

    # Indicadores Consolidados
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase mb-1">Lançamentos</div>\s*<div class="text-xl font-extrabold text-white font-sans">)\d+(</div>)',
        rf'\g<1>{num_lanc}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase mb-1">Fornecedores</div>\s*<div class="text-xl font-extrabold text-white font-sans">)\d+(</div>)',
        rf'\g<1>{num_forn}\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase mb-1">Ticket Médio</div>\s*<div class="text-xl font-extrabold text-white font-sans">)R\$ [^<]+(</div>)',
        rf'\g<1>R$ {ticket_medio:,.0f}'.replace(',', '.') + r'\g<2>',
        html
    )
    html = re.sub(
        r'(<div class="text-xs font-semibold text-text-muted uppercase mb-1">Taxa Quitação</div>\s*<div class="text-xl font-extrabold text-emerald-400 font-sans">)[^<]+(</div>)',
        rf'\g<1>{pct_quit:.2f}%\g<2>',
        html
    )

    # 4. Atualizar Scripts Chart.js
    # Chart Fornecedores
    chart_forn_labels = [f[0][:20] for f in top10_forn]
    chart_forn_data = [round(f[1], 2) for f in top10_forn]
    html = re.sub(
        r"(labels:\s*)\[[^\]]+\](,\s*datasets:\s*\[\{\s*label:\s*'Valor Total \(R\\?\$?\)',\s*data:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(chart_forn_labels, ensure_ascii=False) + m.group(2) + json.dumps(chart_forn_data),
        html
    )

    # Chart Mensal Extendido
    html = re.sub(
        r"(// Evolução Mensal Stacked[^\n]*\s*new Chart\(document\.getElementById\('chartMensalExtendido'\),\s*\{\s*type:\s*'bar',\s*data:\s*\{\s*labels:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(chart_months_labels, ensure_ascii=False),
        html
    )
    html = re.sub(
        r"(label:\s*'Quitado \(R\\?\$?\)',\s*data:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(chart_quit_data),
        html
    )
    html = re.sub(
        r"(label:\s*'A Vencer \(R\\?\$?\)',\s*data:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(chart_aberto_data),
        html
    )

    # Chart Categorias
    html = re.sub(
        r"(// Categorias \(Donut\)[^\n]*\s*new Chart\(document\.getElementById\('chartCategorias'\),\s*\{\s*type:\s*'doughnut',\s*data:\s*\{\s*labels:\s*)\[[^\]]+\](,\s*datasets:\s*\[\{\s*data:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(cat_labels, ensure_ascii=False) + m.group(2) + json.dumps(cat_data),
        html
    )

    # Chart Formas de Pagamento
    html = re.sub(
        r"(// Formas de Pagamento[^\n]*\s*new Chart\(document\.getElementById\('chartFormasPagamento'\),\s*\{\s*type:\s*'bar',\s*data:\s*\{\s*labels:\s*)\[[^\]]+\](,\s*datasets:\s*\[\{\s*label:\s*'Valor \(R\\?\$?\)',\s*data:\s*)\[[^\]]+\]",
        lambda m: m.group(1) + json.dumps(fp_labels, ensure_ascii=False) + m.group(2) + json.dumps(fp_data),
        html
    )

    # Salvar em contas-a-pagar-uva.html e uva.html
    target_uva = os.path.join(repo_dir, "contas-a-pagar-uva.html")
    with open(target_uva, 'w', encoding='utf-8') as f:
        f.write(html)

    # Sincronizar com a pasta ..\UVA se existir
    dest_uva_repo = os.path.join(uva_dir, "NNÓS Group _ Contas a Pagar - Campus BH UVA.html")
    if os.path.exists(uva_dir):
        try:
            with open(dest_uva_repo, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[OK] Atualizado em {dest_uva_repo}")
        except Exception as e:
            print(f"Aviso ao sincronizar pasta UVA externa: {e}")

    print(f"[OK] Relatório Contas a Pagar UVA atualizado com sucesso para {mes_ref}!")

if __name__ == "__main__":
    run()
