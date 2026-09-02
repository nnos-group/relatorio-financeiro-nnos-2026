# Script para registrar a rotina diária no Agendador de Tarefas do Windows
param(
    [string]$Horario = "07:00"
)

$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Item -Path ".").FullName }
$scriptPath = Join-Path $repoDir "atualizar_todos_relatorios.ps1"
$taskName = "NNOS_Atualizacao_Relatorios_2026"

Write-Host "Configurando tarefa agendada: $taskName" -ForegroundColor Cyan
Write-Host "Horário de disparo: $Horario (diariamente)" -ForegroundColor Cyan
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Diretório de trabalho: $repoDir" -ForegroundColor Cyan

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
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Rotina diária automática para compilação e publicação dos relatórios financeiros NNÓS no GitHub Pages."

    Write-Host ""
    Write-Host "✅ Tarefa agendada com sucesso!" -ForegroundColor Green
    Write-Host "Para testar agora sem esperar o horário, execute:" -ForegroundColor Yellow
    Write-Host "Start-ScheduledTask -TaskName `"$taskName`"" -ForegroundColor White
} catch {
    Write-Host "❌ Falha ao registrar tarefa: $_" -ForegroundColor Red
    Write-Host "Dica: Execute o PowerShell como Administrador se necessário." -ForegroundColor Yellow
}
