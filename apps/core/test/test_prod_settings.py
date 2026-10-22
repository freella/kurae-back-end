import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


BASE_DIR = Path(__file__).resolve().parents[3]


class ProductionSettingsTest(SimpleTestCase):
    def run_settings_probe(self, missing_setting=None):
        env = os.environ.copy()
        for name in (
            "SECRET_KEY",
            "DB_ENGINE",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
            "DB_HOST",
            "DB_PORT",
            "ALLOWED_HOSTS",
            "CORS_ALLOWED_ORIGINS",
            "CSRF_TRUSTED_ORIGINS",
            "REDIS_URL",
        ):
            env.pop(name, None)

        env.update(
            {
                "SECRET_KEY": "test-only-secret-key",
                "DB_ENGINE": "django.db.backends.sqlite3",
                "DB_NAME": ":memory:",
                "DB_USER": "",
                "DB_PASSWORD": "",
                "DB_HOST": "",
                "DB_PORT": "",
                "ALLOWED_HOSTS": "api.example.com",
                "CORS_ALLOWED_ORIGINS": "https://front.example.com",
                "CSRF_TRUSTED_ORIGINS": "https://front.example.com",
            }
        )
        env["REDIS_URL"] = "redis://redis:6379/0"
        if missing_setting:
            env.pop(missing_setting, None)

        script = """
import os
import decouple

def config(name, default=None, cast=None):
    if name in os.environ:
        value = os.environ[name]
    elif default is not None:
        value = default
    else:
        raise RuntimeError(f"Missing required setting: {name}")
    return cast(value) if cast else value

decouple.config = config
import config.settings.prod as settings

assert settings.DEBUG is False
assert settings.ALLOWED_HOSTS == ["api.example.com"]
assert settings.CORS_ALLOWED_ORIGINS == ["https://front.example.com"]
assert settings.CSRF_TRUSTED_ORIGINS == ["https://front.example.com"]
assert settings.SESSION_COOKIE_SECURE is True
assert settings.CSRF_COOKIE_SECURE is True
assert settings.SECURE_HSTS_SECONDS > 0
assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
assert settings.SECURE_SSL_REDIRECT is False
assert settings.CACHES["default"]["BACKEND"] == "django.core.cache.backends.redis.RedisCache"
assert settings.CACHES["default"]["LOCATION"] == "redis://redis:6379/0"
assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE
assert settings.MIDDLEWARE.index("whitenoise.middleware.WhiteNoiseMiddleware") == settings.MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1
assert settings.STORAGES["staticfiles"]["BACKEND"] == "whitenoise.storage.CompressedManifestStaticFilesStorage"
assert settings.STATIC_ROOT.endswith("/staticfiles")
"""
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_production_settings_use_secure_production_configuration(self):
        result = self.run_settings_probe()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_settings_require_redis_url(self):
        for missing_setting in (
            "ALLOWED_HOSTS",
            "CORS_ALLOWED_ORIGINS",
            "REDIS_URL",
        ):
            with self.subTest(missing_setting=missing_setting):
                result = self.run_settings_probe(missing_setting=missing_setting)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    f"Missing required setting: {missing_setting}",
                    result.stderr,
                )
