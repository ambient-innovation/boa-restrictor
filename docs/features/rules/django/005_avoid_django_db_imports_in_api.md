# Don't import "django.db" in the API layer (DBR005)

Ensures that no Django low-level database functionality is imported and therefore used in the API layer.
Adding business logic and complex queries to the API layer is discouraged since it simply doesn't belong there.
Secondly, it's hard to write proper unit-tests since you always have to initialise the whole API endpoint, making it
a way more complex integration test.

Note that imports for type-hinting purposes are fine.

*Wrong:*

```python
from django.db.models import QuerySet
from rest_framework import viewsets


class MyViewSet(viewsets.ModelViewSet):
    ...

    def get_queryset(self) -> QuerySet: ...
```

*Correct:*

```python
import typing
from rest_framework import viewsets

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class MyViewSet(viewsets.ModelViewSet):
    ...

    def get_queryset(self) -> "QuerySet": ...
```
