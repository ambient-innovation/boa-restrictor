from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.return_type_hints import ReturnStatementRequiresTypeHintRule

BOA_RESTRICTOR_RULES = (
    AsteriskRequiredRule,
    ReturnStatementRequiresTypeHintRule,
)
