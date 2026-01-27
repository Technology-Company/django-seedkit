"""
Management command for seeding test data.

Usage:
    python manage.py seeddata              # Run all seeds
    python manage.py seeddata --list       # List available seeds
    python manage.py seeddata --apps=app1  # Filter by app
    python manage.py seeddata --dry-run    # Show what would run
"""

from django.core.management.base import BaseCommand

from seedkit.config import get_config
from seedkit.discovery import discover_seed_files
from seedkit.runner import SeedRunner


class Command(BaseCommand):
    help = "Seed test data from seed directories in installed apps"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available seed files without running them",
        )
        parser.add_argument(
            "--apps",
            type=str,
            help="Comma-separated list of app names to seed (e.g., 'myapp,otherapp')",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be run without executing",
        )
        parser.add_argument(
            "--no-atomic",
            action="store_true",
            help="Run without wrapping in a database transaction",
        )

    def handle(self, *args, **options):
        config = get_config()

        # Parse app filter
        app_filter = None
        if options["apps"]:
            app_filter = [a.strip() for a in options["apps"].split(",")]

        # Discover seed files
        seed_files = discover_seed_files(
            seed_dir_name=config.seed_dir,
            file_pattern=config.file_pattern,
            app_filter=app_filter,
            exclude_apps=config.exclude_apps,
        )

        if options["list"]:
            self.list_seed_files(seed_files)
            return

        # Run seeds
        runner = SeedRunner(
            atomic=config.atomic and not options["no_atomic"],
            verbose=True,
            dry_run=options["dry_run"],
            output=self.stdout,
            style=self.style,
        )

        result = runner.run(seed_files)

        if not result.success:
            raise SystemExit(1)

    def list_seed_files(self, app_seeds):
        """List all discovered seed files."""
        if not app_seeds:
            self.stdout.write(self.style.WARNING("No seed files found"))
            return

        self.stdout.write(self.style.SUCCESS("\nAvailable seed files:"))
        for app in app_seeds:
            self.stdout.write(f"\n  {self.style.HTTP_INFO(app.app_name)}:")
            for seed_file in app.files:
                self.stdout.write(f"    - {seed_file.file_name}")