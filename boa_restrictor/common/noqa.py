import re
import tokenize
from io import StringIO

from boa_restrictor.common.rule import LINTING_RULE_PREFIX


def get_noqa_comments(*, source_code: str) -> list[tuple[int, str]]:
    """
    Walk the target code and detect all lines having a "# noqa" comment with "our" prefix.
    """
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    pattern = re.compile(r"^#\snoqa:\s*.*?" + LINTING_RULE_PREFIX + r"\d{3}")

    for token in tokens:
        token_type, token_string, start, _, _ = token

        if token_type == tokenize.COMMENT and pattern.search(token_string):
            noqa_statements.append((start[0], token_string.strip()))

    return noqa_statements
