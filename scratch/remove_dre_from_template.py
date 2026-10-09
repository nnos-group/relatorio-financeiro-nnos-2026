import os
import re

template_path = os.path.abspath("../Booking - Dashboard Executivo de Performance/src/index.template.html")
with open(template_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remover link nav <a href="#dre">...</a>
content = re.sub(r'<a href="#dre">.*?</a>', '', content)

# 2. Remover <section class="section" id="dre">...</section>
section_pattern = r'<section class="section" id="dre">.*?</section>\s*'
content = re.sub(section_pattern, '', content, flags=re.DOTALL)

# 3. Remover new Chart para dreChart e logChart
chart_dre_pattern = r'new Chart\(document\.getElementById\([\'"]dreChart[\'"]\),\{.*?\n'
chart_log_pattern = r'new Chart\(document\.getElementById\([\'"]logChart[\'"]\),\{.*?\n'

content = re.sub(r"new Chart\(document\.getElementById\('dreChart'\),\{.*?\}\);\n*", '', content)
content = re.sub(r"new Chart\(document\.getElementById\('logChart'\),\{.*?\}\);\n*", '', content)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] Template atualizado sem a seção e gráficos de Resultado consolidado ajustado.")
