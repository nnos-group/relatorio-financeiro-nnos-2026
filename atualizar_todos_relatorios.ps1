# Script de automação completa para atualização e publicação no GitHub Pages
param(
    [string]$MensagemCommit = "chore: atualizacao dos relatorios financeiros e portal integrado"
)

$repoDir = "c:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\2026 - Relatório Financeiro - NNÓS -26"
$uvaFile = "c:\Users\Leonardo Campos\OneDrive - NNÓS CONSULTORIA E TREINAMENTO\Contabilidade\Relatórios\UVA\NNÓS Group _ Contas a Pagar - Campus BH UVA.html"

Write-Host "1. Reconstruindo Portal Integrado (index.html)..."
powershell -ExecutionPolicy Bypass -File "$repoDir\build_portal.ps1"

Write-Host "2. Sincronizando arquivos complementares..."
Copy-Item -Path $uvaFile -Destination "$repoDir\contas-a-pagar-uva.html" -Force
Copy-Item -Path $uvaFile -Destination "$repoDir\uva.html" -Force

Write-Host "3. Enviando atualizações para o GitHub..."
git -C $repoDir add index.html contas-a-pagar-uva.html uva.html build_portal.ps1 build_portal.py generate_report_script.py
git -C $repoDir commit -m $MensagemCommit
git -C $repoDir push origin main

Write-Host "✅ Publicação concluída com sucesso no GitHub Pages!"
Write-Host "🔗 Link: https://nnos-group.github.io/relatorio-financeiro-nnos-2026/"
