import ast

from boa_restrictor.common.django_models import find_model_field_aliases, is_model_field_call

FIELD_NAMES = frozenset({"FloatField", "CharField"})


def _call_node(source: str) -> ast.Call:
    return next(node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call))


def test_find_model_field_aliases_plain_import():
    source_tree = ast.parse("""from django.db.models import CharField, FloatField""")

    assert find_model_field_aliases(source_tree) == {"CharField": "CharField", "FloatField": "FloatField"}


def test_find_model_field_aliases_honours_asname():
    source_tree = ast.parse("""from django.db.models import FloatField as Float""")

    assert find_model_field_aliases(source_tree) == {"Float": "FloatField"}


def test_find_model_field_aliases_ignores_other_modules():
    source_tree = ast.parse("""from rest_framework.serializers import FloatField""")

    assert find_model_field_aliases(source_tree) == {}


def test_find_model_field_aliases_without_imports():
    source_tree = ast.parse("""amount = models.FloatField()""")

    assert find_model_field_aliases(source_tree) == {}


def test_models_qualifier_is_model_field():
    node = _call_node("""models.FloatField()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is True


def test_fully_qualified_models_path_is_model_field():
    node = _call_node("""django.db.models.CharField(max_length=10)""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is True


def test_serializer_qualifier_is_not_model_field():
    node = _call_node("""serializers.FloatField()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is False


def test_unlisted_field_name_is_not_matched():
    node = _call_node("""models.DecimalField(max_digits=5, decimal_places=2)""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is False


def test_bare_name_requires_models_import():
    node = _call_node("""FloatField()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is False
    assert is_model_field_call(node, field_names=FIELD_NAMES, field_aliases={"FloatField": "FloatField"}) is True


def test_bare_alias_resolves_to_original_field_name():
    node = _call_node("""Float()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES, field_aliases={"Float": "FloatField"}) is True


def test_non_name_callable_is_not_model_field():
    node = _call_node("""get_field_class()()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is False
