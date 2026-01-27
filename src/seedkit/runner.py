"""Executes seed files with proper transaction handling."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from seedkit.discovery import AppSeeds, SeedFile


class OutputWriter(Protocol):
    """Protocol for output writing (compatible with Django management command)."""

    def write(self, msg: str, ending: str = "\n") -> None:
        """Write a message."""
        ...


class StdoutWriter:
    """Simple stdout writer."""

    def write(self, msg: str, ending: str = "\n") -> None:
        print(msg, end=ending)


@dataclass
class SeedResult:
    """Result of running seed files."""

    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list[tuple[str, Exception]] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if all seeds ran successfully."""
        return self.failed == 0


class SeedRunner:
    """Executes seed files with transaction handling.

    Example:
        >>> from seedkit.discovery import discover_seed_files
        >>> seeds = discover_seed_files()
        >>> runner = SeedRunner(verbose=True)
        >>> result = runner.run(seeds)
        >>> if result.success:
        ...     print("Seeding complete!")
    """

    def __init__(
        self,
        atomic: bool = True,
        verbose: bool = True,
        dry_run: bool = False,
        output: OutputWriter | None = None,
        style: object | None = None,
    ):
        """Initialize the seed runner.

        Args:
            atomic: Whether to wrap all seeds in a database transaction.
            verbose: Whether to print progress messages.
            dry_run: If True, list files without executing them.
            output: Output writer (defaults to stdout).
            style: Django style object for colored output.
        """
        self.atomic = atomic
        self.verbose = verbose
        self.dry_run = dry_run
        self.output = output or StdoutWriter()
        self.style = style

    def run(self, app_seeds: list[AppSeeds]) -> SeedResult:
        """Execute all seed files.

        Args:
            app_seeds: List of AppSeeds from discover_seed_files().

        Returns:
            SeedResult with execution statistics.
        """
        from django.db import transaction

        result = SeedResult()
        result.total_files = sum(len(app.files) for app in app_seeds)

        if not app_seeds:
            self._write_warning("No seed files to run")
            return result

        if self.dry_run:
            self._write_success(f"\nDry run - would execute {result.total_files} file(s):\n")
            for app in app_seeds:
                self._write_info(f"  {app.app_name}:")
                for seed_file in app.files:
                    self._write(f"    - {seed_file.file_name}")
            return result

        self._write_success(f"\nRunning {result.total_files} seed file(s)...\n")

        if self.atomic:
            with transaction.atomic():
                self._execute_seeds(app_seeds, result)
        else:
            self._execute_seeds(app_seeds, result)

        if result.success:
            self._write_success("\nSeeding complete!")
        else:
            self._write_error(f"\nSeeding failed with {result.failed} error(s)")

        return result

    def run_single(self, seed_file: SeedFile) -> bool:
        """Execute a single seed file.

        Args:
            seed_file: The seed file to execute.

        Returns:
            True if successful, False otherwise.
        """
        from django.db import transaction

        if self.atomic:
            with transaction.atomic():
                return self._import_seed(seed_file)
        else:
            return self._import_seed(seed_file)

    def _execute_seeds(self, app_seeds: list[AppSeeds], result: SeedResult) -> None:
        """Execute seed files and update result."""
        for app in app_seeds:
            self._write_info(f"{app.app_name}:")

            for seed_file in app.files:
                file_name = seed_file.file_name

                self._write(f"  Importing {file_name}...", ending="")

                try:
                    importlib.import_module(seed_file.module_path)
                    self._write_success(" OK")
                    result.successful += 1
                except Exception as e:
                    self._write_error(" FAILED")
                    self._write_error(f"    Error: {e}")
                    result.failed += 1
                    result.errors.append((seed_file.module_path, e))
                    raise

    def _import_seed(self, seed_file: SeedFile) -> bool:
        """Import a single seed module."""
        try:
            # Clear from sys.modules if already imported (for re-running)
            if seed_file.module_path in sys.modules:
                del sys.modules[seed_file.module_path]

            importlib.import_module(seed_file.module_path)
            return True
        except Exception:
            return False

    def _write(self, msg: str, ending: str = "\n") -> None:
        """Write a message."""
        if self.verbose:
            self.output.write(msg, ending=ending)

    def _write_success(self, msg: str) -> None:
        """Write a success message."""
        if self.style and hasattr(self.style, "SUCCESS"):
            msg = self.style.SUCCESS(msg)
        self._write(msg)

    def _write_error(self, msg: str) -> None:
        """Write an error message."""
        if self.style and hasattr(self.style, "ERROR"):
            msg = self.style.ERROR(msg)
        self._write(msg)

    def _write_warning(self, msg: str) -> None:
        """Write a warning message."""
        if self.style and hasattr(self.style, "WARNING"):
            msg = self.style.WARNING(msg)
        self._write(msg)

    def _write_info(self, msg: str) -> None:
        """Write an info message."""
        if self.style and hasattr(self.style, "HTTP_INFO"):
            msg = self.style.HTTP_INFO(msg)
        self._write(msg)