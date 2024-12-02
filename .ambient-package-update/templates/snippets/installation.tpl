## Installation

Add the following to your .pre-commit-config.yaml file:

```yaml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v{{ version }}
    hooks:
      - id: boa-restrictor
        args: [ --config=pyproject.toml ]
```

Now you can run the linter manually:

    pre-commit run --all-files boa-restrictor


## Configuration

### Exclude certain files

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

### Exclude configuration rule

You can disable any rule in your `pyproject.toml` file as follows:

```toml
[tool.boa-restrictor]
exclude = [
    "PBR001",
    "PBR002",
]
```

### Ruff support

If you are using `ruff`, you need to tell it about our linting rules. Otherwise, ruff will remove all `# noqa`
statements from your codebase.

```toml
[tool.ruff.lint]
# Avoiding flagging (and removing) any codes starting with `PBR` from any
# `# noqa` directives, despite Ruff's lack of support for `boa-restrictor`.
external = ["PBR"]
```

https://docs.astral.sh/ruff/settings/#lint_extend-unsafe-fixes
