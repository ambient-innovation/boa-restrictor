# Service classes must be named "...Service" (PBR011)

This rule ensures that top-level classes living in the service layer (a `services.py` module or a file under a
`services/` directory) are named with a `Service` suffix. A consistent suffix makes service classes instantly
recognisable and pairs with [PBR005](005_service_class_with_process.md), which constrains their shape.

Only top-level classes are checked. The following are exempt, since they are value objects rather than services:

- enums (`Enum`, `IntEnum`, `TextChoices`, ...),
- dataclasses (`@dataclass`),
- typed dicts and named tuples (`TypedDict`, `NamedTuple`),
- exceptions (subclasses of `Exception`, or names ending in `Error`/`Exception`).

*Wrong:*

```python
class CreateUser:
    def process(self): ...
```

*Correct:*

```python
class CreateUserService:
    def process(self): ...
```
