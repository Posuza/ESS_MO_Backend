"""
app.core.registries
-------------------
Public surface — import from here, not from sub-modules directly.

    from app.core.registries import ACTION_REGISTRY, ERROR_REGISTRY
"""

from app.core.registries.action_registry import ACTION_REGISTRY
from app.core.registries.error_registry import ERROR_REGISTRY

__all__ = ["ACTION_REGISTRY", "ERROR_REGISTRY"]
