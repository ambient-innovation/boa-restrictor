# Use dataclasses with "kw_only" (PBR004)

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
