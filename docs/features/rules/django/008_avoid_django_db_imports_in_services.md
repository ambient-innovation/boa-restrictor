# Don't import "django.db" in the service layer (DBR008)

Ensures that no Django low-level database functionality is imported and therefore used in the service layer.
Database access and complex queries belong in a model manager, not in a service. Keeping `django.db` out of
your services keeps them thin, focused on orchestration, and easy to unit-test without touching the ORM directly.

Note that imports for type-hinting purposes are fine.

*Wrong:*

```python
from django.db.models import QuerySet


class FetchUsersService:
    def process(self) -> QuerySet: ...
```

*Correct:*

```python
import typing

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class FetchUsersService:
    def process(self) -> "QuerySet": ...
```
