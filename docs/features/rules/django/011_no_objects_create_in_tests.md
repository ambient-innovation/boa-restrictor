# Prohibit "<Model>.objects.create()" in tests (DBR011)

This rule prohibits creating model instances via `<Model>.objects.create()` in test files. Use a model
factory instead.

`objects.create()` forces you to spell out every required field by hand, which makes test setup verbose and
brittle: adding a new required field to the model breaks every test that creates it. A model factory fills in
the required fields automatically, so the test only states the values it actually cares about.

The example below uses [model_bakery](https://model-bakery.readthedocs.io/), but any factory library works.

*Wrong:*

```python
def test_user_is_active():
    user = User.objects.create(
        first_name="Ron", last_name="Doe", email="ron@example.com"
    )

    assert user.is_active is True
```

*Correct:*

```python
def test_user_is_active():
    user = baker.make(User)

    assert user.is_active is True
```
