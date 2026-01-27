"""Tests for seedkit.config module."""


class TestGetConfig:
    """Tests for get_config function."""

    def test_default_values(self, settings):
        """Test that defaults are used when SEEDKIT is not configured."""
        from seedkit.config import get_config

        # Remove SEEDKIT if present
        if hasattr(settings, "SEEDKIT"):
            delattr(settings, "SEEDKIT")

        config = get_config()

        assert config.seed_dir == "seeds"
        assert config.file_pattern == "setup_*.py"
        assert config.atomic is True
        assert config.exclude_apps == ()
        assert config.placeholder_service == "picsum"

    def test_custom_values(self, settings):
        """Test that custom settings override defaults."""
        from seedkit.config import get_config

        settings.SEEDKIT = {
            "SEED_DIR": "test_seed",
            "FILE_PATTERN": "seed_*.py",
            "ATOMIC": False,
            "EXCLUDE_APPS": ["django.contrib.admin"],
            "PLACEHOLDER_SERVICE": "placehold",
        }

        config = get_config()

        assert config.seed_dir == "test_seed"
        assert config.file_pattern == "seed_*.py"
        assert config.atomic is False
        assert config.exclude_apps == ["django.contrib.admin"]
        assert config.placeholder_service == "placehold"

    def test_partial_override(self, settings):
        """Test that only specified values are overridden."""
        from seedkit.config import get_config

        settings.SEEDKIT = {
            "SEED_DIR": "my_seeds",
        }

        config = get_config()

        assert config.seed_dir == "my_seeds"
        assert config.file_pattern == "setup_*.py"  # default
        assert config.atomic is True  # default