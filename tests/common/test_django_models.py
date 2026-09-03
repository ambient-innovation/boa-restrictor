import ast

from boa_restrictor.common.ast_utils import index_classes_by_name, node_name
from boa_restrictor.common.django_models import (
    find_bound_field_call,
    find_declared_field_calls,
    find_model_field_aliases,
    find_model_module_aliases,
    is_any_model_field_call,
    is_django_model_class,
    is_model_field_call,
)

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


def test_find_model_module_aliases_defaults_to_models():
    source_tree = ast.parse("""from django.db import models""")

    assert find_model_module_aliases(source_tree) == frozenset({"models"})


def test_find_model_module_aliases_honours_from_import_asname():
    source_tree = ast.parse("""from django.db import models as db_models""")

    assert find_model_module_aliases(source_tree) == frozenset({"models", "db_models"})


def test_find_model_module_aliases_honours_import_asname():
    source_tree = ast.parse("""import django.db.models as m""")

    assert find_model_module_aliases(source_tree) == frozenset({"models", "m"})


def test_find_model_module_aliases_ignores_unrelated_modules():
    source_tree = ast.parse("""from rest_framework import serializers as models_like""")

    assert find_model_module_aliases(source_tree) == frozenset({"models"})


def test_aliased_module_qualifier_is_model_field():
    node = _call_node("""db_models.FloatField()""")

    assert is_model_field_call(node, field_names=FIELD_NAMES) is False
    assert is_model_field_call(node, field_names=FIELD_NAMES, module_aliases=frozenset({"models", "db_models"})) is True


