# Script para registrar a rotina diária no Agendador de Tarefas do Windows
param(
    [string]$Horario = "08:00",
    [string]$ScriptAlvo = "atualizar_relatorios_planilha_projetos.ps1",
    [string]$TaskName = "NNOS_Atualizacao_Relatorios_2026"
)

$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Item -Path ".").FullName }
$scriptPath = Join-Path $repoDir $ScriptAlvo

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Configurando tarefa agendada no Windows: $TaskName" -ForegroundColor Cyan
Write-Host "Horário de disparo: $Horario (diariamente)" -ForegroundColor Cyan
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Diretório de trabalho: $repoDir" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory "$repoDir"

$trigger = New-ScheduledTaskTrigger -Daily -At $Horario

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

try {
    # Remove tarefa anterior se já existir
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Rotina diária automática às $Horario para sincronização dos relatórios da Planilha '2026 - Gestão Financeira Projetos' e publicação no GitHub Pages."

    Write-Host ""
    Write-Host "✅ Tarefa agendada com sucesso para as $Horario da manhã!" -ForegroundColor Green
    Write-Host "Para testar agora sem esperar o horário, execute:" -ForegroundColor Yellow
    Write-Host "Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor White
} catch {
    Write-Host "❌ Falha ao registrar tarefa: $_" -ForegroundColor Red
    Write-Host "Dica: Execute o PowerShell como Administrador se necessário." -ForegroundColor Yellow
}
