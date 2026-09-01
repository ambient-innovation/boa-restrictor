# Avoid `FloatField` (DBR009)

`models.FloatField` maps to the database's binary floating-point type (`double precision` in PostgreSQL),
which PostgreSQL's own documentation calls inexact: "storing and retrieving a value might show slight
discrepancies". The same documentation recommends `numeric` — Django's `DecimalField` — "for storing
monetary amounts and other quantities where exactness is required".

The failure mode is quiet and late. A total drifts by a cent, or a lookup against a stored value stops
matching the number that was written. By the time anyone notices, the column holds production rows and the
correction costs a migration plus a data audit.

This rule flags every `FloatField` on a Django model, so that reaching for a float is a decision somebody
made rather than a default nobody questioned. Where the quantity genuinely is inexact, `# noqa: DBR009`
records that decision in one line.

*Wrong:*

```python
from django.db import models


class Invoice(models.Model):
    # An amount that must add up exactly
    total = models.FloatField()

    # A tax rate compared against stored values
    tax_rate = models.FloatField()
```

*Correct:*

```python
from django.db import models


class Invoice(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)

    tax_rate = models.DecimalField(max_digits=5, decimal_places=4)
```

A float that is inexact by nature is fine — say so and move on:

```python
from django.db import models


class Measurement(models.Model):
    # A sensor reading carries its own measurement error; decimal precision would be false precision
    temperature = models.FloatField()  # noqa: DBR009

    latitude = models.FloatField()  # noqa: DBR009
```

## Rationale

- Binary floating point cannot represent most decimal fractions exactly, so sums and equality comparisons
  are unreliable for anything that has to balance
- `Decimal` arithmetic is slower and its objects are larger, but that only matters in large numeric
  workloads, which are rare in an ORM-backed application; the everyday case is amounts, prices, rates and
  percentages
- The genuinely legitimate float — a measurement, a ratio, a coordinate — is exactly what a per-line
  `noqa` is for
- Migrations are exempt, being generated and out of the developer's hands

## Scope

The rule reports declarations of actual database columns. It recognises `models.FloatField(...)`,
`django.db.models.FloatField(...)`, an aliased models module (`from django.db import models as db_models`)
and a bare `FloatField(...)` imported from `django.db.models`.

Left alone:

- Serializer and form fields (`serializers.FloatField`, `forms.FloatField`) — emitting a `float` over a
  `DecimalField` column is the normal JSON boundary
- The `output_field` of an annotation, aggregate, `Cast` or `ExpressionWrapper`, and the `output_field`
  class attribute of a custom aggregate or database function — these type a query expression, not a column,
  and `DecimalField` is not a substitute there
- Plain `float` type annotations, which carry no persistence semantics

The one `output_field` that *is* reported belongs to `models.GeneratedField`: it decides the type of a real
generated column.

```python
from django.db import models
from django.db.models import Avg
from django.db.models.functions import Cast


class Report(models.Model):
    # Reported: this creates a float column
    score = models.FloatField()

    # Reported: a generated column is still a column
    weighted = models.GeneratedField(
        expression=models.F("score") * 2,
        output_field=models.FloatField(),
        db_persist=True,
    )


def averages(queryset):
    # Not reported: output_field types the annotation, no column involved
    return queryset.annotate(
        average=Avg("score", output_field=models.FloatField()),
        as_float=Cast("score", output_field=models.FloatField()),
    )
```
