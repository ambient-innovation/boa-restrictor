import re
import tokenize
from io import StringIO

# Matches a noqa directive comment and captures the whole code list so we can split it.
_NOQA_PATTERN = re.compile(r"^#\snoqa:\s*(\S.*)$")
_CODE_SEPARATOR = re.compile(r"[,\s]+")


def get_noqa_comments(*, source_code: str) -> list[tuple[int, set[str]]]:
    """
    Walk the target code and collect all "# noqa: <CODE[, ...]>" comments,
    returning each as (line_number, set_of_exact_rule_ids).
    Rule IDs are matched exactly downstream, so a substring like "TST001" in
    "# noqa: TST0011" will not falsely suppress a violation.
    """
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for token in tokens:
        token_type, token_string, start, _, _ = token
        if token_type != tokenize.COMMENT:
            continue
        match = _NOQA_PATTERN.match(token_string.strip())
        if not match:
            continue
        codes = {part for part in _CODE_SEPARATOR.split(match.group(1)) if part}
        if codes:
            noqa_statements.append((start[0], codes))

    return noqa_statements
