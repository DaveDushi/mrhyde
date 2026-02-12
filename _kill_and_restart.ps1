$conns = Get-NetTCPConnection -LocalPort 8432 -ErrorAction SilentlyContinue
foreach ($c in $conns) {
    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1
Start-Process -FilePath "py" -ArgumentList "C:\Users\david\jean\mrhyde-pkg\iconic-whale\_serve_dashboard.py" -WindowStyle Hidden
