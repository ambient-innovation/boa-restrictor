# Require at least one assertion per test (PBR010)

This rule ensures that every test function (a function whose name starts with `test`, inside a test file)
contains at least one assertion. A test that asserts nothing can never fail and therefore provides no
protection against regressions — it only proves the code under test does not raise.

The following are recognised as assertions:

- a bare `assert ...` statement,
- any call to an `assert*` method or function (e.g. `self.assertEqual(...)`, `self.assertRaises(...)`),
- `pytest.raises(...)`, `pytest.warns(...)` and `pytest.deprecated_call(...)`,
- a call to `fail` (e.g. `self.fail(...)`, `pytest.fail(...)`): such a test can still fail — for example
  on the wrong branch of a `try`/`except` — and therefore does protect against regressions.

If you assert through a custom helper that the rule cannot recognise statically, silence the individual
finding with `# noqa: PBR010`.

Functions decorated with `@pytest.fixture` (including parametrized forms such as
`@pytest.fixture(scope="module")` and the directly-imported `@fixture`) are not treated as tests, even when
their name starts with `test`, so they are never required to contain an assertion.

## Known limitation

The rule analyses one function at a time and does not follow calls. If a test delegates its assertions to
a called helper method (e.g. `self._assert_state()`), the rule cannot see them and will flag the test.
Either inline the assertion or suppress the finding with `# noqa: PBR010`.

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
