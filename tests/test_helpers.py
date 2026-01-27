"""Tests for seedkit.helpers module."""

from seedkit.helpers import make_hash_id, make_slug, placeholder_image


class TestMakeSlug:
    """Tests for make_slug function."""

    def test_simple_text(self):
        assert make_slug("Hello World") == "hello-world"

    def test_finnish_characters(self):
        assert make_slug("Mäkitalo") == "makitalo"
        assert make_slug("Åland") == "aland"
        assert make_slug("Töölö") == "toolo"

    def test_swedish_characters(self):
        assert make_slug("Malmö") == "malmo"
        assert make_slug("Göteborg") == "goteborg"

    def test_german_characters(self):
        assert make_slug("Müller") == "muller"
        assert make_slug("Straße") == "strasse"

    def test_french_characters(self):
        assert make_slug("Café résumé") == "cafe-resume"

    def test_special_characters_become_hyphens(self):
        assert make_slug("Hello, World!") == "hello-world"
        assert make_slug("foo@bar.com") == "foo-bar-com"

    def test_strips_leading_trailing_hyphens(self):
        assert make_slug("--hello--") == "hello"
        assert make_slug("  hello  ") == "hello"

    def test_multiple_spaces_become_single_hyphen(self):
        assert make_slug("hello    world") == "hello-world"

    def test_preserves_numbers(self):
        assert make_slug("Test 123") == "test-123"
        assert make_slug("2024 Report") == "2024-report"


class TestMakeHashId:
    """Tests for make_hash_id function."""

    def test_returns_32_char_hex(self):
        result = make_hash_id("test")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_consistent_results(self):
        assert make_hash_id("test") == make_hash_id("test")

    def test_different_inputs_different_outputs(self):
        assert make_hash_id("test1") != make_hash_id("test2")


class TestPlaceholderImage:
    """Tests for placeholder_image function."""

    def test_default_picsum(self):
        url = placeholder_image("test-seed")
        assert url == "https://picsum.photos/seed/test-seed/800/600"

    def test_custom_dimensions(self):
        url = placeholder_image("test", 1600, 1200)
        assert url == "https://picsum.photos/seed/test/1600/1200"

    def test_placehold_service(self):
        url = placeholder_image("test", 400, 300, service="placehold")
        assert url == "https://placehold.co/400x300"

    def test_integer_seed(self):
        url = placeholder_image(42, 100, 100)
        assert url == "https://picsum.photos/seed/42/100/100"