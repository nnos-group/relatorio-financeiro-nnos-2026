import os
import re
import shutil

repo_dir = os.path.dirname(os.path.abspath(__file__))
matriz_file = os.path.join(repo_dir, "2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html")
matriz_target = os.path.join(repo_dir, "matriz.html")
uva_file = os.path.join(repo_dir, "contas-a-pagar-uva.html")
uva_target = os.path.join(repo_dir, "uva.html")
booking_file = os.path.join(repo_dir, "dashboard-executivo-booking.html")
booking_target = os.path.join(repo_dir, "booking.html")
output_index = os.path.join(repo_dir, "index.html")

auth_script = """
<script>
  if (sessionStorage.getItem('nnos_auth') !== 'true') {
    window.location.href = 'index.html';
  }
  function logout() {
    sessionStorage.removeItem('nnos_auth');
    window.location.href = 'index.html';
  }

  // 🛡️ Bloqueio de DevTools e Menu de Contexto
  document.addEventListener('contextmenu', function(e) { e.preventDefault(); }, false);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'F12' || e.keyCode === 123) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (
      e.key === 'I' || e.key === 'i' || e.keyCode === 73 ||
      e.key === 'J' || e.key === 'j' || e.keyCode === 74 ||
      e.key === 'C' || e.key === 'c' || e.keyCode === 67
    )) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'U' || e.key === 'u' || e.keyCode === 85)) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'S' || e.key === 's' || e.keyCode === 83)) { e.preventDefault(); e.stopPropagation(); return false; }
  }, false);
</script>
"""

def build():
    # 1. Sync Matriz
    if os.path.exists(matriz_file):
        with open(matriz_file, "r", encoding="utf-8") as f:
            matriz_raw = f.read()
        if 'sessionStorage.getItem' not in matriz_raw:
            matriz_raw = matriz_raw.replace('</head>', auth_script + '</head>')
        
        with open(matriz_target, "w", encoding="utf-8") as f:
            f.write(matriz_raw)
        with open(matriz_file, "w", encoding="utf-8") as f:
            f.write(matriz_raw)

    # 2. Sync UVA
    if os.path.exists(uva_file):
        with open(uva_file, "r", encoding="utf-8") as f:
            uva_raw = f.read()
        if 'sessionStorage.getItem' not in uva_raw:
            uva_raw = uva_raw.replace('</head>', auth_script + '</head>')
        with open(uva_target, "w", encoding="utf-8") as f:
            f.write(uva_raw)
        with open(uva_file, "w", encoding="utf-8") as f:
            f.write(uva_raw)

    # 3. Sync Booking
    if os.path.exists(booking_file):
        with open(booking_file, "r", encoding="utf-8") as f:
            booking_raw = f.read()
        if 'sessionStorage.getItem' not in booking_raw:
            booking_raw = booking_raw.replace('</head>', auth_script + '</head>')
        with open(booking_target, "w", encoding="utf-8") as f:
            f.write(booking_raw)
        with open(booking_file, "w", encoding="utf-8") as f:
            f.write(booking_raw)

    print("Portal e demonstrativos independentes (matriz.html, uva.html, booking.html, index.html) sincronizados com sucesso!")

if __name__ == "__main__":
    build()
