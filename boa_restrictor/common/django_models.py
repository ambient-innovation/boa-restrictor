import ast
from collections.abc import Iterator

from boa_restrictor.common.ast_utils import node_name

# Module under which Django exposes its model fields, both as "models.CharField" and as the fully
# qualified "django.db.models.CharField". A field reached through any other module ("serializers.CharField",
# "forms.CharField") belongs to a serializer or a form and is never persisted.
MODEL_FIELD_QUALIFIERS = frozenset({"models"})

DJANGO_MODELS_MODULE = "django.db.models"
DJANGO_DB_MODULE = "django.db"
MODELS_MODULE_NAME = "models"

# The "output_field" of an annotation, aggregate or "Cast" types a query expression rather than a column.
# The one exception is "GeneratedField", whose "output_field" decides the type of a real column.
OUTPUT_FIELD_KEYWORD = "output_field"
GENERATED_FIELD = "GeneratedField"

MODEL_CLASS_NAME = "Model"
# Every Django model field class ends in "Field", bar the relation fields spelled without that suffix.
# Together they identify a class as a model when its base cannot be resolved.
MODEL_FIELD_SUFFIX = "Field"
SUFFIXLESS_MODEL_FIELDS = frozenset({"ForeignKey", "ForeignObject"})


def _is_model_field_name(name: str) -> bool:
    """
    Returns whether the given class name is that of a Django model field.
    """
    return name.endswith(MODEL_FIELD_SUFFIX) or name in SUFFIXLESS_MODEL_FIELDS


def find_model_field_aliases(source_tree: ast.AST) -> dict[str, str]:
    """
    Returns the local names under which model fields were imported straight from "django.db.models",
    mapped to their name in that module. Aliases are honoured, so
    "from django.db.models import CharField as Char" yields {"Char": "CharField"}.
    """
    aliases = {}

    for node in ast.walk(source_tree):
        if isinstance(node, ast.ImportFrom) and node.module == DJANGO_MODELS_MODULE:
            for alias in node.names:
                aliases[alias.asname or alias.name] = alias.name

    return aliases


def find_model_module_aliases(source_tree: ast.AST) -> frozenset[str]:
    """
    Returns the local names that refer to Django's models module, so both "models.CharField(...)" and an
    aliased "db_models.CharField(...)" are recognised. "models" is always included: it covers the usual
    "from django.db import models" and the trailing segment of a fully qualified
    "django.db.models.CharField(...)".
    """
    aliases = set(MODEL_FIELD_QUALIFIERS)

    for node in ast.walk(source_tree):
        # An aliased plain import binds the alias to the models module itself.
        if isinstance(node, ast.Import):
            aliases.update(alias.asname for alias in node.names if alias.asname and alias.name == DJANGO_MODELS_MODULE)
        # An aliased from-import binds the alias to the models submodule of django.db.
        elif isinstance(node, ast.ImportFrom) and node.module == DJANGO_DB_MODULE:
            aliases.update(alias.asname for alias in node.names if alias.asname and alias.name == MODELS_MODULE_NAME)

    return frozenset(aliases)


def find_bound_field_call(statement: ast.stmt) -> ast.Call | None:
    """
    Returns the call the given statement binds to a name ("amount = models.FloatField()"), or None when it
    binds none.

    An assignment to "output_field" binds none: it types a query expression rather than a column. The
    common shapes are the "output_field" of an annotation, aggregate, "Cast" or "ExpressionWrapper", and
    the "output_field" class attribute of a custom aggregate or database function.
    """
    if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
        return None

    targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
    if any(node_name(target) == OUTPUT_FIELD_KEYWORD for target in targets):
        return None

    return statement.value if isinstance(statement.value, ast.Call) else None


def find_declared_field_calls(source_tree: ast.AST) -> Iterator[ast.Call]:
    """
    Yields every call that declares a database column: one bound to a name ("amount = models.FloatField()")
    and the "output_field" of a "GeneratedField", which types a generated column.

    A field call reached any other way describes the type of a query expression, not a column.
    """
    for node in ast.walk(source_tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            bound_call = find_bound_field_call(node)
            if bound_call is not None:
                yield bound_call
        elif isinstance(node, ast.Call) and node_name(node.func) == GENERATED_FIELD:
            for keyword in node.keywords:
                if keyword.arg == OUTPUT_FIELD_KEYWORD and isinstance(keyword.value, ast.Call):
                    yield keyword.value


def is_model_field_call(
    node: ast.Call,
    *,
    field_names: frozenset[str],
    field_aliases: dict[str, str] | None = None,
    module_aliases: frozenset[str] = MODEL_FIELD_QUALIFIERS,
) -> bool:
    """
    Returns whether the given call instantiates one of the named Django *model* fields.

    The decision is made from the call expression itself rather than from the class surrounding it: nothing
    but a model field is ever spelled "models.CharField(...)", whereas the enclosing class' base may be
    defined in another file and is therefore not always resolvable. Pass "field_aliases" from
    "find_model_field_aliases" to also recognise fields imported directly from "django.db.models", and
    "module_aliases" from "find_model_module_aliases" to recognise an aliased models module.
    """
    # "models.CharField(...)" and "django.db.models.CharField(...)" both leave "models" as the qualifier.
    if isinstance(node.func, ast.Attribute):
        return node.func.attr in field_names and node_name(node.func.value) in module_aliases

    # A bare "CharField(...)" is only a model field if this file imported it from the models module.
    if isinstance(node.func, ast.Name):
        return (field_aliases or {}).get(node.func.id) in field_names

    return False


def is_any_model_field_call(
    node: ast.Call,
    *,
    field_aliases: dict[str, str] | None = None,
    module_aliases: frozenset[str] = MODEL_FIELD_QUALIFIERS,
) -> bool:
    """
    Returns whether the given call instantiates any Django model field, without naming it up front.
    Recognition works off the "Field" suffix that model field classes carry, plus the relation fields
    spelled without it.
    """
    if isinstance(node.func, ast.Attribute):
        return _is_model_field_name(node.func.attr) and node_name(node.func.value) in module_aliases

    if isinstance(node.func, ast.Name):
        field_name = (field_aliases or {}).get(node.func.id)
        return bool(field_name) and _is_model_field_name(field_name)

    return False


def is_django_model_class(
    class_node: ast.ClassDef,
    *,
    field_aliases: dict[str, str] | None = None,
    module_aliases: frozenset[str] = MODEL_FIELD_QUALIFIERS,
) -> bool:
    """
    Returns whether the given class is a Django model.

    A base spelled "models.Model" or "Model" settles it. Otherwise a declared model field does: a base
    inherited from a project class in another file cannot be resolved one file at a time, but a class
    assigning a "models.CharField(...)" in its body is a model whatever it inherits from.

    Only such a direct assignment counts. A field call further down -- inside a method, a nested class or
    an element of a list literal -- declares no column on this class and says nothing about what it is, and
    neither does an "output_field", which types a query expression.
    """
    for base in class_node.bases:
        if node_name(base) != MODEL_CLASS_NAME:
            continue
        if isinstance(base, ast.Name) or node_name(base.value) in module_aliases:
            return True

    bound_calls = (find_bound_field_call(statement) for statement in class_node.body)

    return any(
        bound_call is not None
        and is_any_model_field_call(bound_call, field_aliases=field_aliases, module_aliases=module_aliases)
        for bound_call in bound_calls
    )
