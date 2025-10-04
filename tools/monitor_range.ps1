param(
  [string]$Inicio,
  [string]$Fim,
  [int]$DurationSec = 120,
  [int]$IntervalMs = 15000,
  [string]$BaseUrl = "http://127.0.0.1:8000/api/v1"
)

# Define intervalo padrão se não for informado (últimos 7 dias)
if (-not $Inicio -or -not $Fim) {
  $Fim = (Get-Date).ToString('yyyy-MM-dd')
  $Inicio = (Get-Date).AddDays(-7).ToString('yyyy-MM-dd')
}

Write-Host "Monitorando intervalo inicio=$Inicio fim=$Fim por $DurationSec s (tick=$IntervalMs ms)" -ForegroundColor Cyan

$reportPath = Join-Path $PSScriptRoot 'monitor_report.csv'
"timestamp,endpoint,status_code,elapsed_ms,content_length" | Out-File -FilePath $reportPath -Encoding utf8

$endpoints = @(
  "/metrics-gerais?inicio=$Inicio&fim=$Fim",
  "/status-niveis?inicio=$Inicio&fim=$Fim",
  "/ranking-tecnicos?inicio=$Inicio&fim=$Fim"
)

$ticks = [math]::Ceiling(($DurationSec * 1000) / $IntervalMs)
$errors = 0

for ($i = 1; $i -le $ticks; $i++) {
  foreach ($ep in $endpoints) {
    $url = "$BaseUrl$ep"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
      $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
      $sw.Stop()
      $line = "{0},{1},{2},{3},{4}" -f (Get-Date).ToString('o'), $ep, $resp.StatusCode, $sw.ElapsedMilliseconds, ($resp.Content.Length)
      Add-Content -Path $reportPath -Value $line
      Write-Host ("[{0}] {1} -> {2} ({3} ms)" -f (Get-Date).ToString('HH:mm:ss'), $ep, $resp.StatusCode, $sw.ElapsedMilliseconds)
    } catch {
      $sw.Stop()
      $errors++
      $line = "{0},{1},{2},{3},{4}" -f (Get-Date).ToString('o'), $ep, "ERROR", $sw.ElapsedMilliseconds, 0
      Add-Content -Path $reportPath -Value $line
      Write-Warning ("[{0}] {1} -> ERROR ({2} ms): {3}" -f (Get-Date).ToString('HH:mm:ss'), $ep, $sw.ElapsedMilliseconds, $_.Exception.Message)
    }
  }
  Start-Sleep -Milliseconds $IntervalMs
}

Write-Host "Concluído. Relatório em: $reportPath" -ForegroundColor Green
if ($errors -gt 0) {
  Write-Warning "Ocorreram $errors erros durante o monitoramento. Verifique o relatório para detalhes."
}