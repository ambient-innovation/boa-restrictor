class TomlParsingError(ValueError):
    def __init__(self, filename: str):
        super().__init__(f'TOML file "{filename}" contains syntax errors.')
