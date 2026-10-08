import re
import os

repo_dir = r"d:\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\2026 - Relatório Financeiro - NNÓS -26"
uva_file = os.path.join(repo_dir, "contas-a-pagar-uva.html")
uva_target = os.path.join(repo_dir, "uva.html")

with open(uva_file, 'r', encoding='utf-8') as f:
    content = f.read()

css_rule = """
  .logo-dark { display: block; }
  .logo-light { display: none; }
  html.light .logo-dark { display: none !important; }
  html.light .logo-light { display: block !important; }
"""

if '.logo-dark' not in content:
    content = content.replace('</style>', css_rule + '</style>', 1)

content = content.replace('  html.light header img { content: url("assets/logo-nnos.png"); }\n', '')

old_img_pattern = r'<img alt="NNÓS Logo" class="h-16 w-auto object-contain flex-shrink-0 opacity-95" src="data:image/png;base64,[^"]+"/>'
new_img_html = '<img alt="NNÓS Logo" class="logo-dark h-16 w-auto object-contain flex-shrink-0 opacity-95" src="assets/logo-nnos-white.png"/>\n<img alt="NNÓS Logo" class="logo-light h-16 w-auto object-contain flex-shrink-0 opacity-95" src="assets/logo-nnos.png"/>'

if re.search(old_img_pattern, content):
    content = re.sub(old_img_pattern, new_img_html, content)
    print("Replaced base64 logo in contas-a-pagar-uva.html successfully")
else:
    print("Pattern not matched!")

with open(uva_file, 'w', encoding='utf-8') as f:
    f.write(content)

with open(uva_target, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved successfully!")
