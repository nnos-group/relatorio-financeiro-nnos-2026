import os
import re
import base64

repo_dir = os.path.dirname(os.path.abspath(__file__))
uva_file = r"c:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\UVA\NNÓS Group _ Contas a Pagar - Campus BH UVA.html"
matriz_file = os.path.join(repo_dir, "2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html")
output_index = os.path.join(repo_dir, "index.html")

def build():
    # Logo base64
    logo_path = os.path.join(repo_dir, "logo_white_trans.png")
    if not os.path.exists(logo_path):
        logo_path = r"c:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\UVA\logo_white_trans.png"
    
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("ascii")
    logo_src = f"data:image/png;base64,{logo_b64}"

    with open(matriz_file, "r", encoding="utf-8") as f:
        matriz_raw = f.read()

    with open(uva_file, "r", encoding="utf-8") as f:
        uva_raw = f.read()

    # Extrair Matriz
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
        <button onclick="showView('hub')" class="px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">grid_view</span> Menu
        </button>
        <button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-300 hover:bg-rose-500/20 border border-rose-500/30 transition-colors flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-sm">lock</span> Sair
        </button>
      </div>
"""
    matriz_header = re.sub(r'<button onclick="logout\(\)"[\s\S]*?<\/button>', matriz_nav_rep, matriz_header)

    # Extrair UVA
    u_header_idx = uva_raw.find('<header class="relative overflow-hidden')
    u_nav_idx = uva_raw.find('<nav class="sticky top-0')
    u_main_idx = uva_raw.find('<main class="max-w-[1440px]')
    u_footer_idx = uva_raw.find('<footer class="bg-transparent')
    u_footer_end_idx = uva_raw.find('</footer>', u_footer_idx) + 9

    uva_header_only = uva_raw[u_header_idx:u_nav_idx]
    uva_main = uva_raw[u_main_idx:u_footer_idx].replace('id="kpis"', 'id="kpis-uva"')
    uva_footer = uva_raw[u_footer_idx:u_footer_end_idx]

    uva_nav_custom = """
<!-- ═══════════ NAV UVA ═══════════ -->
<nav class="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-surface-variant shadow-lg">
<div class="max-w-[1440px] mx-auto px-6 overflow-x-auto">
<div class="flex items-center justify-between gap-2 py-2.5 min-w-max">
<div class="flex items-center gap-1">
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#kpis-uva"><span class="material-symbols-outlined text-sm text-sky-400">monitoring</span> KPIs</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#execucao"><span class="material-symbols-outlined text-sm text-sky-400">analytics</span> Execução</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#imobilizado"><span class="material-symbols-outlined text-sm text-sky-400">inventory_2</span> Imobilizado & Reforma</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#top10"><span class="material-symbols-outlined text-sm text-sky-400">local_fire_department</span> Top Fornecedores</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#mensal"><span class="material-symbols-outlined text-sm text-sky-400">show_chart</span> Evolução Mensal</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#categorias"><span class="material-symbols-outlined text-sm text-sky-400">category</span> Categorias</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#indicadores"><span class="material-symbols-outlined text-sm text-sky-400">assessment</span> Indicadores</a>
<a class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-text-muted hover:text-white hover:bg-surface-variant transition-colors flex items-center gap-1.5" href="#alertas"><span class="material-symbols-outlined text-sm text-sky-400">warning</span> Alertas</a>
</div>
<div class="flex items-center gap-2.5 ml-auto">
<button onclick="showView('matriz')" class="px-3.5 py-1.5 rounded-lg text-xs font-bold text-brand-blue bg-blue-500/20 hover:bg-blue-500/30 border border-brand-blue/40 transition-all flex items-center gap-1.5 shadow-sm hover:scale-[1.02] cursor-pointer">
  <span class="material-symbols-outlined text-sm text-brand-blue">analytics</span>
  <span>Relatório Matriz</span>
  <span class="material-symbols-outlined text-xs">arrow_forward</span>
</button>
<button onclick="showView('hub')" class="px-3 py-1.5 rounded-lg text-xs font-bold text-gray-300 hover:text-white hover:bg-white/10 border border-white/10 transition-colors flex items-center gap-1.5 cursor-pointer">
  <span class="material-symbols-outlined text-sm">grid_view</span> Menu
