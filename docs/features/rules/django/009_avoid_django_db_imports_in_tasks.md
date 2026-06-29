# Don't import "django.db" in the task layer (DBR009)

Ensures that no Django low-level database functionality is imported and therefore used in the task layer
(e.g. Celery tasks). A task should orchestrate work and delegate database access to a model manager or
service, keeping the task itself thin and easy to test.

Note that imports for type-hinting purposes are fine.

*Wrong:*

```python
from django.db.models import QuerySet


@shared_task
def cleanup_users() -> None:
    queryset: QuerySet = ...
```

*Correct:*

```python
import typing

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


@shared_task
def cleanup_users() -> None:
    queryset: "QuerySet" = ...
```
