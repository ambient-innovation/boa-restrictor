import ast

from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

# Base classes whose subclasses are value objects / enums / exceptions and therefore not services.
EXCLUDED_BASE_NAMES = frozenset(
    {
        "Enum",
        "IntEnum",
        "IntFlag",
        "Flag",
        "StrEnum",
        "Choices",
        "TextChoices",
        "IntegerChoices",
        "Exception",
        "BaseException",
        "TypedDict",
        "NamedTuple",
        "Protocol",
    }
)
# Decorators that turn a class into a data container rather than a service.
EXCLUDED_DECORATOR_NAMES = frozenset({"dataclass"})


class ServiceClassNameRule(Rule):
    """
    Ensures that top-level classes living in the service layer are named with a "Service" suffix, so the
    service classes are easy to recognise. Enums, dataclasses, typed dicts and exceptions are exempt.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}011"
    RULE_LABEL = 'Classes in the service layer must be named with a "Service" suffix.'

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_layer_file(self.file_path, layer="services"):
            return occurrences

        # Only top-level classes are checked; nested helper classes (e.g. Meta) are ignored.
        for node in ast.iter_child_nodes(self.source_tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name.endswith("Service"):
                continue
            if self._is_excluded(node):
                continue

            occurrences.append(
                Occurrence(
                    filename=self.filename,
                    file_path=self.file_path,
                    rule_label=self.RULE_LABEL,
                    rule_id=self.RULE_ID,
                    line_number=node.lineno,
                    identifier=node.name,
                )
            )

        return occurrences

    @classmethod
    def _is_excluded(cls, node: ast.ClassDef) -> bool:
        if node.name.endswith(("Error", "Exception")):
            return True
        if any(cls._node_name(decorator) in EXCLUDED_DECORATOR_NAMES for decorator in node.decorator_list):
            return True
        return any(cls._node_name(base) in EXCLUDED_BASE_NAMES for base in node.bases)

    @staticmethod
    def _node_name(node) -> str | None:
        # Unwrap "@decorator(...)" to the decorator itself.
        if isinstance(node, ast.Call):
            node = node.func
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None
