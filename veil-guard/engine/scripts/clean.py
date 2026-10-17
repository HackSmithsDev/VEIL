"""Remove generated Engine build and distribution artifacts."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def clean_artifacts() -> list[Path]:
    """Remove only known build outputs located directly under the Engine root."""
    targets = [
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "dist",
        PROJECT_ROOT / "libs" / "veil_guard_engine.egg-info",
    ]
    allowed_parents = {PROJECT_ROOT, PROJECT_ROOT / "libs"}
    removed: list[Path] = []

    for target in targets:
        if not target.exists() and not target.is_symlink():
            continue
        if target.parent not in allowed_parents:
            raise ValueError(f"Refusing to clean path outside the Engine root: {target}")
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
        removed.append(target)

    return removed


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    for artifact in clean_artifacts():
        print(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())