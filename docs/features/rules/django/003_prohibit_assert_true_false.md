# Prohibit usage of "assertTrue" and "assertFalse" in Django unittests (DBR003)

Using "assertTrue" or "assertFalse" in unittests might lead to false positives in your test results since these methods
will cast the given value to boolean.

This means that x = 1 will make `assertTrue(x)` pass but `assertIs(x, True)` will fail.

Since explicit is better than implicit, the usage of these methods is discouraged.

*Wrong:*

```python
from django.test import TestCase


class MyTest(TestCase):
    def test_x(self):
        ...
        self.assertTrue(x)
        self.assertFalse(y)
```

*Correct:*

```python
from django.test import TestCase


class MyTest(TestCase):
    def test_x(self):
        ...
        self.assertIs(x, True)
        self.assertIs(y, False)
```
