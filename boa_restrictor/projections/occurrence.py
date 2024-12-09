import dataclasses
from typing import Optional


@dataclasses.dataclass
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str
    function_name: Optional[str]
    line_number: int
