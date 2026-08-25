import re

with open('2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Verificar se imagem hero foi removida
print('=== AJUSTE 1: IMAGEM HERO ===')
header = text.split('</header>')[0]
# Procurar por qualquer tag <img que tenha 'background' ou foto de pessoa
has_hero_img = 'background-image' in header
# Contar imagens no header
img_count = header.count('<img')
print(f'Quantidade de imagens no header: {img_count}')
# Verificar se a imagem da mulher/hero esta presente
has_woman_photo = 'woman' in header.lower() or 'hero' in header.lower() or 'gestao' in header.lower()
print(f'Foto hero/mulher no header: {has_woman_photo}')
# O logo NNOS ainda deve estar la
has_logo = 'NNÓS Logo' in header or 'nnos' in header.lower()
print(f'Logo NNÓS presente: {has_logo}')

# 2. Verificar tamanho de fonte dos numeros na DRE
print()
print('=== AJUSTE 2: FONTE MAIOR NOS NUMEROS ===')
print(f'Ocorrencias de text-sm font-sans (novo): {text.count("text-sm font-sans")}')
print(f'Ocorrencias de text-xs font-mono (antigo): {text.count("text-xs font-mono")}')

# 3. Verificar cor verde nos numeros
print()
print('=== AJUSTE 3: NUMEROS VERDES ===')
print(f'Ocorrencias de text-emerald-400 font-bold: {text.count("text-emerald-400 font-bold")}')

# 4. Verificar CAMPUS BH simplificado
print()
print('=== AJUSTE 4: CAMPUS BH SIMPLIFICADO ===')
has_full_name = 'CAMPUS BH (UNIV. VEIGA DE ALMEIDA)' in text
has_short_name = 'CAMPUS BH' in text
print(f'Nome completo AINDA presente: {has_full_name}')
print(f'Nome curto CAMPUS BH presente: {has_short_name}')

# Mostrar contexto de cada ocorrencia
idx = 0
while True:
    pos = text.find('CAMPUS BH', idx)
    if pos == -1:
        break
    snippet = text[pos:pos+60].replace('\n', ' ')
    print(f'  -> Contexto: ...{snippet}...')
    idx = pos + 1

print()
print('=== RESUMO ===')
all_ok = True
if img_count <= 1 and not has_woman_photo:
    print('[OK] Ajuste 1: Imagem hero REMOVIDA do header')
else:
    print('[!!] Ajuste 1: Pode haver imagem hero no header')
    all_ok = False

if text.count('text-sm font-sans') > 10 and text.count('text-xs font-mono') == 0:
    print('[OK] Ajuste 2: Fonte dos numeros MAIOR (text-sm)')
else:
    print('[!!] Ajuste 2: Verificar tamanho da fonte')
    all_ok = False

if text.count('text-emerald-400 font-bold') > 5:
    print('[OK] Ajuste 3: Numeros em VERDE (emerald-400)')
else:
    print('[!!] Ajuste 3: Verificar cor verde')
    all_ok = False

if not has_full_name and has_short_name:
    print('[OK] Ajuste 4: CAMPUS BH simplificado corretamente')
else:
    print('[!!] Ajuste 4: Verificar nome CAMPUS BH')
    all_ok = False

if all_ok:
    print('\n*** TODOS OS 4 AJUSTES APLICADOS COM SUCESSO! ***')
