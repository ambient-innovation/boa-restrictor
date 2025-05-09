# Rules

## Python rules

### Positional arguments not allowed (PBR001)

This rule enforces that functions and methods don't contain any positional arguments.

This will make refactorings easier, is more explicit,
and you avoid the [boolean bug trap](https://adamj.eu/tech/2021/07/10/python-type-hints-how-to-avoid-the-boolean-trap/).

*Wrong:*

```python
def my_func(a, b):
    pass
```

*Correct:*

```python
def my_func(*, a, b):
    pass
```

### Return type hints required if a return statement exists (PBR002)

This rule will enforce that you add a return type-hint to all methods and functions that contain a `return` statement.
This way we can be more explicit and let the IDE help the next developer because it will add warnings if you use
wrong types.

*Wrong:*

```python
def my_func(a, b):
    return a * b
```

*Correct:*

```python
def my_func(a, b) -> int:
    return a * b
```

### Avoid nested import of datetime module (PBR003)

This rule will enforce that you never import a datetime object from the datetime module, but instead import the datetime
module and get the object from there.

Since you can't distinguish in the code between a `datetime` module and `datetime` object without looking at the
imports, this leads to inconsistent and unclear code.

Importing the `date` object can cause a namespace conflict with the Django template tag `date`, therefore this is not
allowed as well.

*Wrong:*

```python
from datetime import datetime

my_datetime = datetime(2024, 9, 19)
```

*Correct:*

```python
import datetime

my_datetime = datetime.datetime(2024, 9, 19)
```

Note, that other imports from the `datetime` module like `UTC` are allowed since there are no known conflicts.

### Use dataclasses with "kw_only" (PBR004)

This rule will enforce that you use the `kw_only` parameter in every dataclass decorator.

This will force the developer to set all dataclass attributes as kwargs instead of args, which is more explicit and
easier to refactor.

*Wrong:*

```python
from dataclasses import dataclass


@dataclass
class MyDataClass:
    pass
```

*Correct:*

```python
from dataclasses import dataclass


@dataclass(kw_only=True)
class MyDataClass:
    pass
```

### Service classes have one public method called "process" (PBR005)

Putting business logic in classes called "service" is a well-known and widely used pattern. To hide the inner workings
of this logic, it's recommended to prefix all methods with an underscore ("_") to mark them as protected. The single
entrypoint should be a public method called "process".

### Abstract classes inherit from "abc.ABC" (PBR006)

Python provides a base class for abstract classes. If a class is named "abstract", it should therefore inherit from
the `abc.ABC` class.

## Django rules

### Prohibit usage of TestCase.assertRaises() (DBR001)

Ensures that `TestCase.assertRaises()` is never used since asserting an exception without the actual error
message leads to false positives. Use `TestCase.assertRaisesMessage()` instead.

*Wrong:*

```python
from django.test import TestCase


class MyTestCase(TestCase):

    def test_my_function(self):
        with self.assertRaises(RuntimeError):
            my_function()
```

*Correct:*

```python
from django.test import TestCase


class MyTestCase(TestCase):

    def test_my_function(self):
        with self.assertRaisesMessage(RuntimeError, "Ooops, that's an error."):
            my_function()
```

### Don't import "django.db" in the view layer (DBR002)

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
    def get_queryset(self) -> QuerySet: ...
```
