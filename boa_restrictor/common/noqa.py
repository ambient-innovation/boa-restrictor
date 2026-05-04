import re
import tokenize
from io import StringIO

# Matches any "# noqa: <CODE>" comment regardless of rule prefix. The per-rule filter
# (rule_class.RULE_ID in comment_string) in main.py decides which comments apply to which rule,
# so this pattern stays permissive to support custom (project-defined) rule IDs.
_NOQA_PATTERN = re.compile(r"^#\snoqa:\s*\S")


def get_noqa_comments(*, source_code: str) -> list[tuple[int, str]]:
    """
    Walk the target code and detect all lines having a "# noqa: <CODE>" comment.
    """
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    for token in tokens:
        token_type, token_string, start, _, _ = token
        if token_type == tokenize.COMMENT and _NOQA_PATTERN.search(token_string):
            noqa_statements.append((start[0], token_string.strip()))

    return noqa_statements
