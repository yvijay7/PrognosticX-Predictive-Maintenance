@echo off
title PrognosticX Local Wi-Fi Sharing Server
echo ====================================================================
echo             PrognosticX Local Network Live Sharing
echo ====================================================================
echo.
echo Starting HTTP Server using Windows built-in services...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi*', 'Ethernet*' | Where-Object { $_.IPAddress -notlike '169.*' } | Select-Object -First 1).IPAddress; ^
$port = 8080; ^
$listener = New-Object System.Net.HttpListener; ^
$listener.Prefixes.Add(\"http://*:$port/\"); ^
try { $listener.Start(); } catch { $listener.Prefixes.Clear(); $listener.Prefixes.Add(\"http://localhost:$port/\"); $listener.Start(); } ^
Write-Host '====================================================================' -ForegroundColor Cyan; ^
Write-Host '   SHARE THIS LINK WITH YOUR FRIEND (Same Wi-Fi or Mobile Hotspot):' -ForegroundColor Yellow; ^
Write-Host \"   --> http://${ip}:${port}/\" -ForegroundColor Green; ^
Write-Host '====================================================================' -ForegroundColor Cyan; ^
Write-Host 'Press Ctrl+C in this window to stop sharing.`n'; ^
$mime = @{ '.html'='text/html'; '.css'='text/css'; '.js'='application/javascript'; '.json'='application/json'; '.csv'='text/csv'; '.png'='image/png' }; ^
while ($listener.IsListening) { ^
    $context = $listener.GetContext(); ^
    $req = $context.Request; ^
    $res = $context.Response; ^
    $urlPath = $req.Url.LocalPath; ^
    if ($urlPath -eq '/') { $urlPath = '/index.html'; } ^
    $filePath = (Get-Location).Path + $urlPath.Replace('/', '\'); ^
    if (Test-Path $filePath -PathType Leaf) { ^
        $ext = [System.IO.Path]::GetExtension($filePath).ToLower(); ^
        $res.ContentType = if ($mime.ContainsKey($ext)) { $mime[$ext] } else { 'application/octet-stream' }; ^
        $bytes = [System.IO.File]::ReadAllBytes($filePath); ^
        $res.ContentLength64 = $bytes.Length; ^
        $res.OutputStream.Write($bytes, 0, $bytes.Length); ^
    } else { ^
        $res.StatusCode = 404; ^
    } ^
    $res.OutputStream.Close(); ^
}"
pause
