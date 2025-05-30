[![PyPI release](https://img.shields.io/pypi/v/boa-restrictor.svg)](https://pypi.org/project/boa-restrictor/)
[![Downloads](https://static.pepy.tech/badge/boa-restrictor)](https://pepy.tech/project/boa-restrictor)
[![Coverage](https://img.shields.io/badge/Coverage-100.0%25-success)](https://github.com/ambient-innovation/boa-restrictor/actions?workflow=CI)
[![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coding Style](https://img.shields.io/badge/code%20style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/boa-restrictor/badge/?version=latest)](https://boa-restrictor.readthedocs.io/en/latest/?badge=latest)

Welcome to the **boa-restrictor** - a custom Python linter from Ambient

* [PyPI](https://pypi.org/project/boa-restrictor/)
* [GitHub](https://github.com/ambient-innovation/boa-restrictor)
* [Full documentation](https://boa-restrictor.readthedocs.io/en/latest/index.html)
* Creator & Maintainer: [Ambient Digital](https://ambient.digital/)




## Installation

Add the following to your .pre-commit-config.yaml file:

```yaml
  - repo: https://github.com/ambient-innovation/boa-restrictor
    rev: v1.7.3
    hooks:
      - id: boa-restrictor
        args: [ --config=pyproject.toml ]
```

Now you can run the linter manually:

    pre-commit run --all-files boa-restrictor

### Publish to ReadTheDocs.io

- Fetch the latest changes in GitHub mirror and push them
- Trigger new build at ReadTheDocs.io (follow instructions in admin panel at RTD) if the GitHub webhook is not yet set
  up.

### Publish to PyPi

- Update documentation about new/changed functionality

- Update the `Changelog`

- Increment version in main `__init__.py`

- Create pull request / merge to main

- This project uses the flit package to publish to PyPI. Thus, publishing should be as easy as running:
  ```
  flit publish
  ```

  To publish to TestPyPI use the following to ensure that you have set up your .pypirc as
  shown [here](https://flit.readthedocs.io/en/latest/upload.html#using-pypirc) and use the following command:

  ```
  flit publish --repository testpypi
  ```

### Create new version for pre-commit

To be able to use the latest version in pre-commit, you have to create a git tag for the current commit.
So please tag your commit and push it to GitHub.

### Maintenance

Please note that this package supports the [ambient-package-update](https://pypi.org/project/ambient-package-update/).
So you don't have to worry about the maintenance of this package. This updater is rendering all important
configuration and setup files. It works similar to well-known updaters like `pyupgrade` or `django-upgrade`.

To run an update, refer to the [documentation page](https://pypi.org/project/ambient-package-update/)
of the "ambient-package-update".
