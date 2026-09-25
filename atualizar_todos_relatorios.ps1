# Script de automacao completa para atualizacao e publicacao diaria no GitHub Pages
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

Log-Message "=== Iniciando rotina de atualizacao dos relatorios ==="

try {
    # 0. Sincroniza Dashboard de Performance via Google Sheets API
    Log-Message "0. Sincronizando Performance de Projetos via Google Sheets API..."
    & py "$repoDir\sync_booking_from_sheets.py" *>> $logFile

    # 1. Processa as bases CSV mais recentes da Matriz (Receita, Despesas, Reembolsos)
    Log-Message "1. Processando bases financeiras CSV da Matriz (parse_financial_data.py)..."
    & py "$repoDir\parse_financial_data.py" *>> $logFile

    # 2. Recalcula o demonstrativo e DRE da Matriz
    Log-Message "2. Gerando relatorio e DRE da Matriz (generate_report_script.py)..."
    & py "$repoDir\generate_report_script.py" *>> $logFile

    # 3. Processa a base de dados mais recente do Campus BH UVA
    Log-Message "3. Processando base de dados CSV do Campus BH UVA (update_uva_from_csv.py)..."
    & py "$repoDir\update_uva_from_csv.py" *>> $logFile

    # 4. Sincroniza portal e demonstrativos integrados
    Log-Message "4. Reconstruindo portal integrado (build_portal.py)..."
    & py "$repoDir\build_portal.py" *>> $logFile

    # 5. Verifica alteracoes no Git
    & git -C $repoDir add .
    $status = & git -C $repoDir status --porcelain

    if (-not [string]::IsNullOrWhiteSpace($status)) {
        if ([string]::IsNullOrWhiteSpace($MensagemCommit)) {
            $MensagemCommit = "auto: atualizacao diaria dos relatorios - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
        }
        Log-Message "5. Mudancas detectadas. Criando commit: $MensagemCommit"
        & git -C $repoDir commit -m $MensagemCommit *>> $logFile

        Log-Message "6. Enviando atualizacoes para o GitHub Pages..."
        & git -C $repoDir push origin main *>> $logFile
        Log-Message "[OK] Sincronizacao concluida com sucesso no GitHub Pages!"
    } else {
        Log-Message "[INFO] Nenhuma alteracao encontrada nos dados. Push dispensado."
    }
} catch {
    Log-Message "[ERRO] Falha durante a execucao da rotina: $_"
}

Log-Message "=== Fim da rotina de atualizacao ==="
