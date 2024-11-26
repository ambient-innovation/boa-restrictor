import dataclasses


@dataclasses.dataclass
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str
    function_name: str
    line_number: int
