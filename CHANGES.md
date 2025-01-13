# Changelog

* *1.3.0* (2025-01-13)
    * Added rule `PBR005` for ensuring service classes have exactly one public method called "process"
    * Added rule `PBR006` for ensuring abstract classes inherit from `abc.ABC`

* *1.2.1* (2024-12-13)
    * Allowed other imports from `datetime` module except `datetime` and `date`

* *1.2.0* (2024-12-10)
    * Added per-file exclusion list in configuration
    * Added warnings if non-existing rules are excluded in the configuration
    * Removed occurrence counter output in CLI since `pre-commit` calls the linter recursively

* *1.1.2* (2024-12-09)
    * Removed success message since `pre-commit` runs any linter *x* times

* *1.1.1* (2024-12-09)
    * Fixed a bug that caused `PBR004` not to be executed

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
