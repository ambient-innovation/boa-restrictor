# Don't import "django.db" in the view layer (DBR002)

Ensures that no Django low-level database functionality is imported and therefore used in the view layer.
Adding business logic and complex queries to the view layer is discouraged since it simply doesn't belong there.
Secondly, it's hard to write proper unit-tests since you always have to initialise the whole view, making it a way more
complex integration test.

Note that imports for type-hinting purposes are fine.

*Wrong:*

```python
from django.db.models import QuerySet
from django.views import generic


class MyView(generic.DetailView):
    def get_queryset(self) -> QuerySet: ...
```

*Correct:*

```python
import typing
from django.views import generic

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class MyView(generic.DetailView):
    def get_queryset(self) -> "QuerySet": ...
```
