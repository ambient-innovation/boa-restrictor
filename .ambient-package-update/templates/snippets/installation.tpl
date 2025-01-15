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
