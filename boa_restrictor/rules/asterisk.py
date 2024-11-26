import ast

from boa_restrictor.projections.occurrence import Occurrence


class AsteriskRequiredRule:
    RULE_ID = "BR001"
    RULE_LABEL = "Positional arguments in functions and methods are discouraged. Add an \"*\" as the first argument."

    filename: str

    @classmethod
    def run_check(cls, filename: str):
        instance = cls(filename=filename)
        with open(filename, "r") as f:
            return instance.check(f.read())

    def __init__(self, filename: str):
        super().__init__()

        self.filename = filename

    def _missing_asterisk(self, node):
        """
        Prüft, ob die Funktion oder Methode einen `*` verwendet,
        um Positionsargumente zu verbieten und nur kwargs zu erlauben.
        """
        for arg in node.args.args:  # Normale Positionsargumente
            if isinstance(arg, ast.arg):
                return True

        for default in node.args.defaults:  # Standardwerte für args
            if default is not None:
                return True

        return False

    def check(self, source_code: str):
        """
        Prüft, ob alle Funktionen in dem angegebenen Python-Quellcode einen `*` in den Parametern enthalten,
        um zu gewährleisten, dass sie nur mit benannten Argumenten aufgerufen werden können.

        :param source_code: Der zu analysierende Python-Quellcode als String.
        :return: Eine Liste mit Informationen zu Funktionen, die keinen `*` in den Parametern enthalten.
        """
        tree = ast.parse(source_code)
        functions_without_star = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if self._missing_asterisk(node=node):
                functions_without_star.append(
                    Occurrence(
                        rule_id=self.RULE_ID,
                        rule_label=self.RULE_LABEL,
                        filename=self.filename,
                        function_name=node.name,
                        line_number=node.lineno,
                    )
                )

        return functions_without_star

# todo
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
#
# a = 7 + 4
# """
