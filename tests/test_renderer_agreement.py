"""Fast-vs-MC agreement test.

The README claims the fast analytical renderer matches the Monte Carlo
Boolean model in expectation. This test checks that the per-pixel mean of
many MC realizations converges to the fast-renderer output, averaged over
many fast-renderer realizations — i.e., the two renderers agree on the
signal-dependent mean even if individual realizations differ in texture.

Marked `slow` so it can be excluded from fast CI runs.
"""

from __future__ import annotations

import numpy as np
import pytest

from core import (
    render_grayscale,
    render_grayscale_fast,
    warmup_jit,
)


@pytest.mark.slow
def test_fast_and_mc_means_agree_on_ramp(gray_ramp: np.ndarray) -> None:
    # Warm up JIT so it doesn't count against per-call variance intuition
    warmup_jit()

    mu_r, sigma_r = 0.05, 0.01

    # Average a handful of realizations of each renderer
    n_trials = 3
    fast_sum = np.zeros(gray_ramp.shape, dtype=np.float64)
    for s in range(n_trials):
        fast_sum += render_grayscale_fast(
            gray_ramp, mu_r, sigma_r, seed=s
        ).astype(np.float64)
    fast_mean = fast_sum / n_trials

    mc_sum = np.zeros(gray_ramp.shape, dtype=np.float64)
    for s in range(n_trials):
        mc_sum += render_grayscale(
            gray_ramp, mu_r, sigma_r, n_mc=50, seed=s
        ).astype(np.float64)
    mc_mean = mc_sum / n_trials

    # Compare column-averaged profiles (averages out grain noise, leaves
    # the signal-dependent response). The ramp is horizontal so rows are
    # redundant.
    fast_profile = fast_mean.mean(axis=0)
    mc_profile = mc_mean.mean(axis=0)

    # Allow a generous tolerance — this is statistical agreement, not
    # pixel-perfect. If this fails by a lot, the renderers disagree on the
    # tonal response, which is the signature of a real bug.
    diff = np.abs(fast_profile - mc_profile)
    assert diff.mean() < 8.0, (
        f"Fast vs MC ramp mean differs too much: "
        f"mean abs diff = {diff.mean():.2f}, max = {diff.max():.2f}"
    )
