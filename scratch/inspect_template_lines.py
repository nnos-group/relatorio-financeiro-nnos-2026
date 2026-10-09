import os

template_path = os.path.abspath("../Booking - Dashboard Executivo de Performance/src/index.template.html")
with open(template_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(302, 316):
    if i < len(lines):
        print(f"Line {i+1}: {repr(lines[i])}")
