"""Tests for seedkit.runner module - integration tests for seed execution."""

from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from seedkit.discovery import AppSeeds, SeedFile
from seedkit.runner import SeedResult, SeedRunner


class TestSeedResult:
    """Tests for SeedResult dataclass."""

    def test_success_when_no_failures(self):
        result = SeedResult(total_files=3, successful=3, failed=0)
        assert result.success is True

    def test_not_success_when_failures(self):
        result = SeedResult(total_files=3, successful=2, failed=1)
        assert result.success is False


class TestSeedRunner:
    """Tests for SeedRunner class."""

    def test_dry_run_does_not_execute(self):
        """Test that dry run mode lists files without executing."""
        runner = SeedRunner(dry_run=True, verbose=False)

        seed_file = SeedFile(
            app_name="testapp",
            file_path=Path("/fake/path/setup_test.py"),
            module_path="testapp.seeds.setup_test",
        )
        app_seeds = [AppSeeds(app_name="testapp", files=[seed_file])]

        with patch.object(runner, "_import_seed") as mock_import:
            result = runner.run(app_seeds)

        mock_import.assert_not_called()
        assert result.total_files == 1

    def test_empty_seeds_returns_early(self):
        """Test that empty seed list returns without error."""
        runner = SeedRunner(verbose=False)
        result = runner.run([])

        assert result.total_files == 0
        assert result.success is True


@pytest.mark.django_db(transaction=True)
class TestSeedRunnerIntegration:
    """Integration tests that actually run seed files."""

    def test_seeds_create_user(self, settings, tmp_path):
        """Test that a seed file can create a user in the database."""
        User = get_user_model()

        # Create a seed file that creates a test user
        settings.BASE_DIR = tmp_path
        seeds_dir = tmp_path / "testapp" / "seeds"
        seeds_dir.mkdir(parents=True)

        seed_content = '''
from django.contrib.auth import get_user_model
User = get_user_model()

test_user, created = User.objects.get_or_create(
    username="seedkit_test_user",
    defaults={"email": "test@seedkit.example"}
)
'''
        (seeds_dir / "setup_users.py").write_text(seed_content)

        # Create the seed file object
        seed_file = SeedFile(
            app_name="testapp",
            file_path=seeds_dir / "setup_users.py",
            module_path="testapp.seeds.setup_users",
        )
        app_seeds = [AppSeeds(app_name="testapp", files=[seed_file])]

        # Add tmp_path to sys.path so the module can be imported
        import sys
        sys.path.insert(0, str(tmp_path))

        try:
            runner = SeedRunner(atomic=True, verbose=False)
            result = runner.run(app_seeds)

            assert result.success is True
            assert result.successful == 1
            assert User.objects.filter(username="seedkit_test_user").exists()
        finally:
            sys.path.remove(str(tmp_path))
            # Clean up the module from sys.modules
            if "testapp.seeds.setup_users" in sys.modules:
                del sys.modules["testapp.seeds.setup_users"]

    def test_seeds_are_idempotent(self, settings, tmp_path):
        """Test that running seeds twice doesn't create duplicates."""
        User = get_user_model()

        settings.BASE_DIR = tmp_path
        seeds_dir = tmp_path / "testapp2" / "seeds"
        seeds_dir.mkdir(parents=True)

        seed_content = '''
from django.contrib.auth import get_user_model
User = get_user_model()

idempotent_user, created = User.objects.get_or_create(
    username="idempotent_user",
    defaults={"email": "idempotent@seedkit.example"}
)
'''
        (seeds_dir / "setup_idempotent.py").write_text(seed_content)

        seed_file = SeedFile(
            app_name="testapp2",
            file_path=seeds_dir / "setup_idempotent.py",
            module_path="testapp2.seeds.setup_idempotent",
        )
        app_seeds = [AppSeeds(app_name="testapp2", files=[seed_file])]

        import sys
        sys.path.insert(0, str(tmp_path))

        try:
            runner = SeedRunner(atomic=False, verbose=False)

            # Run once
            result1 = runner.run(app_seeds)
            assert result1.success is True
            count1 = User.objects.filter(username="idempotent_user").count()

            # Clear module cache to allow re-import
            if "testapp2.seeds.setup_idempotent" in sys.modules:
                del sys.modules["testapp2.seeds.setup_idempotent"]

            # Run again
            result2 = runner.run(app_seeds)
            assert result2.success is True
            count2 = User.objects.filter(username="idempotent_user").count()

            # Should still be exactly 1 user
            assert count1 == 1
            assert count2 == 1
        finally:
            sys.path.remove(str(tmp_path))
            if "testapp2.seeds.setup_idempotent" in sys.modules:
                del sys.modules["testapp2.seeds.setup_idempotent"]