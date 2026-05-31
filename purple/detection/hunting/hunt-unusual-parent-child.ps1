# Detect suspicious parent-child process relationships
# Usage: powershell -ExecutionPolicy Bypass -File hunt-unusual-parent-child.ps1

Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID      = 4688
} -MaxEvents 1000 -ErrorAction SilentlyContinue | Where-Object {
    $_.Message -match 'winword\.exe.*cmd\.exe' -or
    $_.Message -match 'excel\.exe.*powershell\.exe' -or
    $_.Message -match 'outlook\.exe.*wscript\.exe' -or
    $_.Message -match 'mshta\.exe.*powershell\.exe'
} | Select-Object TimeCreated, Message