</button>
<button onclick="logout()" class="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-300 hover:bg-rose-500/20 border border-rose-500/30 transition-colors flex items-center gap-1.5 cursor-pointer">
  <span class="material-symbols-outlined text-sm">lock</span> Sair
</button>
</div>
</div>
</div>
</nav>
"""

    full_portal = f"""<!DOCTYPE html>
<html class="dark" lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>NNÓS Group | Portal de Relatórios Financeiros & Controladoria 2026</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
  tailwind.config = {{
    darkMode: "class",
    theme: {{
      extend: {{
        colors: {{
          "brand-blue": "#38bdf8",
          "brand-navy": "#0a192f",
          "brand-dark": "#020c1b",
          "surface": "#0c1322",
          "surface-container": "#191f2f",
          "surface-container-high": "#232a3a",
          "surface-variant": "#2e3545",
          "surface-card": "#1e293b",
          "on-surface": "#dce2f7",
          "text-primary": "#FFFFFF",
          "text-secondary": "#94a3b8",
          "text-muted": "#9CA3AF",
          "accent-amber": "#FBBF24",
          "accent-emerald": "#10b981",
          "accent-rose": "#f43f5e"
        }},
        fontFamily: {{
          sans: ["Inter", "sans-serif"],
          display: ["Manrope", "sans-serif"]
        }}
      }}
    }}
  }}
</script>
<style>
  body {{
    background: linear-gradient(135deg, #090e17 0%, #0d1b2a 40%, #1b263b 80%, #0a192f 100%);
    color: #dce2f7;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
  }}
  h1, h2, h3, h4, h5, h6, .font-display {{
    font-family: 'Manrope', sans-serif;
  }}
  .glass-card {{
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
  }}
  .glass-card:hover {{
    border-color: rgba(255, 255, 255, 0.2);
  }}
  .glass-panel {{
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}
  .hub-card {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }}
  .hub-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
  }}
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-track {{ background: rgba(15, 23, 42, 0.5); }}
  ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.2); border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.3); }}
</style>
</head>
<body class="antialiased selection:bg-brand-blue selection:text-white">

<!-- ═══════════ SECURITY GATE / LOGIN OVERLAY ═══════════ -->
<div id="login-overlay" class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/95 backdrop-blur-xl px-4">
  <div class="glass-card w-full max-w-md p-8 rounded-2xl border border-white/10 shadow-2xl relative overflow-hidden">
    <div class="absolute -top-24 -right-24 w-48 h-48 bg-brand-blue/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>

    <div class="text-center mb-8">
      <img src="{logo_src}" alt="NNÓS Logo" class="h-12 mx-auto mb-4 opacity-95"/>
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-blue/10 border border-brand-blue/30 text-brand-blue text-[11px] font-bold tracking-wider uppercase mb-3">
        <span class="material-symbols-outlined text-xs">lock</span> Acesso Restrito
      </div>
      <h2 class="text-2xl font-bold font-display text-white tracking-tight">Portal de Relatórios 2026</h2>
      <p class="text-xs text-gray-400 mt-1">Controladoria & Gestão Estratégica • NNÓS Group</p>
    </div>

    <form onsubmit="handleLogin(event)" class="space-y-4">
      <div>
        <label class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">Usuário</label>
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3 top-2.5 text-gray-400 text-lg">person</span>
          <input type="text" id="login-user" required autocomplete="username" class="w-full bg-slate-900/80 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-colors" placeholder="Digite seu usuário"/>
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">Senha</label>
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3 top-2.5 text-gray-400 text-lg">key</span>
          <input type="password" id="login-pass" required autocomplete="current-password" class="w-full bg-slate-900/80 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue transition-colors" placeholder="••••••••"/>
        </div>
      </div>

      <div id="login-error" class="hidden p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">error</span>
        <span>Usuário ou senha incorretos.</span>
      </div>

      <button type="submit" class="w-full py-2.5 px-4 rounded-lg bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-sm tracking-wide shadow-lg shadow-sky-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer mt-2">
        <span>Entrar no Sistema</span>
        <span class="material-symbols-outlined text-sm">arrow_forward</span>
      </button>
    </form>

    <div class="mt-6 text-center text-[11px] text-gray-500">
      NNÓS Business Solutions • Informações Confidenciais
    </div>
  </div>
