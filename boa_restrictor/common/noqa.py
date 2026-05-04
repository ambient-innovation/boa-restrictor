import re
import tokenize
from io import StringIO

# Matches a noqa directive comment; requires at least one non-whitespace char after the colon.
_NOQA_PATTERN = re.compile(r"^#\snoqa:\s*\S")
# Rule code pattern: 1+ uppercase letters followed by 1+ digits (e.g. PBR001, DBR007, TST0011, F401).
# Anything in the noqa payload that doesn't match this is ignored (prose, stray punctuation, ...).
_CODE_PATTERN = re.compile(r"\b[A-Z]+\d+\b")


def get_noqa_comments(*, source_code: str) -> list[tuple[int, set[str]]]:
    """
    Walk the target code and collect all "# noqa: <CODE[, ...]>" comments,
    returning each as (line_number, set_of_exact_rule_ids).

    Rule IDs are matched exactly downstream, so:
      - "# noqa: TST0011" does NOT suppress rule TST001 (substring guard).
      - "# noqa: PBR001 explanation here" yields just {"PBR001"} — prose tokens
        are ignored because they don't match the rule-code shape.
    """
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for token in tokens:
        token_type, token_string, start, _, _ = token
        if token_type != tokenize.COMMENT:
            continue
        stripped = token_string.strip()
        if not _NOQA_PATTERN.match(stripped):
            continue
        codes = set(_CODE_PATTERN.findall(stripped))
        if codes:
            noqa_statements.append((start[0], codes))

    return noqa_statements
