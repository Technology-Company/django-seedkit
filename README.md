# django-seedkit

Minimal test data seeding for Django — plain Python, no magic.

**Auto-discovery • Idempotent • Atomic transactions • Zero configuration**

## Features

- **Simple**: Seed files are plain Python — just use `get_or_create()` and imports
- **Auto-discovery**: Automatically finds `setup_*.py` files in your apps' `seeds/` directories
- **Idempotent**: Safe to run multiple times; uses `get_or_create()` pattern
- **Atomic**: All seeds run in a single database transaction (configurable)
- **Dependency management**: Use Python imports to control execution order
- **No magic**: No decorators, no registration — just import and run

## Installation

```bash
pip install django-seedkit
```

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "seedkit",
]
```

## Quick Start

### 1. Create a seed file

Create a `seeds/` directory in your app and add seed files:

```python
# myapp/seeds/setup_users.py
from django.contrib.auth import get_user_model
from seedkit import log

User = get_user_model()

admin, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@example.com",
        "is_staff": True,
        "is_superuser": True,
    }
)

if created:
    admin.set_password("admin")
    admin.save()
    log("Created admin user")
```

### 2. Run the seeds

```bash
python manage.py seeddata
```

That's it! Your seed file runs automatically.

## Managing Dependencies

Seed files execute when imported. Control the order by importing dependencies:

```python
# myapp/seeds/setup_posts.py
from django.contrib.auth import get_user_model

# Import user seeds first - this ensures users exist before posts
from myapp.seeds.setup_users import admin

from myapp.models import Post
from seedkit import log

post, created = Post.objects.get_or_create(
    slug="welcome",
    defaults={
        "title": "Welcome!",
        "author": admin,
        "content": "Hello world",
    }
)

if created:
    log("Created welcome post")
```

Python's import caching ensures each seed file runs only once, even if imported multiple times.

## Commands

```bash
# Run all seeds
python manage.py seeddata

# List available seeds without running
python manage.py seeddata --list

# Run seeds for specific apps only
python manage.py seeddata --apps=myapp,otherapp

# Preview what would run (dry run)
python manage.py seeddata --dry-run

# Run without transaction wrapper
python manage.py seeddata --no-atomic
```

## Configuration

Optional configuration via Django settings:

```python
# settings.py
SEEDKIT = {
    # Directory name in each app (default: "seeds")
    "SEED_DIR": "seeds",

    # File pattern to match (default: "setup_*.py")
    "FILE_PATTERN": "setup_*.py",

    # Wrap all seeds in atomic transaction (default: True)
    "ATOMIC": True,

    # Apps to exclude from discovery
    "EXCLUDE_APPS": ["django.contrib.admin"],
}
```

## Helper Functions

Seedkit provides utility functions for common seeding tasks:

```python
from seedkit import log, make_slug, make_hash_id, placeholder_image

# Log messages during seeding
log("Created user")                    # "  Created user"
log("Warning!", level="warning")       # "  ⚠ Warning!"

# Create URL-safe slugs (handles Finnish, Swedish, German, etc.)
make_slug("Pekka Mäkinen")            # "pekka-makinen"
make_slug("Müller Straße")            # "muller-strasse"

# Generate stable hash IDs
make_hash_id("unique-identifier")      # "a1b2c3d4..."

# Placeholder images for development
placeholder_image("apartment-1", 1600, 1200)
# "https://picsum.photos/seed/apartment-1/1600/1200"
```

## Best Practices

### Use `get_or_create()` for Idempotency

```python
# Good - can run multiple times safely
user, created = User.objects.get_or_create(
    username="admin",
    defaults={"email": "admin@example.com"}
)

# Avoid - will fail on second run
user = User.objects.create(username="admin")
```

### Create Related Objects Conditionally

```python
user, created = User.objects.get_or_create(username="admin", ...)

if created:
    # Only create profile if user is new
    Profile.objects.create(user=user, bio="Admin user")
    log("Created admin with profile")
```

### Export Objects for Dependencies

```python
# myapp/seeds/setup_users.py
admin, _ = User.objects.get_or_create(username="admin", ...)
editor, _ = User.objects.get_or_create(username="editor", ...)

# Now other files can import:
# from myapp.seeds.setup_users import admin, editor
```

## License

MIT