def test_find_declared_field_calls_yields_assigned_calls():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount = models.FloatField()
    name: models.CharField = models.CharField(max_length=10)""")

    calls = list(find_declared_field_calls(source_tree))

    assert [node_name(call.func) for call in calls] == ["FloatField", "CharField"]


def test_find_declared_field_calls_skips_output_field_attribute():
    source_tree = ast.parse("""class Variance(Aggregate):
    output_field = models.FloatField()""")

    assert list(find_declared_field_calls(source_tree)) == []


def test_find_declared_field_calls_skips_nested_keyword_calls():
    source_tree = ast.parse("""average = Avg("price", output_field=models.FloatField())""")

    calls = list(find_declared_field_calls(source_tree))

    assert [node_name(call.func) for call in calls] == ["Avg"]


def test_find_declared_field_calls_yields_generated_field_output_field():
    source_tree = ast.parse(
        """total = models.GeneratedField(expression=F("a"), output_field=models.FloatField(), db_persist=True)"""
    )

    calls = list(find_declared_field_calls(source_tree))

    assert sorted(node_name(call.func) for call in calls) == ["FloatField", "GeneratedField"]


def test_is_django_model_class_direct_base():
    class_node = ast.parse("""class M(models.Model):
    pass""").body[0]

    assert is_django_model_class(class_node) is True


def test_is_django_model_class_bare_model_base():
    class_node = ast.parse("""class M(Model):
    pass""").body[0]

    assert is_django_model_class(class_node) is True


def test_is_django_model_class_aliased_module_base():
    class_node = ast.parse("""class M(db_models.Model):
    pass""").body[0]

    assert is_django_model_class(class_node) is False
    assert is_django_model_class(class_node, module_aliases=frozenset({"models", "db_models"})) is True


def test_is_django_model_class_recognised_by_declared_fields():
    class_node = ast.parse("""class Invoice(CommonInfo):
    reference = models.CharField(max_length=10)""").body[0]

    assert is_django_model_class(class_node) is True


def test_is_django_model_class_without_bases_or_fields():
    class_node = ast.parse("""class Config:
    STATUS = (("a", "A"),)""").body[0]

    assert is_django_model_class(class_node) is False


def test_is_django_model_class_ignores_serializer_fields():
    class_node = ast.parse("""class S(serializers.Serializer):
    name = serializers.CharField()""").body[0]

    assert is_django_model_class(class_node) is False


def test_is_any_model_field_call_matches_any_field_suffix():
    assert is_any_model_field_call(_call_node("""models.DecimalField(max_digits=5)""")) is True
    assert is_any_model_field_call(_call_node("""models.Manager()""")) is False
    assert is_any_model_field_call(_call_node("""serializers.CharField()""")) is False


def test_is_any_model_field_call_bare_name_needs_import():
    node = _call_node("""CharField()""")

    assert is_any_model_field_call(node) is False
    assert is_any_model_field_call(node, field_aliases={"CharField": "CharField"}) is True


def test_is_any_model_field_call_with_non_name_callable():
    node = _call_node("""get_field_class()()""")

    assert is_any_model_field_call(node) is False


def test_is_django_model_class_recognised_by_declared_relation_field():
    class_node = ast.parse("""class Membership(CommonInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)""").body[0]

    assert is_django_model_class(class_node) is True


def test_is_django_model_class_recognised_by_annotated_field():
    class_node = ast.parse("""class Invoice(CommonInfo):
    reference: CharField = models.CharField(max_length=10)""").body[0]

    assert is_django_model_class(class_node) is True


def test_is_django_model_class_ignores_field_call_in_method():
    class_node = ast.parse("""class FieldFactory:
    DEFAULTS = (("a", "A"),)

    def build(self):
        return models.CharField(max_length=10)""").body[0]

    assert is_django_model_class(class_node) is False


def test_is_django_model_class_ignores_field_call_in_nested_class():
    class_node = ast.parse("""class Wrapper:
    STATUS = (("a", "A"),)

    class Inner(models.Model):
        name = models.CharField(max_length=10)""").body[0]

    assert is_django_model_class(class_node) is False


def test_is_django_model_class_ignores_field_call_nested_in_assigned_value():
    class_node = ast.parse("""class Migration(migrations.Migration):
    dependencies = (("app", "0001_initial"),)
    operations = [migrations.AddField(field=models.CharField(max_length=10))]""").body[0]

    assert is_django_model_class(class_node) is False


def test_is_any_model_field_call_matches_suffixless_relation_fields():
    assert is_any_model_field_call(_call_node("""models.ForeignKey(User)""")) is True
    assert is_any_model_field_call(_call_node("""models.ForeignObject(User)""")) is True
    assert is_any_model_field_call(_call_node("""serializers.ForeignKey(User)""")) is False


def test_is_any_model_field_call_suffixless_relation_field_as_bare_name():
    node = _call_node("""ForeignKey(User)""")

    assert is_any_model_field_call(node) is False
    assert is_any_model_field_call(node, field_aliases={"ForeignKey": "ForeignKey"}) is True


def test_is_django_model_class_ignores_output_field_declaration():
    """An "output_field" types a query expression, so it makes its class no model."""
    class_node = ast.parse("""class ConcatName(models.Func):
    output_field = models.CharField()""").body[0]

    assert is_django_model_class(class_node) is False


def test_find_bound_field_call_returns_assigned_call():
    statement = ast.parse("""amount = models.FloatField()""").body[0]

    assert find_bound_field_call(statement) is statement.value


def test_find_bound_field_call_returns_annotated_assigned_call():
    statement = ast.parse("""amount: FloatField = models.FloatField()""").body[0]

    assert find_bound_field_call(statement) is statement.value


def test_find_bound_field_call_without_output_field_target():
    statement = ast.parse("""output_field = models.CharField()""").body[0]

    assert find_bound_field_call(statement) is None


def test_find_bound_field_call_without_call_value():
    statement = ast.parse("""STATUS = (("a", "A"),)""").body[0]

    assert find_bound_field_call(statement) is None


def test_find_bound_field_call_with_non_assignment():
    statement = ast.parse("""models.CharField()""").body[0]

    assert find_bound_field_call(statement) is None


def test_is_django_model_class_follows_a_base_declared_in_the_same_file():
    source_tree = ast.parse("""class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class Invoice(CommonInfo):
    STATUS = (("a", "A"),)""")
    classes_by_name = index_classes_by_name(source_tree)

    assert is_django_model_class(source_tree.body[1]) is False
    assert is_django_model_class(source_tree.body[1], classes_by_name=classes_by_name) is True


def test_is_django_model_class_follows_a_base_chain():
    source_tree = ast.parse("""class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class Auditable(CommonInfo):
    pass


class Invoice(Auditable):
    STATUS = (("a", "A"),)""")

    assert is_django_model_class(source_tree.body[2], classes_by_name=index_classes_by_name(source_tree)) is True


def test_is_django_model_class_does_not_follow_a_non_model_base():
    source_tree = ast.parse("""class Mixin:
    LABEL = "x"


class Config(Mixin):
    STATUS = (("a", "A"),)""")

    assert is_django_model_class(source_tree.body[1], classes_by_name=index_classes_by_name(source_tree)) is False


def test_is_django_model_class_survives_a_circular_base_chain():
    """A cycle cannot arise in valid Python, but the index is name-based and must not recurse endlessly."""
    source_tree = ast.parse("""class A(B):
    pass


class B(A):
    pass""")

    assert is_django_model_class(source_tree.body[0], classes_by_name=index_classes_by_name(source_tree)) is False
