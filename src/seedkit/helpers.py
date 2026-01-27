"""Utility functions for seed files."""

from __future__ import annotations

import hashlib
import re
import sys


def log(message: str, level: str = "info") -> None:
    """Log a message during seeding.

    Args:
        message: The message to log.
        level: Log level (info, warning, error, success). Default is "info".

    Example:
        >>> log("Created admin user")
        >>> log("User already exists", level="warning")
    """
    prefix = "  "
    if level == "warning":
        prefix = "  ⚠ "
    elif level == "error":
        prefix = "  ✗ "
    elif level == "success":
        prefix = "  ✓ "

    print(f"{prefix}{message}", file=sys.stdout)


def make_slug(text: str, locale: str | None = None) -> str:
    """Create a URL-safe slug from text.

    Handles special characters from various locales (Finnish, Swedish, German, etc.).

    Args:
        text: The text to slugify.
        locale: Optional locale hint for character handling (e.g., "fi", "de").
                If not provided, handles common European characters.

    Returns:
        A URL-safe lowercase slug.

    Example:
        >>> make_slug("Pekka Kuumalainen")
        'pekka-kuumalainen'
        >>> make_slug("Mäkitalo Åland")
        'makitalo-aland'
        >>> make_slug("Müller Straße")
        'muller-strasse'
    """
    slug = text.lower()

    # Handle common European special characters
    replacements = {
        # Finnish/Swedish
        "ä": "a",
        "å": "a",
        "ö": "o",
        # German
        "ü": "u",
        "ß": "ss",
        # French/Spanish/Portuguese
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "ù": "u",
        "û": "u",
        "ô": "o",
        "î": "i",
        "ï": "i",
        "ç": "c",
        "ñ": "n",
        "ã": "a",
        "õ": "o",
        # Nordic
        "æ": "ae",
        "ø": "o",
        # Polish
        "ł": "l",
        "ż": "z",
        "ź": "z",
        "ś": "s",
        "ć": "c",
        "ń": "n",
    }

    for char, replacement in replacements.items():
        slug = slug.replace(char, replacement)

    # Replace any remaining non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Strip leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def make_hash_id(value: str) -> str:
    """Create an MD5 hash ID from a string value.

    Useful for creating stable, unique identifiers from names or other strings.

    Args:
        value: The string to hash.

    Returns:
        32-character lowercase hexadecimal MD5 hash.

    Example:
        >>> make_hash_id("Pekka Kuumalainen")
        'a1b2c3d4e5f6...'
    """
    return hashlib.md5(value.encode()).hexdigest()


def placeholder_image(
    seed: str | int,
    width: int = 800,
    height: int = 600,
    service: str = "picsum",
) -> str:
    """Generate a placeholder image URL.

    Creates stable, reproducible placeholder image URLs for seeding.

    Args:
        seed: A seed value for consistent image selection (string or int).
        width: Image width in pixels.
        height: Image height in pixels.
        service: The placeholder service to use. Options:
            - "picsum" (default): picsum.photos - real photos
            - "placehold": placehold.co - simple colored placeholders

    Returns:
        A URL string for the placeholder image.

    Example:
        >>> placeholder_image("apartment-1", 1600, 1200)
        'https://picsum.photos/seed/apartment-1/1600/1200'
        >>> placeholder_image("test", 400, 300, service="placehold")
        'https://placehold.co/400x300'
    """
    if service == "placehold":
        return f"https://placehold.co/{width}x{height}"

    # Default to picsum.photos
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"