import os
import re
import base64

repo_dir = os.path.dirname(os.path.abspath(__file__))
uva_file = r"c:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\UVA\NNÓS Group _ Contas a Pagar - Campus BH UVA.html"
matriz_file = os.path.join(repo_dir, "2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html")
booking_file = os.path.join(repo_dir, "dashboard-executivo-booking.html")
output_index = os.path.join(repo_dir, "index.html")

def build():
    with open(matriz_file, "r", encoding="utf-8") as f:
        matriz_raw = f.read()

    # Extrair partes do Matriz
    m_header_idx = matriz_raw.find('<header class="relative overflow-hidden')
    m_main_idx = matriz_raw.find('<main class="max-w-[1440px]')
    m_footer_idx = matriz_raw.find('<footer class="bg-slate-950')
    m_footer_end_idx = matriz_raw.find('</footer>', m_footer_idx) + 9

    matriz_header = matriz_raw[m_header_idx:m_main_idx]
    matriz_main = matriz_raw[m_main_idx:m_footer_idx]
    matriz_footer = matriz_raw[m_footer_idx:m_footer_end_idx]

    matriz_nav_rep = """
      <div class="flex items-center gap-2.5 ml-auto">
        <button onclick="showView('uva')" class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-sky-200 bg-sky-500/20 hover:bg-sky-500/30 border border-sky-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm text-sky-300">account_balance_wallet</span>
          <span>Campus BH UVA</span>
          <span class="material-symbols-outlined text-xs">arrow_forward</span>
        </button>
        <button onclick="showView('booking')" class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-emerald-300 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
          <span class="material-symbols-outlined text-sm text-emerald-300">query_stats</span>
          <span>Performance Projetos</span>
          <span class="material-symbols-outlined text-xs">arrow_forward</span>
        </button>
        <button onclick="showView('hub')" class="px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">grid_view</span> Menu
        </button>
        <button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-300 hover:bg-rose-500/20 border border-rose-500/30 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">lock</span> Sair
        </button>
      </div>
"""
    matriz_header = re.sub(r'<button onclick="logout\(\)"[\s\S]*?<\/button>', matriz_nav_rep, matriz_header)
    new_matriz_view_inner = f"\n{matriz_header}\n{matriz_main}\n{matriz_footer}\n"

    if os.path.exists(output_index):
        with open(output_index, "r", encoding="utf-8") as f:
            index_content = f.read()

        # Substituir o contêiner #view-matriz no index.html se existir
        pattern = r'(<div[^>]*id=["\']view-matriz["\'][^>]*>)([\s\S]*?)(</div>\s*<!-- \d+\. VIEW UVA|</div>\s*<!-- 3\. VIEW BOOKING|<div[^>]*id=["\']view-uva["\'])'
        if re.search(pattern, index_content):
            def repl(m):
                return m.group(1) + new_matriz_view_inner + m.group(3)
            index_content = re.sub(pattern, repl, index_content)
            
            # Garantir texto da fonte sem duplicidade
            index_content = index_content.replace(
                ' - Fonte Conta Azul - Fonte Conta Azul',
                ' - Fonte Conta Azul'
            )

            with open(output_index, "w", encoding="utf-8") as f:
                f.write(index_content)
            print(f"Portal Integrado (index.html) atualizado preservando os 3 relatórios!")
            return

    print("Portal Integrado (index.html) mantido.")

if __name__ == "__main__":
    build()
