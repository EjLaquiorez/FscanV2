"""Pytest fixtures: repo root on path, deterministic RNG where needed."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _deterministic_numpy_random():
    np.random.seed(123)
    yield
    np.random.seed()
