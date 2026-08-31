# Script de automação para sincronização dos relatórios independentes e portal NNÓS 2026
$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Item -Path ".").FullName }

Write-Host "Executando build_portal.py..." -ForegroundColor Cyan
py "$repoDir\build_portal.py"

Write-Host "✅ build_portal.ps1 concluído com sucesso!" -ForegroundColor Green
