# Prohibit usage of "datetime.now" (DBR004)

When using Django, you should always use `django.utils.timezone.now()` instead of Pythons native
`datetime.datetime.now()`.

`timezone.now()` will automatically set the project's timezone while the Python implementation won't be timezone-aware.

*Wrong:*

```python
from datetime import datetime

timestamp = datetime.now()
```

*Correct:*

```python
from django.utils import timezone

timestamp = timezone.now()
```
