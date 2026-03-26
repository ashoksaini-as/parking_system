# 🅿 ParkSmart — Parking Management System

Full-stack Flask + MySQL parking management system with role-based access, real-time slot tracking, PDF receipts, and revenue analytics.

---

## 📁 Project Structure

```
parking_system/
├── app.py                  # App factory (entry point)
├── gunicorn.conf.py        # Gunicorn config
├── Procfile                # Render/Heroku deploy
├── render.yaml             # Render deploy spec
├── requirements.txt
├── schema.sql              # MySQL schema + seed data
├── init_db.py              # Admin password seeder
├── .env.example            # Environment variables template
└── app/
    ├── __init__.py         # MySQL init
    ├── routes/
    │   ├── auth.py         # Login, register, logout
    │   ├── admin.py        # Admin CRUD routes
    │   └── user.py         # User routes
    ├── models/
    │   └── db.py           # All DB queries (CRUD)
    ├── services/
    │   └── parking.py      # Fee calc + PDF receipt
    ├── templates/
    │   ├── shared/
    │   │   └── base.html   # Sidebar + navbar layout
    │   ├── auth/
    │   │   ├── login.html
    │   │   └── register.html
    │   ├── admin/
    │   │   ├── dashboard.html
    │   │   ├── entry.html
    │   │   ├── exit.html
    │   │   ├── slots.html
    │   │   ├── history.html
    │   │   └── users.html
    │   └── user/
    │       ├── dashboard.html
    │       ├── entry.html
    │       └── history.html
    └── static/
        └── receipts/       # Generated PDF receipts
```

---

## ⚙️ Local Setup

### 1. Clone & create virtualenv
```bash
git clone <repo>
cd parking_system
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MySQL setup
```bash
mysql -u root -p
```
```sql
CREATE DATABASE parking_db;
EXIT;
```
```bash
mysql -u root -p parking_db < schema.sql
```

### 3. Seed admin password
```bash
python init_db.py
# Copy the generated INSERT statement and run it in MySQL
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DB=parking_db
SECRET_KEY=any-random-secret-key
```

### 5. Run development server
```bash
python app.py
# Visit: http://localhost:5000
```

### 6. Run with Gunicorn (production-like)
```bash
gunicorn "app:create_app()" -c gunicorn.conf.py
# Visit: http://localhost:8000
```

---

## 🚀 Render Deploy Steps

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "app:create_app()" -c gunicorn.conf.py`
5. Add Environment Variables:
   - `MYSQL_HOST` → your PlanetScale/Aiven/Railway MySQL host
   - `MYSQL_USER` → db user
   - `MYSQL_PASSWORD` → db password
   - `MYSQL_DB` → `parking_db`
   - `SECRET_KEY` → random string
6. Deploy ✅

**Recommended MySQL providers for Render:**
- [PlanetScale](https://planetscale.com) (free tier)
- [Aiven](https://aiven.io) (free tier)
- [Railway](https://railway.app) (free tier)

---

## 👤 Default Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | 1234     |

---

## 🧩 Features

| Feature | Admin | User |
|---------|-------|------|
| Dashboard with stats | ✅ | ✅ |
| Vehicle entry (auto slot) | ✅ | ✅ |
| Vehicle exit + fee calc | ✅ | ❌ (admin only) |
| PDF receipt download | ✅ | ✅ |
| Slot grid (50 slots) | ✅ | ❌ |
| Full history + search/sort | ✅ | Own only |
| Revenue charts | ✅ | ❌ |
| User management | ✅ | ❌ |
| Delete records | ✅ | ❌ |

---

## 💰 Pricing Logic

- **Rate:** ₹20 per hour
- **Minimum:** ₹20 (even for <1 hour)
- **Formula:** `fee = max(duration_hours × 20, 20)`

---

## 🔒 Security

- Passwords hashed with `werkzeug.security` (PBKDF2 SHA-256)
- Role-based decorators (`@admin_required`, `@login_required`)
- SQL injection prevented via parameterized queries
- Foreign key constraints enforced
- No duplicate vehicle numbers (UNIQUE constraint)
