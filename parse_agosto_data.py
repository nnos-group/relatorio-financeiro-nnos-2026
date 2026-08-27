import csv
import json
import unicodedata
from collections import defaultdict

def norm(s):
    if not s:
        return ''
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def parse_num(val_str):
    if not val_str or val_str.strip() in ['-', '', ' - ', '—']:
        return 0.0
    cleaned = val_str.strip().replace('.', '').replace(',', '.')
    try:
        return float(cleaned)
    except:
        return 0.0

month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago']

# 1. RECEITA
rec_bruta = [0.0] * 8
un_ytd = defaultdict(float)
proj_ytd = defaultdict(float)

month_map = {
    'JANEIRO': 0, 'FEVEREIRO': 1, 'MARCO': 2,
    'ABRIL': 3, 'MAIO': 4, 'JUNHO': 5, 'JULHO': 6, 'AGOSTO': 7
}

with open('Agosto - Receita JAN-AGO.csv', 'r', encoding='cp1252') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for row in reader:
        if len(row) >= 6:
            m_str = norm(row[0]).upper()
            proj = row[1].strip()
            val = parse_num(row[4])
            un = row[5].strip()
            
            if m_str in month_map:
                m_idx = month_map[m_str]
                rec_bruta[m_idx] += val
                if un:
                    un_ytd[un] += val
                if proj:
                    proj_ytd[proj] += val

# Sort Top Projects
top_proj = sorted(proj_ytd.items(), key=lambda x: x[1], reverse=True)[:10]

# 2. DESPESAS
impostos_tot = [0.0] * 8
custo_consultores = [0.0] * 8
comissoes = [0.0] * 8
viagens_desp = [0.0] * 8
funcionarios = [0.0] * 8
desp_adm = [0.0] * 8
aluguel = [0.0] * 8
contabilidade = [0.0] * 8
desp_operacionais = [0.0] * 8
juros_tarifas = [0.0] * 8
viag_op = [0.0] * 8
viag_prosp = [0.0] * 8

cc_ytd = defaultdict(float)

with open('Agosto - Base Despesas Jan-Ago.csv', 'r', encoding='cp1252') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for row in reader:
        if len(row) >= 13:
            dash_n = norm(row[0])
            dre_n = norm(row[1])
            gest_n = norm(row[2])
            cc = row[3].strip()
            orig_n = norm(row[4])
            
            vals = [parse_num(row[i]) for i in range(5, 13)]
            tot_row = sum(vals)
            if cc:
                cc_ytd[cc] += tot_row
                
            for i in range(8):
                v = vals[i]
                
                if dash_n == 'impostos':
                    impostos_tot[i] += v
                elif dash_n == 'consultor':
                    custo_consultores[i] += v
                elif 'comiss' in dash_n or 'comiss' in orig_n:
                    comissoes[i] += v
                elif dash_n == 'viagens':
                    viagens_desp[i] += v
                    if 'prospec' in cc.lower() or 'prospec' in orig_n or 'prospec' in gest_n:
                        viag_prosp[i] += v
                    else:
                        viag_op[i] += v
                elif dash_n == 'funcionarios':
                    funcionarios[i] += v
                elif dash_n == 'despesa adm.':
                    desp_adm[i] += v
                elif dash_n == 'aluguel':
                    aluguel[i] += v
                elif dash_n == 'contabilidade':
                    contabilidade[i] += v
                elif dash_n == 'despesas operacionais':
                    desp_operacionais[i] += v
                elif dash_n == 'despesa financeira' or 'financeir' in dash_n:
                    if 'juros' in orig_n or 'tarifa' in orig_n:
                        juros_tarifas[i] += v
# Apply PIS/COFINS (6.15%) on revenue and add to total taxes
pis_cofins = [rec_bruta[i] * 0.0615 for i in range(8)]
for i in range(8):
    impostos_tot[i] += pis_cofins[i]

# 3. REEMBOLSO E APLICAÇÃO
reembolso_viagens = [0.0] * 8
receita_financeira = [0.0] * 8

with open('Agosto - Reembolso e Aplicação.csv', 'r', encoding='cp1252') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)
    for row in reader:
        if len(row) >= 13:
            dash_n = norm(row[0])
            orig_n = norm(row[4])
            vals = [parse_num(row[i]) for i in range(5, 13)]
            
            for i in range(8):
                v = vals[i]
                if dash_n == 'reembolso':
                    reembolso_viagens[i] += v
                elif 'rendimentos' in orig_n or dash_n == 'resultado financeiro':
                    receita_financeira[i] += v
                elif ('despesa financeira' in dash_n or 'financeir' in dash_n) and ('juros' in orig_n or 'tarifa' in orig_n):
                    juros_tarifas[i] += v

# DERIVED METRICS
rec_liquida = [rec_bruta[i] - impostos_tot[i] for i in range(8)]
margem_bruta = [rec_liquida[i] - (custo_consultores[i] + comissoes[i] + viagens_desp[i] - reembolso_viagens[i]) for i in range(8)]
margem_bruta_pct = [(margem_bruta[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(8)]

custo_fixo_tot = [funcionarios[i] + desp_adm[i] + aluguel[i] + contabilidade[i] for i in range(8)]
ebitda = [margem_bruta[i] - custo_fixo_tot[i] - desp_operacionais[i] for i in range(8)]
ebitda_pct = [(ebitda[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(8)]

res_financeiro = [receita_financeira[i] - juros_tarifas[i] for i in range(8)]
resultado_periodo = [ebitda[i] + res_financeiro[i] for i in range(8)]
resultado_pct = [(resultado_periodo[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(8)]

top_cc = sorted(cc_ytd.items(), key=lambda x: x[1], reverse=True)[:7]

output_data = {
    "rec_bruta": rec_bruta,
    "impostos_tot": impostos_tot,
    "rec_liquida": rec_liquida,
    "custo_consultores": custo_consultores,
    "comissoes": comissoes,
    "viagens_desp": viagens_desp,
    "reembolso_viagens": reembolso_viagens,
    "margem_bruta": margem_bruta,
    "margem_bruta_pct": margem_bruta_pct,
    "funcionarios": funcionarios,
    "desp_adm": desp_adm,
    "aluguel": aluguel,
    "contabilidade": contabilidade,
    "custo_fixo_tot": custo_fixo_tot,
    "desp_operacionais": desp_operacionais,
    "ebitda": ebitda,
    "ebitda_pct": ebitda_pct,
    "receita_financeira": receita_financeira,
    "juros_tarifas": juros_tarifas,
    "res_financeiro": res_financeiro,
    "resultado_periodo": resultado_periodo,
    "resultado_pct": resultado_pct,
    "viag_op": viag_op,
    "viag_prosp": viag_prosp,
    "un_ytd": dict(un_ytd),
    "top_proj": top_proj,
    "top_cc": top_cc
}

with open('calculated_data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("calculated_data.json updated successfully with robust normalization!")
