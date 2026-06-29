# Require at least one assertion per test (PBR010)

This rule ensures that every test function (a function whose name starts with `test`, inside a test file)
contains at least one assertion. A test that asserts nothing can never fail and therefore provides no
protection against regressions — it only proves the code under test does not raise.

The following are recognised as assertions:

- a bare `assert ...` statement,
- any call to an `assert*` method or function (e.g. `self.assertEqual(...)`, `self.assertRaises(...)`),
- `pytest.raises(...)`, `pytest.warns(...)` and `pytest.deprecated_call(...)`.

If you assert through a custom helper that the rule cannot recognise statically, silence the individual
finding with `# noqa: PBR010`.

*Wrong:*

```python
def test_user_can_be_created():
    user = baker.make(User)
    user.activate()
```

*Correct:*

```python
def test_user_can_be_created():
    user = baker.make(User)
    user.activate()

    assert user.is_active is True
```
