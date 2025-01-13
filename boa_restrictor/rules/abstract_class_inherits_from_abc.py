import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AbstractClassesInheritFromAbcRule(Rule):
    """
    Checks if classes having "abstract" in their name inherit from Pythons "abstract base class".
    """

    RULE_ID = f"{LINTING_RULE_PREFIX}006"
    RULE_LABEL = 'Abstract classes have to inherit from "abc.ABC".'

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if "abstract" in node.name.lower():
                # Check whether the class inherits from `ABC`
                inherits_abc = any(self.is_abc(base=base) for base in node.bases)
                uses_abcmeta = self.has_abcmeta(node=node)

                if not (inherits_abc or uses_abcmeta):
                    occurrences.append(
                        Occurrence(
                            rule_id=self.RULE_ID,
                            rule_label=self.RULE_LABEL,
                            filename=self.filename,
                            identifier=node.name,
                            line_number=node.lineno,
                        )
                    )

        return occurrences

    def is_abc(self, *, base) -> bool:
        """
        Checks whether a given base class is `ABC`.
        """
        if isinstance(base, ast.Name):
            # Direkte Referenz (z. B. `ABC`)
            return base.id == "ABC"
        elif isinstance(base, ast.Attribute):
            # Modul-Attribut (z. B. `abc.ABC`)
            return base.attr == "ABC"
        return False

    def has_abcmeta(self, *, node) -> bool:
        """
        Checks whether the class `ABCMeta` is used as a metaclass.
        """
        for keyword in node.keywords:
            if keyword.arg == "metaclass":
                if isinstance(keyword.value, ast.Name):
                    return keyword.value.id == "ABCMeta"
                elif isinstance(keyword.value, ast.Attribute):
                    return keyword.value.attr == "ABCMeta"
        return False
