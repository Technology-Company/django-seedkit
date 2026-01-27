"""Discovers seed files across Django apps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class SeedFile:
    """Represents a discovered seed file."""

    app_name: str
    file_path: Path
    module_path: str

    @property
    def file_name(self) -> str:
        """Get the file name without path."""
        return self.file_path.name


@dataclass
class AppSeeds:
    """Collection of seed files for an app."""

    app_name: str
    files: list[SeedFile]

    def __len__(self) -> int:
        return len(self.files)


def discover_seed_files(
    seed_dir_name: str = "seeds",
    file_pattern: str = "setup_*.py",
    app_filter: Sequence[str] | None = None,
    exclude_apps: Sequence[str] | None = None,
) -> list[AppSeeds]:
    """Discover all seed files from installed Django apps.

    Searches for seed files in each installed app's seed directory.

    Args:
        seed_dir_name: Name of the seed directory within each app.
        file_pattern: Glob pattern for seed files.
        app_filter: If provided, only include these app names.
        exclude_apps: App names to exclude from discovery.

    Returns:
        List of AppSeeds objects containing discovered seed files.

    Example:
        >>> seeds = discover_seed_files()
        >>> for app_seeds in seeds:
        ...     print(f"{app_seeds.app_name}: {len(app_seeds)} files")
    """
    from django.apps import apps
    from django.conf import settings

    discovered: list[AppSeeds] = []
    exclude_set = set(exclude_apps or [])
    filter_set = set(app_filter) if app_filter else None

    base_dir = Path(settings.BASE_DIR)

    for app_config in apps.get_app_configs():
        # Skip apps without a path
        if not hasattr(app_config, "path"):
            continue

        app_path = Path(app_config.path)

        # Only process apps within the project directory
        try:
            app_path.relative_to(base_dir)
        except ValueError:
            continue

        # Skip excluded apps
        if app_config.name in exclude_set:
            continue

        # Apply app filter if specified
        if filter_set and app_config.name not in filter_set:
            continue

        # Look for seed directory
        seed_dir = app_path / seed_dir_name
        if not seed_dir.exists() or not seed_dir.is_dir():
            continue

        # Find seed files
        seed_files = []
        for file_path in sorted(seed_dir.glob(file_pattern)):
            if file_path.name == "__init__.py":
                continue

            module_path = _file_to_module(file_path, base_dir)
            seed_files.append(
                SeedFile(
                    app_name=app_config.name,
                    file_path=file_path,
                    module_path=module_path,
                )
            )

        if seed_files:
            discovered.append(AppSeeds(app_name=app_config.name, files=seed_files))

    return discovered


def _file_to_module(file_path: Path, base_dir: Path) -> str:
    """Convert a file path to a Python module path.

    Args:
        file_path: Absolute path to the Python file.
        base_dir: Project base directory.

    Returns:
        Dotted module path (e.g., "myapp.seeds.setup_users").
    """
    rel_path = file_path.relative_to(base_dir)
    # Remove .py extension and convert to module path
    return str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")