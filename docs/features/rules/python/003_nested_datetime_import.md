# Avoid nested import of datetime module (PBR003)

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
