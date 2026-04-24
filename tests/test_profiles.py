"""Smoke tests for the film profile registry.

These catch typos in profile definitions, missing required fields, and
regressions where a profile silently disappears from the registry.
"""

from __future__ import annotations

import pytest

from core import get_profile


# The profiles explicitly advertised in README.md. If any of these stop
# resolving, README examples break.
ADVERTISED_PROFILES = [
    "tri-x",
    "hp5",
    "tmax100",
    "delta3200",
    "panf",
    "portra400",
    "ektar100",
    "superia400",
    "ultramax400",
]


@pytest.mark.parametrize("name", ADVERTISED_PROFILES)
def test_advertised_profiles_resolve(name: str) -> None:
    profile = get_profile(name)
    assert profile is not None
    assert profile.name  # non-empty
    assert profile.mu_r > 0
    assert profile.sigma_r >= 0
    assert profile.filter_sigma > 0


def test_color_profiles_have_per_channel_params() -> None:
    """Color profiles need 3 per-channel grain sizes."""
    for name in ("portra400", "ektar100", "superia400", "ultramax400"):
        p = get_profile(name)
        assert p.color is True
        assert len(p.channel_mu_r) == 3
        assert len(p.channel_sigma_r) == 3
        assert all(x > 0 for x in p.channel_mu_r)


def test_unknown_profile_raises() -> None:
    with pytest.raises(KeyError):
        get_profile("this-profile-does-not-exist")
