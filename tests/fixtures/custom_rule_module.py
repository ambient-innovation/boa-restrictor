from boa_restrictor.common.rule import Rule
from boa_restrictor.projections.occurrence import Occurrence


class SampleCustomRule(Rule):
    RULE_ID = "TST001"
    RULE_LABEL = "Sample custom rule for tests."

    def check(self) -> list[Occurrence]:
        return []


class AnotherCustomRule(Rule):
    RULE_ID = "TST002"
    RULE_LABEL = "Another sample rule."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithoutRuleId(Rule):
    RULE_LABEL = "Forgot the RULE_ID."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithoutRuleLabel(Rule):
    RULE_ID = "TST003"

    def check(self) -> list[Occurrence]:
        return []


class RuleWithReservedPrefix(Rule):
    RULE_ID = "PBR999"
    RULE_LABEL = "Pretends to be a built-in."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithReservedDjangoPrefix(Rule):
    RULE_ID = "DBR999"
    RULE_LABEL = "Pretends to be a built-in Django rule."

    def check(self) -> list[Occurrence]:
        return []


class RuleCollidingWithBuiltin(Rule):
    RULE_ID = "PBR001"
    RULE_LABEL = "Collides with a real built-in ID."

    def check(self) -> list[Occurrence]:
        return []


class RuleClashingWithSample(Rule):
    RULE_ID = "TST001"
    RULE_LABEL = "Collides with SampleCustomRule."

    def check(self) -> list[Occurrence]:
        return []


class ThirdRuleClashingWithSample(Rule):
    RULE_ID = "TST001"
    RULE_LABEL = "Third rule clashing on TST001."

    def check(self) -> list[Occurrence]:
        return []


class NotARuleSubclass:
    RULE_ID = "TST998"
    RULE_LABEL = "Not a Rule subclass."


class RuleWithNonStringRuleId(Rule):
    RULE_ID = 123
    RULE_LABEL = "RULE_ID is not a string."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithNonStringRuleLabel(Rule):
    RULE_ID = "TST900"
    RULE_LABEL = 42

    def check(self) -> list[Occurrence]:
        return []


class RuleWithLowercaseRuleId(Rule):
    RULE_ID = "tst001"
    RULE_LABEL = "Lowercase RULE_ID — would never be silenceable via # noqa:."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithPunctuatedRuleId(Rule):
    RULE_ID = "MY-001"
    RULE_LABEL = "Hyphenated RULE_ID — not allowed."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithLettersOnlyRuleId(Rule):
    RULE_ID = "TST"
    RULE_LABEL = "Letters-only RULE_ID — missing required digits."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithDigitsOnlyRuleId(Rule):
    RULE_ID = "001"
    RULE_LABEL = "Digits-only RULE_ID — missing required letters."

    def check(self) -> list[Occurrence]:
        return []


class RuleWithTrailingLettersRuleId(Rule):
    RULE_ID = "TST001A"
    RULE_LABEL = "Trailing letters after digits — not allowed."

    def check(self) -> list[Occurrence]:
        return []


not_a_class = "I am a string, not a class."
