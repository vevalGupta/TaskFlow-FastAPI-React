# TaskFlow — FastAPI + React

Scalable REST API with JWT authentication, role-based access control, and a React dashboard.

## Stack

| Layer     | Technology                                   |
|-----------|----------------------------------------------|
| Backend   | FastAPI · SQLAlchemy · Alembic · Pydantic v2 |
| Auth      | JWT (python-jose) · bcrypt (passlib)         |
| Database  | MySQL 8+                                     |
| Frontend  | React 18 · React Router v6 · Axios           |
| Rate limit| SlowAPI                                      |
| Logging   | Loguru                                       |

---

## Project structure

```
fastapi-app/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth/router.py       ← register, login, refresh, logout
│   │   │   ├── users/router.py      ← profile, admin user management
│   │   │   ├── tasks/router.py      ← full task CRUD
│   │   │   ├── admin/router.py      ← dashboard, all tasks
│   │   │   ├── router.py            ← combines all routers under /api/v1
│   │   │   └── deps.py              ← get_current_user, require_role
│   │   ├── core/
│   │   │   ├── config.py            ← Pydantic settings
│   │   │   ├── security.py          ← hashing + JWT
│   │   │   ├── exceptions.py        ← AppError helpers
│   │   │   ├── responses.py         ← unified response envelope
│   │   │   └── logger.py            ← Loguru setup
│   │   ├── db/session.py            ← SQLAlchemy engine + get_db
│   │   ├── models/models.py         ← User, Task, RefreshToken ORM
│   │   ├── schemas/schemas.py       ← Pydantic request/response models
│   │   ├── services/
│   │   │   ├── auth_service.py      ← register, login, refresh, logout
│   │   │   └── task_service.py      ← list, get, create, update, delete
│   │   └── main.py                  ← FastAPI app factory, middleware, error handlers
│   ├── alembic/env.py
│   ├── schema.sql                   ← raw MySQL DDL
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/client.js            ← Axios + auto-refresh interceptor
    │   ├── context/AuthContext.jsx  ← global auth state
    │   ├── components/
    │   │   ├── UI.jsx               ← Button, Badge, Alert, Spinner, FormField
    │   │   └── Layout.jsx           ← sidebar navigation
    │   ├── pages/
    │   │   ├── Auth.jsx             ← Login + Register
    │   │   ├── Dashboard.jsx
    │   │   ├── Tasks.jsx            ← full CRUD with modal
    │   │   └── Admin.jsx            ← Overview, Users, All Tasks
    │   └── App.jsx                  ← protected routing
    └── package.json
```

---

## Quick start

### 1 — Database

```sql
-- Run schema.sql or let SQLAlchemy auto-create on first boot (DEBUG=true)
mysql -u root -p < backend/schema.sql
```

### 2 — Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set DATABASE_URL and JWT_SECRET

uvicorn app.main:app --reload --port 8000
```

API docs auto-generated at:
- Swagger UI → http://localhost:8000/api/docs
- ReDoc      → http://localhost:8000/api/redoc

### 3 — Frontend

```bash
cd frontend
npm install
npm start          # proxies /api → http://localhost:8000
```

Open http://localhost:3000

---

## API reference (v1)

### Auth — public
| Method | Endpoint                  | Description                       |
|--------|---------------------------|-----------------------------------|
| POST   | /api/v1/auth/register     | Register (returns 201 + user)     |
| POST   | /api/v1/auth/login        | Login → accessToken + refreshToken|
| POST   | /api/v1/auth/refresh      | Rotate refresh token              |
| POST   | /api/v1/auth/logout       | Invalidate refresh token (JWT req)|

### Users — JWT required
| Method | Endpoint                  | Description                       |
|--------|---------------------------|-----------------------------------|
| GET    | /api/v1/users/me          | Own profile                       |
| PATCH  | /api/v1/users/me          | Update name / password            |
| GET    | /api/v1/users             | List users **admin**              |
| PATCH  | /api/v1/users/:id/role    | Change role **admin**             |
| DELETE | /api/v1/users/:id         | Soft-delete **admin**             |

### Tasks — JWT required
| Method | Endpoint                  | Description                       |
|--------|---------------------------|-----------------------------------|
| GET    | /api/v1/tasks             | List own tasks (filter+paginate)  |
| POST   | /api/v1/tasks             | Create task → 201                 |
| GET    | /api/v1/tasks/:id         | Get task by ID                    |
| PUT    | /api/v1/tasks/:id         | Full replace                      |
| PATCH  | /api/v1/tasks/:id         | Partial update                    |
| DELETE | /api/v1/tasks/:id         | Soft-delete → 204                 |

### Admin — role: admin
| Method | Endpoint                  | Description                       |
|--------|---------------------------|-----------------------------------|
| GET    | /api/v1/admin/dashboard   | System stats                      |
| GET    | /api/v1/admin/tasks       | All tasks with owner info         |

---

## Security notes

- Passwords hashed with **bcrypt** (cost factor 12)
- Access tokens expire in **15 minutes**; refresh tokens in **7 days**
- Refresh tokens stored in DB and **rotated on every use**
- Role **privilege escalation blocked** — only an existing admin can create another admin
- Rate limiting: **100 req/min** per IP via SlowAPI
- CORS configured via `CORS_ORIGINS` env var
- Request body capped to prevent payload attacks