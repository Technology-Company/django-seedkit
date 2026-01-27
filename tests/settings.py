"""Minimal Django settings for testing seedkit."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "test-secret-key-not-for-production"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "seedkit",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

# Seedkit configuration for tests
SEEDKIT = {
    "SEED_DIR": "seeds",
    "FILE_PATTERN": "setup_*.py",
    "ATOMIC": True,
}