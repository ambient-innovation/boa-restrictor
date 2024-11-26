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
        return instance.check(source_code=source_code)

    def __init__(self, *, filename: str, source_code: str):
        super().__init__()

        self.filename = filename
        self.source_code = source_code

    def check(self, *, source_code: str) -> list[Occurrence]:
        raise NotImplementedError
