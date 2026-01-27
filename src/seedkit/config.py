"""Configuration management for seedkit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class SeedkitConfig:
    """Configuration for seedkit.

    All settings can be overridden via Django settings:

        SEEDKIT = {
            "SEED_DIR": "seeds",
            "FILE_PATTERN": "setup_*.py",
            "ATOMIC": True,
            "EXCLUDE_APPS": [],
            "PLACEHOLDER_SERVICE": "picsum",
            "LOG_LEVEL": "INFO",
        }
    """

    seed_dir: str = "seeds"
    file_pattern: str = "setup_*.py"
    atomic: bool = True
    exclude_apps: Sequence[str] = ()
    placeholder_service: str = "picsum"
    log_level: str = "INFO"


def get_config() -> SeedkitConfig:
    """Get seedkit configuration from Django settings."""
    from django.conf import settings

    user_config = getattr(settings, "SEEDKIT", {})

    return SeedkitConfig(
        seed_dir=user_config.get("SEED_DIR", "seeds"),
        file_pattern=user_config.get("FILE_PATTERN", "setup_*.py"),
        atomic=user_config.get("ATOMIC", True),
        exclude_apps=user_config.get("EXCLUDE_APPS", ()),
        placeholder_service=user_config.get("PLACEHOLDER_SERVICE", "picsum"),
        log_level=user_config.get("LOG_LEVEL", "INFO"),
    )