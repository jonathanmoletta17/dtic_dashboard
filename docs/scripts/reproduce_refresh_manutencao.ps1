# Guides reproducing refresh behavior for Maintenance dashboard without code changes

param(
  [int]$PollingMs = 12000,
  [string]$FrontendPath = "apps/manutencao/frontend",
  [string]$BackendApiBase = "/api/v1"
)

Write-Host "=== Reproduzir Refresh no Dashboard de Manutenção ==="
Write-Host "Frontend path: $FrontendPath"
Write-Host "Objetivo: polling ~$PollingMs ms (" ([math]::Round($PollingMs / 1000.0, 2)) " s) sem alterar código"
Write-Host ""

Write-Host "Passos sugeridos de configuração (.env do frontend):"
Write-Host "1) Definir VITE_API_BASE_URL para apontar o backend correto:"
Write-Host "   VITE_API_BASE_URL=$BackendApiBase"
Write-Host "2) Escolher uma das variáveis de polling:"
Write-Host "   VITE_REALTIME_POLL_INTERVAL_MS=$PollingMs    # milissegundos"
Write-Host "   ou"
Write-Host "   VITE_REALTIME_POLL_INTERVAL_SEC=" ([math]::Round($PollingMs / 1000.0)) "  # segundos"
Write-Host ""

Write-Host "Notas de alinhamento com backend:"
Write-Host "- O backend usa cache por TTL (CACHE_TTL_SEC) e sessão GLPI por TTL (SESSION_TTL_SEC)."
Write-Host "- Se PollingMs < (CACHE_TTL_SEC * 1000), as respostas se manterão estáveis até expirar o cache."
Write-Host "- Ajuste CACHE_TTL_SEC conforme necessidade de frescor e carga na API GLPI."
Write-Host ""

Write-Host "Observabilidade: verifique logs do backend para cache_hit=true/false, TTL aplicado e eventuais erros."