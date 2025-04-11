import ast

from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ServiceClassHasOnlyOnePublicMethodRule(Rule):
    """
    Checks if service class, which is defined by ending on "Service" has only one public method called "process".
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}005"
    RULE_LABEL = 'Service classes must have exactly one public method named "process".'

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name.endswith("Service"):
                public_methods = []

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Check method names
                        if not item.name.startswith("_"):
                            public_methods.append(item.name)

                # Check whether the only public method is 'process'
                if public_methods != ["process"]:
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
