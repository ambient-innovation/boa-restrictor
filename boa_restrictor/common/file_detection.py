from pathlib import Path


def is_layer_file(path: Path, *, layer: str) -> bool:
    """
    Returns whether the given file belongs to the named architectural layer, either by being named
    "<layer>.py" or by living inside a "<layer>" directory.
    """
    if path.name == f"{layer}.py" or layer in path.parts:
        return True

    # Fall back to the resolved (absolute) path so a relative path inside a "<layer>" directory still matches.
    return layer in path.resolve().parts


def is_test_file(path: Path) -> bool:
    """
    Returns whether the given file is a unit-test module (named "test_*.py" inside a "tests" directory).
    """
    return any(part == "tests" for part in path.parts) and path.name.startswith("test_") and path.name.endswith(".py")
