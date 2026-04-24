"""Console script entry point for the `grainrx` command.

Declared in pyproject.toml as:
    [project.scripts]
    grainrx = "core.cli:main"

This module just re-exports `main` from the top-level `render.py` so that
`python render.py ...` and `grainrx ...` behave identically.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    # Ensure the repo root (which contains render.py) is importable when
    # the package is installed in editable mode from the repo.
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from render import main as _render_main
    _render_main()


if __name__ == "__main__":
    main()
