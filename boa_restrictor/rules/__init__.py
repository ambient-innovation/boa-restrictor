from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.dataclass_kw_only import DataclassWithKwargsOnlyRule
from boa_restrictor.rules.global_import_datetime import GlobalImportDatetimeRule
from boa_restrictor.rules.return_type_hints import ReturnStatementRequiresTypeHintRule

BOA_RESTRICTOR_RULES = (
    AsteriskRequiredRule,
    ReturnStatementRequiresTypeHintRule,
    GlobalImportDatetimeRule,
    DataclassWithKwargsOnlyRule,
)
