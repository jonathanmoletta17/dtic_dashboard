# Prints mapping of backend refresh-related configuration for DTIC
# Usage: Run from repo root or any directory; it will locate apps/dtic/backend/.env or .env.example

param(
  [string]$BackendPath = "apps/dtic/backend"
)

function Read-DotEnv($path) {
  $vars = @{}
  if (-not (Test-Path $path)) { return $vars }
  Get-Content -Path $path | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^(#|\s*$)') { return }
    $kv = $line -split '=', 2
    if ($kv.Length -eq 2) {
      $key = $kv[0].Trim()
      $val = $kv[1].Trim()
      $vars[$key] = $val
    }
  }
  return $vars
}

$envFile = Join-Path $BackendPath ".env"
$exampleFile = Join-Path $BackendPath ".env.example"

$vars = @{}
if (Test-Path $envFile) {
  $vars = Read-DotEnv $envFile
} elseif (Test-Path $exampleFile) {
  $vars = Read-DotEnv $exampleFile
}

Write-Host "=== Backend DTIC Refresh/Timing Configuration ==="
Write-Host "Backend path: $BackendPath"
Write-Host "Source: " ((Test-Path $envFile) ? $envFile : ((Test-Path $exampleFile) ? $exampleFile : 'none'))
Write-Host ""

function Get-OrDefault($map, $key, $default) {
  if ($map.ContainsKey($key) -and $map[$key]) { return $map[$key] }
  return $default
}

$API_URL = Get-OrDefault $vars 'API_URL' '[missing]'
$APP_TOKEN = Get-OrDefault $vars 'APP_TOKEN' '[missing]'
$USER_TOKEN = Get-OrDefault $vars 'USER_TOKEN' '[missing]'
$CACHE_TTL_SEC = [int](Get-OrDefault $vars 'CACHE_TTL_SEC' '300')
$SESSION_TTL_SEC = [int](Get-OrDefault $vars 'SESSION_TTL_SEC' '300')
$RANKING_GROUP_ID = Get-OrDefault $vars 'RANKING_TECHNICIAN_PARENT_GROUP_ID' '17'

Write-Host "API_URL:            $API_URL"
Write-Host "APP_TOKEN:          " (($APP_TOKEN -ne '[missing]') ? '[present]' : '[missing]')
Write-Host "USER_TOKEN:         " (($USER_TOKEN -ne '[missing]') ? '[present]' : '[missing]')
Write-Host "CACHE_TTL_SEC:      $CACHE_TTL_SEC  (data cache TTL; affects freshness)"
Write-Host "SESSION_TTL_SEC:    $SESSION_TTL_SEC  (GLPI session-token reuse TTL)"
Write-Host "RANKING_GROUP_ID:   $RANKING_GROUP_ID  (business logic group for ranking)"
Write-Host ""
Write-Host "Notes:"
Write-Host "- Frontend polling interval (e.g., 12000–15000 ms) determines call frequency."
Write-Host "- If polling < CACHE_TTL_SEC, responses remain stable until cache expires."
Write-Host "- Adjust TTLs to balance freshness vs. load on GLPI API."