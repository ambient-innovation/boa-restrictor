class BoaRestrictorParsingError(SyntaxError):
    def __init__(self, filename: str):
        super().__init__(f'Source code of file "{filename}" contains syntax errors.')
