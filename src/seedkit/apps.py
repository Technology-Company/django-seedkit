"""Django app configuration for seedkit."""

from django.apps import AppConfig


class SeedkitConfig(AppConfig):
    """Django app config for seedkit."""

    name = "seedkit"
    verbose_name = "Seedkit"
    default_auto_field = "django.db.models.BigAutoField"