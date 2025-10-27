@echo off
cd dropout-prediction
docker-compose down
docker-compose up --build -d
echo.
echo ========================================
echo ระบบทำนายการออกกลางคันของนักศึกษา
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo กด Enter เพื่อปิดหน้าต่างนี้...
pause
