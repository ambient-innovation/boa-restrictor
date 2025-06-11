# Positional arguments not allowed (PBR001)

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
