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
        if isinstance(original, SyntaxError):
            hint = "Fix the syntax error in your rule module."
        else:
            hint = (
                "Make sure your project is on the Python path "
                "(see boa-restrictor docs on running with custom rules under pre-commit)."
            )
        super().__init__(f'Could not import module "{module_path}" for custom rule "{dotted_path}": {original}. {hint}')


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


class CustomRuleInvalidRuleIdTypeError(CustomRuleValidationError):
    def __init__(self, *, dotted_path: str, value):
        super().__init__(
            f'Custom rule "{dotted_path}" has a non-string RULE_ID '
            f"(got {type(value).__name__}: {value!r}). RULE_ID must be a string."
        )


class CustomRuleInvalidRuleLabelTypeError(CustomRuleValidationError):
    def __init__(self, *, dotted_path: str, value):
        super().__init__(
            f'Custom rule "{dotted_path}" has a non-string RULE_LABEL '
            f"(got {type(value).__name__}: {value!r}). RULE_LABEL must be a string."
        )


class CustomRuleInvalidRuleIdShapeError(CustomRuleValidationError):
    def __init__(self, *, dotted_path: str, rule_id: str):
        super().__init__(
            f'Custom rule "{dotted_path}" has malformed RULE_ID "{rule_id}". '
            "RULE_IDs must be one or more uppercase ASCII letters followed by one or more digits "
            '(e.g. "TST001"). Lowercase or punctuated IDs cannot be silenced via "# noqa:".'
        )


class CustomRuleReservedPrefixError(CustomRuleValidationError):
    def __init__(self, *, dotted_path: str, prefix: str, reserved_prefixes: tuple[str, ...]):
        super().__init__(
            f'Custom rule "{dotted_path}" uses reserved RULE_ID prefix "{prefix}". '
            f"Prefixes {reserved_prefixes} are reserved for built-in rules."
        )


class DuplicateRuleIdError(CustomRuleValidationError):
    def __init__(self, *, clashes: dict[str, list[type]]):
        """
        `clashes` maps each clashing RULE_ID to the list of classes sharing that ID.
        Grouped by ID so triple-clashes show as one line listing all offenders rather than
        N-1 pairwise lines.
        """
        lines = [
            f'  - "{rule_id}": ' + ", ".join(f'"{c.__module__}.{c.__qualname__}"' for c in classes)
            for rule_id, classes in clashes.items()
        ]
        super().__init__("Duplicate RULE_IDs detected:\n" + "\n".join(lines))
