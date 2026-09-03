# Avoid using old tuple-based Django model choices (DBR006)

Django model choices should use the modern class-based approach instead of the legacy tuple-based definitions. Class-based choices provide better maintainability, type safety, and IDE support.

The old tuple-based choices are prone to errors and harder to maintain, especially when choices need to be referenced elsewhere in the codebase.

*Wrong:*

```python
from django.db import models


class MyModel(models.Model):
    STATUS_CHOICES = (
        ("A", "Active"),
        ("I", "Inactive"),
        ("P", "Pending"),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)


# Also detected outside of models
PRIORITY_CHOICES = (
    ("H", "High"),
    ("M", "Medium"),
    ("L", "Low"),
)
```

*Correct:*

```python
from django.db import models


class MyModel(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = "A", "Active"
        INACTIVE = "I", "Inactive"
        PENDING = "P", "Pending"

    status = models.CharField(max_length=1, choices=StatusChoices.choices)


# For integer-based choices
class Task(models.Model):
    class PriorityChoices(models.IntegerChoices):
        HIGH = 1, "High"
        MEDIUM = 2, "Medium"
        LOW = 3, "Low"

    priority = models.IntegerField(choices=PriorityChoices.choices)
```

## Benefits of class-based choices

- **Better maintainability**: Values can be referenced as `StatusChoices.ACTIVE` instead of magic strings
- **Type safety**: IDEs can provide autocompletion and type checking
- **Extensibility**: Easy to add methods to choice classes for additional functionality
- **Consistency**: Follows Django's modern best practices (Django 3.0+)

## Scope

Inside a model, every tuple-of-pairs assignment is reported. Elsewhere only one whose name ends in
`CHOICES` is, because a tuple of pairs is an ordinary data structure outside that context.

A class counts as a model when a base is spelled `models.Model` (or `Model`, or an aliased models module),
or when its body assigns at least one Django model field. The second signal is what covers a model
inheriting from a project base class defined in another file, since the linter sees one file at a time. A
model declaring no fields at all cannot be identified this way; name the tuple `*_CHOICES` there, or use
`# noqa: DBR006`.

Migrations are exempt, since they are generated and out of the developer's hands.

A violation is reported on the line the assignment starts on, so a `# noqa: DBR006` belongs there whether
or not the surrounding class could be identified as a model.
