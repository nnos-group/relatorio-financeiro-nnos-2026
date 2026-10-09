# ==============================================================================
# Script de Atualizacao Diaria - Relatorios com Conexao Direta a Planilha
# Planilha: "2026 - Gestão Financeira Projetos" (Google Sheets API)
# Relatórios Atualizados:
#   1. Booking - Dashboard Executivo de Performance (sync_booking_from_sheets.py)
#   2. Despesas Operacionais & Prospeccao (sync_prospeccao_from_sheets.py)
#   3. Painel por Lider (sync_lider_from_sheets.py)
#   4. Portal Executivo Integrado (build_portal.py)
#   5. Publicacao Automatica no GitHub Pages
# ==============================================================================

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

Log-Message "=== Iniciando atualizacao dos relatorios da Planilha '2026 - Gestão Financeira Projetos' ==="

try {
    # 1. Sincroniza Dashboard de Performance (Booking) via Google Sheets API
    Log-Message "1/4. Sincronizando Performance de Projetos (Booking) via Google Sheets API..."
    & py "$repoDir\sync_booking_from_sheets.py" *>> $logFile

    # 2. Sincroniza Despesas Operacionais & Prospecção via Google Sheets API
    Log-Message "2/4. Sincronizando Despesas Operacionais & Prospecção via Google Sheets API..."
    & py "$repoDir\sync_prospeccao_from_sheets.py" *>> $logFile

    # 3. Sincroniza Painel por Líder via Google Sheets API
    Log-Message "3/4. Sincronizando Painel por Líder via Google Sheets API..."
    & py "$repoDir\sync_lider_from_sheets.py" *>> $logFile

    # 4. Reconstroi portal executivo integrado (index.html)
    Log-Message "4/4. Reconstruindo portal executivo integrado (build_portal.py)..."
    & py "$repoDir\build_portal.py" *>> $logFile

    # 5. Verifica alteracoes no Git e publica no GitHub Pages
    & git -C $repoDir add .
    $status = & git -C $repoDir status --porcelain

    if (-not [string]::IsNullOrWhiteSpace($status)) {
        if ([string]::IsNullOrWhiteSpace($MensagemCommit)) {
            $MensagemCommit = "auto: atualizacao diaria (08:00) - Planilha Gestao Financeira Projetos - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
        }
        Log-Message "5. Mudancas detectadas. Criando commit: $MensagemCommit"
        & git -C $repoDir commit -m $MensagemCommit *>> $logFile

        Log-Message "6. Enviando atualizacoes para o GitHub Pages..."
        & git -C $repoDir push origin main *>> $logFile
        Log-Message "[OK] Sincronizacao concluida com sucesso no GitHub Pages!"
    } else {
        Log-Message "[INFO] Nenhuma alteracao encontrada nos dados da planilha. Push dispensado."
    }
} catch {
    Log-Message "[ERRO] Falha durante a execucao da rotina: $_"
}

Log-Message "=== Fim da atualizacao da Planilha '2026 - Gestão Financeira Projetos' ==="
