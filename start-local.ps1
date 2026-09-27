$ErrorActionPreference = 'Stop'
$projectDirectory = $PSScriptRoot
$logDirectory = Join-Path $projectDirectory 'scratch\server-logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try { $client.Connect('127.0.0.1', $Port); return $true }
    catch { return $false }
    finally { $client.Dispose() }
}

if (-not (Test-LocalPort 8000)) {
    Start-Process -FilePath (Join-Path $projectDirectory '.venv\Scripts\python.exe') `
        -ArgumentList @('-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', '8000', '--workers', '1') `
        -WorkingDirectory $projectDirectory -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDirectory 'backend.log') `
        -RedirectStandardError (Join-Path $logDirectory 'backend-error.log') | Out-Null
}
if (-not (Test-LocalPort 5173)) {
    Start-Process -FilePath (Get-Command node.exe).Source `
        -ArgumentList @('node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5173', '--strictPort') `
        -WorkingDirectory (Join-Path $projectDirectory 'frontend') -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDirectory 'frontend.log') `
        -RedirectStandardError (Join-Path $logDirectory 'frontend-error.log') | Out-Null
}
Write-Output 'Local services starting. Open http://127.0.0.1:5173. Logs: scratch/server-logs'
