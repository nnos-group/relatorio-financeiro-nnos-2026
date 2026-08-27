# 🏢 Portal de Relatórios Financeiros 2026 — NNÓS Group

🔗 **Link Oficial:** [https://nnos-group.github.io/relatorio-financeiro-nnos-2026/](https://nnos-group.github.io/relatorio-financeiro-nnos-2026/)

🔐 **Acesso Restrito:**
- **Usuário:** `nnos`
- **Senha:** `nnos2026`

---

## 🏛️ Arquitetura do Portal Integrado

O arquivo `index.html` atua como um **Portal Integrado de Relatórios** composto por:
1. **Gate de Autenticação:** Login criptografado via SHA-256 no cliente.
2. **Hub Executivo de Seleção (2 Opções):**
   - **Opção 1:** 📊 *Relatório Financeiro & DRE Gerencial 2026 (Matriz)*
   - **Opção 2:** 🏛️ *Contas a Pagar | Campus BH UVA*
3. **Alternância Instantânea no Canto Superior Direito:**
   - Botão para alternar diretamente entre a Matriz e a UVA sem sair ou recarregar.
   - Botão de retorno ao Menu (Hub de seleção).

---

## ⚠️ Regra Fundamental para Atualizações

**NUNCA sobrescrever o `index.html` diretamente com apenas um dos relatórios isolados.**

### 🔄 Como atualizar os relatórios:

1. **Se atualizar o Relatório Matriz:**
   - O script `generate_report_script.py` já foi programado para atualizar o `2026 - Relatório Financeiro - NNÓS - MATRIZ-26.html` e em seguida chamar automaticamente o `build_portal.py` para remontar o `index.html`.

2. **Se atualizar o Contas a Pagar UVA:**
   - Atualize o arquivo `NNÓS Group _ Contas a Pagar - Campus BH UVA.html` na pasta `../UVA/`.
   - Execute o script `build_portal.ps1` ou `build_portal.py`.

3. **Automação Completa (Reconstrução + Git Push):**
   - Execute no terminal PowerShell:
   ```powershell
   .\atualizar_todos_relatorios.ps1 -MensagemCommit "feat: atualizacao dados AGO-26"
   ```
   Este script recompila o `index.html`, sincroniza as cópias e faz o deploy automático no GitHub Pages.
