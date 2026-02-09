import sys


class BoaRestrictorParsingError(SyntaxError):
    def __init__(self, filename: str):
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        super().__init__(
            f'Source code of file "{filename}" contains syntax errors. '
            f"Note: boa-restrictor uses Python {python_version}'s built-in parser. "
            f"If your code targets a newer Python version, run boa-restrictor with that version."
        )
