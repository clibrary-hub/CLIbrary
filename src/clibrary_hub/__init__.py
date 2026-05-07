"""
clibrary-hub — Production-grade tool routing for AI agents.

Quick usage::

    # Route an intent to a CLI
    from clibrary_hub import router
    result = router.route("查上週銷售總額")

    # Validate a manifest you wrote
    from clibrary_hub import validator
    r = validator.validate_file("my-tool.json")
    if not r.ok:
        for e in r.errors: print("ERROR:", e)

The package makes no external API calls. Path B of the router returns
empty params; the caller decides how to fill them.
"""

from clibrary_hub.router import CLIbrary
from clibrary_hub import validator

__version__ = "0.2.0"


class _DefaultRouter:
    """Lazy-initialized default router. Forwards every attribute to a real
    ``CLIbrary`` instance built on first access."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = None

    def _get(self) -> CLIbrary:
        if self._impl is None:
            self._impl = CLIbrary()
        return self._impl

    def __getattr__(self, name):
        return getattr(self._get(), name)

    def __repr__(self) -> str:
        state = "loaded" if self._impl is not None else "not loaded yet"
        return f"<clibrary_hub.router default CLIbrary ({state})>"


router = _DefaultRouter()

__all__ = ["CLIbrary", "router", "validator"]
