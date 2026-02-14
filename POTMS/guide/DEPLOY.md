# คู่มือ Deploy POTMS ตั้งแต่ต้นจนจบ

## ขั้นตอนที่ 1: ตั้งค่า Google OAuth Credentials

1.  เปิด [Google Cloud Console](https://console.cloud.google.com/)
2.  สร้าง Project ใหม่ หรือเลือก Project ที่มี
3.  ไปที่ **APIs & Services** → **OAuth consent screen**
    *   **User Type:** External
    *   **App name:** POTMS
    *   **User support email:** email ของคุณ
    *   **Developer contact:** email ของคุณ
    *   Save and Continue (กดผ่าน Scopes, Test users ได้เลย)
4.  ไปที่ **APIs & Services** → **Credentials** → **+ CREATE CREDENTIALS** → **OAuth client ID**
    *   **Application type:** Web application
    *   **Name:** POTMS
    *   **Authorized redirect URIs** เพิ่ม:
        *   `http://localhost:8000/accounts/google/login/callback/`
    *   กด **Create**
5.  จะได้ **Client ID** กับ **Client Secret** → จดไว้

---

## ขั้นตอนที่ 2: Clone โปรเจค

```bash
git clone https://github.com/Thavizup-Deesan/DSSI-PROJECT-2568.git
cd DSSI-PROJECT-2568/POTMS
```

---

## ขั้นตอนที่ 3: ตั้งค่า Environment

แก้ไขไฟล์ `docker-compose.dev.yml` ใส่ค่า `GOOGLE_CLIENT_SECRET`:

```yaml
environment:
  - GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx   # ← ใส่ค่าจาก Google Console
```

หรือถ้าต้องการใช้ **Client ID** ตัวใหม่ ให้เพิ่มทั้งสองค่า:

```yaml
environment:
  - GOOGLE_CLIENT_ID=xxxxxxxxxxxx.apps.googleusercontent.com
  - GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxx
```

---

## ขั้นตอนที่ 4: Build และ Run

รันคำสั่งต่อไปนี้เพื่อเริ่มระบบ:

```bash
docker compose -f docker-compose.dev.yml up --build
```

คำสั่งนี้จะทำขั้นตอนทั้งหมดอัตโนมัติ:
1.  **Build Docker image** (ติดตั้ง Python dependencies)
2.  **Migrate Database** (`python manage.py migrate --noinput`)
3.  **Seed Data** (Migration 0002):
    *   สร้าง Admin users: `wayo.p@ubu.ac.th`, `thavizup.de.66@ubu.ac.th`
    *   ตั้งค่า Google SocialApp โดยใช้ Client ID + Secret จาก environment variables
4.  **Start Server** (`runserver 0.0.0.0:8000`)

---

## ขั้นตอนที่ 5: ทดสอบ

1.  เปิดเบราว์เซอร์ไปที่: [http://localhost:8000](http://localhost:8000)
2.  กด **Login with Google**
3.  เลือกบัญชี `@ubu.ac.th`
4.  เข้าสู่ระบบสำเร็จ

---

## สรุป Flow ทั้งหมด

```txt
Google Cloud Console          Docker Compose
──────────────────          ──────────────
1. สร้าง OAuth Client ID    3. ใส่ GOOGLE_CLIENT_SECRET ใน docker-compose.dev.yml
2. จด Client ID + Secret    4. docker compose up --build
   ↓                            ↓
   Redirect URI:             อัตโนมัติ:
   localhost:8000/accounts/    ├─ migrate (สร้างตาราง)
   google/login/callback/      ├─ seed admin users
                               ├─ seed Google SocialApp (Client ID + Secret)
                               └─ runserver :8000
                                    ↓
                              5. เปิด http://localhost:8000 → Login with Google
```

> **หมายเหตุ:** ปัจจุบัน Client ID default (`129454383537-...`) ถูก hardcode ไว้แล้วใน `settings.py` และ `migration` ดังนั้นถ้าใช้ Client ID เดิมที่มีอยู่ แค่ใส่ `GOOGLE_CLIENT_SECRET` ก็พอ ไม่ต้องสร้าง OAuth Client ใหม่
