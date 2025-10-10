import dataclasses
from pathlib import Path


# TODO: Add kw_only when we drop Python 3.9 support
@dataclasses.dataclass
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str
    file_path: Path
    identifier: str | None
    line_number: int
