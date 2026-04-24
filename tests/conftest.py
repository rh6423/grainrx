"""Shared fixtures for grainrx tests."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def gray_ramp() -> np.ndarray:
    """A small horizontal gray ramp, uint8, 64x128.

    Horizontal ramp (dark on the left, bright on the right) is a useful test
    input because it exercises the full tonal range of the grain model in a
    single image without needing test assets on disk.
    """
    w, h = 128, 64
    ramp = np.linspace(0, 255, w, dtype=np.float32)
    img = np.tile(ramp, (h, 1))
    return img.astype(np.uint8)


@pytest.fixture
def color_ramp(gray_ramp: np.ndarray) -> np.ndarray:
    """Same ramp stacked into 3 channels."""
    return np.stack([gray_ramp, gray_ramp, gray_ramp], axis=-1)
