import dataclasses


@dataclasses.dataclass
class Occurrence:
    rule_id: str
    rule_label: str
    filename: str  # TODO: kann der filename hier raus? ich brauch den ja nur in der main
    function_name: str
    line_number: int
