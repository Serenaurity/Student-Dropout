# การแก้ไขปัญหา Port 8000 ถูกใช้งานอยู่

## ปัญหา
```
Error response from daemon: driver failed programming external connectivity on endpoint dropout-api: Bind for 0.0.0.0:8000 failed: port is already allocated
```

## สาเหตุ
Port 8000 ถูกใช้งานโดยโปรแกรมอื่นอยู่แล้ว (อาจเป็น FastAPI server อื่น, Jupyter Notebook, หรือโปรแกรมอื่น)

## วิธีแก้ไข

### วิธีที่ 1: ใช้ Port ใหม่ (แนะนำ)
ระบบได้ถูกปรับให้ใช้ port 8001 แทนแล้ว:

**การเข้าถึงระบบ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

**วิธีรันระบบ:**
1. ดับเบิลคลิกไฟล์ `start-system.bat` หรือ `start-system.ps1`
2. หรือใช้คำสั่ง:
   ```bash
   cd dropout-prediction
   docker-compose down
   docker-compose up --build -d
   ```

### วิธีที่ 2: หยุดโปรแกรมที่ใช้ Port 8000

**Windows:**
```cmd
# หาโปรแกรมที่ใช้ port 8000
netstat -ano | findstr :8000

# หยุดโปรแกรม (แทน PID ด้วยหมายเลขที่ได้)
taskkill /PID <PID> /F
```

**PowerShell:**
```powershell
# หาโปรแกรมที่ใช้ port 8000
Get-NetTCPConnection -LocalPort 8000

# หยุดโปรแกรม
Stop-Process -Id <PID> -Force
```

### วิธีที่ 3: เปลี่ยน Port ใน Docker Compose

หากต้องการใช้ port อื่น สามารถแก้ไขไฟล์ `dropout-prediction/docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8002:8000"  # เปลี่ยน 8001 เป็น 8002 หรือ port อื่น
```

และอัปเดตไฟล์ `dropout-prediction/frontend/index.html`:
```javascript
const API_BASE = 'http://localhost:8002/api/v1';  // เปลี่ยน port ให้ตรงกัน
```

## การตรวจสอบสถานะ

**ตรวจสอบ containers:**
```bash
docker-compose ps
```

**ดู logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**เข้าถึง container:**
```bash
docker exec -it dropout-api bash
```

## การทดสอบระบบ

1. **ทดสอบ Backend:**
   - เปิด http://localhost:8001/docs
   - ทดสอบ API endpoints

2. **ทดสอบ Frontend:**
   - เปิด http://localhost:3000
   - กรอกข้อมูลและทดสอบการทำนาย

3. **ทดสอบการเชื่อมต่อ:**
   ```bash
   curl http://localhost:8001/api/v1/health
   ```

## ปัญหาอื่นๆ ที่อาจพบ

### CORS Error
หากพบ CORS error ใน frontend ให้ตรวจสอบ:
- Backend รันอยู่ที่ port 8001
- Frontend เชื่อมต่อกับ port ที่ถูกต้อง

### Model Not Loaded
หากพบ error "Model not loaded":
- ตรวจสอบว่าไฟล์ model อยู่ใน `dropout-prediction/backend/ml_models/`
- ตรวจสอบ logs ของ backend container

### Container ไม่เริ่ม
หาก container ไม่เริ่ม:
- ตรวจสอบ Docker Desktop เปิดอยู่
- ลองรัน `docker-compose down` แล้ว `docker-compose up --build -d` ใหม่

## การลบระบบทั้งหมด

หากต้องการเริ่มใหม่ทั้งหมด:
```bash
cd dropout-prediction
docker-compose down
docker system prune -f
docker-compose up --build -d
```

## ติดต่อขอความช่วยเหลือ

หากยังมีปัญหา:
1. ตรวจสอบ logs ของ containers
2. ตรวจสอบว่า Docker Desktop ทำงานปกติ
3. ลองรีสตาร์ท Docker Desktop
4. ตรวจสอบ firewall settings
