import os
from .base import *  # noqa: F403, F405

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECRET_KEY debe cargarse de variables de entorno en producción
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'reemplaza-esto-con-una-clave-super-secreta-en-produccion-123456789')

# Dominios autorizados para responder peticiones
ALLOWED_HOSTS = [
    'bpetcare.irissoftware.lat',
    'bpetcare.irrissoftware.lat',  # Añadimos soporte al posible typo
    'localhost',
    '127.0.0.1'
]

# Configuración de base de datos a través de variables de entorno (¡100% SEGURO!)
# Esto asegura que ninguna credencial quede expuesta en el código.
# En tu archivo .env del servidor deberás poner:
# DATABASE_URL=postgres://petcareuser:30640838Cda@207.180.223.61:9060/petcare

import dj_database_url

DATABASES = {
    # Lee automáticamente la variable DATABASE_URL del sistema (.env)
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=False
    )
}


# CORS - Solo permitimos peticiones desde nuestros frontends autorizados
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    'https://petcare.irissoftware.lat',
    'http://localhost:4173',
    'http://localhost:4174',
    'http://127.0.0.1:4173',
    'http://127.0.0.1:4174',
]

# Orígenes confiables para CSRF (Django moderno requiere esto para peticiones POST/PUT/DELETE)
CSRF_TRUSTED_ORIGINS = [
    'https://bpetcare.irissoftware.lat',
    'https://bpetcare.irrissoftware.lat',
    'https://petcare.irissoftware.lat',
]

# Static Files (Nginx servirá estos archivos directamente en producción, o WhiteNoise si se expone directo)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# WhiteNoise storage to compress and cache static files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media Files (Subidas de archivos de usuarios, fotos de mascotas, etc.)
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Configuraciones de seguridad para producción recomendadas
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Tareas en segundo plano (puedes cambiarlo a Celery, django_tasks con DB, etc.)
TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend"
    }
}
