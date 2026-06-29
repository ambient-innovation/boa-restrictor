import ast
from collections.abc import Iterator

from boa_restrictor.common.ast_utils import node_name
from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

# Django model fields that create a reverse relation and therefore should declare an explicit related_name.
RELATION_FIELDS = frozenset({"ForeignKey", "OneToOneField", "ManyToManyField"})


class RelatedNameRequiredRule(Rule):
    """
    Ensures that relational model fields (ForeignKey, OneToOneField, ManyToManyField) declare an explicit
    "related_name". Relying on the auto-generated default ("<model>_set") makes reverse accessors implicit and
    easy to break when a model is renamed.

    Models whose effective "Meta" declares a "default_related_name" are exempt: Django then derives explicit
    reverse accessors for every relation on that model, which is exactly what this rule wants to enforce. The
    "Meta" is resolved through inheritance as far as the current file allows -- i.e. abstract base models and
    base "Meta" classes defined in the same file are honoured. A "default_related_name" inherited from a base
    defined in another file cannot be seen (the linter processes one file at a time) and must be silenced with
    "# noqa: DBR012" if needed.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}012"
    RULE_LABEL = 'Relational model fields must declare an explicit "related_name".'

    def check(self) -> list[Occurrence]:
        occurrences = []

        # Migrations are generated and out of the developer's hands, so they are exempt.
        if is_layer_file(self.file_path, layer="migrations"):
            return occurrences

        # Index every class in the file by name so base classes can be resolved during Meta inheritance.
        classes_by_name = {node.name: node for node in ast.walk(self.source_tree) if isinstance(node, ast.ClassDef)}

        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # A default_related_name on the model's (effective) Meta makes every reverse accessor explicit.
            if self._model_provides_default_related_name(node, classes_by_name):
                continue

            for call in self._relation_field_calls(node):
                field_name = node_name(call.func)
                if field_name not in RELATION_FIELDS:
                    continue

                keyword_names = {keyword.arg for keyword in call.keywords}
                # A "**kwargs" spread (arg is None) could contain related_name; don't flag what we can't see.
                if None in keyword_names:
                    continue
                if "related_name" in keyword_names:
                    continue

                occurrences.append(self._build_occurrence(line_number=call.lineno, identifier=field_name))

        return occurrences

    @classmethod
    def _model_provides_default_related_name(
        cls, model_class: ast.ClassDef, classes_by_name: dict[str, ast.ClassDef], _seen: set[int] | None = None
    ) -> bool:
        _seen = set() if _seen is None else _seen
        if id(model_class) in _seen:
            return False
        _seen.add(id(model_class))

        meta = cls._find_meta(model_class)
        if meta is not None:
            # A model with its own Meta uses exactly that Meta; inheritance only applies if it subclasses one.
            return cls._meta_provides_default_related_name(meta, classes_by_name, _seen)

        # Without its own Meta, an (abstract) base model's Meta is inherited wholesale -- follow the bases.
        for base in model_class.bases:
            base_class = cls._resolve_class(base, classes_by_name)
            if base_class is not None and cls._model_provides_default_related_name(base_class, classes_by_name, _seen):
                return True
        return False

    @classmethod
    def _meta_provides_default_related_name(
        cls, meta_class: ast.ClassDef, classes_by_name: dict[str, ast.ClassDef], _seen: set[int]
    ) -> bool:
        if cls._sets_default_related_name(meta_class):
            return True

        # "class Meta(Parent.Meta)" or "class Meta(BaseMeta)" inherits the base Meta's options.
        for base in meta_class.bases:
            if isinstance(base, ast.Attribute) and base.attr == "Meta":
                # "Parent.Meta" -> follow the parent model's effective Meta.
                parent_class = cls._resolve_class(base.value, classes_by_name)
                if parent_class is not None and cls._model_provides_default_related_name(
                    parent_class, classes_by_name, _seen
                ):
                    return True
            else:
                # A standalone base Meta class referenced by its bare name.
                base_meta = cls._resolve_class(base, classes_by_name)
                if base_meta is not None and id(base_meta) not in _seen:
                    _seen.add(id(base_meta))
                    if cls._meta_provides_default_related_name(base_meta, classes_by_name, _seen):
                        return True
        return False

    @staticmethod
    def _resolve_class(node, classes_by_name: dict[str, ast.ClassDef]) -> ast.ClassDef | None:
        name = node_name(node)
        return classes_by_name.get(name) if name is not None else None

    @staticmethod
    def _find_meta(class_node: ast.ClassDef) -> ast.ClassDef | None:
        for statement in class_node.body:
            if isinstance(statement, ast.ClassDef) and statement.name == "Meta":
                return statement
        return None

    @staticmethod
    def _sets_default_related_name(class_node: ast.ClassDef) -> bool:
        for statement in class_node.body:
            if isinstance(statement, ast.Assign):
                targets = statement.targets
            elif isinstance(statement, ast.AnnAssign):
                targets = [statement.target]
            else:
                continue
            if any(isinstance(target, ast.Name) and target.id == "default_related_name" for target in targets):
                return True
        return False

    @staticmethod
    def _relation_field_calls(class_node: ast.ClassDef) -> Iterator[ast.Call]:
        # Only inspect fields declared directly on this model. Nested classes (e.g. Meta or inner models)
        # carry their own Meta and are covered by their own ClassDef iteration.
        for statement in class_node.body:
            if isinstance(statement, ast.ClassDef):
                continue
            for node in ast.walk(statement):
                if isinstance(node, ast.Call):
                    yield node
