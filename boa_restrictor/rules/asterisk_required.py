import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AsteriskRequiredRule(Rule):
    RULE_ID = f"{LINTING_RULE_PREFIX}001"
    RULE_LABEL = 'Positional arguments in functions and methods are discouraged. Add an "*" as the first argument.'

    def _missing_asterisk(self, *, node) -> bool:
        for arg in node.args.args:
            if isinstance(arg, ast.arg):
                return True

        for default in node.args.defaults:
            if default is not None:
                return True

        return False

    def check(self, *, source_code: str) -> list[Occurrence]:
        tree = ast.parse(source_code)
        occurrences = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if self._missing_asterisk(node=node):
                occurrences.append(
                    Occurrence(
                        rule_id=self.RULE_ID,
                        rule_label=self.RULE_LABEL,
                        filename=self.filename,
                        function_name=node.name,
                        line_number=node.lineno,
                    )
                )

        return occurrences


# # Beispiel: Test mit einer Datei
# source_code_example = """
# class MyClass:
#
#     def test_method1_evil(a, b):
#         pass
#
#     def test_method2_good(*, a, b):
#         pass
#
#     def test_method3_good():
#         pass
#
# def test_func1_evil(a, b, c):
#     pass
#
# def test_func2_good(*, a, b, c):
#     pass
#
# async def test_afunc1_evil(a, b, c):
#     pass
#
# async def test_afunc2_good(*, a, b, c):
#     pass
#
# a = 7 + 4
# """
