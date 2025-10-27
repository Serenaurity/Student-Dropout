# ระบบทำนายการออกกลางคันของนักศึกษา
# Start System Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ระบบทำนายการออกกลางคันของนักศึกษา" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# เปลี่ยนไปยังโฟลเดอร์โปรเจค
Set-Location "dropout-prediction"

Write-Host "กำลังหยุด containers ที่รันอยู่..." -ForegroundColor Yellow
docker-compose down

Write-Host "กำลังเริ่มระบบใหม่..." -ForegroundColor Yellow
docker-compose up --build -d

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "ระบบพร้อมใช้งาน!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "กด Enter เพื่อปิดหน้าต่างนี้..." -ForegroundColor Gray
Read-Host
