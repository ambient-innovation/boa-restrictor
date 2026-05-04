class CustomRuleError(ValueError):
    """Base error for custom-rule loading and validation failures."""


class CustomRuleConfigurationError(CustomRuleError):
    """Structural problem in the custom_rules config value."""


class CustomRulesNotAListError(CustomRuleConfigurationError):
    def __init__(self):
        super().__init__('Configuration value "custom_rules" must be a list.')


class CustomRulePathNotAStringError(CustomRuleConfigurationError):
    def __init__(self, value):
        super().__init__(
            f"Each entry in custom_rules must be a string (dotted import path); got {type(value).__name__}: {value!r}."
        )


class DuplicateCustomRulePathError(CustomRuleConfigurationError):
    def __init__(self, dotted_path: str):
        super().__init__(f'Duplicate entry in custom_rules: "{dotted_path}".')


class CustomRuleImportError(CustomRuleError):
    """Failure importing a custom rule's module or attribute."""


class InvalidCustomRulePathError(CustomRuleImportError):
    def __init__(self, dotted_path: str):
        super().__init__(
            f'Invalid custom rule path "{dotted_path}". Expected a dotted path of the form "module.ClassName".'
        )


class CustomRuleModuleImportFailedError(CustomRuleImportError):
    def __init__(self, *, module_path: str, dotted_path: str, original: BaseException):
        super().__init__(
            f'Could not import module "{module_path}" for custom rule "{dotted_path}": {original}. '
            f"Make sure your project is on the Python path "
            f"(see boa-restrictor docs on running with custom rules under pre-commit)."
        )


class CustomRuleAttributeMissingError(CustomRuleImportError):
    def __init__(self, *, module_path: str, attr_name: str, dotted_path: str):
        super().__init__(f'Module "{module_path}" has no attribute "{attr_name}" (custom rule "{dotted_path}").')


class CustomRuleValidationError(CustomRuleError):
    """A loaded object failed Rule contract validation."""


class CustomRuleNotAClassError(CustomRuleValidationError):
    def __init__(self, dotted_path: str):
        super().__init__(f'Custom rule "{dotted_path}" is not a class.')


class CustomRuleNotARuleSubclassError(CustomRuleValidationError):
    def __init__(self, dotted_path: str):
        super().__init__(f'Custom rule "{dotted_path}" must subclass boa_restrictor.common.rule.Rule.')


class CustomRuleMissingRuleIdError(CustomRuleValidationError):
    def __init__(self, dotted_path: str):
        super().__init__(f'Custom rule "{dotted_path}" does not set RULE_ID.')


class CustomRuleMissingRuleLabelError(CustomRuleValidationError):
    def __init__(self, dotted_path: str):
        super().__init__(f'Custom rule "{dotted_path}" does not set RULE_LABEL.')


class CustomRuleReservedPrefixError(CustomRuleValidationError):
    def __init__(self, *, dotted_path: str, prefix: str, reserved_prefixes: tuple[str, ...]):
        super().__init__(
            f'Custom rule "{dotted_path}" uses reserved RULE_ID prefix "{prefix}". '
            f"Prefixes {reserved_prefixes} are reserved for built-in rules."
        )


class DuplicateRuleIdError(CustomRuleValidationError):
    def __init__(self, *, clashes: list[tuple[str, type, type]]):
        """
        `clashes` is a list of (rule_id, first_class, second_class) for every detected duplicate.
        """
        lines = [
            f'  - "{rule_id}": "{first.__module__}.{first.__qualname__}" '
            f'and "{second.__module__}.{second.__qualname__}"'
            for rule_id, first, second in clashes
        ]
        super().__init__("Duplicate RULE_IDs detected:\n" + "\n".join(lines))
