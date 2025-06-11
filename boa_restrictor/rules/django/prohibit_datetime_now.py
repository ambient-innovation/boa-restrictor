import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ProhibitDatetimeNow(Rule):
    """
    Prohibit the usage of "datetime.now()" in favour of "django.utils.timezone.now()".
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}004"
    RULE_LABEL = 'Do not use "datetime.now()". Use "django.utils.timezone.now()" instead.'

    def check(self) -> list[Occurrence]:  # noqa: C901
        occurrences = []

        imports = {}
        for node in ast.walk(self.source_tree):
            # Collect import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name

            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    imports[alias.asname or alias.name] = full_name

        # Iterate source tree again to find all matches
        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.Call):
                parts = []
                func = node.func

                # Reconstruct fully qualified name of the function call
                while isinstance(func, ast.Attribute):
                    parts.insert(0, func.attr)
                    func = func.value
                if isinstance(func, ast.Name):  # pragma: no cover (this "False" case seems to be invalid Python
                    parts.insert(0, func.id)
                    root = imports.get(parts[0], parts[0])
                    parts[0] = root

                full_call = ".".join(parts)

                if full_call in ("datetime.datetime.now", "datetime.now", "datetime.now"):
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            file_path=self.file_path,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=None,
                        )
                    )

        return occurrences
