# Changelog

* *1.1.0* (2024-12-09)
    * Added rule `PBR003` for prohibiting import nested datetime from datetime module
    * Added rule `PBR004` for enforcing `kw_only` parameter for dataclasses
    * Moved AST creation from rule declaration to cli level for performance reasons

* *1.0.3* (2024-12-02)
    * Re-added Django dependency
    * Added ruff linting rules

* *1.0.2* (2024-12-02)
    * Fixed sphinx docs

* *1.0.1* (2024-12-02)
    * Added forgotten changelog
    * Added docs for git tags for pre-commit

* *1.0.0* (2024-12-02)
    * Added rule `PBR001` for enforcing kwargs in functions and methods
    * Added rule `PBR002` for enforcing return type-hints when a function contains a return statement
    * Project setup and configuration