</div>

<!-- ═══════════ MAIN PORTAL CONTAINER ═══════════ -->
<div id="portal-container" class="hidden">

  <!-- ═══════════ 1. HUB DE SELEÇÃO DE RELATÓRIOS ═══════════ -->
  <div id="view-hub" class="min-h-screen flex flex-col justify-between py-12 px-6">
    <div class="max-w-[1280px] mx-auto w-full">
      
      <div class="text-center max-w-2xl mx-auto mb-12">
        <img src="{logo_src}" alt="NNÓS Logo" class="h-14 mx-auto mb-4 opacity-95"/>
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-blue/10 border border-brand-blue/30 text-brand-blue text-xs font-bold uppercase tracking-wider mb-3">
          <span class="material-symbols-outlined text-sm">verified_user</span> Ambiente Seguro • Controladoria Executiva
        </div>
        <h1 class="text-3xl md:text-5xl font-extrabold font-display text-white tracking-tight mb-3">
          Painel de Relatórios <span class="text-sky-400">2026</span>
        </h1>
        <p class="text-text-muted text-base">Selecione o demonstrativo que deseja consultar em tempo real:</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
        
        <!-- CARD 1: RELATÓRIO MATRIZ -->
        <div class="hub-card glass-card rounded-2xl p-8 border border-sky-500/30 hover:border-sky-400 flex flex-col justify-between relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-32 h-32 bg-sky-500/10 rounded-full blur-2xl pointer-events-none"></div>
          
          <div>
            <div class="flex items-center justify-between gap-2 mb-6">
              <div class="w-14 h-14 rounded-xl bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center justify-center shadow-lg">
                <span class="material-symbols-outlined text-3xl">analytics</span>
              </div>
              <span class="px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-300 text-xs font-bold uppercase tracking-wider">
                NNÓS Matriz • YTD 2026
              </span>
            </div>

            <h2 class="text-2xl font-bold font-display text-white mb-2 group-hover:text-sky-300 transition-colors">
              Relatório Financeiro & DRE Gerencial
            </h2>
            <p class="text-text-muted text-sm leading-relaxed mb-6">
              Demonstrativo de Resultados acumulado de 8 meses (Jan a Ago/2026), Faturamento Mensal, Análise por Unidades de Negócio, Centros de Custo, Viagens & Reembolsos e Síntese Executiva.
            </p>

            <div class="grid grid-cols-3 gap-3 mb-8">
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Receita YTD</div>
                <div class="text-base font-extrabold text-white mt-0.5">R$ 6,80M</div>
              </div>
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Margem Bruta</div>
                <div class="text-base font-extrabold text-emerald-400 mt-0.5">45,8%</div>
              </div>
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Período</div>
                <div class="text-base font-extrabold text-sky-300 mt-0.5">8 Meses</div>
              </div>
            </div>
          </div>

          <button onclick="showView('matriz')" class="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer group-hover:scale-[1.01]">
            <span>Acessar Relatório Matriz</span>
            <span class="material-symbols-outlined text-base">arrow_forward</span>
          </button>
        </div>

        <!-- CARD 2: CONTAS A PAGAR UVA -->
        <div class="hub-card glass-card rounded-2xl p-8 border border-amber-500/30 hover:border-amber-400 flex flex-col justify-between relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl pointer-events-none"></div>

          <div>
            <div class="flex items-center justify-between gap-2 mb-6">
              <div class="w-14 h-14 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center shadow-lg">
                <span class="material-symbols-outlined text-3xl">account_balance_wallet</span>
              </div>
              <span class="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold uppercase tracking-wider">
                Campus BH UVA • AGO/2026
              </span>
            </div>

            <h2 class="text-2xl font-bold font-display text-white mb-2 group-hover:text-amber-300 transition-colors">
              Contas a Pagar | Campus BH UVA
            </h2>
            <p class="text-text-muted text-sm leading-relaxed mb-6">
              Universidade Veiga de Almeida — Controle analítico por data de vencimento (Out/25 a Jan/27), Realizado vs. Projeções Futuras, Detalhamento de Imobilizado & Obras, Top Fornecedores e Formas de Pagamento.
            </p>

            <div class="grid grid-cols-3 gap-3 mb-8">
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Total Geral</div>
                <div class="text-base font-extrabold text-white mt-0.5">R$ 555,4K</div>
              </div>
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Taxa Quitação</div>
                <div class="text-base font-extrabold text-emerald-400 mt-0.5">97,63%</div>
              </div>
              <div class="p-3 rounded-lg bg-slate-900/80 border border-white/5 text-center">
                <div class="text-[10px] text-gray-400 uppercase font-semibold">Imobilizado</div>
                <div class="text-base font-extrabold text-amber-300 mt-0.5">R$ 337,8K</div>
              </div>
            </div>
          </div>

          <button onclick="showView('uva')" class="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold text-sm shadow-lg shadow-amber-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer group-hover:scale-[1.01]">
            <span>Acessar Campus BH UVA</span>
            <span class="material-symbols-outlined text-base font-bold">arrow_forward</span>
          </button>
        </div>

      </div>

      <div class="mt-12 text-center">
        <button onclick="logout()" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-rose-300 hover:text-white bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 transition-all cursor-pointer">
          <span class="material-symbols-outlined text-sm">logout</span> Encerrar Sessão
        </button>
      </div>

    </div>

    <footer class="text-center py-6 text-xs text-gray-500 border-t border-white/5 mt-12">
      <p>NNÓS Business Solutions • Controladoria & Inteligência Financeira • Confidencial</p>
    </footer>
  </div>

  <!-- ═══════════ 2. VIEW MATRIZ ═══════════ -->
  <div id="view-matriz" class="hidden">
    {matriz_header}
    {matriz_main}
    {matriz_footer}
  </div>

  <!-- ═══════════ 3. VIEW UVA ═══════════ -->
  <div id="view-uva" class="hidden">
    {uva_header_only}
    {uva_nav_custom}
    {uva_main}
    {uva_footer}
  </div>

