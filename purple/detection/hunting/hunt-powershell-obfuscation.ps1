# Hunt for obfuscated PowerShell commands
# Usage: powershell -ExecutionPolicy Bypass -File hunt-powershell-obfuscation.ps1

Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-PowerShell/Operational'
    ID      = 4104
} -MaxEvents 500 -ErrorAction SilentlyContinue | Where-Object {
    $_.Message -match 'encodedcommand|enc\s|FromBase64String|bxor|::Compress|Invoke-Expression|\bIEX\b'
} | Select-Object TimeCreated, Id, Message
