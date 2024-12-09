## Rules

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

### Use dataclasses with "kw_only" (PBR004)

This rule will enforce that you use the `kw_only` parameter in every dataclass decorator.

This will force the developer to set all dataclass attributes as kwargs instead of args, which is more explicit and
easier to refactor.

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
