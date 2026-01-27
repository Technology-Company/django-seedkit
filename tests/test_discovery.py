"""Tests for seedkit.discovery module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestDiscoverSeedFiles:
    """Tests for discover_seed_files function."""

    def test_empty_when_no_apps(self, settings):
        """Test returns empty list when no apps have seed directories."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = "/tmp/test_project"

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = []
            result = discover_seed_files()

        assert result == []

    def test_skips_apps_without_path(self, settings):
        """Test skips app configs that don't have a path attribute."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = "/tmp/test_project"

        mock_app = MagicMock(spec=[])  # No 'path' attribute
        mock_app.name = "no_path_app"

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app]
            result = discover_seed_files()

        assert result == []

    def test_skips_apps_outside_base_dir(self, settings):
        """Test skips apps that are outside the project directory."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = Path("/tmp/test_project")

        mock_app = MagicMock()
        mock_app.name = "external_app"
        mock_app.path = "/usr/lib/python/site-packages/external_app"

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app]
            result = discover_seed_files()

        assert result == []

    def test_respects_app_filter(self, settings, tmp_path):
        """Test that app_filter limits which apps are included."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = tmp_path

        # Create seed directories for two apps
        app1_seeds = tmp_path / "app1" / "seeds"
        app1_seeds.mkdir(parents=True)
        (app1_seeds / "setup_test.py").write_text("# seed")

        app2_seeds = tmp_path / "app2" / "seeds"
        app2_seeds.mkdir(parents=True)
        (app2_seeds / "setup_test.py").write_text("# seed")

        mock_app1 = MagicMock()
        mock_app1.name = "app1"
        mock_app1.path = str(tmp_path / "app1")

        mock_app2 = MagicMock()
        mock_app2.name = "app2"
        mock_app2.path = str(tmp_path / "app2")

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app1, mock_app2]
            result = discover_seed_files(app_filter=["app1"])

        assert len(result) == 1
        assert result[0].app_name == "app1"

    def test_respects_exclude_apps(self, settings, tmp_path):
        """Test that exclude_apps removes apps from results."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = tmp_path

        # Create seed directories
        app1_seeds = tmp_path / "app1" / "seeds"
        app1_seeds.mkdir(parents=True)
        (app1_seeds / "setup_test.py").write_text("# seed")

        mock_app = MagicMock()
        mock_app.name = "app1"
        mock_app.path = str(tmp_path / "app1")

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app]
            result = discover_seed_files(exclude_apps=["app1"])

        assert result == []

    def test_discovers_seed_files(self, settings, tmp_path):
        """Test that seed files are discovered correctly."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = tmp_path

        # Create seed directory with files
        seeds_dir = tmp_path / "myapp" / "seeds"
        seeds_dir.mkdir(parents=True)
        (seeds_dir / "setup_users.py").write_text("# users")
        (seeds_dir / "setup_data.py").write_text("# data")
        (seeds_dir / "other.py").write_text("# not matched")

        mock_app = MagicMock()
        mock_app.name = "myapp"
        mock_app.path = str(tmp_path / "myapp")

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app]
            result = discover_seed_files()

        assert len(result) == 1
        assert result[0].app_name == "myapp"
        assert len(result[0].files) == 2

        file_names = [f.file_name for f in result[0].files]
        assert "setup_data.py" in file_names
        assert "setup_users.py" in file_names
        assert "other.py" not in file_names

    def test_custom_seed_dir_name(self, settings, tmp_path):
        """Test that custom seed directory name is respected."""
        from seedkit.discovery import discover_seed_files

        settings.BASE_DIR = tmp_path

        # Create custom seed directory
        seeds_dir = tmp_path / "myapp" / "test_seed"
        seeds_dir.mkdir(parents=True)
        (seeds_dir / "setup_test.py").write_text("# test")

        mock_app = MagicMock()
        mock_app.name = "myapp"
        mock_app.path = str(tmp_path / "myapp")

        with patch("django.apps.apps") as mock_apps:
            mock_apps.get_app_configs.return_value = [mock_app]
            result = discover_seed_files(seed_dir_name="test_seed")

        assert len(result) == 1
        assert result[0].app_name == "myapp"