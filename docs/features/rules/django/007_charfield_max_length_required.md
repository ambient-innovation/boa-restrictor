# CharField must have `max_length` set (DBR007)

Django's `CharField` does not strictly require `max_length` for PostgreSQL and SQLite backends, but omitting it creates a UX problem: `CharField` renders as an `<input>` element in forms and the admin, while `TextField` renders as a `<textarea>`. A `CharField` without `max_length` gives users a single-line input with no length constraint — misleading and inconsistent. If there's no meaningful max length, a `TextField` should be used instead.

This rule enforces that every `CharField` in a Django model has `max_length` set to a non-None value.

*Wrong:*

```python
from django.db import models


class MyModel(models.Model):
    # CharField without max_length — renders as <input> with no constraint
    name = models.CharField()

    # CharField with max_length=None — same problem
    title = models.CharField(max_length=None)
```

*Correct:*

```python
from django.db import models


class MyModel(models.Model):
    # CharField with explicit max_length
    name = models.CharField(max_length=255)

    # Or use TextField if no max length is needed
    description = models.TextField()
```

## Rationale

- `CharField` renders as `<input type="text">` in Django forms and admin — a single-line field
- `TextField` renders as `<textarea>` — a multi-line field
- A `CharField` without `max_length` gives users an `<input>` that accepts unlimited text, which is confusing
- If the field truly has no length constraint, `TextField` is the appropriate choice
