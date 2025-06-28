# Prohibit usage of loops in unittests (PBR008)

This rule will prohibit the usage of loops (`for`, `while`) in unittests.

This is bad because a loop will introduce complexity and make the test case harder to understand and therefore change.

Additionally, unittests are supposed to be atomic, meaning should only test exactly one case.

*Wrong:*

```python
def test_result_contains_all_results():
    expected_results = [user_1, user_2]

    result = MyService()
    for i, item in enumerate(result):
        assert item == expected_results[i]
```

*Correct:*

```python
def test_result_contains_all_results():
    result = MyService()

    assert user_1 in result
    assert user_2 in result
```
