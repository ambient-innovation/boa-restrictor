from boa_restrictor.common.django_db import find_django_db_import_line_numbers
from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoDjangoDbImportInLayerRule(Rule):
    """
    Base rule prohibiting "django.db" imports in a specific architectural layer. Concrete subclasses declare
    only RULE_ID, RULE_LABEL and the LAYER they guard. Imports for type-checking purposes are allowed.
    """

    LAYER: str

    def check(self) -> list[Occurrence]:
        if not is_layer_file(self.file_path, layer=self.LAYER):
            return []

        return [
            self._build_occurrence(line_number=line_number)
            for line_number in find_django_db_import_line_numbers(self.source_tree)
        ]
