"""Fixture module that raises a non-ImportError at import time.

Used to verify the custom-rules loader frames generic module-load failures
instead of letting them propagate raw (e.g. Django's ImproperlyConfigured).
"""

raise RuntimeError("simulated module-import-time failure")  # noqa: TRY003
