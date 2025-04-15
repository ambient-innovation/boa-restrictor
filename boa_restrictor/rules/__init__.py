from boa_restrictor.rules.django.no_db_in_views import NoDjangoDbImportInViewsRule
from boa_restrictor.rules.django.prohibit_assert_raises import AssertRaisesProhibitedRule
from boa_restrictor.rules.python.abstract_class_inherits_from_abc import AbstractClassesInheritFromAbcRule
from boa_restrictor.rules.python.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.python.dataclass_kw_only import DataclassWithKwargsOnlyRule
from boa_restrictor.rules.python.global_import_datetime import GlobalImportDatetimeRule
from boa_restrictor.rules.python.return_type_hints import ReturnStatementRequiresTypeHintRule
from boa_restrictor.rules.python.service_class_only_one_public import ServiceClassHasOnlyOnePublicMethodRule

BOA_RESTRICTOR_RULES = (
    AsteriskRequiredRule,
    ReturnStatementRequiresTypeHintRule,
    GlobalImportDatetimeRule,
    DataclassWithKwargsOnlyRule,
    ServiceClassHasOnlyOnePublicMethodRule,
    AbstractClassesInheritFromAbcRule,
)

DJANGO_BOA_RULES = (
    AssertRaisesProhibitedRule,
    NoDjangoDbImportInViewsRule,
)


def get_rules(*, use_django_rules: bool) -> tuple:
    """
    Returns a list of all enabled rules.
    """
    if use_django_rules:
        return BOA_RESTRICTOR_RULES + DJANGO_BOA_RULES
    return BOA_RESTRICTOR_RULES
