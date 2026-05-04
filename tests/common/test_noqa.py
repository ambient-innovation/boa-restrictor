from boa_restrictor.common.noqa import get_noqa_comments


def test_get_noqa_comments_has_pbr_noqa():
    source_code = """x = 7  # noqa: PBR001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert isinstance(result[0], tuple)
    assert result[0][0] == 1
    assert result[0][1] == "# noqa: PBR001"


def test_get_noqa_comments_has_dbr_noqa():
    source_code = """from django.db.models import QuerySet  # noqa: DBR002"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert isinstance(result[0], tuple)
    assert result[0][0] == 1
    assert result[0][1] == "# noqa: DBR002"


def test_get_noqa_comments_no_noqa_comment():
    source_code = """x = 7  # Great!"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_has_custom_rule_noqa():
    """Custom (project-defined) rule IDs should be picked up too."""
    source_code = """x = 7  # noqa: TST001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, "# noqa: TST001")


def test_get_noqa_comments_ignores_bare_noqa_keyword():
    """A # noqa with no code following should not be collected (we do not support a global noqa)."""
    source_code = """x = 7  # noqa"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0
