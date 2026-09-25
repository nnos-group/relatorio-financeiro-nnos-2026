import os
import glob
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

MONTH_ORDER = [
    ('JANEIRO', 'Jan', 'JAN-26'),
    ('FEVEREIRO', 'Fev', 'FEV-26'),
    ('MARCO', 'Mar', 'MAR-26'),
    ('ABRIL', 'Abr', 'ABR-26'),
    ('MAIO', 'Mai', 'MAI-26'),
    ('JUNHO', 'Jun', 'JUN-26'),
    ('JULHO', 'Jul', 'JUL-26'),
    ('AGOSTO', 'Ago', 'AGO-26'),
    ('SETEMBRO', 'Set', 'SET-26'),
    ('OUTUBRO', 'Out', 'OUT-26'),
    ('NOVEMBRO', 'Nov', 'NOV-26'),
    ('DEZEMBRO', 'Dez', 'DEZ-26')
]

month_map = {item[0]: idx for idx, item in enumerate(MONTH_ORDER)}

def run():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Encontrar os arquivos CSV mais recentes
    # Preferência explícita por Setembro se existir, ou o mais recente modificado
    desp_files = sorted(glob.glob(os.path.join(repo_dir, "*Base Despesas*.csv")), key=os.path.getmtime, reverse=True)
    rec_files = sorted(glob.glob(os.path.join(repo_dir, "*Receita*.csv")), key=os.path.getmtime, reverse=True)
    reemb_files = sorted(glob.glob(os.path.join(repo_dir, "*Reembolso*.csv")), key=os.path.getmtime, reverse=True)
    
    if not desp_files or not rec_files or not reemb_files:
        raise FileNotFoundError("Não foi possível localizar os arquivos CSV de Despesas, Receita e Reembolso.")
        
    desp_file = desp_files[0]
    rec_file = rec_files[0]
    reemb_file = reemb_files[0]
    
    print(f"Processando bases financeiras:")
    print(f"  - Receita: {os.path.basename(rec_file)}")
    print(f"  - Despesas: {os.path.basename(desp_file)}")
    print(f"  - Reembolso: {os.path.basename(reemb_file)}")
    
    # Determinar a quantidade de meses analisando o header de despesas
    with open(desp_file, 'r', encoding='cp1252') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        # As primeiras 5 colunas são metadados: Categoria - Dashboard;Categoria - DRE;Categoria Gestional;Centro de custo;Categoria Original
        month_headers = header[5:]
        num_months = len(month_headers)
        
    print(f"Quantidade de meses identificada na base: {num_months}")
    month_names = [MONTH_ORDER[i][1] for i in range(num_months)]
    month_cols = [MONTH_ORDER[i][2] for i in range(num_months)]
    
    # 2. RECEITA
    rec_bruta = [0.0] * num_months
    un_ytd = defaultdict(float)
    proj_ytd = defaultdict(float)
    
    with open(rec_file, 'r', encoding='cp1252') as f:
        reader = csv.reader(f, delimiter=';')
        rec_header = next(reader)
        for row in reader:
            if len(row) >= 6:
                m_str = norm(row[0]).upper()
                proj = row[1].strip()
                val = parse_num(row[4])
                un = row[5].strip()
                
                # Regra de negócio: CAMPUS BH é da UN EDUCAÇÃO
                if 'CAMPUS BH' in proj.upper():
                    un = 'EDUCAÇÃO'
                    
                if m_str in month_map:
                    m_idx = month_map[m_str]
                    if m_idx < num_months:
                        rec_bruta[m_idx] += val
                        if un:
                            un_ytd[un] += val
                        if proj:
                            proj_ytd[proj] += val
                            
    top_proj = sorted(proj_ytd.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 3. DESPESAS
    impostos_tot = [0.0] * num_months
    custo_consultores = [0.0] * num_months
    comissoes = [0.0] * num_months
    viagens_desp = [0.0] * num_months
    funcionarios = [0.0] * num_months
    desp_adm = [0.0] * num_months
    aluguel = [0.0] * num_months
    contabilidade = [0.0] * num_months
    desp_operacionais = [0.0] * num_months
    juros_tarifas = [0.0] * num_months
    viag_op = [0.0] * num_months
    viag_prosp = [0.0] * num_months
    cc_ytd = defaultdict(float)
    
    with open(desp_file, 'r', encoding='cp1252') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader) # header
        for row in reader:
            if len(row) >= 5 + num_months:
                dash_n = norm(row[0])
                dre_n = norm(row[1])
                gest_n = norm(row[2])
                cc = row[3].strip()
                orig_n = norm(row[4])
                
                vals = [parse_num(row[i]) for i in range(5, 5 + num_months)]
                tot_row = sum(vals)
                if cc:
                    cc_ytd[cc] += tot_row
                    
                for i in range(num_months):
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

    # Aplicação de PIS/COFINS (6,15% sobre a receita bruta de cada mês)
    pis_cofins = [rec_bruta[i] * 0.0615 for i in range(num_months)]
    for i in range(num_months):
        impostos_tot[i] += pis_cofins[i]
        
    # 4. REEMBOLSO E APLICAÇÃO
    reembolso_viagens = [0.0] * num_months
    receita_financeira = [0.0] * num_months
    
    with open(reemb_file, 'r', encoding='cp1252') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) >= 5 + num_months:
                dash_n = norm(row[0])
                orig_n = norm(row[4])
                vals = [parse_num(row[i]) for i in range(5, 5 + num_months)]
                for i in range(num_months):
                    v = vals[i]
                    if dash_n == 'reembolso':
                        reembolso_viagens[i] += v
                    elif 'rendimentos' in orig_n or dash_n == 'resultado financeiro':
                        receita_financeira[i] += v
                    elif ('despesa financeira' in dash_n or 'financeir' in dash_n) and ('juros' in orig_n or 'tarifa' in orig_n):
                        juros_tarifas[i] += v

    # 5. DERIVED METRICS
    rec_liquida = [rec_bruta[i] - impostos_tot[i] for i in range(num_months)]
    margem_bruta = [rec_liquida[i] - (custo_consultores[i] + comissoes[i] + viagens_desp[i] - reembolso_viagens[i]) for i in range(num_months)]
    margem_bruta_pct = [(margem_bruta[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(num_months)]

    custo_fixo_tot = [funcionarios[i] + desp_adm[i] + aluguel[i] + contabilidade[i] for i in range(num_months)]
    ebitda = [margem_bruta[i] - custo_fixo_tot[i] - desp_operacionais[i] for i in range(num_months)]
    ebitda_pct = [(ebitda[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(num_months)]

    res_financeiro = [receita_financeira[i] - juros_tarifas[i] for i in range(num_months)]
    resultado_periodo = [ebitda[i] + res_financeiro[i] for i in range(num_months)]
    resultado_pct = [(resultado_periodo[i] / rec_bruta[i] * 100) if rec_bruta[i] > 0 else 0 for i in range(num_months)]

    top_cc = sorted(cc_ytd.items(), key=lambda x: x[1], reverse=True)[:7]

    output_data = {
        "num_months": num_months,
        "month_names": month_names,
        "month_cols": month_cols,
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

    output_path = os.path.join(repo_dir, "calculated_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] calculated_data.json atualizado com sucesso ({num_months} meses analisados: {', '.join(month_names)})!")

if __name__ == "__main__":
    run()
