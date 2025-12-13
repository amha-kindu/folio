# Library Management System

## 📌 Overview
- Backend service for managing a library’s catalog and lending operations.
- Serves anonymous visitors (browse/search), registered members (JWT auth), and administrators (full management + dashboard).
- Core capabilities: browse/search books, borrow/return, administer books/users/loans, and view metrics via the admin dashboard.
 - REST APIs with JWT auth; session-based admin dashboard for operational control (admin-only).

---

## ✨ Features

### User Features
- Browse and search books (public access).
- Borrow and return books (authenticated; current policy restricts loan creation to admin/staff).
- JWT-based authentication (register, login, refresh).

### Admin Features
- Manage books (add, edit, delete).
- Manage users (activate/deactivate, assign roles via admin APIs).
- View/manage loans and dashboard metrics (Tailwind UI with filters, pagination, modals).

---

## 🧑‍🤝‍🧑 User Roles & Permissions
- **Anonymous users**: browse books.
- **Registered users (members)**: search books; borrowing currently restricted to admin/staff via loans API; dashboard is admin-only.
- **Administrators**: manage books, users, and loans; access dashboard UI.
- **Staff**: supported role; dashboard remains admin-only; loan creation allowed per API policy.

---

## 🔐 Authentication & Authorization
- User registration and login endpoints.
- JWT authentication using DRF SimpleJWT.
- Role-based access control on protected endpoints (admin/staff for mutations; admin-only dashboard).

---

## 🗄️ Data Models

### User
- Custom user model extending Django User with `role` (admin/staff/member); hashed passwords; admin/staff imply staff/superuser flags as appropriate.

### Book
- Title, Author, ISBN, Page count, Description, Published date.
- Availability: `total_copies`, `available_copies`, `is_active`, derived `is_available`.

### Loan
- User (borrower), Book, Borrowed timestamp, Due timestamp (optional), Returned timestamp.
- Unique active loan constraint per user/book; availability updates on borrow/return.

---

## 🔌 API Endpoints (high level)

### Authentication
- Register: `/api/auth/register/`
- Login (JWT): `/api/auth/login/`
- Token refresh: `/api/auth/refresh/`

### Books
- List/search/filter with pagination: `/api/books/` (public list/retrieve; admin create/update/delete).
- Query params: `q` (title/author/isbn), `author`, `availability` (available|unavailable), ordering.

### Loans
- Borrow (create) and list: `/api/loans/` (admin/staff per current policy).
- Return: `POST /api/loans/{id}/return/`
- Filters: `status` (active/returned/overdue), `user`, `book`, `start`, `end`.

### Users (admin)
- CRUD via `/api/admin/users/`

---

## 🧪 Testing

```bash
# full suite with coverage
poetry run pytest

# coverage report with missing lines and HTML/XML outputs
poetry run pytest --cov --cov-report=term-missing --cov-report=html --cov-report=xml

# open HTML coverage report
start htmlcov/index.html      # Windows
open htmlcov/index.html       # macOS
xdg-open htmlcov/index.html   # Linux
```

---

## 📖 API Documentation
- Swagger UI: `/swagger/`
- JSON/YAML schema: `/swagger.json`, `/swagger.yaml`
- ReDoc: `/redoc/`

---

## 🛠️ Tech Stack

### Backend
- Django 6, Django REST Framework.

### Database
- SQLite by default; PostgreSQL recommended for production (set `DATABASE_URL`).

### Authentication
- JWT (SimpleJWT).

### Tooling
- Docker, Poetry, Git, Gunicorn, Whitenoise (Heroku-friendly).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Poetry
- Docker (optional)
- PostgreSQL (optional for local/prod)

### Installation
```bash
poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py createsuperuser  # required for dashboard
poetry run python manage.py runserver
```

### Environment
Create `.env` (example):
```
SECRET_KEY=dev-secret
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 🐳 Docker Setup
- Dockerfile builds with Poetry and uses `entrypoint.sh` to run migrations and create a superuser if env vars are provided.
- Run:
```bash
docker build -t library-api .
docker run -p 8000:8000 --env-file .env \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=changeme \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  library-api
```
- Entrypoint runs migrations and creates the superuser before starting Gunicorn.
- Static files are collected at build; ensure reverse proxy serves `/static/` (Whitenoise storage configured).

---

## ☁️ Deployment
- Heroku-friendly: use Gunicorn and Whitenoise.
- Set environment variables (SECRET_KEY, DEBUG=0, ALLOWED_HOSTS, DATABASE_URL, JWT settings).
- Use managed PostgreSQL (e.g., Heroku Postgres).
- Collect static files before release (`python manage.py collectstatic`).
- Enforce HTTPS and secure cookies in production; set `CSRF_TRUSTED_ORIGINS` to your domain(s).
 - Add `whitenoise.middleware.WhiteNoiseMiddleware` if serving static assets from the app in production.

---

## 🔒 Security Considerations
- CSRF protection enabled (Django); set `CSRF_TRUSTED_ORIGINS`.
- XSS prevention via Django templating; avoid unsafe `mark_safe`.
- SQL injection protection via Django ORM.
- Production settings: HTTPS redirect, secure cookies, HSTS, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS=DENY`; lock down `ALLOWED_HOSTS`; keep `SECRET_KEY` secret.

---

## 📈 Future Improvements
- Due dates/overdue notifications.
- Book categories/tags and recommendations.
- Fine management.
- Email/notification workflows.
- Advanced analytics for admins.

---

## 🤝 Contributing
- Fork and open a PR with a clear description.
- Follow existing code style; add/maintain tests.
- Ensure `pytest` passes and keep coverage healthy.

---

## 📄 License
- Add your chosen license file (e.g., MIT/Apache-2.0) and update this section accordingly.