</div>

<!-- ═══════════ SCRIPTS DE LÓGICA E GRÁFICOS ═══════════ -->
<script>
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color = '#f1f5f9';

let chartFaturamentoInstance = null;
let chartFornecedoresInstance = null;
let chartMensalExtendidoInstance = null;
let chartCategoriasInstance = null;
let chartFormasPagamentoInstance = null;

function initMatrizCharts() {{
  const ctx = document.getElementById('chartFaturamento');
  if (ctx) {{
    if (chartFaturamentoInstance) {{
      chartFaturamentoInstance.destroy();
    }}
    chartFaturamentoInstance = new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: ['Jan/26', 'Fev/26', 'Mar/26', 'Abr/26', 'Mai/26', 'Jun/26', 'Jul/26', 'Ago/26'],
        datasets: [{{
          label: 'Receita Bruta (R$)',
          data: [618822.31, 785304.16, 750586.97, 820033.27, 971443.58, 881333.71, 1008002.15, 962778.62],
          backgroundColor: 'rgba(56, 189, 248, 0.85)',
          borderColor: '#38bdf8',
          borderWidth: 1.5,
          borderRadius: 6
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                return 'Receita: R$ ' + context.raw.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
              }}
            }}
          }}
        }},
        scales: {{
          y: {{
            grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
            ticks: {{ color: '#9CA3AF', font: {{ family: 'Inter', size: 11 }} }}
          }},
          x: {{
            grid: {{ display: false }},
            ticks: {{ color: '#9CA3AF', font: {{ family: 'Inter', size: 11 }} }}
          }}
        }}
      }}
    }});
  }}
}}

