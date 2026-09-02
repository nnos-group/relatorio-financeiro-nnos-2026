# Script de automação completa para atualização e publicação diária no GitHub Pages
param(
    [string]$MensagemCommit = ""
)

$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Item -Path ".").FullName }
Set-Location -Path $repoDir

$logFile = Join-Path $repoDir "execucao_automatica.log"

function Log-Message([string]$msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Log-Message "=== Iniciando rotina diária de atualização ==="

try {
    # 1. Recalcula bases financeiras e DRE
    Log-Message "1. Executando generate_report_script.py..."
    & py "$repoDir\generate_report_script.py" *>> $logFile

    # 2. Sincroniza portal e demonstrativos
    Log-Message "2. Executando build_portal.py..."
    & py "$repoDir\build_portal.py" *>> $logFile

    # 3. Verifica alterações no Git
    & git -C $repoDir add .
    $status = & git -C $repoDir status --porcelain

    if (-not [string]::IsNullOrWhiteSpace($status)) {
        if ([string]::IsNullOrWhiteSpace($MensagemCommit)) {
            $MensagemCommit = "auto: atualizacao diaria dos relatorios - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
        }
        Log-Message "3. Mudanças detectadas. Criando commit: $MensagemCommit"
        & git -C $repoDir commit -m $MensagemCommit *>> $logFile

        Log-Message "4. Enviando atualizações para o GitHub Pages..."
        & git -C $repoDir push origin main *>> $logFile
        Log-Message "✅ Sincronização concluída com sucesso no GitHub Pages!"
    } else {
        Log-Message "ℹ️ Nenhuma alteração encontrada nos dados. Push dispensado."
    }
} catch {
    Log-Message "❌ ERRO durante a execução da rotina: $_"
}

Log-Message "=== Fim da rotina diária ==="
