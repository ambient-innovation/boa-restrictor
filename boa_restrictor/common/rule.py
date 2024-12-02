from boa_restrictor.projections.occurrence import Occurrence

LINTING_RULE_PREFIX = "PBR"


class Rule:
    RULE_ID: str
    RULE_LABEL: str

    filename: str
    source_code: str

    @classmethod
    def run_check(cls, *, filename: str, source_code: str) -> list[Occurrence]:
        instance = cls(filename=filename, source_code=source_code)
        return instance.check()

    def __init__(self, *, filename: str, source_code: str):
        """
        A rule is called via pre-commit for a specific file.
        Variable `source_code` is the content of the given file.
        """
        super().__init__()

        self.filename = filename
        self.source_code = source_code

    def check(self) -> list[Occurrence]:
        raise NotImplementedError
