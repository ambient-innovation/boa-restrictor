from pathlib import Path


def is_layer_file(path: Path, *, layer: str) -> bool:
    """
    Returns whether the given file belongs to the named architectural layer, either by being named
    "<layer>.py" or by living inside a "<layer>" directory.

    Matching is done on the path as passed (pre-commit hands us repo-relative paths). We deliberately do
    NOT resolve to an absolute path: doing so would match any ancestor directory of the checkout that happens
    to be named like a layer (e.g. a project living under ".../services/"), flagging every file in the repo.
    """
    return path.name == f"{layer}.py" or layer in path.parts


def is_test_file(path: Path) -> bool:
    """
    Returns whether the given file is a unit-test module (named "test_*.py" inside a "tests" directory).
    """
    return any(part == "tests" for part in path.parts) and path.name.startswith("test_") and path.name.endswith(".py")
