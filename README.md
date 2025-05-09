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
    rev: v1.7.0
    hooks:
      - id: boa-restrictor
        args: [ --config=pyproject.toml ]
```

Now you can run the linter manually:

    pre-commit run --all-files boa-restrictor

## Contribute

### Setup package for development

- Create a Python virtualenv and activate it
- Install "pip-tools" with `pip install -U pip-tools`
- Compile the requirements with `pip-compile --extra dev, -o requirements.txt pyproject.toml --resolver=backtracking`
- Sync the dependencies with your virtualenv with `pip-sync`

### Add functionality

- Create a new branch for your feature
- Change the dependency in your requirements.txt to a local (editable) one that points to your local file system:
  `-e /Users/workspace/boa-restrictor` or via pip  `pip install -e /Users/workspace/boa-restrictor`
- Ensure the code passes the tests
- Create a pull request

### Run tests

- Run tests
  ````
  pytest --ds settings tests
  ````

- Check coverage
  ````
  coverage run -m pytest tests
  coverage report -m
  ````

### Git hooks (via pre-commit)

We use pre-push hooks to ensure that only linted code reaches our remote repository and pipelines aren't triggered in
vain.

To enable the configured pre-push hooks, you need to [install](https://pre-commit.com/) pre-commit and run once:

    pre-commit install -t pre-push -t pre-commit --install-hooks

This will permanently install the git hooks for both, frontend and backend, in your local
[`.git/hooks`](./.git/hooks) folder.
The hooks are configured in the [`.pre-commit-config.yaml`](templates/.pre-commit-config.yaml.tpl).

You can check whether hooks work as intended using the [run](https://pre-commit.com/#pre-commit-run) command:

    pre-commit run [hook-id] [options]

Example: run single hook

    pre-commit run ruff --all-files

Example: run all hooks of pre-push stage

    pre-commit run --all-files --hook-stage push

### Update documentation

- To build the documentation, run: `sphinx-build docs/ docs/_build/html/`.
- Open `docs/_build/html/index.html` to see the documentation.



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

