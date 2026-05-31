# Find processes making external connections on unusual ports
# Usage: powershell -ExecutionPolicy Bypass -File hunt-suspicious-network.ps1

Get-NetTCPConnection -ErrorAction SilentlyContinue | Where-Object {
    $_.RemoteAddress -notmatch '^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|127\.)' -and
    $_.RemotePort -notin @(80, 443, 53, 123) -and
    $_.State -eq 'Established'
} | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess, @{
    Name       = 'ProcessName'
    Expression = {
        try { (Get-Process -Id $_.OwningProcess -ErrorAction Stop).ProcessName } catch { 'unknown' }
    }
}
