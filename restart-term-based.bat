@echo off
echo ========================================
echo รีสตาร์ทระบบทำนายการออกกลางคัน (Term-based Models)
echo ========================================
echo.

echo กำลังหยุด containers...
cd dropout-prediction
docker-compose down

echo.
echo กำลังลบ containers และ images เก่า...
docker system prune -f

echo.
echo กำลังเริ่มระบบใหม่...
docker-compose up --build -d

echo.
echo รอให้ระบบเริ่มต้น...
timeout /t 20 /nobreak

echo.
echo ========================================
echo ระบบรีสตาร์ทเสร็จสิ้น!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo ระบบใหม่ใช้ XGBoost Models แยกตามเทอม:
echo - Term 1: model_term1.json (100 trees)
echo - Term 2: model_term2.json (200 trees)  
echo - Term 3+: model_term3.json (300 trees)
echo.
echo ทดสอบระบบที่: http://localhost:3000
echo.
echo กด Enter เพื่อปิดหน้าต่างนี้...
pause
