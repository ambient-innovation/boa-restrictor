from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX
from boa_restrictor.rules.django.no_db_in_layer import NoDjangoDbImportInLayerRule


class NoDjangoDbImportInViewsRule(NoDjangoDbImportInLayerRule):
    """
    Ensures that no Django low-level database functionality is imported and therefore used in the view layer.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}002"
    RULE_LABEL = 'Do not use "django.db" in the view layer. Move it to a manager instead.'
    LAYER = "views"
