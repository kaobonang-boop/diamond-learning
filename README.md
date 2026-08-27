# Diamond Learning

**Pressure makes diamonds.**

A full-stack Django web application for Botswana students preparing for
PSLE, JCE and BGCSE exams: syllabus tracking, notes, past papers, solved
papers, topic-by-topic practice quizzes, a study timetable, progress
tracking, and an AI study assistant ("Ask Tebogo").

This is a real, runnable application — not a mockup. It ships with
realistic seed data (every official PSLE/JCE/BGCSE subject, plus fully
worked topics/notes/questions for a demo subject set) and a demo student
account so you can test everything immediately.

---

## Tech stack

- **Backend:** Python, Django 6.1, Django REST Framework, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Django templates, HTML5, CSS3, vanilla JavaScript (no build step)
- **Auth:** Django's built-in authentication system
- **AI:** Pluggable provider abstraction (`apps/chatbot/providers.py`) — works out of the box with no API key, swaps to OpenAI or Anthropic via `.env`

## Project structure

```
diamond_learning/
├── config/                  # settings (base/development/production), root urls, wsgi/asgi
├── apps/
│   ├── accounts/             # registration, login, profile, password reset
│   ├── syllabus/              # EducationLevel, Subject, Topic, Subtopic, TopicProgress
│   ├── notes/                # Note, favourites, reading progress
│   ├── papers/                # PastPaper, SolvedQuestion, TopicalQuestion + quiz scoring
│   ├── progress/              # progress % calculations + My Progress dashboard
│   ├── timetable/             # StudySession CRUD, weekly/monthly views
│   ├── chatbot/               # Ask Tebogo: ChatConversation/ChatMessage + AI provider layer
│   └── core/                  # home page, student dashboard, global search, seed_data command
├── templates/                # all HTML templates, organised to mirror the apps above
├── static/css/style.css      # shared design system
├── media/                    # uploaded past papers, avatars (created at runtime)
├── requirements.txt
├── .env.example
├── gunicorn.conf.py
├── Procfile
└── manage.py
```

---

## Local development

