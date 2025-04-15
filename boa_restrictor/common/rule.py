from _ast import AST
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence

PYTHON_LINTING_RULE_PREFIX = "PBR"
DJANGO_LINTING_RULE_PREFIX = "DBR"


class Rule:
    RULE_ID: str
    RULE_LABEL: str

    file_path: Path
    filename: str
    source_tree: AST

    @classmethod
    def run_check(cls, *, file_path: Path, source_tree: AST) -> list[Occurrence]:
        instance = cls(file_path=file_path, source_tree=source_tree)
        return instance.check()

    def __init__(self, *, file_path: Path, source_tree: AST):
        """
        A rule is called via pre-commit for a specific file.
        Variable `source_code` is the content of the given file.
        """
        super().__init__()

        self.file_path = file_path
        self.source_tree = source_tree

        self.filename = file_path.name

    def check(self) -> list[Occurrence]:
        raise NotImplementedError
