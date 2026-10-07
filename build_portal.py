import os
import re
import json
import shutil

repo_dir = os.path.dirname(os.path.abspath(__file__))
matriz_file = os.path.join(repo_dir, "2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html")
matriz_target = os.path.join(repo_dir, "matriz.html")
uva_file = os.path.join(repo_dir, "contas-a-pagar-uva.html")
uva_target = os.path.join(repo_dir, "uva.html")
booking_file = os.path.join(repo_dir, "dashboard-executivo-booking.html")
booking_target = os.path.join(repo_dir, "booking.html")
prospeccao_file = os.path.join(repo_dir, "dashboard-executivo-prospeccao.html")
prospeccao_target = os.path.join(repo_dir, "prospeccao.html")
lider_file = os.path.join(repo_dir, "painel-por-lider.html")
lider_target = os.path.join(repo_dir, "lider.html")
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

favicon_tags = """<link rel="icon" type="image/png" href="assets/logo-nnos.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png"/>
<link rel="icon" type="image/png" sizes="64x64" href="favicon.png"/>
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon"/>
<link rel="apple-touch-icon" href="assets/logo-nnos.png"/>"""

def ensure_favicon(html):
    if 'rel="icon"' not in html and '</head>' in html:
        return html.replace('</head>', favicon_tags + '\n</head>')
    return html

