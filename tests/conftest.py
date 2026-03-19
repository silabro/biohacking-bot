"""
Shared pytest fixtures for Silabro Biohacking Bot.

Database and Redis fixtures will be added in Task 1.2 / Task 2.2.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def anyio_backend() -> str:
    """Force asyncio backend for all async tests."""
    return "asyncio"
