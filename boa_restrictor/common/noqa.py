import re
import tokenize
from io import StringIO

# Matches a noqa directive anywhere within a comment token, so a noqa following another
# inline pragma still registers. Case-insensitive (accepts uppercase NOQA) and tolerant
# of missing whitespace around the leading hash and the colon.
_NOQA_PATTERN = re.compile(r"#\s*noqa\s*:", re.IGNORECASE)
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

    Only the payload after "# noqa:" (and before any subsequent "#") contributes
    codes, so code-shaped tokens elsewhere in the comment do not silently widen
    the suppression.
    """
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for token in tokens:
        token_type, token_string, start, _, _ = token
        if token_type != tokenize.COMMENT:
            continue
        match = _NOQA_PATTERN.search(token_string)
        if not match:
            continue
        payload = token_string[match.end() :].split("#", 1)[0]
        codes = set(_CODE_PATTERN.findall(payload))
        if codes:
            noqa_statements.append((start[0], codes))

    return noqa_statements
