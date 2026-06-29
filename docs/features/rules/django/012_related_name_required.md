# Relational model fields must declare an explicit "related_name" (DBR012)

This rule ensures that relational model fields (`ForeignKey`, `OneToOneField`, `ManyToManyField`) declare an
explicit `related_name`.

Relying on the auto-generated default (`<model>_set`) makes reverse accessors implicit: they are easy to
overlook, collide when two relations point at the same model, and silently break when a model is renamed.
An explicit `related_name` documents the reverse relation and keeps it stable. To intentionally disable the
reverse relation, pass `related_name="+"` — that counts as explicit and is accepted.

Models whose effective `Meta` declares a `default_related_name` are exempt: Django then derives an explicit
reverse accessor for every relation on that model, which is exactly what this rule enforces. The `Meta` is
resolved through inheritance as far as the current file allows — abstract base models and base `Meta` classes
defined in the **same file** are honoured (including `class Meta(Parent.Meta)` and multi-level chains).

Because the linter processes one file at a time, a `default_related_name` inherited from a base defined in
**another file** cannot be seen and the relation will still be flagged. Silence those with `# noqa: DBR012`.

Files inside a `migrations/` directory are exempt, since they are generated.

*Wrong:*

```python
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

*Correct:*

```python
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
```

*Also correct (exempted via `Meta.default_related_name`, including inheritance within the same file):*

```python
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "books"


class CommonInfo(models.Model):
    class Meta:
        abstract = True
        default_related_name = "objects_set"


class Review(CommonInfo):
    # Inherits default_related_name from the abstract base above — not flagged.
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
```
