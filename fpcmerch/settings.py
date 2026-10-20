"""Settings for the FPCMerch project."""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}

DEBUG = env_bool("DEBUG", True)
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-change-this-key-before-deploying"
    else:
        raise ImproperlyConfigured("Define SECRET_KEY en el entorno de producción.")

def env_list(name, default=""):
    return [value.strip() for value in os.environ.get(name, default).split(",") if value.strip()]

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if render_hostname:
    render_origin = f"https://{render_hostname}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "apps.users.apps.UsersConfig", "apps.products.apps.ProductsConfig",
    "apps.cart.apps.CartConfig", "apps.orders.apps.OrdersConfig",
    "apps.contact.apps.ContactConfig", "apps.pages.apps.PagesConfig", "apps.api.apps.ApiConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "fpcmerch.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug", "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
        "apps.products.context_processors.store_categories", "apps.cart.context_processors.cart_summary",
        "apps.pages.context_processors.store_info",
    ]},
}]
WSGI_APPLICATION = "fpcmerch.wsgi.application"
ASGI_APPLICATION = "fpcmerch.asgi.application"
database_url = os.environ.get("DATABASE_URL", "").strip()
if database_url:
    DATABASES = {"default": dj_database_url.parse(
        database_url,
        conn_max_age=60,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    )}
elif DEBUG:
    database_name = Path(os.environ.get("DATABASE_NAME", "devFPCMerch.db"))
    if not database_name.is_absolute():
        database_name = BASE_DIR / database_name
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": database_name,
        "OPTIONS": {"timeout": 20},
    }}
else:
    raise ImproperlyConfigured("Define DATABASE_URL en producción; SQLite local no es persistente en Render.")
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["apps.users.backends.EmailBackend"]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "").strip()
if CLOUDINARY_URL:
    import cloudinary

    cloudinary.config(secure=True)
    STORAGES["default"] = {"BACKEND": "apps.products.storage.CloudinaryMediaStorage"}
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "users:login"
CSRF_FAILURE_VIEW = "apps.api.views.csrf_failure"
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "FPCMerch <hola@fpcmerch.co>"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_SAVE_EVERY_REQUEST = False
FREE_SHIPPING_THRESHOLD = 150000
SHIPPING_FLAT_RATE = 12000
STORE_INFO = {
    "address": "Calle 72 #15-30, Bogotá",
    "phone": "+57 (601) 234-5678",
    "email": "hola@FPCMerch.co",
    "hours_week": "Lunes a sábado de 9:00 a. m. a 7:00 p. m.",
    "hours_sunday": "Domingos de 10:00 a. m. a 4:00 p. m.",
}
EXTERNAL_RATE_URL = os.environ.get("EXTERNAL_RATE_URL", "https://open.er-api.com/v6/latest/USD")
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "fpcmerch-cache"}}
# Local sessions live in memory so logout does not need to write to a locked SQLite file.
# Production keeps Django's persistent database-backed sessions.
SESSION_ENGINE = "django.contrib.sessions.backends.cache" if DEBUG else "django.contrib.sessions.backends.db"
LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "{levelname} {asctime} {name}: {message}", "style": "{"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
        "file": {"class": "logging.FileHandler", "filename": LOG_DIR / "fpcmerch.log", "formatter": "standard"},
    },
    "loggers": {"django": {"handlers": ["console", "file"], "level": "INFO"}, "apps": {"handlers": ["console", "file"], "level": "INFO", "propagate": False}},
}
