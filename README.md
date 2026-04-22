# Smart Lock Face (Web + Server + WebSocket)

## 1. Cài đặt và chạy

### Bước 1: Tạo môi trường
```bash
cd smart-lock-face/server
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### Bước 2: Cấu hình ENV và chạy server
```bash
cp ../.env.example .env
# sửa JWT_SECRET nếu muốn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Server sẽ phục vụ các URL sau:
# API: http://localhost:8000/api
# Swagger Docs: http://localhost:8000/docs
# Websocket: ws://localhost:8000/ws
# Web Owner (Admin UI): http://localhost:8000/owner/
# Web User (User UI): http://localhost:8000/user/
# (Truy cập http://localhost:8000/ sẽ tự động redirect tới /owner/login.html)
```

### Bước 2.5: Tạo dữ liệu mẫu (tuỳ chọn)
Để có sẵn dữ liệu test mà không cần tạo thủ công qua giao diện, hãy chạy file seed (đảm bảo đang đứng ở thư mục `server` và đã kích hoạt môi trường `.venv`):
```bash
python -m app.scripts.seed_dev
```
Dữ liệu mẫu sinh ra gồm:
- **Owner**: `owner@example.com` / `Owner123456`
- **User**: `user@example.com` / `User123456`
- **Lock mẫu**: `LOCK-001` (đã được gán sẵn cho Owner và User trên)
- **Device UID**: `lock_001`

### Bước 3: Hướng dẫn sử dụng Web
```bash
1. Truy cập Web Owner: http://localhost:8000/owner/ để đăng nhập.
2. Vào mục "Locks" để tạo một khóa mới (nếu chưa có).
3. Vào mục "Users" để tạo người dùng và gán cho khóa.
4. Vào mục "Enroll": Chọn Lock và User -> "Start Camera" -> "Auto 5" -> "Enroll Face Templates".
5. Truy cập Web User: http://localhost:8000/user/ -> Đăng nhập.
6. Tại giao diện Verify: Chọn Lock -> "Start Camera" -> "Capture & Verify" để mở khóa.
```

## 2. Cơ chế hoạt động

### Auth + Role
```bash
Account đăng ký / đăng nhập -> JWT
Lock có members với role:
   OWNER: tạo lock, add member   
   USER: có thể verify/enroll nếu được cấp quyền (hiện MVP cho member được enroll; production có thể siết theo OWNER)
```

### Enroll
```bash
Web chụp 5 ảnh -> POST /api/enroll
Server embed từng ảnh -> lưu FaceTemplate (bytes float32) kèm model_key/dim
Broadcast event ENROLL lên WebSocket
```

### Verify
```bash
Web chụp 1 ảnh -> POST /api/verify
Server embed -> load templates theo (lock_id + model_key)
score = cosine(query, template)
best_score >= THRESH => success
Lưu AccessLog
Broadcast event VERIFY + LOCK_CMD (OPEN/DENY) lên WebSocket
```