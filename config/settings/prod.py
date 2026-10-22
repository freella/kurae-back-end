import os

from decouple import Csv, config

from .base import *  # noqa

DEBUG = False

# Sem default de propósito: se faltar na hospedagem, o app falha alto.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Domínios do frontend, com https:// e sem barra no final.
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Atrás do proxy da hospedagem (que termina o HTTPS).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600  # aumente depois que tudo estiver estável
SECURE_CONTENT_TYPE_NOSNIFF = True

# Estáticos do admin e do Swagger via WhiteNoise.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# WhiteNoise logo depois do SecurityMiddleware (e depois do CorsMiddleware).
_i = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
MIDDLEWARE.insert(_i + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Cache compartilhado entre os workers (exigido pelo django-ratelimit).
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    }}
else:
    CACHES = {'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }}
    SILENCED_SYSTEM_CHECKS = ['django_ratelimit.W001']
# Cache compartilhado (Redis), exigido pelo django-ratelimit.
# Sem default de propósito: se faltar REDIS_URL, o app não sobe.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL'),
    }
}
