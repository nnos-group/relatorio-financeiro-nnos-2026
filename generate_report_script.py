import json
import hashlib
from logo_b64 import LOGO_B64_WHITE

# Credenciais de acesso ao relatório (Usuário e Senha)
USER_PLAIN = "nnos"
PASS_PLAIN = "nnos2026"

USER_HASH = hashlib.sha256(USER_PLAIN.encode('utf-8')).hexdigest()
PASS_HASH = hashlib.sha256(PASS_PLAIN.encode('utf-8')).hexdigest()

with open('calculated_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

fmt = lambda x: f"{round(x):,}".replace(",", ".")
fmt_float = lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
fmt_pct = lambda x: f"{x:.2f}%".replace(".", ",")

def fmt_val_table(x):
    if x < 0:
        return f'<span class="text-rose-400 font-bold">({fmt(-x)})</span>'
    elif x == 0:
        return '<span class="text-text-muted">—</span>'
    else:
        return f'<span class="text-white font-bold">{fmt(x)}</span>'

def fmt_val_table_rev(x):
    if x < 0:
        return f'<span class="text-rose-400 font-bold">({fmt(-x)})</span>'
    elif x == 0:
        return '<span class="text-text-muted">—</span>'
    else:
        return f'<span class="text-emerald-400 font-bold">{fmt(x)}</span>'

def fmt_val_table_exp(x):
    if x < 0:
        return f'<span class="text-rose-400 font-bold">({fmt(-x)})</span>'
    elif x == 0:
        return '<span class="text-text-muted">—</span>'
    else:
        return f'<span class="text-rose-400 font-bold">{fmt(x)}</span>'

def get_row(label, key, row_type="normal"):
    if row_type == "group":
        return f'''<tr class="bg-surface-container-high/90 border-y border-surface-variant/80">
          <td colspan="11" class="py-2.5 px-4 text-xs font-bold text-brand-blue uppercase tracking-widest">{label}</td>
        </tr>\n'''
    elif row_type == "spacer":
        return f'''<tr class="h-2">
          <td colspan="11"></td>
        </tr>\n'''
        
    vals = d[key]
    tot = sum(vals)
    
    if row_type == "revenue":
        tds = "".join([f'<td class="py-3 px-3 text-right text-sm font-sans">{fmt_val_table_rev(v)}</td>' for v in vals])
        tot_td = f'<td class="py-3 px-3 text-right text-sm font-sans font-bold">{fmt_val_table_rev(tot)}</td>'
        return f'''<tr class="hover:bg-surface-container-high/40 transition-colors border-b border-surface-variant/30">
          <td class="py-3 px-4 text-xs font-medium text-white">{label}</td>{tds}{tot_td}
        </tr>\n'''
    elif row_type == "expense":
        tds = "".join([f'<td class="py-3 px-3 text-right text-sm font-sans">{fmt_val_table_exp(v)}</td>' for v in vals])
        tot_td = f'<td class="py-3 px-3 text-right text-sm font-sans font-bold">{fmt_val_table_exp(tot)}</td>'
        return f'''<tr class="hover:bg-surface-container-high/40 transition-colors border-b border-surface-variant/30">
          <td class="py-3 px-4 text-xs font-medium text-gray-300">{label}</td>{tds}{tot_td}
        </tr>\n'''
    elif row_type == "subtotal":
        tds = "".join([f'<td class="py-3 px-3 text-right text-sm font-sans font-bold text-brand-blue">{fmt_val_table(v)}</td>' for v in vals])
        tot_td = f'<td class="py-3 px-3 text-right text-sm font-sans font-extrabold text-brand-blue">{fmt_val_table(tot)}</td>'
        return f'''<tr class="bg-surface-container/80 border-y border-brand-blue/40 hover:bg-surface-container-high/60 transition-colors">
          <td class="py-3 px-4 text-xs font-bold text-brand-blue uppercase tracking-wider">{label}</td>{tds}{tot_td}
        </tr>\n'''
    elif row_type == "subtotal_neg":
        is_neg = tot < 0
        text_cls = "text-rose-400" if is_neg else "text-emerald-400"
        border_cls = "border-rose-500/40" if is_neg else "border-emerald-500/40"
        tds = "".join([f'<td class="py-3 px-3 text-right text-sm font-sans font-bold {text_cls}">{fmt_val_table(v)}</td>' for v in vals])
        tot_td = f'<td class="py-3 px-3 text-right text-sm font-sans font-extrabold {text_cls}">{fmt_val_table(tot)}</td>'
        return f'''<tr class="bg-surface-container/80 border-y {border_cls} hover:bg-surface-container-high/60 transition-colors">
          <td class="py-3 px-4 text-xs font-bold {text_cls} uppercase tracking-wider">{label}</td>{tds}{tot_td}
        </tr>\n'''
    elif row_type == "result":
        is_pos = tot >= 0
        bg_cls = "bg-gradient-to-r from-emerald-900/60 to-emerald-800/40 border-emerald-500/60" if is_pos else "bg-gradient-to-r from-rose-950/80 to-rose-900/50 border-rose-500/60"
        text_cls = "text-emerald-300" if is_pos else "text-rose-300"
        tds = "".join([f'<td class="py-3.5 px-3 text-right text-sm font-sans font-bold {text_cls}">{fmt_val_table(v)}</td>' for v in vals])
        tot_td = f'<td class="py-3.5 px-3 text-right text-sm font-sans font-black text-base {text_cls}">{fmt_val_table(tot)}</td>'
        return f'''<tr class="{bg_cls} border-y-2 hover:brightness-110 transition-all">
          <td class="py-3.5 px-4 text-xs font-extrabold {text_cls} uppercase tracking-wider">{label}</td>{tds}{tot_td}
        </tr>\n'''
    elif row_type == "hint":
        pcts = [(v / d['rec_bruta'][i])*100 for i, v in enumerate(d[key])]
        tot_pct = (sum(d[key]) / sum(d['rec_bruta'])) * 100
        pct_tds = "".join([f'<td class="py-1.5 px-3 text-right text-xs font-sans text-text-muted italic">{fmt_pct(p)}</td>' for p in pcts])
        tot_pct_td = f'<td class="py-1.5 px-3 text-right text-xs font-sans font-semibold text-text-muted italic">{fmt_pct(tot_pct)}</td>'
        return f'''<tr class="bg-surface-container-lowest/30 border-b border-surface-variant/20">
          <td class="py-1.5 px-4 text-xs font-medium text-text-muted italic">{label}</td>{pct_tds}{tot_pct_td}
        </tr>\n'''

table_body = ""
table_body += get_row("RECEITAS", None, "group")
table_body += get_row("(=) Receita Bruta", "rec_bruta", "revenue")
table_body += get_row("(-) Impostos", "impostos_tot", "expense")
table_body += get_row("(=) RECEITA LÍQUIDA", "rec_liquida", "subtotal")

table_body += get_row("", None, "spacer")
table_body += get_row("CUSTOS VARIÁVEIS", None, "group")
table_body += get_row("(-) Custo Serviço (Consultores)", "custo_consultores", "expense")
table_body += get_row("(-) Comissões", "comissoes", "expense")
table_body += get_row("(-) Viagens", "viagens_desp", "expense")
table_body += get_row("(+) Reembolso de Viagens", "reembolso_viagens", "revenue")
table_body += get_row("(=) MARGEM BRUTA", "margem_bruta", "subtotal")
table_body += get_row("% Margem Bruta / Receita Bruta", "margem_bruta", "hint")

table_body += get_row("", None, "spacer")
table_body += get_row("CUSTO FIXO", None, "group")
table_body += get_row("(-) Funcionários (Sal+Enc+Benef)", "funcionarios", "expense")
table_body += get_row("(-) Despesa Administrativa", "desp_adm", "expense")
table_body += get_row("(-) Aluguel + Cond + Seguro", "aluguel", "expense")
table_body += get_row("(-) Contabilidade", "contabilidade", "expense")
table_body += get_row("(=) Custo Fixo Total", "custo_fixo_tot", "subtotal_neg")
table_body += get_row("(-) Despesas Operacionais", "desp_operacionais", "expense")

table_body += get_row("", None, "spacer")
table_body += get_row("(=) EBITDA", "ebitda", "subtotal_neg")
table_body += get_row("% EBITDA / Receita Bruta", "ebitda", "hint")

table_body += get_row("", None, "spacer")
table_body += get_row("RESULTADO FINANCEIRO", None, "group")
table_body += get_row("(+) Receita Financeira (Rend. Aplic.)", "receita_financeira", "revenue")
table_body += get_row("(-) Despesa Financeira (juros+tarifas)", "juros_tarifas", "expense")
table_body += get_row("(=) Resultado Financeiro", "res_financeiro", "subtotal")

table_body += get_row("", None, "spacer")
table_body += get_row("(=) RESULTADO DO PERÍODO", "resultado_periodo", "result")
table_body += get_row("% Resultado / Receita Bruta", "resultado_periodo", "hint")

# ── Imobilizado & Reforma (Atualizado com base no painel Campus BH UVA) ──
imob_total = 337754.41
imob_fornecedores = [
    ("MR ENGENHARIA", "Obras", 189589.65),
    ("OTHON DE CARVALHO", "Materiais Elétricos", 29730.33),
    ("NORONHA COMUNICAÇÃO VISUAL", "Sinalização", 26090.00),
    ("THERMOBRAS AR CONDICIONADO", "Climatização", 21300.00),
    ("AÇO INOX IMPERIAL", "", 18749.90),
    ("ANDRADES COMERCIO", "", 14692.19),
]

# Build fornecedores HTML cards
imob_fornecedores_html = ""
imob_colors = ['bg-rose-500', 'bg-amber-500', 'bg-brand-blue', 'bg-purple-500', 'bg-teal-500', 'bg-slate-400']
for idx, (nome, desc, valor) in enumerate(imob_fornecedores):
    pct_imob = (valor / imob_total) * 100
    color_cls = imob_colors[idx % len(imob_colors)]
    desc_label = f' <span class="text-gray-500">({desc})</span>' if desc else ""
    bar_width = (valor / imob_fornecedores[0][2]) * 100
    imob_fornecedores_html += f'''<div class="p-3.5 rounded-xl bg-surface-container-high/60 border border-surface-variant/40 hover:bg-surface-container-high transition-colors">
  <div class="flex items-center justify-between mb-2">
    <div class="text-xs font-bold text-white uppercase tracking-wide">{nome}{desc_label}</div>
    <div class="text-[10px] font-bold text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded-full border border-amber-500/30">{fmt_pct(pct_imob)}</div>
  </div>
  <div class="text-sm font-extrabold text-emerald-400 font-sans mb-2">R$ {fmt_float(valor)}</div>
  <div class="h-1.5 w-full bg-surface-container-lowest rounded-full overflow-hidden">
    <div class="h-full {color_cls} rounded-full" style="width: {bar_width:.1f}%"></div>
  </div>
</div>\n'''

# Imobilizado header row in the DRE table
table_body += '''<tr class="h-6">
  <td colspan="11"></td>
</tr>
'''
table_body += f'''<tr class="bg-surface-container-high/90 border-y border-surface-variant/80">
  <td class="py-3 px-4 text-xs font-bold text-brand-blue uppercase tracking-widest">Imobilizado &amp; Reforma</td>
  <td colspan="8" class="py-3 px-3"></td>
  <td class="py-3 px-3 text-right text-sm font-sans font-bold text-amber-300">R$ {fmt_float(imob_total)}</td>
</tr>
'''

# Resultado sem Imobilizado - same monthly values, but YTD deducts imobilizado
res_sem_imob = list(d['resultado_periodo'])
res_sem_imob_ytd = sum(res_sem_imob) + imob_total

is_pos_sem = res_sem_imob_ytd >= 0
bg_cls_sem = "bg-gradient-to-r from-emerald-900/60 to-emerald-800/40 border-emerald-500/60" if is_pos_sem else "bg-gradient-to-r from-rose-950/80 to-rose-900/50 border-rose-500/60"
text_cls_sem = "text-emerald-300" if is_pos_sem else "text-rose-300"

monthly_tds_sem = "".join([f'<td class="py-3.5 px-3 text-right text-sm font-sans font-bold {text_cls_sem}">{fmt_val_table(v)}</td>' for v in res_sem_imob])

# YTD cell with special formatting using fmt_float
if res_sem_imob_ytd < 0:
    ytd_sem_cell = f'<span class="text-rose-300 font-bold">({fmt_float(-res_sem_imob_ytd)})</span>'
else:
    ytd_sem_cell = f'<span class="text-emerald-300 font-bold">{fmt_float(res_sem_imob_ytd)}</span>'

table_body += f'''<tr class="{bg_cls_sem} border-y-2 hover:brightness-110 transition-all">
  <td class="py-3.5 px-4 text-xs font-extrabold {text_cls_sem} uppercase tracking-wider">(=) RESULTADO DO PERÍODO SEM IMOBILIZADO &amp; REFORMA</td>
  {monthly_tds_sem}
  <td class="py-3.5 px-3 text-right text-sm font-sans font-black text-base {text_cls_sem}">{ytd_sem_cell}</td>
</tr>
'''

# Hint row for resultado sem imobilizado
res_sem_imob_pcts = [(v / d['rec_bruta'][i])*100 for i, v in enumerate(res_sem_imob)]
res_sem_imob_ytd_pct = (res_sem_imob_ytd / sum(d['rec_bruta'])) * 100
pct_tds_sem = "".join([f'<td class="py-1.5 px-3 text-right text-xs font-sans text-text-muted italic">{fmt_pct(p)}</td>' for p in res_sem_imob_pcts])
tot_pct_td_sem = f'<td class="py-1.5 px-3 text-right text-xs font-sans font-semibold text-text-muted italic">{fmt_pct(res_sem_imob_ytd_pct)}</td>'
table_body += f'''<tr class="bg-surface-container-lowest/30 border-b border-surface-variant/20">
  <td class="py-1.5 px-4 text-xs font-medium text-text-muted italic">% Resultado / Receita Bruta</td>
  {pct_tds_sem}{tot_pct_td_sem}
</tr>
'''

# Top 10 Projetos Rows (Fonte maior, bem legível e verde vibrante)
proj_rows_html = ""
for idx, (proj, val) in enumerate(d['top_proj'], 1):
    badge_bg = "bg-amber-500 text-black font-bold" if idx == 1 else "bg-slate-400 text-black font-bold" if idx == 2 else "bg-amber-700 text-white font-bold" if idx == 3 else "bg-surface-container-high text-text-muted border border-surface-variant"
    proj_rows_html += f'''<div class="flex items-center justify-between p-3.5 rounded-lg bg-surface-container-high/40 hover:bg-surface-container-high border border-surface-variant/40 transition-colors">
  <div class="flex items-center gap-3">
    <div class="w-7 h-7 rounded-full {badge_bg} flex items-center justify-center text-xs flex-shrink-0">{idx}</div>
    <div class="text-xs font-bold text-white tracking-wide uppercase">{proj}</div>
  </div>
  <div class="text-sm font-extrabold text-emerald-400 font-sans">R$ {fmt(val)}</div>
</div>\n'''

# UN Grid & Bars
un_grid_html = ""
un_bars_html = ""
tot_rec_ytd = sum(d['rec_bruta'])
un_colors = ['bg-brand-blue', 'bg-emerald-500', 'bg-purple-500', 'bg-amber-500', 'bg-teal-500', 'bg-rose-400', 'bg-slate-400']
un_display_names = {
    'OUTSOURCING': 'OUTSOURCING',
    'HRD - HUMAN RESOURCE\xa0DEVELOPMENT': 'HRD',
    'BUSINESS SOLUTIONS': 'BUSINESS SOLUTIONS',
    'DEALER DEVELOPMENT': 'DEALER DEVELOPMENT',
    'INNOVATION': 'INNOVATION',
    'EDUCAÇÃO': 'EDUCAÇÃO',
}
for idx, (un, val) in enumerate(sorted(d['un_ytd'].items(), key=lambda x: x[1], reverse=True)):
    pct = (val / tot_rec_ytd) * 100
    val_k = val / 1000
    display = un_display_names.get(un, un.split(' - ')[0])
    grid_col_span = ' class="col-span-full"' if un == 'INNOVATION' else ''
    un_grid_html += f'''<div class="glass-card p-4 rounded-xl border border-surface-variant/60 flex items-center justify-between{grid_col_span}">
  <div>
    <div class="text-xs font-bold text-brand-blue uppercase tracking-wider">{display}</div>
    <div class="text-[11px] text-text-muted mt-0.5">{pct:.1f}% do faturamento total</div>
  </div>
  <div class="text-lg font-extrabold text-white font-display">R$ {val_k:,.0f}K</div>
</div>\n'''.replace(',', '.')

    color_cls = un_colors[idx % len(un_colors)]
    un_bars_html += f'''<div class="space-y-1.5">
  <div class="flex justify-between text-xs font-medium">
    <span class="text-text-muted">{display}</span>
    <span class="text-white font-semibold">{pct:.1f}%</span>
  </div>
  <div class="h-3 w-full bg-surface-container-high rounded-full overflow-hidden border border-surface-variant/40">
    <div class="h-full {color_cls} rounded-full transition-all duration-500" style="width: {pct:.1f}%"></div>
  </div>
</div>\n'''

# Top CC Rows (Ajustado CAMPUS BH e alinhamento de barras)
cc_rows_html = ""
max_cc = max(v for cc, v in d['top_cc'])
cc_colors = ['bg-rose-500', 'bg-amber-500', 'bg-brand-blue', 'bg-purple-500', 'bg-slate-400', 'bg-rose-400', 'bg-amber-400']
for idx, (cc, val) in enumerate(d['top_cc']):
    cc_name_display = "CAMPUS BH" if "CAMPUS BH" in cc else cc
    pct_bar = (val / max_cc) * 100
    color_cls = cc_colors[idx % len(cc_colors)]
    val_k = val / 1000
    cc_rows_html += f'''<div class="flex items-center gap-4 py-2.5 border-b border-surface-variant/30 last:border-none">
  <div class="text-xs font-bold text-gray-300 uppercase tracking-wider w-44 flex-shrink-0 truncate">{cc_name_display}</div>
  <div class="flex-1 h-7 bg-surface-container-high rounded-lg overflow-hidden border border-surface-variant/40">
    <div class="h-full {color_cls} rounded-lg flex items-center px-3 text-xs font-bold text-white min-w-[75px]" style="width: {pct_bar:.1f}%">R$ {val_k:,.0f}K</div>
  </div>
  <div class="text-sm font-extrabold text-emerald-400 font-sans w-28 flex-shrink-0 text-right">R$ {fmt(val)}</div>
</div>\n'''.replace(',', '.')

# Viagens Comparativo
viagens_comp_html = ""
max_viag = max(max(d['viagens_desp']), max(d['reembolso_viagens']))
months_viag = ['JAN-26', 'FEV-26', 'MAR-26', 'ABR-26', 'MAI-26', 'JUN-26', 'JUL-26', 'AGO-26']
for i in range(len(months_viag)):
    desp_v = d['viagens_desp'][i]
    reemb_v = d['reembolso_viagens'][i]
    p_desp = (desp_v / max_viag) * 100
    p_reemb = (reemb_v / max_viag) * 100
    viagens_comp_html += f'''<div class="space-y-2">
  <div class="text-sm font-bold text-brand-blue">{months_viag[i]}</div>
  <div class="grid grid-cols-1 gap-1.5">
    <div class="flex items-center gap-3">
      <span class="text-sm text-text-muted w-20 font-medium">Despesa</span>
      <div class="flex-1 h-7 bg-surface-container-high rounded-lg overflow-hidden">
        <div class="h-full bg-rose-500 rounded-lg flex items-center px-3 text-xs font-bold text-white" style="width: {p_desp:.1f}%">R$ {fmt(desp_v)}</div>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <span class="text-sm text-text-muted w-20 font-medium">Reembolso</span>
      <div class="flex-1 h-7 bg-surface-container-high rounded-lg overflow-hidden">
        <div class="h-full bg-emerald-500 rounded-lg flex items-center px-3 text-xs font-bold text-white" style="width: {p_reemb:.1f}%">R$ {fmt(reemb_v)}</div>
      </div>
    </div>
  </div>
</div>\n'''

tot_viag_desp = sum(d['viagens_desp'])
tot_viag_op = sum(d['viag_op'])
tot_viag_prosp = sum(d['viag_prosp'])
tot_viag_reemb = sum(d['reembolso_viagens'])
gap_viagens = tot_viag_reemb - tot_viag_desp
cobertura_pct = (tot_viag_reemb / tot_viag_desp) * 100

# ── KPI 5: Resultado sem Imobilizado & Reforma ──
_res_sem = res_sem_imob_ytd  # already calculated above
_res_sem_pct = (_res_sem / sum(d['rec_bruta'])) * 100
_imob_val_k = imob_total / 1000
if _res_sem >= 0:
    _kpi5_color = 'text-emerald-400'
    _kpi5_gradient = 'from-emerald-500 to-teal-400'
    _kpi5_badge_cls = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    _kpi5_icon_cls = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    _kpi5_value_fmt = f'R$ {fmt(abs(_res_sem))}'
    _kpi5_sub_icon = 'arrow_upward'
    _kpi5_sub_color = 'text-emerald-400'
else:
    _kpi5_color = 'text-rose-400'
    _kpi5_gradient = 'from-teal-600 to-cyan-500'
    _kpi5_badge_cls = 'bg-teal-500/20 text-teal-300 border-teal-500/30'
    _kpi5_icon_cls = 'bg-teal-500/20 text-teal-300 border-teal-500/30'
    _kpi5_value_fmt = f'-R$ {fmt(abs(_res_sem))}'
    _kpi5_sub_icon = 'trending_down'
    _kpi5_sub_color = 'text-rose-400'

kpi5_card = f'''<div class="glass-card rounded-xl p-5 relative overflow-hidden group border-2 border-teal-500/30">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg {_kpi5_icon_cls} flex items-center justify-center border">
            <span class="material-symbols-outlined">construction</span>
          </div>
          <span class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full {_kpi5_badge_cls} border">Ex-Imob.</span>
        </div>
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Resultado s/ Imob. &amp; Reforma</div>
        <div class="text-2xl font-extrabold font-display {_kpi5_color} mb-1">{_kpi5_value_fmt}</div>
        <div class="text-xs {_kpi5_sub_color} font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">{_kpi5_sub_icon}</span> {_res_sem_pct:+.1f}% rec. bruta | Imob.: R$ {_imob_val_k:.0f}k
        </div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r {_kpi5_gradient}"></div>
      </div>'''

full_html = f'''<!DOCTYPE html>
<html class="dark" lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>NNÓS — Dashboard Executivo & DRE Gerencial JAN–JUL 2026</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        "colors": {{
          "secondary-fixed-dim": "#ffb4a2",
          "on-error-container": "#ffdad6",
          "on-surface-variant": "#bfc7d2",
          "primary-fixed": "#cee5ff",
          "on-secondary-fixed": "#3c0700",
          "tertiary-container": "#d37b1d",
          "outline-variant": "#3f4851",
          "surface-container-high": "#232a3a",
          "on-primary-fixed-variant": "#004a75",
          "secondary-container": "#822610",
          "tertiary": "#ffb77a",
          "secondary": "#ffb4a2",
          "on-surface": "#dce2f7",
          "inverse-on-surface": "#293040",
          "background": "#0c1322",
          "tertiary-fixed-dim": "#ffb77a",
          "surface-elevation-2": "#374151",
          "on-primary-fixed": "#001d32",
          "on-secondary-container": "#ff9b82",
          "on-secondary": "#621100",
          "on-error": "#690005",
          "surface-tint": "#96ccff",
          "text-primary": "#FFFFFF",
          "surface": "#0c1322",
          "error": "#ffb4ab",
          "on-tertiary-fixed-variant": "#6c3a00",
          "text-muted": "#9CA3AF",
          "accent-amber": "#FBBF24",
          "primary-container": "#3197df",
          "on-secondary-fixed-variant": "#822610",
          "on-background": "#dce2f7",
          "surface-bright": "#323949",
          "primary-fixed-dim": "#96ccff",
          "surface-container-highest": "#2e3545",
          "surface-container": "#191f2f",
          "on-primary-container": "#002c48",
          "on-tertiary-container": "#422100",
          "outline": "#89919c",
          "error-container": "#93000a",
          "surface-container-low": "#141b2b",
          "tertiary-fixed": "#ffdcc1",
          "inverse-primary": "#00639a",
          "on-tertiary": "#4c2700",
          "surface-variant": "#2e3545",
          "surface-elevation-1": "#1F2937",
          "surface-container-lowest": "#070e1d",
          "inverse-surface": "#dce2f7",
          "on-tertiary-fixed": "#2e1500",
          "primary": "#96ccff",
          "on-primary": "#003353",
          "secondary-fixed": "#ffdad2",
          "surface-dim": "#0c1322",
          "brand-blue": "#0083ca"
        }},
        "borderRadius": {{
          "DEFAULT": "0.25rem",
          "lg": "0.5rem",
          "xl": "0.75rem",
          "full": "9999px"
        }},
        "fontFamily": {{
          "sans": ["Inter", "sans-serif"],
          "display": ["Manrope", "sans-serif"],
        }}
      }},
    }},
  }}
</script>
<style>
  body {{
    background: linear-gradient(135deg, #0f172a 0%, #1e40af 50%, #3b82f6 100%);
    color: #dce2f7;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
  }}
  h1, h2, h3, h4, h5, h6, .font-display {{
    font-family: 'Manrope', sans-serif;
  }}
  .glass-card {{
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }}
  .glass-panel {{
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-track {{ background: rgba(15, 23, 42, 0.5); }}
  ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.2); border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.3); }}
</style>
</head>
<body class="antialiased selection:bg-brand-blue selection:text-white bg-slate-950">

<!-- LOGIN GATE OVERLAY -->
<div id="login-overlay" class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/95 backdrop-blur-2xl transition-all duration-500">
  <div class="w-full max-w-md bg-slate-900/90 border border-white/10 rounded-2xl p-8 shadow-2xl backdrop-blur-2xl relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand-blue via-blue-500 to-emerald-400"></div>
    <div class="flex flex-col items-center text-center mb-8">
      <img alt="NNÓS Logo" class="h-16 w-auto object-contain mb-4" src="{LOGO_B64_WHITE}"/>
      <h2 class="text-xl font-bold font-display text-white tracking-tight">Acesso ao Relatório Executivo</h2>
      <p class="text-xs text-gray-400 mt-1">Área restrita • Digite suas credenciais para visualizar</p>
    </div>
    
    <form id="login-form" class="space-y-4" onsubmit="handleLogin(event)">
      <div>
        <label class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">Usuário</label>
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-sm">person</span>
          <input id="login-user" type="text" required placeholder="Digite seu usuário" class="w-full bg-slate-800/80 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-all"/>
        </div>
      </div>
      
      <div>
        <label class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">Senha</label>
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-sm">lock</span>
          <input id="login-pass" type="password" required placeholder="••••••••" class="w-full bg-slate-800/80 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-all"/>
        </div>
      </div>

      <div id="login-error" class="hidden text-xs font-medium text-rose-400 bg-rose-500/10 border border-rose-500/20 p-3 rounded-xl flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">error</span> Usuário ou senha incorretos. Tente novamente.
      </div>

      <button type="submit" class="w-full py-3 px-4 rounded-xl bg-brand-blue hover:bg-blue-600 text-white font-bold text-sm transition-all shadow-lg shadow-brand-blue/20 flex items-center justify-center gap-2 group">
        <span>Acessar Relatório</span>
        <span class="material-symbols-outlined text-sm group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
      </button>
    </form>

    <div class="mt-6 pt-6 border-t border-white/10 text-center text-[11px] text-gray-500">
      NNÓS Business Solutions • Controladoria & Gestão
    </div>
  </div>
</div>

<!-- REPORT CONTENT WRAPPER -->
<div id="report-wrapper" class="hidden">

<!-- HEADER -->
<header class="relative overflow-hidden bg-transparent border-b border-white/10">
  <div class="max-w-[1440px] mx-auto px-6 py-10 relative z-10 flex items-center justify-between gap-8">
    <div class="max-w-4xl">
      <div class="flex items-center gap-4 mb-4">
        <img alt="NNÓS Logo" class="h-16 w-auto object-contain" src="{LOGO_B64_WHITE}"/>
        <div class="h-8 w-[1px] bg-white/20"></div>
        <span class="text-xs font-bold text-brand-blue uppercase tracking-widest bg-brand-blue/10 px-3 py-1 rounded-full border border-brand-blue/30">Relatório Financeiro Gerencial</span>
      </div>
      <h1 class="text-3xl md:text-4xl font-extrabold font-display text-white mb-2 tracking-tight">Demonstrativo de Resultados & Dashboard Executivo</h1>
      <p class="text-gray-300 text-base mb-6">Análise financeira gerencial — Visão acumulada de 8 meses (Janeiro a Agosto/2026) - Fonte Conta Azul</p>
      <div class="flex flex-wrap gap-3 text-xs font-semibold">
        <span class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 text-white border border-white/10">
          <span class="material-symbols-outlined text-brand-blue text-sm">calendar_month</span> Jan/2026 a Ago/2026 (8 Meses)
        </span>
        <span class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 text-white border border-white/10">
          <span class="material-symbols-outlined text-emerald-400 text-sm">payments</span> Rec. Bruta: R$ 6,80M
        </span>
        <span class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 text-white border border-white/10">
          <span class="material-symbols-outlined text-brand-blue text-sm">trending_up</span> Margem Bruta: 45,8%
        </span>
        <span class="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 text-white border border-white/10">
          <span class="material-symbols-outlined text-amber-400 text-sm">verified</span> Controladoria & Gestão
        </span>
      </div>
    </div>
  </div>
</header>

<!-- NAV BAR -->
<nav class="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-white/10 shadow-lg">
  <div class="max-w-[1440px] mx-auto px-6 overflow-x-auto">
    <div class="flex items-center justify-between gap-2 py-2.5 min-w-max">
      <div class="flex items-center gap-2">
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#kpis"><span class="material-symbols-outlined text-base text-brand-blue">monitoring</span> KPIs Estratégicos</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#dre"><span class="material-symbols-outlined text-base text-brand-blue">table_chart</span> DRE Gerencial</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#faturamento"><span class="material-symbols-outlined text-base text-brand-blue">show_chart</span> Faturamento Mensal</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#projetos-un"><span class="material-symbols-outlined text-base text-brand-blue">domain</span> Projetos & UNs</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#centros-custo"><span class="material-symbols-outlined text-base text-brand-blue">account_balance</span> Centros de Custo</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#viagens"><span class="material-symbols-outlined text-base text-brand-blue">flight_takeoff</span> Viagens & Reembolsos</a>
        <a class="px-4 py-2 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 transition-colors flex items-center gap-2" href="#sintese"><span class="material-symbols-outlined text-base text-brand-blue">lightbulb</span> Síntese Executiva</a>
      </div>
      <div class="flex items-center gap-2.5 ml-auto">
        <a href="uva.html" class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-amber-300 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">account_balance</span> Campus BH UVA
        </a>
        <a href="booking.html" class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-emerald-300 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm">trending_up</span> Performance Projetos
        </a>
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

<!-- MAIN CONTENT -->
<main class="max-w-[1440px] mx-auto px-6 py-10 space-y-12">

  <!-- ──────── SECTION 1: KPIS ──────── -->
  <section class="scroll-mt-24" id="kpis">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
          <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
          Indicadores Estratégicos YTD (8 Meses)
        </h2>
        <p class="text-xs text-gray-400 mt-1 ml-4.5">Visão sintética do desempenho financeiro acumulado de Janeiro a Agosto/2026</p>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
      <!-- KPI 1 -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-brand-blue/20 flex items-center justify-center text-brand-blue border border-brand-blue/30">
            <span class="material-symbols-outlined">payments</span>
          </div>
          <span class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-brand-blue/20 text-brand-blue border border-brand-blue/30">8 Meses</span>
        </div>
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Receita Bruta YTD</div>
        <div class="text-2xl font-extrabold font-display text-white mb-1">R$ 6,80M</div>
        <div class="text-xs text-emerald-400 font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">trending_up</span> Média: R$ 849,8k/mês
        </div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-brand-blue to-blue-600"></div>
      </div>
      <!-- KPI 2 -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 border border-emerald-500/30">
            <span class="material-symbols-outlined">add_chart</span>
          </div>
          <span class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Agosto: 49,2%</span>
        </div>
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Margem Bruta Acumulada</div>
        <div class="text-2xl font-extrabold font-display text-white mb-1">45,8%</div>
        <div class="text-xs text-emerald-400 font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">arrow_upward</span> R$ 3,12M em Margem Bruta
        </div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-emerald-500 to-teal-400"></div>
      </div>
      <!-- KPI 3 -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center text-amber-400 border border-amber-500/30">
            <span class="material-symbols-outlined">analytics</span>
          </div>
          <span class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">Ago: +R$ 287k</span>
        </div>
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">EBITDA Acumulado</div>
        <div class="text-2xl font-extrabold font-display text-rose-400 mb-1">-R$ 631k</div>
        <div class="text-xs text-gray-400 font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">timeline</span> Margin EBITDA: -9,3%
        </div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-amber-500 to-rose-500"></div>
      </div>
      <!-- KPI 4 -->
      <div class="glass-card rounded-xl p-5 relative overflow-hidden group">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400 border border-purple-500/30">
            <span class="material-symbols-outlined">account_balance</span>
          </div>
          <span class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">+R$ 287k em Ago</span>
        </div>
        <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Resultado YTD Período</div>
        <div class="text-2xl font-extrabold font-display text-rose-400 mb-1">-R$ 473k</div>
        <div class="text-xs text-emerald-400 font-medium flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">savings</span> Rec. Financeira: R$ 229k
        </div>
        <div class="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-purple-500 to-indigo-500"></div>
      </div>
      <!-- KPI 5 -->
      {kpi5_card}
    </div>
  </section>

  <!-- ──────── SECTION 2: DRE TABLE ──────── -->
  <section class="scroll-mt-24" id="dre">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Demonstração do Resultado do Exercício (DRE Gerencial)
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Apuração mensal detalhada (Jan a Ago/26) — Impostos (ISS Efetivo + 6,15% PIS/COFINS) e Resultado Financeiro</p>
    </div>
    <div class="glass-panel rounded-2xl overflow-hidden border border-white/15 shadow-2xl">
      <div class="p-4 bg-slate-900/90 border-b border-white/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-brand-blue">table_view</span>
          <h3 class="text-sm font-bold text-white uppercase tracking-wider">DRE Mensal e Acumulado YTD — 2026</h3>
        </div>
        <span class="text-xs font-bold bg-brand-blue/20 text-brand-blue border border-brand-blue/40 px-3 py-1 rounded-full">Valores Expressos em R$</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[950px]">
          <thead>
            <tr class="bg-slate-950 text-gray-300 text-xs font-extrabold uppercase tracking-wider border-b border-white/15">
              <th class="py-3.5 px-4">Descrição</th>
              <th class="py-3.5 px-3 text-right">JAN-26</th>
              <th class="py-3.5 px-3 text-right">FEV-26</th>
              <th class="py-3.5 px-3 text-right">MAR-26</th>
              <th class="py-3.5 px-3 text-right">ABR-26</th>
              <th class="py-3.5 px-3 text-right">MAI-26</th>
              <th class="py-3.5 px-3 text-right">JUN-26</th>
              <th class="py-3.5 px-3 text-right">JUL-26</th>
              <th class="py-3.5 px-3 text-right">AGO-26</th>
              <th class="py-3.5 px-3 text-right text-brand-blue font-black">YTD (8 MESES)</th>
            </tr>
          </thead>
          <tbody>
{table_body}          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- ──────── SECTION 3: FATURAMENTO & CHART ──────── -->
  <section class="scroll-mt-24" id="faturamento">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Evolução do Faturamento Mensal
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Tendência de crescimento da Receita Bruta com destaque para o recorde de R$ 1,007 milhão em Julho/26</p>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="glass-card rounded-2xl p-6 border border-white/10 lg:col-span-2">
        <h3 class="text-base font-bold text-white mb-1">Gráfico de Evolução de Receita Bruta (R$)</h3>
        <p class="text-xs text-gray-400 mb-6">Comparativo mês a mês</p>
        <div class="h-72 w-full relative">
          <canvas id="chartFaturamento"></canvas>
        </div>
      </div>
      <div class="glass-card rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-white mb-1">Média & Performance</h3>
          <p class="text-xs text-gray-400 mb-6">Resumo executivo de vendas</p>
          <div class="space-y-4">
            <div class="p-4 rounded-xl bg-slate-900/80 border border-white/10">
              <div class="text-xs text-gray-400">Média Mensal de Faturamento</div>
              <div class="text-2xl font-extrabold text-brand-blue font-display mt-1">R$ {fmt(sum(d['rec_bruta'])/7)}</div>
            </div>
            <div class="p-4 rounded-xl bg-slate-900/80 border border-white/10">
              <div class="text-xs text-gray-400">Mês de Maior Faturamento</div>
              <div class="text-xl font-extrabold text-emerald-400 font-display mt-1">Julho/26 (R$ 1,007M)</div>
            </div>
            <div class="p-4 rounded-xl bg-slate-900/80 border border-white/10">
              <div class="text-xs text-gray-400">Crescimento Jan → Jul</div>
              <div class="text-xl font-extrabold text-emerald-400 font-display mt-1">+62,8%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ──────── SECTION 4: PROJETOS & UN ──────── -->
  <section class="scroll-mt-24" id="projetos-un">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Projetos & Unidades de Negócio
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Concentração de receita por contrato e distribuição de faturamento por UN</p>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- TOP 10 PROJETOS -->
      <div class="glass-card rounded-2xl p-6 border border-white/10">
        <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
          <span class="material-symbols-outlined text-amber-400">local_fire_department</span> Top 10 Projetos por Faturamento
        </h3>
        <p class="text-xs text-gray-400 mb-6">Ranking acumulado YTD (7 Meses)</p>
        <div class="space-y-2.5">
{proj_rows_html}        </div>
      </div>

      <!-- UNIDADES DE NEGÓCIO -->
      <div class="glass-card rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
            <span class="material-symbols-outlined text-brand-blue">pie_chart</span> Faturamento por Unidade de Negócio
          </h3>
          <p class="text-xs text-gray-400 mb-6">Participação relativa na Receita Bruta YTD</p>
          
          <div class="grid grid-cols-2 gap-3 mb-6">
{un_grid_html}          </div>
          
          <div class="space-y-4">
{un_bars_html}          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ──────── SECTION 5: CENTROS DE CUSTO ──────── -->
  <section class="scroll-mt-24" id="centros-custo">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Ranking por Centro de Custo
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Principais centros acumuladores de custos e despesas operacionais no ano</p>
    </div>
    <div class="glass-card rounded-2xl p-6 border border-white/10">
      <div class="space-y-3">
{cc_rows_html}      </div>
    </div>
  </section>

  <!-- ──────── SECTION 6: VIAGENS ──────── -->
  <section class="scroll-mt-24" id="viagens">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Análise de Viagens & Reembolsos
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Comparativo entre gastos com viagens e a taxa de recuperação via reembolso de clientes</p>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="glass-card rounded-2xl p-6 border border-white/10">
        <h3 class="text-base font-bold text-white mb-1">Comparativo Mensal (Despesa vs. Reembolso)</h3>
        <p class="text-xs text-gray-400 mb-6">Taxa de cobertura acumulada: <strong class="text-emerald-400">{cobertura_pct:.1f}%</strong></p>
        <div class="space-y-4">
{viagens_comp_html}        </div>
      </div>

      <div class="glass-card rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
        <div>
          <h3 class="text-lg font-bold text-white mb-1">Saldo Líquido — Operacional vs. Reembolso</h3>
          <p class="text-sm text-gray-400 mb-6">Indicador principal: NET entre despesas operacionais e reembolsos recebidos</p>

          <!-- NET Principal -->
          <div class="mb-6 p-5 rounded-xl border-2 {'border-emerald-500/60 bg-emerald-950/40' if (tot_viag_reemb - tot_viag_op) >= 0 else 'border-rose-500/60 bg-rose-950/40'} text-center">
            <div class="text-xs font-bold uppercase text-gray-400 tracking-wider mb-1">NET Operacional (Reembolsos − Desp. Operacionais)</div>
            <div class="text-3xl font-black {'text-emerald-400' if (tot_viag_reemb - tot_viag_op) >= 0 else 'text-rose-400'} font-display mt-1">{'+ ' if (tot_viag_reemb - tot_viag_op) >= 0 else '- '}R$ {fmt(abs(tot_viag_reemb - tot_viag_op))}</div>
            <div class="text-sm text-gray-300 mt-2 font-medium">{'Reembolsos superaram as despesas operacionais' if (tot_viag_reemb - tot_viag_op) >= 0 else 'Despesas operacionais superaram os reembolsos'}</div>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between items-center p-3.5 rounded-lg bg-slate-900/80 border border-white/10">
              <span class="text-sm text-gray-300 font-medium">(-) Despesas Operacionais com Viagens</span>
              <span class="text-base font-bold text-rose-400 font-sans">R$ {fmt(tot_viag_op)}</span>
            </div>
            <div class="flex justify-between items-center p-3.5 rounded-lg bg-slate-900/80 border border-white/10">
              <span class="text-sm text-gray-300 font-medium">(+) Reembolso Recebido de Clientes</span>
              <span class="text-base font-bold text-emerald-400 font-sans">R$ {fmt(tot_viag_reemb)}</span>
            </div>
          </div>

          <div class="mt-5 pt-4 border-t border-white/10 space-y-3">
            <div class="text-xs font-bold text-gray-400 uppercase tracking-wider">Detalhamento Adicional</div>
            <div class="flex justify-between items-center p-3 rounded-lg bg-slate-900/60 border border-white/5">
              <span class="text-sm text-gray-400">Despesa Total com Viagens (Op. + Prosp.)</span>
              <span class="text-sm font-bold text-rose-400 font-sans">R$ {fmt(tot_viag_desp)}</span>
            </div>
            <div class="flex justify-between items-center p-3 rounded-lg bg-slate-900/60 border border-white/5 pl-6">
              <span class="text-sm text-gray-400">↳ Viagens Prospecção (Comercial)</span>
              <span class="text-sm font-bold text-amber-400 font-sans">R$ {fmt(tot_viag_prosp)}</span>
            </div>
            <p class="text-xs text-gray-500 leading-relaxed mt-2">A despesa com prospecção é investimento comercial não reembolsável e não impacta o NET operacional.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ──────── SECTION 7: SÍNTESE EXECUTIVA ──────── -->
  <section class="scroll-mt-24" id="sintese">
    <div class="mb-6">
      <h2 class="text-xl font-display font-bold text-white flex items-center gap-3">
        <div class="w-1.5 h-6 bg-brand-blue rounded-full"></div>
        Síntese Executiva & Parecer do Controller
      </h2>
      <p class="text-xs text-gray-400 mt-1 ml-4.5">Avaliação estratégica dos pontos fortes, pontos de atenção e mitigação de riscos</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- POSITIVOS -->
      <div class="glass-card rounded-2xl overflow-hidden border border-emerald-500/30">
        <div class="bg-emerald-500/20 px-5 py-3 border-b border-emerald-500/30 text-emerald-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
          <span class="material-symbols-outlined text-sm">check_circle</span> Pontos Positivos
        </div>
        <div class="p-5 space-y-3 text-xs text-gray-300 leading-relaxed">
          <p><strong class="text-white">● Resultado Positivo em Agosto:</strong> Com R$ +286,7k de resultado líquido, Agosto foi o melhor mês do ano, sinalizando uma trajetória consistente de melhora operacional no 2º semestre.</p>
          <p><strong class="text-white">● Faturamento Sustentado no 2º Semestre:</strong> Julho (R$ 1,008M) e Agosto (R$ 962,8k) mantiveram a receita em níveis elevados, demonstrando robustez na carteira de projetos ativa.</p>
          <p><strong class="text-white">● Redução do Déficit Acumulado:</strong> O resultado YTD evoluiu de -R$ 759k em Junho para -R$ 473k em Agosto, uma melhora de R$ +286k em apenas dois meses — tendência que, se mantida, pode zerar o déficit até o encerramento do ano.</p>
          <p><strong class="text-white">● Reembolso Eficiente de Viagens:</strong> Das despesas brutas com viagens (R$ 944,5k YTD), R$ 716k foram reembolsados pelos clientes — taxa de recuperação de 75,8%, reduzindo o impacto líquido significativamente.</p>
        </div>
      </div>

      <!-- ATENÇÃO -->
      <div class="glass-card rounded-2xl overflow-hidden border border-amber-500/30">
        <div class="bg-amber-500/20 px-5 py-3 border-b border-amber-500/30 text-amber-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
          <span class="material-symbols-outlined text-sm">warning</span> Pontos de Atenção
        </div>
        <div class="p-5 space-y-3 text-xs text-gray-300 leading-relaxed">
          <p><strong class="text-white">● Margem Bruta Abaixo do Potencial:</strong> A Margem Bruta YTD de 45,8% indica pressão de custos diretos — em especial consultores e comissões. Recomenda-se revisar a estrutura de precificação dos contratos para elevar a margem para o patamar ideal de 50–55%.</p>
          <p><strong class="text-white">● Custo Fixo Elevado Proporcionalmente:</strong> Funcionários, aluguel, contabilidade e despesas adm. juntos consomem parcela substancial da Receita Líquida. Avaliar oportunidades de ganho de eficiência — como renegocição de contratos de aluguel ou serviços de TI — pode liberar margem operacional.</p>
          <p><strong class="text-white">● Receita Financeira Não Recorrente:</strong> R$ 229,1k de rendimentos de aplicações foram registrados em Agosto. Esse valor, embora positivo, é pontual e não deve ser utilizado como base para projeções futuras de resultado.</p>
        </div>
      </div>

      <!-- RISCOS -->
      <div class="glass-card rounded-2xl overflow-hidden border border-rose-500/30">
        <div class="bg-rose-500/20 px-5 py-3 border-b border-rose-500/30 text-rose-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
          <span class="material-symbols-outlined text-sm">error</span> Riscos &amp; Recomendações
        </div>
        <div class="p-5 space-y-3 text-xs text-gray-300 leading-relaxed">
          <p><strong class="text-white">● Déficit YTD Requer Atenção Continuáda:</strong> O acumulado de -R$ 472,6k em 8 meses exige resultado médio de +R$ 236k nos próximos 4 meses para fechar o ano no zero. Setembro e Outubro são críticos para essa trajetória.</p>
          <p><strong class="text-white">● Gestão do Fluxo de Caixa:</strong> O resultado YTD acumulado de -R$ 472,6k reforça a necessidade de priorizar contratos de maior rentabilidade e antecipar recebíveis nos meses seguintes, garantindo liquidez operacional para o 2º semestre.</p>
          <p><strong class="text-white">● Concentração de Receita por UN:</strong> Dependência elevada de poucos projetos ou unidades de negócio representa risco de ruptura caso haja não-renovação de contratos. Recomenda-se acelerar a diversificação da carteira comercial.</p>
          <p><strong class="text-white">● Encargos Financeiros (Juros + Tarifas):</strong> R$ 70,7k YTD em juros e tarifas bancárias (média R$ 8,8k/mês). Consolidar operações e negociar tarifas com os bancos pode gerar economia anual estimada acima de R$ 20k.</p>
        </div>
      </div>
    </div>
  </section>

</main>

<!-- FOOTER -->
<footer class="bg-slate-950 border-t border-white/10 py-8 px-6 text-center text-xs text-gray-400">
  <div class="max-w-[1440px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <img alt="NNÓS Logo" class="h-10 w-auto object-contain opacity-90" src="{LOGO_B64_WHITE}"/>
      <span class="font-bold text-white">NNÓS Business Solutions</span>
    </div>
    <div>Relatório Financeiro Gerencial • Período: Janeiro a Agosto de 2026</div>
    <div class="text-[11px] text-gray-500">Controladoria & Gestão Financeira</div>
  </div>
</footer>

</div><!-- END #report-wrapper -->

<script>
// CHART.JS FATURAMENTO MENSAL
let chartFaturamentoInstance = null;

function initFaturamentoChart() {{
  const ctxFaturamento = document.getElementById('chartFaturamento');
  if (ctxFaturamento) {{
    if (chartFaturamentoInstance) {{
      chartFaturamentoInstance.destroy();
    }}
    chartFaturamentoInstance = new Chart(ctxFaturamento, {{
      type: 'bar',
      data: {{
        labels: ['Jan/26', 'Fev/26', 'Mar/26', 'Abr/26', 'Mai/26', 'Jun/26', 'Jul/26', 'Ago/26'],
        datasets: [{{
          label: 'Receita Bruta (R$)',
          data: [{", ".join(str(round(x, 2)) for x in d['rec_bruta'])}],
          backgroundColor: 'rgba(0, 131, 202, 0.85)',
          borderColor: '#0083ca',
          borderWidth: 1.5,
          borderRadius: 6
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                return 'Receita: R$ ' + context.raw.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
              }}
            }}
          }}
        }},
        scales: {{
          y: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
            ticks: {{ color: '#9CA3AF', font: {{ family: 'Inter', size: 11 }} }}
          }},
          x: {{
            grid: {{ display: false }},
            ticks: {{ color: '#9CA3AF', font: {{ family: 'Inter', size: 11 }} }}
          }}
        }}
      }}
    }});
  }}
}}

// AUTHENTICATION SECURITY GATE (SHA-256)
const AUTH_USER_HASH = "{USER_HASH}";
const AUTH_PASS_HASH = "{PASS_HASH}";

async function sha256(str) {{
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}}

async function handleLogin(e) {{
  e.preventDefault();
  const u = document.getElementById('login-user').value.trim();
  const p = document.getElementById('login-pass').value;
  const uHash = await sha256(u);
  const pHash = await sha256(p);

  if (uHash === AUTH_USER_HASH && pHash === AUTH_PASS_HASH) {{
    sessionStorage.setItem('nnos_auth', 'true');
    unlockDashboard();
  }} else {{
    document.getElementById('login-error').classList.remove('hidden');
  }}
}}

function unlockDashboard() {{
  const overlay = document.getElementById('login-overlay');
  const wrapper = document.getElementById('report-wrapper');
  if (overlay) overlay.classList.add('hidden');
  if (wrapper) wrapper.classList.remove('hidden');
  setTimeout(initFaturamentoChart, 50);
}}

function logout() {{
  sessionStorage.removeItem('nnos_auth');
  location.reload();
}}

// Check active session on page load & observe chart visibility
document.addEventListener('DOMContentLoaded', () => {{
  if (sessionStorage.getItem('nnos_auth') === 'true') {{
    unlockDashboard();
  }}

  const canvas = document.getElementById('chartFaturamento');
  if (canvas && 'IntersectionObserver' in window) {{
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          initFaturamentoChart();
        }}
      }});
    }}, {{ threshold: 0.1 }});
    observer.observe(canvas);
  }}
}});
</script>

</body>
</html>
'''

target_filename = '2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html'
with open(target_filename, 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f"Relatório Matriz atualizado em: {target_filename}")

# Atualiza automaticamente o Portal Integrado (Hub de Seleção + Matriz + UVA) no index.html
try:
    import build_portal
    build_portal.build()
    print("Portal Integrado index.html atualizado automaticamente com sucesso!")
except Exception as e:
    print(f"Aviso: execute build_portal.py para atualizar o index.html ({e})")
