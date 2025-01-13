from boa_restrictor.rules.abstract_class_inherits_from_abc import AbstractClassesInheritFromAbcRule
from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.dataclass_kw_only import DataclassWithKwargsOnlyRule
from boa_restrictor.rules.global_import_datetime import GlobalImportDatetimeRule
from boa_restrictor.rules.return_type_hints import ReturnStatementRequiresTypeHintRule
from boa_restrictor.rules.service_class_only_one_public import ServiceClassHasOnlyOnePublicMethodRule

BOA_RESTRICTOR_RULES = (
    AsteriskRequiredRule,
    ReturnStatementRequiresTypeHintRule,
    GlobalImportDatetimeRule,
    DataclassWithKwargsOnlyRule,
    ServiceClassHasOnlyOnePublicMethodRule,
    AbstractClassesInheritFromAbcRule,
)
