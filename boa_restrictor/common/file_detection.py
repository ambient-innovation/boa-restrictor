from pathlib import Path


def is_layer_file(path: Path, *, layer: str) -> bool:
    """
    Returns whether the given file belongs to the named architectural layer, either by being named
    "<layer>.py" or by living inside a "<layer>" directory.
    """
    path = path.resolve()

    if path.name == f"{layer}.py":
        return True

    return layer in path.parts


def is_test_file(path: Path) -> bool:
    """
    Returns whether the given file is a unit-test module (named "test_*.py" inside a "tests" directory).
    """
    return any(part == "tests" for part in path.parts) and path.name.startswith("test_") and path.name.endswith(".py")