function initUvaCharts() {{
  const ctxForn = document.getElementById('chartFornecedores');
  if (ctxForn && !chartFornecedoresInstance) {{
    chartFornecedoresInstance = new Chart(ctxForn, {{
      type: 'bar',
      data: {{
        labels: ['MR ENGENHARIA', 'AL TREINAMENTO', 'OTHON CARVALHO', 'EMÍLIA ALCÂNTARA', 'NORONHA VISUAL', 'CAFETERIA GOURMET', 'THERMOBRAS', 'ACO INOX IMPERIAL', 'ANDRADES COMERCIO', 'DEFLEX'],
        datasets: [{{
          label: 'Valor Total (R$)',
          data: [189589.65, 126574.83, 29730.33, 28369.94, 26090.00, 21510.63, 21300.00, 18749.90, 14692.19, 9210.00],
          backgroundColor: '#38bdf8cc',
          borderColor: '#38bdf8',
          borderWidth: 1, borderRadius: 4
        }}]
      }},
      options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ beginAtZero: true, ticks: {{ callback: v => 'R$ '+(v/1000).toFixed(0)+'K', color: '#f1f5f9', font: {{ weight: '600' }} }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }},
          y: {{ ticks: {{ color: '#f1f5f9', font: {{ weight: '500' }} }}, grid: {{ display: false }} }}
        }}
      }}
    }});
  }}

  const ctxMensal = document.getElementById('chartMensalExtendido');
  if (ctxMensal && !chartMensalExtendidoInstance) {{
    chartMensalExtendidoInstance = new Chart(ctxMensal, {{
      type: 'bar',
      data: {{
        labels: ['Out/25','Nov/25','Dez/25','Jan/26','Fev/26','Mar/26','Abr/26','Mai/26','Jun/26','Jul/26','Ago/26','Set/26','Out/26','Nov/26','Dez/26','Jan/27'],
        datasets: [
          {{
            label: 'Quitado (R$)',
            data: [6150.00, 9458.55, 102332.00, 123960.28, 30235.52, 80794.49, 45058.11, 45159.57, 39825.22, 32008.19, 27294.55, 0, 0, 0, 0, 0],
            backgroundColor: '#38bdf8cc',
            borderColor: '#38bdf8',
            borderWidth: 1, borderRadius: 2
          }},
          {{
            label: 'A Vencer (R$)',
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 600.00, 3762.16, 2717.97, 2717.97, 2717.97, 650.00],
            backgroundColor: '#fb7185cc',
            borderColor: '#fb7185',
            borderWidth: 1, borderRadius: 2
          }}
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ position: 'top', labels: {{ color: '#f1f5f9', font: {{ weight: '600' }} }} }} }},
        scales: {{
          x: {{ stacked: true, ticks: {{ color: '#f1f5f9', font: {{ weight: '500' }} }}, grid: {{ display: false }} }},
          y: {{ stacked: true, ticks: {{ callback: v => 'R$ '+(v/1000).toFixed(0)+'K', color: '#f1f5f9', font: {{ weight: '600' }} }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }}
        }}
      }}
    }});
  }}

  const ctxCat = document.getElementById('chartCategorias');
  if (ctxCat && !chartCategoriasInstance) {{
    chartCategoriasInstance = new Chart(ctxCat, {{
      type: 'doughnut',
      data: {{
        labels: ['Manutenção Predial', 'Honorários Serviços', 'Móveis e Utensílios', 'Despesas Operacionais', 'Máquinas e Equipamentos', 'Viagens', 'Ajuda de Custo', 'Outros'],
        datasets: [{{
          data: [278892.11, 133821.61, 37062.25, 25924.01, 21800.05, 16807.90, 9235.00, 32899.62],
          backgroundColor: ['#38bdf8', '#60a5fa', '#a78bfa', '#fbbf24', '#34d399', '#f472b6', '#fb923c', '#94a3b8'],
          borderWidth: 0
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false, cutout: '65%',
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#f1f5f9', font: {{ weight: '500' }}, usePointStyle: true }} }} }}
      }}
    }});
  }}

  const ctxFormas = document.getElementById('chartFormasPagamento');
  if (ctxFormas && !chartFormasPagamentoInstance) {{
    chartFormasPagamentoInstance = new Chart(ctxFormas, {{
      type: 'bar',
      data: {{
        labels: ['Pagamento Instantâneo (PIX)', 'Cartão de Crédito', 'Boleto Bancário', 'Cobrança PIX'],
        datasets: [{{
          label: 'Valor (R$)',
          data: [409586.99, 110432.66, 11517.53, 10739.30],
          backgroundColor: ['#38bdf8cc', '#34d399cc', '#fbbf24cc', '#a78bfacc'],
          borderColor: ['#38bdf8', '#34d399', '#fbbf24', '#a78bfa'],
          borderWidth: 1, borderRadius: 4
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#f1f5f9', font: {{ weight: '500' }} }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ callback: v => 'R$ '+(v/1000).toFixed(0)+'K', color: '#f1f5f9', font: {{ weight: '600' }} }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }}
        }}
      }}
    }});
  }}
}}

const AUTH_USER_HASH = "b902e7f3badabb511f1449224d9738ea94f1f73bf272adc8f823aa3c2b19e959";
const AUTH_PASS_HASH = "a4177e355fbec6fdca3918f02b0a903b5e63a268fee6691c3f1fb96583d72115";

async function sha256(str) {{
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}}

async function handleLogin(e) {{
  e.preventDefault();
  const u = document.getElementById('login-user').value.trim();
  const p = document.getElementById('login-pass').value;
  const uHash = await sha256(u);
  const pHash = await sha256(p);

  if (uHash === AUTH_USER_HASH && pHash === AUTH_PASS_HASH) {{
    sessionStorage.setItem('nnos_auth', 'true');
    unlockDashboard();
  }} else {{
    document.getElementById('login-error').classList.remove('hidden');
  }}
}}

function unlockDashboard() {{
  const overlay = document.getElementById('login-overlay');
  const portal = document.getElementById('portal-container');
  if (overlay) overlay.classList.add('hidden');
  if (portal) portal.classList.remove('hidden');
  
  const hash = window.location.hash.replace('#', '').toLowerCase();
  if (hash === 'matriz') {{
    showView('matriz', false);
  }} else if (hash === 'uva') {{
    showView('uva', false);
  }} else {{
    showView('hub', false);
  }}
}}

function showView(viewName, updateHash = true) {{
  const hub = document.getElementById('view-hub');
  const matriz = document.getElementById('view-matriz');
  const uva = document.getElementById('view-uva');

  if (hub) hub.classList.add('hidden');
  if (matriz) matriz.classList.add('hidden');
  if (uva) uva.classList.add('hidden');

  if (viewName === 'matriz') {{
    if (matriz) matriz.classList.remove('hidden');
    if (updateHash) window.location.hash = 'matriz';
    document.title = "NNÓS Group | Relatório Financeiro & DRE Gerencial 2026";
    setTimeout(initMatrizCharts, 50);
  }} else if (viewName === 'uva') {{
    if (uva) uva.classList.remove('hidden');
    if (updateHash) window.location.hash = 'uva';
    document.title = "NNÓS Group | Contas a Pagar — Campus BH UVA";
    setTimeout(initUvaCharts, 50);
  }} else {{
    if (hub) hub.classList.remove('hidden');
    if (updateHash) window.location.hash = 'hub';
    document.title = "NNÓS Group | Portal de Relatórios Financeiros 2026";
  }}

  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function logout() {{
  sessionStorage.removeItem('nnos_auth');
  window.location.hash = '';
  location.reload();
}}

window.addEventListener('hashchange', () => {{
  if (sessionStorage.getItem('nnos_auth') === 'true') {{
    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (['matriz', 'uva', 'hub'].includes(hash)) {{
      showView(hash, false);
    }}
  }}
}});

document.addEventListener('DOMContentLoaded', () => {{
  if (sessionStorage.getItem('nnos_auth') === 'true') {{
    unlockDashboard();
  }}

  if ('IntersectionObserver' in window) {{
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          if (entry.target.id === 'chartFaturamento') initMatrizCharts();
          if (['chartFornecedores', 'chartMensalExtendido', 'chartCategorias', 'chartFormasPagamento'].includes(entry.target.id)) initUvaCharts();
        }}
      }});
    }}, {{ threshold: 0.1 }});

    ['chartFaturamento', 'chartFornecedores', 'chartMensalExtendido', 'chartCategorias', 'chartFormasPagamento'].forEach(id => {{
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }});
  }}
}});
</script>
</body>
</html>
"""

    with open(output_index, "w", encoding="utf-8") as f:
        f.write(full_portal)
    print(f"Portal Integrado gerado com sucesso em: {output_index}")

if __name__ == "__main__":
    build()
