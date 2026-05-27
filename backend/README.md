# 🛡️ A2 Sentinel

> *AI jo aapke code ko hacker ki nazar se test kare — aur exploit hone se pehle fix kar de.*

**AI-Powered Security Scanning SaaS** — finds vulnerabilities before hackers do.

---

## 📁 Project Structure

```
a2-sentinel/
│
├── app/                          # Main application
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # POST /api/auth/register, /login
│   │   │   ├── scan.py           # POST /api/scan, /simulate, /fix
│   │   │   └── user.py           # GET /api/user/me, /usage
│   │   └── dependencies.py       # Auth, quota enforcement
│   │
│   ├── core/
│   │   ├── config.py             # All settings (env vars)
│   │   ├── security.py           # JWT + password hashing
│   │   ├── exceptions.py         # Custom exception classes
│   │   └── logging.py            # Loguru setup
│   │
│   ├── db/
│   │   └── database.py           # Async SQLAlchemy engine + session
│   │
│   ├── models/
│   │   ├── user.py               # User DB model
│   │   └── scan.py               # Scan DB model
│   │
│   ├── schemas/
│   │   ├── user.py               # User Pydantic schemas
│   │   └── scan.py               # Scan Pydantic schemas
│   │
│   ├── services/
│   │   ├── ai_engine.py          # Claude AI integration (scan/simulate/fix)
│   │   ├── rule_scanner.py       # OWASP rule-based scanner (regex)
│   │   ├── scan_service.py       # Scan orchestration pipeline
│   │   └── auth_service.py       # User auth business logic
│   │
│   ├── utils/
│   │   └── helpers.py            # Utility functions
│   │
│   ├── workers/
│   │   ├── celery_app.py         # Celery configuration
│   │   └── tasks.py              # Background tasks
│   │
│   └── main.py                   # FastAPI app entry point
│
├── tests/
│   ├── unit/
│   │   ├── test_rule_scanner.py  # Rule scanner tests (30+ cases)
│   │   └── test_helpers.py       # Helper utility tests
│   └── integration/              # API integration tests (Phase 2)
│
├── migrations/                   # Alembic DB migrations
│   ├── env.py
│   └── versions/
│
├── scripts/                      # Dev utility scripts
├── .env.example                  # Environment variables template
├── alembic.ini                   # Alembic config
├── docker-compose.yml            # Docker services
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/yourname/a2-sentinel.git
cd a2-sentinel

# 2. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Start all services
docker-compose up

# API runs at: http://localhost:8000
# Docs at:    http://localhost:8000/docs
# Flower at:  http://localhost:5555
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

# 4. Start PostgreSQL and Redis (via Docker)
docker-compose up db redis -d

# 5. Run migrations
alembic upgrade head

# 6. Start the API
uvicorn app.main:app --reload
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ❌ | Create account |
| POST | `/api/auth/login` | ❌ | Login, get JWT |
| POST | `/api/scan` | ✅ | Scan code for vulnerabilities |
| POST | `/api/scan/simulate` | ✅ | Attack simulation |
| POST | `/api/scan/fix` | ✅ | Auto-generate secure code |
| GET | `/api/scan/history` | ✅ | Paginated scan history |
| GET | `/api/scan/{id}` | ✅ | Get specific scan |
| GET | `/api/user/me` | ✅ | Profile info |
| GET | `/api/user/usage` | ✅ | Scan usage + API key |
| PUT | `/api/user/profile` | ✅ | Update profile |
| POST | `/api/user/regenerate-key` | ✅ | New API key |
| GET | `/health` | ❌ | Health check |

---

## 🔐 Authentication

Two methods supported:

**JWT Bearer Token** (for dashboard/frontend):
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**API Key** (for programmatic/CI-CD access):
```
X-API-Key: a2s_abc123def456...
```

---

## 📦 Example Usage

### 1. Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@company.com", "password": "SecurePass1", "full_name": "Ali Hassan"}'
```

### 2. Scan Code
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "query = \"SELECT * FROM users WHERE id = \" + user_id\ncursor.execute(query)",
    "language": "python",
    "include_simulation": true,
    "include_fix": true
  }'
```

### 3. Use API Key (CI/CD)
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "X-API-Key: a2s_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"code": "...", "language": "python"}'
```

---

## 🧪 Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 💰 Plans

| Plan | Scans/Month | Price |
|------|-------------|-------|
| Free | 10 | $0 |
| Pro | 500 | $20-50/mo |
| Team | 2,000 | $100-500/mo |
| Enterprise | Unlimited | $1000+/mo |
| API | Pay-per-scan | $0.01-0.10/scan |

---

## 🗺️ Roadmap

- **Phase 1** ✅ Core scan engine + API
- **Phase 2** → Attack simulation + dashboard
- **Phase 3** → GitHub integration + CI/CD
- **Phase 4** → Real-time API shield
