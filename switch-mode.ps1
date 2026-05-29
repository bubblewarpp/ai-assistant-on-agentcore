# Switch between Development and Production mode
# Usage: .\switch-mode.ps1 [dev|prod]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Mode
)

$appFile = "src\App.jsx"
$devFile = "src\App.dev.jsx"
$prodFile = "src\App.prod.jsx"

if ($Mode -eq "dev") {
    Write-Host "🔄 Switching to DEVELOPMENT mode..." -ForegroundColor Cyan
    Write-Host "   - Authentication will be bypassed" -ForegroundColor Yellow
    Write-Host "   - Mock user will be used" -ForegroundColor Yellow
    
    if (Test-Path $devFile) {
        Copy-Item $devFile $appFile -Force
        Write-Host "✅ Switched to DEV mode successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next steps:" -ForegroundColor Cyan
        Write-Host "   1. Restart dev server if running (Ctrl+C, then npm run dev)" -ForegroundColor White
        Write-Host "   2. Refresh browser (Ctrl+Shift+R)" -ForegroundColor White
        Write-Host "   3. You should now bypass login screen" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $devFile not found!" -ForegroundColor Red
    }
}
elseif ($Mode -eq "prod") {
    Write-Host "🔄 Switching to PRODUCTION mode..." -ForegroundColor Cyan
    Write-Host "   - Real authentication will be required" -ForegroundColor Yellow
    Write-Host "   - Backend must be deployed" -ForegroundColor Yellow
    
    if (Test-Path $prodFile) {
        Copy-Item $prodFile $appFile -Force
        Write-Host "✅ Switched to PROD mode successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Next steps:" -ForegroundColor Cyan
        Write-Host "   1. Ensure backend is deployed (terraform apply)" -ForegroundColor White
        Write-Host "   2. Update .env with real values from Terraform outputs" -ForegroundColor White
        Write-Host "   3. Restart dev server (Ctrl+C, then npm run dev)" -ForegroundColor White
        Write-Host "   4. Login with real credentials" -ForegroundColor White
    } else {
        Write-Host "❌ Error: $prodFile not found!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Current mode: " -NoNewline -ForegroundColor Cyan
if ($Mode -eq "dev") {
    Write-Host "DEVELOPMENT 🛠️" -ForegroundColor Yellow
} else {
    Write-Host "PRODUCTION 🚀" -ForegroundColor Green
}
