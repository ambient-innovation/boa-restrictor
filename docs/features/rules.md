# Rules

## Positional arguments not allowed (PBR001)

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

## Return type hints required if a return statement exists (PBR002)

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

## Avoid nested import of datetime module (PBR003)

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

## Use dataclasses with "kw_only" (PBR004)

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

## Service classes have one public method called "process" (PBR005)

Putting business logic in classes called "service" is a well-known and widely used pattern. To hide the inner workings
of this logic, it's recommended to prefix all methods with an underscore ("_") to mark them as protected. The single
entrypoint should be a public method called "process".

## Abstract classes inherit from "abc.ABC" (PBR006)

Python provides a base class for abstract classes. If a class is named "abstract", it should therefore inherit from
the `abc.ABC` class.
