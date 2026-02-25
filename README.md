# Smart Lock Face (Web + Server + WebSocket)

## 1) Ý tưởng
- Web admin mở camera (PC/Phone browser), chụp ảnh (base64) -> gửi backend
- Backend detect+align+embed bằng InsightFace (ArcFace buffalo_l) -> so khớp 1:N
- Enroll theo cơ chế 5 shots: embed 5 ảnh -> lấy trung bình (mean embedding) -> lưu DB
- Verify 1:N theo lock: so sánh cosine với embedding của các user đã enroll trong lock
- Broadcast event realtime qua WebSocket (/ws)
- Thiết kế DB có Lock + Member + Template + Log để sau này đồng bộ Mobile App + ESP32

## 2) Cài và chạy
### Bước 1: tạo môi trường
```bash
cd smart-lock-face/server
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```
### Bước 2: cấu hình ENV và chạy server
   cp ../.env.example .env
   # sửa JWT_SECRET nếu muốn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```bash
Server sẽ:
#API: http://localhost:8000/api
#Swagger: http://localhost:8000/docs
#Websocket: ws://localhost:8000/ws
#Web admin static (serve sẵn): http://localhost:8000/
```
### Bước 3: mở web admin
```bash
Mở trình duyệt vào: http://localhost:8000/
Bấm "Start Camera"
Nhập tên -> "Enroll 5 shots"
Bấm "Verify"
```
## 3) Cơ chế hoạt động
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
## 4) Đổi model sau này
```bash
Thêm engine mới trong app/face/engines/
Map trong app/face/registry.py
Đổi MODEL_KEY trong .env
Lưu ý: embeddings cũ không dùng chung -> re-enroll hoặc versioning theo model_key.

---

# 13) Gợi ý nâng cấp “chống sinh đôi” (đúng hướng cho bạn)
Bạn đang muốn “nhận diện được sinh đôi” → thường không chỉ dựa vào ArcFace + threshold cố định. Khung kiến trúc hiện tại đã sẵn để bạn nâng cấp theo 3 hướng (không cần sửa router):

1) **Quality + anti-spoof**  
- Thêm quality gates (blur/too dark/face size/pose) vào `app/face/quality/filters.py`.
- Sau này thêm anti-spoof (liveness) như model riêng, đặt trong `face/quality/`.

2) **Adaptive threshold theo user/lock**  
- Lưu `threshold_override` theo lock hoặc theo account (thêm cột DB), verify_service dùng ưu tiên override.

3) **Multi-template nâng cao thay vì 1 mean**  
- Hiện MVP: 5 shots -> mean -> 1 template/user/model.
- Nâng cấp: lưu **K templates** (theo session) và match theo:
  - `score_person = max(cos(query, tpl_i))`
  - hoặc **mean of top-k** để ổn định.
  - cái này bạn chỉ sửa `templates_repo` + `verify_service`.

---

Nếu bạn muốn, mình có thể viết tiếp **module “device transport”** (MQTT/WebSocket-to-ESP32) theo đúng kiến trúc này:  
- `app/device/transport/mqtt.py`  
- `app/services/device_service.py` publish command  
- ESP32 subscribe topic `smartlock/{lock_code}/cmd` và báo trạng thái `.../status` (đèn xanh/đỏ/công tắc).

```
## 5) Thiết kế sẵn để kết nối ESP32
```bash
DB có bảng locks với field code (pairing code)
Có router /api/device/heartbeat (stub)
Khi verify, server broadcast event LOCK_CMD:
   action: OPEN / DENY / ALARM
   ok: true/false
   Sau này chỉ cần thêm lớp transport:
MQTT publish
hoặc ESP32 gọi HTTP long-poll / WebSocket client
mà không phải sửa logic verify/enroll.
```