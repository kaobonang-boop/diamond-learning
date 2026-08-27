import os
from .base import *  # noqa

DEBUG = False

# Serve static files directly from Gunicorn via WhiteNoise — no separate
# static file server needed for a small-to-medium deployment.
MIDDLEWARE = [MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]

# Use DATABASE_URL if provided (Render/Railway style), else discrete PG* vars.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import re
    m = re.match(
        r"postgres(?:ql)?://(?P<user>[^:]+):(?P<password>[^@]*)@(?P<host>[^:/]+):?(?P<port>\d*)/(?P<name>.+)",
        DATABASE_URL,
    )
    if not m:
        raise RuntimeError("DATABASE_URL is set but could not be parsed. Expected postgres://user:pass@host:port/dbname")
    g = m.groupdict()
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": g["name"],
            "USER": g["user"],
            "PASSWORD": g["password"],
            "HOST": g["host"],
            "PORT": g["port"] or "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "diamond_learning"),
            "USER": os.getenv("POSTGRES_USER", "diamond_learning"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

# Render (and most PaaS hosts) terminate HTTPS at a proxy and forward plain
# HTTP to the app, setting X-Forwarded-Proto to say what the original
# request was. Without this line, Django can't tell the request was secure,
# which breaks SECURE_SSL_REDIRECT and — critically — CSRF validation on
# every POST request, including login. This is what was breaking sign-in.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
