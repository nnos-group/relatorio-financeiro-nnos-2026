import os

path = os.path.abspath("../Booking - Dashboard Executivo de Performance/scripts/build-dashboard.mjs")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('writeFileSync')
print(content[idx-400:idx+200])
