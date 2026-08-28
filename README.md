# 🏢 Portal de Relatórios Financeiros 2026 — NNÓS Group

🔗 **Link Oficial do Portal:** [https://nnos-group.github.io/relatorio-financeiro-nnos-2026/](https://nnos-group.github.io/relatorio-financeiro-nnos-2026/)

🔐 **Acesso Restrito (Sessão Integrada):**
- **Usuário:** `nnos`
- **Senha:** `nnos2026`

---

## 🏛️ Arquitetura do Portal Integrado

O ecossistema é hospedado diretamente no **GitHub Pages** e estruturado de forma desacoplada, permitindo que cada demonstrativo funcione de maneira 100% independente, mas totalmente integrado e navegável entre si:

1. **Gate de Autenticação & Hub Executivo (`index.html`):**
   - Autenticação criptografada (SHA-256) no cliente com sessão persistida (`sessionStorage`).
   - Painel principal de seleção com 3 cards dinâmicos para acesso direto aos relatórios.

2. **Demonstrativos Independentes Hospedados:**
   - 📊 **Opção 1 — Relatório Financeiro & DRE Gerencial 2026:** [`matriz.html`](matriz.html)
   - 🏛️ **Opção 2 — Contas a Pagar | Campus BH UVA:** [`uva.html`](uva.html)
   - 📈 **Opção 3 — Dashboard Executivo de Performance de Projetos (Booking):** [`booking.html`](booking.html)

3. **Navegabilidade e Interação Multidirecional:**
   - Todos os relatórios possuem barra de navegação superior (Navbar) que permite alternar instantaneamente entre **Matriz**, **UVA**, **Performance** e o **Menu Principal**, além do botão para **Encerrar Sessão**.
   - A autenticação é verificada automaticamente em todas as páginas: se o usuário não estiver autenticado, é redirecionado para a tela de login.

---

## 🔄 Como atualizar os relatórios

1. **Se atualizar o Relatório Matriz:**
   - Execute o script `generate_report_script.py`. Ele recalcula as bases DRE, atualiza o `matriz.html` e executa o `build_portal.py`.

2. **Se atualizar o Contas a Pagar UVA:**
   - Atualize o arquivo `contas-a-pagar-uva.html` e execute `build_portal.py` (ou `build_portal.ps1`).

3. **Se atualizar o Dashboard de Performance (Booking):**
   - Atualize o arquivo `dashboard-executivo-booking.html` e execute `build_portal.py`.

4. **Automação Completa (Reconstrução + Git Push):**
   - Execute no terminal PowerShell:
   ```powershell
   .\atualizar_todos_relatorios.ps1 -MensagemCommit "feat: atualizacao dados AGO-26"
   ```
   Este script sincroniza todos os demonstrativos e publica automaticamente no GitHub Pages.
