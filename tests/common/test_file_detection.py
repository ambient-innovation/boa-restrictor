from pathlib import Path

from boa_restrictor.common.file_detection import is_layer_file, is_test_file


def test_is_layer_file_inside_layer_dir():
    assert is_layer_file(Path("apps/services/foo.py"), layer="services") is True


def test_is_layer_file_named_like_layer():
    assert is_layer_file(Path("apps/myapp/services.py"), layer="services") is True


def test_is_layer_file_unrelated_path():
    assert is_layer_file(Path("apps/myapp/views_helper.py"), layer="services") is False


def test_is_layer_file_does_not_match_absolute_ancestor_dirs(tmp_path, monkeypatch):
    # Regression: the layer name appears only in an ancestor directory of the checkout, not in the
    # repo-relative path pre-commit passes. Resolving to the absolute path used to match it and flag
    # every file in the repo; it must NOT match.
    checkout = tmp_path / "services" / "myproject"
    checkout.mkdir(parents=True)
    monkeypatch.chdir(checkout)

    assert is_layer_file(Path("myapp/foo.py"), layer="services") is False


def test_is_test_file_test_file_in_test_dir():
    assert is_test_file(Path("path/to/tests/test_file.py")) is True


def test_is_test_file_test_file_but_not_test_dir():
    assert is_test_file(Path("path/to/code/test_file.py")) is False


def test_is_test_file_no_test_file_in_test_dir():
    assert is_test_file(Path("path/to/tests/mixins.py")) is False


def test_is_test_file_test_file_in_test_dir_but_not_py():
    assert is_test_file(Path("path/to/tests/test_file.md")) is False
