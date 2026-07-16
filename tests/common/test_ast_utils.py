import ast

from boa_restrictor.common.ast_utils import is_fixture, is_test_function


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
