# Configuration

## Exclude certain files

You can easily exclude certain files, for example, your tests, by using the `exclude` parameter from `pre-commit`:

```yaml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v{{ version }}
    hooks:
      - id: boa-restrictor
        ...
        exclude: |
          (?x)^(
            /.*/tests/.*
            |.*/test_.*\.py
          )$
```

## Globally exclude configuration rule

You can disable any rule in your `pyproject.toml` file as follows:

```toml
[tool.boa-restrictor]
exclude = [
    "PBR001",
    "PBR002",
]
```

## Disable Django rules

You can disable Django-specific rules by setting `enable_django_rules` to `false`.

```toml
[tool.boa-restrictor]
enable_django_rules = false
```

## Per-file exclusion of configuration rule

You can disable rules on a per-file-basis in your `pyproject.toml` file as follows:

```toml
[tool.boa-restrictor.per-file-excludes]
"*/tests/*.py" = [
    "PBR001",
    "PBR002",
]
"scripts/*.py" = [
    "DBR001",
]
"*/my_app/*.py" = [
    "PBR003",
]
```

Take care that the path is relative to the location of your pyproject.toml. This means that example two targets all
files living in a `scripts/` directory on the projects top level.

## Project-specific (custom) rules

You can register your own rule classes alongside the built-in ones by listing them in your `pyproject.toml`:

```toml
[tool.boa-restrictor]
custom_rules = [
    "myproject.linting.NoFooBarRule",
    "myproject.linting.RequireBazRule",
]
```

Each entry is a dotted import path to a class that subclasses
`boa_restrictor.common.rule.Rule` and sets a `RULE_ID` and `RULE_LABEL`. A minimal example:

```python
import ast

from boa_restrictor.common.rule import Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoFooBarRule(Rule):
    RULE_ID = "MYP001"
    RULE_LABEL = 'Functions must not be named "foo_bar".'

    def check(self) -> list[Occurrence]:
        occurrences = []
        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.FunctionDef) and node.name == "foo_bar":
                occurrences.append(
                    Occurrence(
                        rule_id=self.RULE_ID,
                        rule_label=self.RULE_LABEL,
                        filename=self.filename,
                        file_path=self.file_path,
                        identifier=node.name,
                        line_number=node.lineno,
                    )
                )
        return occurrences
```

Custom rules participate in the same exclusion mechanisms as the built-ins
(`exclude`, `per-file-excludes`, and `# noqa: <rule_id>`).

### Rule ID requirements

* The `PBR` and `DBR` prefixes are reserved for built-in rules. Pick any other prefix.
* Every loaded rule must have a unique `RULE_ID`. Duplicate IDs (within your custom rules,
  or against a built-in) abort the run with an error naming both classes.
* Validation is eager: a misconfigured `custom_rules` entry fails the run before any file is linted.
* If a custom rule raises during `check()`, the linting run halts. Treat exceptions inside
  `check()` as bugs in your rule.

### Running custom rules under pre-commit

Custom rules need your project's modules to be importable when boa-restrictor runs. The standard
pre-commit hook installs boa-restrictor into an isolated virtualenv that does **not** see your
project code, so you have two options:

**Option A — `language: system` (simplest).** boa-restrictor runs in the environment you've installed
it into (typically your project venv). You lose pre-commit's automatic version management — pin
boa-restrictor in your dev requirements instead.

```yaml
  - repo: local
    hooks:
      - id: boa-restrictor
        name: boa-restrictor
        entry: boa-restrictor
        language: system
        types: [python]
        args: [--config=pyproject.toml]
```

**Option B — `additional_dependencies` (preferable if your project is pip-installable).** Keeps
pre-commit's hermetic environment and installs your package into the hook's venv.

```yaml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v{{ version }}
    hooks:
      - id: boa-restrictor
        args: [--config=pyproject.toml]
        additional_dependencies: [".", "boa-restrictor"]
```

### Trust model

Listing a path under `custom_rules` causes boa-restrictor to **import and execute** the named
module at lint time. boa-restrictor does not sandbox imported rule modules. Only point this at
code you trust. If you run boa-restrictor against contributors' branches in CI (e.g. PRs from
forks), assume that whoever can edit `pyproject.toml` can run arbitrary code in your CI
environment.

### Common gotcha: Django imports at module top-level

boa-restrictor does not bootstrap Django before importing your custom rule modules. If your rule
needs anything from `django.conf` / `django.db` / etc., import it inside `check()`, not at module
scope, or you will see `ImproperlyConfigured` errors during loading.

## Python version compatibility

boa-restrictor uses Python's built-in `ast.parse()` to analyze your source code. This means the Python version
running boa-restrictor must support all syntax used in the files being linted.

For example, Python 3.14 introduced unparenthesized multiple exception types (`except TypeError, ValueError:`).
If your code uses this syntax but boa-restrictor runs on Python 3.13 or earlier, parsing will fail with a
`SyntaxError`.

**Solution:** Run boa-restrictor with a Python version that matches (or exceeds) the version your code targets.

In pre-commit, you can pin the Python version with `language_version`:

```yaml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v{{ version }}
    hooks:
      - id: boa-restrictor
        language_version: python3.14
```

## noqa & ruff support

As any other linter, you can disable certain rules on a per-line basis with `#noqa`.

````python
def function_with_args(arg1, arg2):  # noqa: PBR001
    ...
````

If you are using `ruff`, you need to tell it about our linting rules. Otherwise, ruff will remove all `# noqa`
statements from your codebase.

```toml
[tool.ruff.lint]
# Avoiding flagging (and removing) any codes starting with `PBR` from any
# `# noqa` directives, despite Ruff's lack of support for `boa-restrictor`.
external = ["PBR", "DBR"]
```

https://docs.astral.sh/ruff/settings/#lint_extend-unsafe-fixes
