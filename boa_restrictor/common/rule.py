import tokenize
from io import StringIO

from boa_restrictor.projections.occurrence import Occurrence

LINTING_RULE_PREFIX = "BR"

class Rule:
    RULE_ID: str
    RULE_LABEL: str

    filename: str

    @classmethod
    def run_check(cls, filename: str):
        instance = cls(filename=filename)
        with open(filename, "r") as f:
            return instance.check(f.read())

    def __init__(self, filename: str):
        super().__init__()

        self.filename = filename

    def check(self, source_code: str) -> list[Occurrence]:
        raise NotImplementedError
