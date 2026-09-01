import ast

from boa_restrictor.common.ast_utils import node_name

# Module under which Django exposes its model fields, both as "models.CharField" and as the fully
# qualified "django.db.models.CharField". A field reached through any other module ("serializers.CharField",
# "forms.CharField") belongs to a serializer or a form and is never persisted.
MODEL_FIELD_QUALIFIERS = frozenset({"models"})

DJANGO_MODELS_MODULE = "django.db.models"


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


def is_model_field_call(
    node: ast.Call, *, field_names: frozenset[str], field_aliases: dict[str, str] | None = None
) -> bool:
    """
    Returns whether the given call instantiates one of the named Django *model* fields.

    The decision is made from the call expression itself rather than from the class surrounding it: nothing
    but a model field is ever spelled "models.CharField(...)", whereas the enclosing class' base may be
    defined in another file and is therefore not always resolvable. Pass "field_aliases" from
    "find_model_field_aliases" to also recognise fields imported directly from "django.db.models".
    """
    # "models.CharField(...)" and "django.db.models.CharField(...)" both leave "models" as the qualifier.
    if isinstance(node.func, ast.Attribute):
        return node.func.attr in field_names and node_name(node.func.value) in MODEL_FIELD_QUALIFIERS

    # A bare "CharField(...)" is only a model field if this file imported it from the models module.
    if isinstance(node.func, ast.Name):
        return (field_aliases or {}).get(node.func.id) in field_names

    return False
