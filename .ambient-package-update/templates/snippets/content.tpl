## Rules

### Positional arguments not allowed (PBR001)

This rule enforces that functions and methods don't contain any positional arguments.

This will make refactorings easier, is more explicit, and you avoid the boolean bug trap.

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

This rule will enforce that you add a return statement to all methods and functions that contain a `return` statement.

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
