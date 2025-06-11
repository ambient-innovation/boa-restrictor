# Avoid using type hints in variable names (PBR007)

This rule will enforce that variables don't contain type hints as suffixes like "user_list" or "project_qs".

This is bad because the types are implicitly defined in the variable name. It's not possible to statically check
them, and if the content changes, it's often forgotten to update the variable name.

*Wrong:*

```python
user_list = []
```

*Correct:*

```python
users = []
```
