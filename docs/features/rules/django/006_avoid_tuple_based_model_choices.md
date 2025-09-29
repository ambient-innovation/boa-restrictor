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
