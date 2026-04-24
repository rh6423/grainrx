"""Reproducibility tests.

The CLI advertises `--seed` as producing the same grain pattern on repeat
runs. These tests lock that contract in.
"""

from __future__ import annotations

import numpy as np

from core import render_grayscale_fast, render_color_fast


def test_fast_grayscale_seed_is_deterministic(gray_ramp: np.ndarray) -> None:
    a = render_grayscale_fast(gray_ramp, mu_r=0.05, sigma_r=0.01, seed=42)
    b = render_grayscale_fast(gray_ramp, mu_r=0.05, sigma_r=0.01, seed=42)
    np.testing.assert_array_equal(a, b)


def test_fast_grayscale_different_seed_differs(gray_ramp: np.ndarray) -> None:
    a = render_grayscale_fast(gray_ramp, mu_r=0.05, sigma_r=0.01, seed=42)
    b = render_grayscale_fast(gray_ramp, mu_r=0.05, sigma_r=0.01, seed=7)
    # Nearly-zero probability of these being pixelwise equal; assert at least
    # some pixels differ.
    assert not np.array_equal(a, b)


def test_fast_color_seed_is_deterministic(color_ramp: np.ndarray) -> None:
    mu = [0.05, 0.05, 0.06]
    sigma = [0.01, 0.01, 0.015]
    a = render_color_fast(color_ramp, mu, sigma, seed=123)
    b = render_color_fast(color_ramp, mu, sigma, seed=123)
    np.testing.assert_array_equal(a, b)


def test_fast_output_shape_matches_input(gray_ramp: np.ndarray) -> None:
    out = render_grayscale_fast(gray_ramp, mu_r=0.05, sigma_r=0.01, seed=0)
    assert out.shape == gray_ramp.shape
    assert out.dtype == np.uint8
