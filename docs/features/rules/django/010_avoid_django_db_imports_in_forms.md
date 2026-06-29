# Don't import "django.db" in the form layer (DBR010)

Ensures that no Django low-level database functionality is imported and therefore used in the form layer.
Forms are responsible for validating and cleaning input, not for running queries. Move any database access
into a model manager or service so the form stays focused and easy to test.

Note that imports for type-hinting purposes are fine.

*Wrong:*

```python
from django import forms
from django.db.models import QuerySet


class UserForm(forms.Form):
    def clean(self) -> QuerySet: ...
```

*Correct:*

```python
import typing

from django import forms

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class UserForm(forms.Form):
    def clean(self) -> "QuerySet": ...
```
