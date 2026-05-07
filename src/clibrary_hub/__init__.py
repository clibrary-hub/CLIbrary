"""
clibrary-hub — Production-grade tool routing for AI agents.

Quick usage::

    from clibrary_hub import router
    result = router.route("查上週銷售總額")

The ``router`` symbol is a lazy-initialized default ``CLIbrary`` instance.
The first call to any method loads the model and FAISS indices; subsequent
calls reuse them. For full control, instantiate ``CLIbrary`` yourself.
"""

from clibrary_hub.router import CLIbrary

__version__ = "0.1.5"


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

__all__ = ["CLIbrary", "router"]
