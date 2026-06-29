from boa_restrictor.common.django_db import find_django_db_import_line_numbers
from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoDjangoDbImportInViewsRule(Rule):
    """
    Ensures that no Django low-level database functionality is imported and therefore used in the view layer.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}002"
    RULE_LABEL = 'Do not use "django.db" in the view layer. Move it to a manager instead.'

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_layer_file(self.file_path, layer="views"):
            return occurrences

        for line_number in find_django_db_import_line_numbers(self.source_tree):
            occurrences.append(
                Occurrence(
                    filename=self.filename,
                    file_path=self.file_path,
                    rule_label=self.RULE_LABEL,
                    rule_id=self.RULE_ID,
                    line_number=line_number,
                    identifier=None,
                )
            )

        return occurrences