### 1. Clone the project
```bash
git clone <your-repo-url> diamond_learning
cd diamond_learning
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure `.env`
```bash
cp .env.example .env
```
The defaults in `.env.example` are already correct for local development
(SQLite, `AI_PROVIDER=echo`, debug on) — you don't need to change anything
to get started. Generate a real `DJANGO_SECRET_KEY` before deploying.

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Load sample data (recommended)
```bash
python manage.py seed_data
```
This populates every PSLE/JCE/BGCSE subject, fleshes out topics/notes/
past-papers/solved-questions/topical-quizzes for a demo subject set
(BGCSE & JCE & PSLE Mathematics/English, plus BGCSE Physics), and creates
a demo student account:

```
username: student
password: diamond2026
```

### 7. Create a superuser (for /admin/)
```bash
python manage.py createsuperuser
```

### 8. Start the development server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/**. Sign in with the demo student account
above, or your own superuser at **http://127.0.0.1:8000/admin/**.

---

## Testing

Run the full test suite (43 tests covering registration, login, protected
pages, models, API endpoints, and progress calculations):

```bash
python manage.py test
```

Run a single app's tests:
```bash
python manage.py test apps.papers
```

---

## Ask Tebogo — AI provider configuration

Tebogo's backend is provider-agnostic (`apps/chatbot/providers.py`). Out of
the box, `AI_PROVIDER=echo` gives deterministic, no-key-required replies so
the whole app runs without any external account. To connect a real model,
set in `.env`:

```
AI_PROVIDER=openai        # or "anthropic"
AI_API_KEY=sk-...
AI_MODEL=gpt-4o-mini       # or e.g. claude-sonnet-4-6
```

Then install the matching optional dependency (see the commented-out lines
in `requirements.txt`). No other code changes are needed — every view and
API endpoint calls `get_ai_provider()` and never talks to a vendor SDK
directly. API keys are never hardcoded or committed; they're read from the
environment only.

---

## API

Browsable API root: **`/api/`** (session-authenticated; log in via
`/accounts/login/` first, or use `/api-auth/login/`).

| Endpoint | Methods | Notes |
|---|---|---|
| `/api/education-levels/` | GET | Public |
| `/api/subjects/` | GET | `?level=BGCSE` |
| `/api/topics/` | GET | `?subject=<id>` |
| `/api/notes/` | GET | `?subject=<id>&topic=<id>&q=<text>` |
| `/api/past-papers/` | GET | `?subject=<id>&year=<yyyy>` |
| `/api/solved-questions/` | GET | |
| `/api/topical-questions/` | GET | |
| `/api/progress/` | GET | Auth required. `?level=BGCSE` — the logged-in student's completion % |
| `/api/chat/conversations/` | GET, POST | Auth required |
| `/api/chat/conversations/<id>/` | GET, PUT, DELETE | Auth required |
| `/api/chat/conversations/<id>/send/` | POST `{"message": "..."}` | Auth required |

See `config/api_urls.py` for the full router definition.

---

## Deployment

The app is deployment-ready for Render, Railway, DigitalOcean App Platform,
or PythonAnywhere. General steps:

### 1. Environment variables
Set these on your platform (see `.env.example` for the full list):
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY` — a long random value (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `DJANGO_ALLOWED_HOSTS` — your domain(s)
- `DJANGO_CSRF_TRUSTED_ORIGINS` — `https://yourdomain.com`
- `DATABASE_URL` (or the discrete `POSTGRES_*` variables) — pointing at a managed PostgreSQL instance
- `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL` if you want Tebogo connected to a real model

### 2. Install & migrate
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 3. Run with Gunicorn
```bash
gunicorn -c gunicorn.conf.py config.wsgi:application
```
`gunicorn.conf.py` reads `PORT`/`WEB_CONCURRENCY` from the environment, so
it works as-is on Render/Railway/Heroku-style platforms. Static files are
served by WhiteNoise directly from Gunicorn — no separate static file host
needed for small-to-medium traffic.

### Platform notes
- **Render / Railway:** point the build command at `pip install -r requirements.txt && python manage.py collectstatic --noinput`, the release/start command at the `Procfile` entries (`release: python manage.py migrate --noinput`, `web: gunicorn -c gunicorn.conf.py config.wsgi:application`), and attach a managed Postgres add-on (both platforms inject `DATABASE_URL` automatically).
- **DigitalOcean App Platform:** same build/run commands; attach a Managed Database (Postgres) component and copy its connection string into `DATABASE_URL`.
- **PythonAnywhere:** upload the project, create a virtualenv, set the WSGI file to import `config.wsgi.application` with `DJANGO_SETTINGS_MODULE=config.settings.production`, and use their MySQL/Postgres add-on or an external Postgres host (PythonAnywhere's own DB is MySQL — swap the `ENGINE` in `config/settings/production.py` if you go that route).

### Media files in production
`PastPaper.file` and `UserProfile.avatar` are stored under `MEDIA_ROOT`.
For production, point `DEFAULT_FILE_STORAGE` at S3-compatible object
storage (e.g. `django-storages`) if your platform's filesystem isn't
persistent — the default `FileSystemStorage` in `production.py` assumes a
persistent disk.

---

## Security

- CSRF protection on every form (Django's built-in middleware)
- Passwords hashed with Django's PBKDF2 hasher (default)
- `SECRET_KEY`, database credentials, and AI API keys are read from
  environment variables only — never hardcoded, never committed
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
  HSTS, and clickjacking protection are all enabled in
  `config/settings/production.py`
- Every view that touches a student's own data (`@login_required`) checks
  `user=request.user` in its queryset, so one student can never read or
  modify another's timetable, chat, or progress

---

## Independent platform

Diamond Learning is an independent study platform and is **not affiliated
with the Botswana Examinations Council (BEC)**.
