# Prohibit usage of TestCase.assertRaises() (DBR001)

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
