## Installation

Add the following to your .pre-commit-config.yaml file:

```yml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v0.1.6  # todo: version
    hooks:
      - id: boa-restrictor
        args: [ --config=pyproject.toml ]
```

Now you can run the linter manually:

    pre-commit run --all-files boa-restrictor

# todo: add rules and example output
