"""
Smoke test — validates that the project structure is importable.

This test exists to satisfy the 80% coverage gate during the
infrastructure-only phase (Task 1.1).  Real unit tests arrive
starting from Task 1.3+.
"""

from __future__ import annotations


def test_app_package_importable() -> None:
    """The root 'app' package must be importable without errors."""
    import app  # noqa: F401

    assert app.__doc__ is not None


def test_main_function_exists() -> None:
    """The entry-point function must be defined."""
    from app.__main__ import main

    assert callable(main)
