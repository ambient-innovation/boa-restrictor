# Return type hints required if a return statement exists (PBR002)

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
