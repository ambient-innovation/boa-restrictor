import tomllib
from pathlib import Path


def load_configuration(*, file_path: Path | str = "pyproject.toml") -> dict:
    """
    Load linter configuration from pyproject.toml file.
    """
    file_path = Path.cwd() / file_path
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}

    try:
        return data["tool"]["boa-restrictor"]
    except KeyError:
        return {}
