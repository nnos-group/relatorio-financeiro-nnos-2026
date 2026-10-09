import json
import csv

proj_to_un = {}
with open('Setembro - Receita JAN-SET.csv', 'r', encoding='cp1252') as f:
    r = csv.reader(f, delimiter=';')
    next(r)
    for row in r:
        if len(row) >= 6:
            p = row[1].strip().upper()
            u = row[5].strip()
            if 'CAMPUS BH' in p:
                u = 'EDUCAÇÃO'
            proj_to_un[p] = u

with open('lider_data.json', 'r', encoding='utf-8') as f:
    ld = json.load(f)

for leader in ld['leaders']:
    lname = leader['nome']
    print(f"=== {lname} ===")
    for p in leader['projetos']:
        p_name = p['titulo'].upper()
        matched = proj_to_un.get(p_name)
        if not matched:
            for k, v in proj_to_un.items():
                if k in p_name or p_name in k:
                    matched = v
                    break
        print(f"  {p['titulo']} -> {matched}")
