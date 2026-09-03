import ast

from boa_restrictor.common.ast_utils import index_classes_by_name, is_fixture, is_test_function, resolve_class


def _function_node(source: str):
    return ast.parse(source).body[0]


def test_plain_test_function_is_test_function():
    node = _function_node("""def test_something():
    pass""")

    assert is_test_function(node) is True


def test_async_test_function_is_test_function():
    node = _function_node("""async def test_something():
    pass""")

    assert is_test_function(node) is True


def test_non_test_function_is_not_test_function():
    node = _function_node("""def helper():
    pass""")

    assert is_test_function(node) is False


def test_pytest_fixture_is_not_test_function():
    node = _function_node("""@pytest.fixture
def test_client():
    return Client()""")

    assert is_test_function(node) is False


def test_parametrized_pytest_fixture_is_not_test_function():
    node = _function_node("""@pytest.fixture(scope="module")
def test_client():
    return Client()""")

    assert is_test_function(node) is False


def test_directly_imported_fixture_is_not_test_function():
    node = _function_node("""@fixture
def test_data():
    return {}""")

    assert is_test_function(node) is False


def test_non_fixture_decorator_stays_test_function():
    node = _function_node("""@pytest.mark.django_db
def test_something():
    pass""")

    assert is_test_function(node) is True


def test_non_function_node_is_not_test_function():
    node = ast.parse("x = 1").body[0]

    assert is_test_function(node) is False


def test_pytest_fixture_is_fixture():
    node = _function_node("""@pytest.fixture
def some_fixture():
    return object()""")

    assert is_fixture(node) is True


def test_undecorated_function_is_not_fixture():
    node = _function_node("""def some_function():
    return object()""")

    assert is_fixture(node) is False


def test_non_function_node_is_not_fixture():
    node = ast.parse("x = 1").body[0]

    assert is_fixture(node) is False


def test_index_classes_by_name_covers_nested_classes():
    source_tree = ast.parse("""class Outer:
    class Inner:
        pass


class Other:
    pass""")

    classes_by_name = index_classes_by_name(source_tree)

    assert set(classes_by_name) == {"Outer", "Inner", "Other"}


def test_index_classes_by_name_keeps_the_last_definition():
    source_tree = ast.parse("""class Duplicate:
    first = 1


class Duplicate:
    second = 2""")

    classes_by_name = index_classes_by_name(source_tree)

    assert classes_by_name["Duplicate"] is source_tree.body[1]


def test_resolve_class_finds_a_class_by_bare_name():
    source_tree = ast.parse("""class CommonInfo:
    pass


class Invoice(CommonInfo):
    pass""")
    classes_by_name = index_classes_by_name(source_tree)

    assert resolve_class(source_tree.body[1].bases[0], classes_by_name) is source_tree.body[0]


def test_resolve_class_without_a_matching_class():
    source_tree = ast.parse("""class Invoice(CommonInfo):
    pass""")

    assert resolve_class(source_tree.body[0].bases[0], {}) is None


def test_resolve_class_with_an_unnamed_node():
    source_tree = ast.parse("""class Invoice(bases[0]):
    pass""")

    assert resolve_class(source_tree.body[0].bases[0], {}) is None
