# Relational model fields must declare an explicit "related_name" (DBR012)

This rule ensures that relational model fields (`ForeignKey`, `OneToOneField`, `ManyToManyField`) declare an
explicit `related_name`.

Relying on the auto-generated default (`<model>_set`) makes reverse accessors implicit: they are easy to
overlook, collide when two relations point at the same model, and silently break when a model is renamed.
An explicit `related_name` documents the reverse relation and keeps it stable. To intentionally disable the
reverse relation, pass `related_name="+"` — that counts as explicit and is accepted.

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
