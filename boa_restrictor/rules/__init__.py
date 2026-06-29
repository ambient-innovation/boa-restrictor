from boa_restrictor.rules.django.avoid_tuple_based_model_choices import AvoidTupleBasedModelChoices
from boa_restrictor.rules.django.charfield_max_length_required import CharFieldMaxLengthRequiredRule
from boa_restrictor.rules.django.no_assert_booleans_in_tests import ProhibitAssertBooleanInTests
from boa_restrictor.rules.django.no_db_in_api import NoDjangoDbImportInApiRule
from boa_restrictor.rules.django.no_db_in_forms import NoDjangoDbImportInFormsRule
from boa_restrictor.rules.django.no_db_in_services import NoDjangoDbImportInServicesRule
from boa_restrictor.rules.django.no_db_in_tasks import NoDjangoDbImportInTasksRule
from boa_restrictor.rules.django.no_db_in_views import NoDjangoDbImportInViewsRule
from boa_restrictor.rules.django.no_objects_create_in_tests import NoObjectsCreateInTestsRule
from boa_restrictor.rules.django.prohibit_assert_raises import AssertRaisesProhibitedRule
from boa_restrictor.rules.django.prohibit_datetime_now import ProhibitDatetimeNow
from boa_restrictor.rules.django.related_name_required import RelatedNameRequiredRule
from boa_restrictor.rules.python.abstract_class_inherits_from_abc import AbstractClassesInheritFromAbcRule
from boa_restrictor.rules.python.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.python.dataclass_kw_only import DataclassWithKwargsOnlyRule
from boa_restrictor.rules.python.global_import_datetime import GlobalImportDatetimeRule
from boa_restrictor.rules.python.mandatory_test_assertion import MandatoryTestAssertionRule
from boa_restrictor.rules.python.no_inline_imports_in_tests import NoInlineImportInTestsRule
from boa_restrictor.rules.python.no_loops_in_tests import NoLoopsInTestsRule
from boa_restrictor.rules.python.no_type_hints_in_variable_names import AvoidTypeHintsInVariableNamesAsSuffix
from boa_restrictor.rules.python.return_type_hints import ReturnStatementRequiresTypeHintRule
from boa_restrictor.rules.python.service_class_naming import ServiceClassNameRule
from boa_restrictor.rules.python.service_class_only_one_public import ServiceClassHasOnlyOnePublicMethodRule

BOA_RESTRICTOR_RULES = (
    AsteriskRequiredRule,
    ReturnStatementRequiresTypeHintRule,
    GlobalImportDatetimeRule,
    DataclassWithKwargsOnlyRule,
    ServiceClassHasOnlyOnePublicMethodRule,
    AbstractClassesInheritFromAbcRule,
    AvoidTypeHintsInVariableNamesAsSuffix,
    NoLoopsInTestsRule,
    NoInlineImportInTestsRule,
    MandatoryTestAssertionRule,
    ServiceClassNameRule,
)

DJANGO_BOA_RULES = (
    AssertRaisesProhibitedRule,
    NoDjangoDbImportInViewsRule,
    ProhibitAssertBooleanInTests,
    ProhibitDatetimeNow,
    NoDjangoDbImportInApiRule,
    AvoidTupleBasedModelChoices,
    CharFieldMaxLengthRequiredRule,
    NoDjangoDbImportInServicesRule,
    NoDjangoDbImportInTasksRule,
    NoDjangoDbImportInFormsRule,
    NoObjectsCreateInTestsRule,
    RelatedNameRequiredRule,
)


def get_rules(*, use_django_rules: bool) -> tuple:
    """
    Returns a list of all enabled rules.
    """
    if use_django_rules:
        return BOA_RESTRICTOR_RULES + DJANGO_BOA_RULES
    return BOA_RESTRICTOR_RULES