def build():
    # 1. Sync Matriz
    if os.path.exists(matriz_file):
        with open(matriz_file, "r", encoding="utf-8") as f:
            matriz_raw = f.read()
        matriz_raw = ensure_favicon(matriz_raw)
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
        uva_raw = ensure_favicon(uva_raw)
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
        booking_raw = ensure_favicon(booking_raw)
        if 'sessionStorage.getItem' not in booking_raw:
            booking_raw = booking_raw.replace('</head>', auth_script + '</head>')
        with open(booking_target, "w", encoding="utf-8") as f:
            f.write(booking_raw)
        with open(booking_file, "w", encoding="utf-8") as f:
            f.write(booking_raw)

    # 4. Sync Prospeccao
    if os.path.exists(prospeccao_file):
        with open(prospeccao_file, "r", encoding="utf-8") as f:
            prosp_raw = f.read()
        prosp_raw = ensure_favicon(prosp_raw)
        if 'sessionStorage.getItem' not in prosp_raw:
            prosp_raw = prosp_raw.replace('</head>', auth_script + '</head>')
        with open(prospeccao_target, "w", encoding="utf-8") as f:
            f.write(prosp_raw)
        with open(prospeccao_file, "w", encoding="utf-8") as f:
            f.write(prosp_raw)

    # 5. Sync Painel por Líder
    if os.path.exists(lider_file):
        with open(lider_file, "r", encoding="utf-8") as f:
            lider_raw = f.read()
        lider_raw = ensure_favicon(lider_raw)
        if 'sessionStorage.getItem' not in lider_raw:
            lider_raw = lider_raw.replace('</head>', auth_script + '</head>')
        with open(lider_target, "w", encoding="utf-8") as f:
            f.write(lider_raw)
        with open(lider_file, "w", encoding="utf-8") as f:
            f.write(lider_raw)

    # 6. Sync Index Cards
    if os.path.exists(output_index):
        with open(output_index, "r", encoding="utf-8") as f:
            index_raw = f.read()

        # Update Card 1 from calculated_data.json
        calc_path = os.path.join(repo_dir, "calculated_data.json")
        if os.path.exists(calc_path):
            with open(calc_path, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            num_m = cdata.get('num_months', 8)
            last_m = cdata.get('month_names', ['Ago'])[-1]
            rec_ytd = sum(cdata.get('rec_bruta', []))
            marg_ytd = sum(cdata.get('margem_bruta', []))
            pct_marg = (marg_ytd / rec_ytd * 100) if rec_ytd > 0 else 0
            
            rec_ytd_str = f"R$ {rec_ytd/1e6:.2f}M".replace('.', ',')
            pct_marg_str = f"{pct_marg:.1f}%".replace('.', ',')
            period_str = f"{num_m} Meses"
            desc_m = f"Demonstrativo de Resultados acumulado de {num_m} meses (Jan a {last_m}/2026), Faturamento Mensal, Análise por Unidades de Negócio, Centros de Custo, Viagens & Reembolsos e Síntese Executiva."
            
            # Card 1 description and KPIs
            index_raw = re.sub(
                r'Demonstrativo de Resultados acumulado de \d+ meses \([^)]+\)[^<]+',
                desc_m,
                index_raw
            )
            card1_pattern = r'(<!-- Card 1: Relatório Matriz.*?Receita YTD</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Margem Bruta</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Período</div>\s*<div class="[^"]*">)[^<]+(</div>)'
            def replace_card1(m):
                return f"{m.group(1)}{rec_ytd_str}{m.group(2)}{pct_marg_str}{m.group(3)}{period_str}{m.group(4)}"
            index_raw = re.sub(card1_pattern, replace_card1, index_raw, flags=re.DOTALL)

        # Update Card 2 from UVA html
        if os.path.exists(uva_file):
            with open(uva_file, "r", encoding="utf-8") as f:
                uva_content = f.read()
            m_badge = re.search(r'<span class="material-symbols-outlined text-emerald-400 text-sm">update</span>\s*([A-Z]{3}/\d{4})', uva_content)
            m_tot = re.search(r'Total:\s*R\$\s*([0-9.,]+)', uva_content)
            m_quit = re.search(r'Quitado: R\$\s*[0-9.,]+\s*\(([0-9.,]+)%\)', uva_content)
            m_imob = re.search(r'Imobilizado &amp; Reforma</div>\s*</div>\s*<div class="[^"]*">R\$\s*([0-9.,]+)', uva_content)
            
            uva_ref = m_badge.group(1) if m_badge else "SET/2026"
            if m_tot:
                tot_num = float(m_tot.group(1).replace('.', '').replace(',', '.'))
                uva_tot_str = f"R$ {tot_num/1e3:.1f}K".replace('.', ',')
            else:
                uva_tot_str = "R$ 765,9K"
            uva_quit_str = f"{m_quit.group(1)}%" if m_quit else "94,51%"
            if m_imob:
                imob_num = float(m_imob.group(1).replace('.', '').replace(',', '.'))
                uva_imob_str = f"R$ {imob_num/1e3:.1f}K".replace('.', ',')
            else:
                uva_imob_str = "R$ 337,8K"

            # Badge Card 2
            index_raw = re.sub(
                r'Campus BH UVA • [A-Z]{3}/\d{4}',
                f'Campus BH UVA • {uva_ref}',
                index_raw
            )
            card2_pattern = r'(<!-- Card 2: Campus BH UVA.*?Total Geral</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Taxa Quitação</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Imobilizado</div>\s*<div class="[^"]*">)[^<]+(</div>)'
            def replace_card2(m):
                return f"{m.group(1)}{uva_tot_str}{m.group(2)}{uva_quit_str}{m.group(3)}{uva_imob_str}{m.group(4)}"
            index_raw = re.sub(card2_pattern, replace_card2, index_raw, flags=re.DOTALL)

        # Update Card 4 from prospeccao_data.json
        prosp_json = os.path.join(repo_dir, "prospeccao_data.json")
        if os.path.exists(prosp_json):
            with open(prosp_json, "r", encoding="utf-8") as f:
                p_items = json.load(f)
            p_total = sum(it["valor"] for it in p_items)
            p_count = len(p_items)
            p_prosp = sum(it["valor"] for it in p_items if it.get("categoria") == "Prospecção")
            
            p_total_str = f"R$ {p_total/1e3:.1f}K".replace('.', ',')
            p_prosp_str = f"R$ {p_prosp/1e3:.1f}K".replace('.', ',')
            
            card4_pattern = r'(<!-- Card 4: Despesas Operacionais.*?Total Geral</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Atividades</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Prospecção</div>\s*<div class="[^"]*">)[^<]+(</div>)'
            def replace_card4(m):
                return f"{m.group(1)}{p_total_str}{m.group(2)}{p_count}{m.group(3)}{p_prosp_str}{m.group(4)}"
            index_raw = re.sub(card4_pattern, replace_card4, index_raw, flags=re.DOTALL)

        # Update Card 5 from lider_data.json
        lider_json = os.path.join(repo_dir, "lider_data.json")
        if os.path.exists(lider_json):
            with open(lider_json, "r", encoding="utf-8") as f:
                l_data = json.load(f)
            l_summary = l_data.get("summary", {})
            l_tot_rec = l_summary.get("total_receita", 0)
            l_tot_proj = l_summary.get("total_projetos", 0)
            l_tot_leaders = l_summary.get("total_leaders", 0)
            
            l_tot_rec_str = f"R$ {l_tot_rec/1e6:.2f}M".replace('.', ',')
            
            card5_pattern = r'(<!-- Card 5: Painel por Líder.*?Líderes</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Projetos</div>\s*<div class="[^"]*">)[^<]+(</div>.*?Receita Total</div>\s*<div class="[^"]*">)[^<]+(</div>)'
            def replace_card5(m):
                return f"{m.group(1)}{l_tot_leaders}{m.group(2)}{l_tot_proj}{m.group(3)}{l_tot_rec_str}{m.group(4)}"
            index_raw = re.sub(card5_pattern, replace_card5, index_raw, flags=re.DOTALL)

        index_updated = ensure_favicon(index_raw)
        with open(output_index, "w", encoding="utf-8") as f:
            f.write(index_updated)

    print("Portal e demonstrativos independentes (matriz.html, uva.html, booking.html, prospeccao.html, lider.html, index.html) sincronizados com sucesso!")

if __name__ == "__main__":
    build()
