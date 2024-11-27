## Installation

Add the following to your .pre-commit-config.yaml file:

```yml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v0.1.6  # todo: version
    hooks:
      - id: boa-restrictor
        args: [ --config=pyproject.toml ]
        stages: [ pre-push ]
```

Now you can run the linter manually:

    pre-commit run --all-files --hook-stage push
