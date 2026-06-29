# Prohibit local/inline imports in test files (PBR009)

This rule prohibits local/inline imports (imports nested inside a function or method) within test files.

Imports belong at the top of the module. Keeping them there makes a test's dependencies obvious at a glance and
avoids hiding setup details inside the test body. Inline imports in tests are usually a sign that something is
being patched or worked around in a way that would be clearer as an explicit, top-level dependency.

*Wrong:*

```python
def test_something():
    from myapp.services import MyService

    assert MyService().process() is True
```

*Correct:*

```python
from myapp.services import MyService


def test_something():
    assert MyService().process() is True
```
