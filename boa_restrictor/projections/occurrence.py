import dataclasses
from typing import Optional


@dataclasses.dataclass(kw_only=True)
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str
    identifier: Optional[str]
    line_number: int
