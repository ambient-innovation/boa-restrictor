import dataclasses
from typing import Optional


# TODO: Add kw_only when we drop Python 3.9 support
@dataclasses.dataclass
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str
    identifier: Optional[str]
    line_number: int
