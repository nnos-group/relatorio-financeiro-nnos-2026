# Script de automação completa para atualização e publicação no GitHub Pages
param(
    [string]$MensagemCommit = "chore: atualizacao dos relatorios financeiros e portal integrado"
)

$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Item -Path ".").FullName }

Write-Host "1. Recalculando bases financeiras e DRE Gerencial..." -ForegroundColor Cyan
py "$repoDir\generate_report_script.py"

Write-Host "2. Sincronizando relatórios e portal integrado..." -ForegroundColor Cyan
py "$repoDir\build_portal.py"

Write-Host "3. Enviando atualizações para o GitHub..." -ForegroundColor Cyan
git -C $repoDir add .
git -C $repoDir commit -m $MensagemCommit
git -C $repoDir push origin main

Write-Host "✅ Publicação concluída com sucesso no GitHub Pages!" -ForegroundColor Green
Write-Host "🔗 Link Oficial: https://nnos-group.github.io/relatorio-financeiro-nnos-2026/" -ForegroundColor Yellow
