"""
django-seedkit — Minimal test data seeding for Django.

Auto-discovery • Idempotent • Atomic transactions • Zero configuration
"""

from seedkit.helpers import log, make_hash_id, make_slug, placeholder_image

__version__ = "0.1.0"
__all__ = [
    "log",
    "make_slug",
    "make_hash_id",
    "placeholder_image",
]

default_app_config = "seedkit.apps.SeedkitConfig"