import pytest

from boa_restrictor.common.noqa import get_noqa_comments
from boa_restrictor.exceptions.syntax_errors import BoaRestrictorParsingError


def test_get_noqa_comments_has_pbr_noqa():
    source_code = """x = 7  # noqa: PBR001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_has_dbr_noqa():
    source_code = """from django.db.models import QuerySet  # noqa: DBR002"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"DBR002"})


def test_get_noqa_comments_no_noqa_comment():
    source_code = """x = 7  # Great!"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_has_custom_rule_noqa():
    """Custom (project-defined) rule IDs should be picked up too."""
    source_code = """x = 7  # noqa: TST001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"TST001"})


def test_get_noqa_comments_ignores_bare_noqa_keyword():
    """A # noqa with no code following should not be collected (we do not support a global noqa)."""
    source_code = """x = 7  # noqa"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_parses_multiple_codes_comma_separated():
    source_code = """x = 7  # noqa: PBR001, F401"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001", "F401"})


def test_get_noqa_comments_parses_multiple_codes_space_separated():
    source_code = """x = 7  # noqa: PBR001 F401"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001", "F401"})


def test_get_noqa_comments_codes_are_exact_not_substrings():
    """Regression: # noqa: TST0011 must NOT be parsed as also containing TST001."""
    source_code = """x = 7  # noqa: TST0011"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"TST0011"})
    assert "TST001" not in result[0][1]


def test_get_noqa_comments_separator_only_input_yields_no_codes():
    """A noqa with only commas after the colon should not register as a directive."""
    source_code = """x = 7  # noqa: ,,,"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_whitespace_only_after_colon_yields_no_codes():
    """A noqa with only whitespace after the colon must not match (no codes to silence)."""
    source_code = "x = 7  # noqa:    "

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_ignores_prose_tokens_after_codes():
    """Prose tokens in the noqa payload (not matching the rule-code shape) must be ignored."""
    source_code = """x = 7  # noqa: PBR001 explanation here"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_ignores_inline_second_hash():
    """A second '#' (e.g. trailing comment) must not become a phantom code."""
    source_code = """x = 7  # noqa: PBR001 # leftover note"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_directive_after_another_pragma():
    """Combined inline pragmas like `# type: ignore # noqa: PBR001` must still register."""
    source_code = """x = 7  # type: ignore  # noqa: PBR001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_uppercase_noqa_directive():
    """Ruff/flake8 accept '# NOQA:' (uppercase). We should too."""
    source_code = """x = 7  # NOQA: PBR001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_no_space_around_directive():
    """Tolerate '#noqa:' without a space and no space before the colon."""
    source_code = """x = 7  #noqa:PBR001"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_codes_outside_directive_are_ignored():
    """A code-shaped token in a comment without a noqa directive must NOT be treated as a code."""
    source_code = """x = 7  # see ticket PBR001 for details"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 0


def test_get_noqa_comments_codes_before_directive_are_ignored():
    """Code-shaped tokens in prose BEFORE the noqa directive must not be silenced."""
    source_code = """x = 7  # fixes PBR001 ticket  # noqa: PBR002"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR002"})


def test_get_noqa_comments_codes_in_leftover_note_are_ignored():
    """Code-shaped tokens in a trailing note after a second '#' must not be silenced."""
    source_code = """x = 7  # noqa: PBR001  # also see PBR777"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR001"})


def test_get_noqa_comments_codes_in_other_pragma_are_ignored():
    """Code-shaped tokens inside another inline pragma before noqa must not be silenced."""
    source_code = """x = 7  # type: ignore[PBR999]  # noqa: PBR002"""

    result = get_noqa_comments(source_code=source_code)

    assert len(result) == 1
    assert result[0] == (1, {"PBR002"})


def test_get_noqa_comments_tokenize_error_is_reframed():
    """A TokenizeError (e.g. unterminated triple-quoted string) must surface as the
    user-friendly BoaRestrictorParsingError, not a raw tokenize crash."""
    source_code = 'x = """unterminated\n'

    with pytest.raises(BoaRestrictorParsingError) as exc_info:
        get_noqa_comments(source_code=source_code, filename="broken.py")

    assert "broken.py" in str(exc_info.value)
